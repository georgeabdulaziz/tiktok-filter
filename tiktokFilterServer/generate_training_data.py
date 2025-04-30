import cv2
import numpy as np
import os
import random
import argparse

def generate_training_data(video_path, output_folder, watermark_coords):
    # Create output folders
    os.makedirs(f"{output_folder}/images", exist_ok=True)
    os.makedirs(f"{output_folder}/masks", exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Skip frames to get variety (e.g., every 10th frame)
        if frame_count % 10 == 0:
            # Save original frame
            cv2.imwrite(f"{output_folder}/images/frame_{frame_count}.png", frame)
            
            # Create mask (black background with white watermark area)
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            x, y, w, h = watermark_coords
            mask[y:y+h, x:x+w] = 255
            
            # Save mask
            cv2.imwrite(f"{output_folder}/masks/frame_{frame_count}_mask.png", mask)
            
        frame_count += 1
    
    cap.release()

def process_multiple_videos(video_folder, output_folder):
    # Define watermark coordinates (you'll need to adjust these values)
    watermark_coords = (100, 100, 200, 50)  # x, y, width, height
    
    for video_file in os.listdir(video_folder):
        if video_file.endswith(('.mp4', '.avi')):
            video_path = os.path.join(video_folder, video_file)
            print(f"Processing video: {video_file}")
            generate_training_data(video_path, output_folder, watermark_coords)

def generate_synthetic_data(background_images, watermark, num_samples, output_folder):
    # Create output directory
    os.makedirs(f"{output_folder}/synth_images", exist_ok=True)
    os.makedirs(f"{output_folder}/synth_masks", exist_ok=True)
    
    # Filter out background images that are too small
    valid_backgrounds = [bg for bg in background_images 
                        if bg.shape[0] > watermark.shape[0] and 
                           bg.shape[1] > watermark.shape[1]]
    
    if not valid_backgrounds:
        print("Warning: No background images are large enough for the watermark")
        return
        
    for i in range(num_samples):
        # Randomly select background from valid backgrounds
        bg = random.choice(valid_backgrounds)
        
        # Random position for watermark
        x = np.random.randint(0, bg.shape[1] - watermark.shape[1])
        y = np.random.randint(0, bg.shape[0] - watermark.shape[0])
        
        # Create image with watermark
        image = bg.copy()
        # Blend watermark with background (instead of direct replacement)
        alpha = 0.7  # Watermark transparency
        image[y:y+watermark.shape[0], x:x+watermark.shape[1]] = \
            cv2.addWeighted(image[y:y+watermark.shape[0], x:x+watermark.shape[1]], 1-alpha,
                           watermark, alpha, 0)
        
        # Create corresponding mask
        mask = np.zeros(bg.shape[:2], dtype=np.uint8)
        mask[y:y+watermark.shape[0], x:x+watermark.shape[1]] = 255
        
        # Save both
        cv2.imwrite(f"{output_folder}/synth_images/image_{i}.png", image)
        cv2.imwrite(f"{output_folder}/synth_masks/mask_{i}.png", mask)
        if i % 100 == 0:
            print(f"Generated {i} synthetic samples")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate training data for watermark detection')
    parser.add_argument('--output_folder', type=str, default='training_data',
                        help='Folder to store generated data')
    parser.add_argument('--video_folder', type=str, default='videos',
                        help='Folder containing input videos')
    parser.add_argument('--background_folder', type=str, default='backgrounds',
                        help='Folder containing background images')
    parser.add_argument('--watermark_path', type=str, default='watermark.png',
                        help='Path to watermark image')
    parser.add_argument('--num_synthetic', type=int, default=1000,
                        help='Number of synthetic samples to generate')
    
    args = parser.parse_args()
    
    # Create output folder
    os.makedirs(args.output_folder, exist_ok=True)
    
    # Process videos if video folder exists
    if os.path.exists(args.video_folder):
        print("Processing videos...")
        process_multiple_videos(args.video_folder, args.output_folder)
    
    # Generate synthetic data if background folder and watermark exist
    if os.path.exists(args.background_folder) and os.path.exists(args.watermark_path):
        print("Generating synthetic data...")
        # Load background images
        background_images = []
        for img_path in os.listdir(args.background_folder):
            if img_path.endswith(('.jpg', '.png')):
                img = cv2.imread(os.path.join(args.background_folder, img_path))
                if img is not None:
                    background_images.append(img)
        
        # Load watermark
        watermark = cv2.imread(args.watermark_path)
        
        if background_images and watermark is not None:
            generate_synthetic_data(background_images, watermark, args.num_synthetic, args.output_folder)
        else:
            print("Warning: Could not load background images or watermark")
    
    print("Data generation complete!")