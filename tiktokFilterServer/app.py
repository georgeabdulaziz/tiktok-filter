from flask import Flask, request, jsonify
import cv2
import numpy as np
import tensorflow as tf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

class WatermarkDetector:
    def __init__(self):
        self.model = tf.keras.models.load_model('watermark_detector_model.h5')
        
    def detect_watermark(self, frame):
        # Preprocess frame
        frame = cv2.resize(frame, (256, 256))
        frame = frame / 255.0
        frame = np.expand_dims(frame, axis=0)
        
        # Get prediction
        prediction = self.model.predict(frame, verbose=0)
        
        # Process prediction
        watermark_mask = np.squeeze(prediction[0] > 0.5)  # Ensure 2D mask
        if np.any(watermark_mask):
            y_indices, x_indices = np.where(watermark_mask)
            y1, y2 = np.min(y_indices), np.max(y_indices)
            x1, x2 = np.min(x_indices), np.max(x_indices)
            
            # Scale coordinates back to original frame size
            scale_y = frame.shape[1] / 256
            scale_x = frame.shape[2] / 256
            y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
            x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
            
            return True, (y1, y2, x1, x2)
        
        return False, None

def process_video(input_path, output_path):
    """Process video using CNN-based watermark detection"""
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    watermark_detector = WatermarkDetector()
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Detect watermark
        detected, position = watermark_detector.detect_watermark(frame)
        
        if detected:
            y1, y2, x1, x2 = position
            # Apply blur to detected region
            frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (7, 7), 0)
        
        out.write(frame)
        
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames")
    
    cap.release()
    out.release()

@app.route('/process-video', methods=['POST'])
def process_video_endpoint():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join('uploads', filename)
        output_path = os.path.join('processed', filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Process video
        process_video(input_path, output_path)
        
        return jsonify({'message': 'Video processed successfully', 'output_path': output_path})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('processed', exist_ok=True)
    
    app.run(debug=True)
