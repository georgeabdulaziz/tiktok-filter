import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import os
from pathlib import Path
from torch.utils.data import Dataset

class WatermarkDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        
        self.image_files = []
        self.mask_files = []
        
        # Load real training data
        real_images_dir = os.path.join(data_dir, 'images')
        real_masks_dir = os.path.join(data_dir, 'masks')
        
        print(f"Checking directory: {real_images_dir}")
        if os.path.exists(real_images_dir):
            print(f"Found {len(os.listdir(real_images_dir))} files in images directory")
            for img_name in os.listdir(real_images_dir):
                if img_name.endswith('.png'):
                    img_path = os.path.join(real_images_dir, img_name)
                    # For real images: frame_num.png -> frame_num_mask.png
                    base_name = img_name[:-4]  # remove '.png'
                    mask_name = f"{base_name}_mask.png"
                    mask_path = os.path.join(real_masks_dir, mask_name)
                    print(f"Checking mask path: {mask_path}")
                    if os.path.exists(mask_path):
                        self.image_files.append(img_path)
                        self.mask_files.append(mask_path)
                        print(f"Added real image: {img_path}")
                    else:
                        print(f"Warning: Mask not found for {img_name}")
        
        # Load synthetic data
        synth_images_dir = os.path.join(data_dir, 'synth_images')
        synth_masks_dir = os.path.join(data_dir, 'synth_masks')
        
        print(f"Checking directory: {synth_images_dir}")
        if os.path.exists(synth_images_dir):
            print(f"Found {len(os.listdir(synth_images_dir))} files in synth_images directory")
            for img_name in os.listdir(synth_images_dir):
                if img_name.endswith('.png'):
                    img_path = os.path.join(synth_images_dir, img_name)
                    # For synthetic images: image_num.png -> mask_num.png
                    mask_name = img_name.replace('image', 'mask')
                    mask_path = os.path.join(synth_masks_dir, mask_name)
                    print(f"Checking mask path: {mask_path}")
                    if os.path.exists(mask_path):
                        self.image_files.append(img_path)
                        self.mask_files.append(mask_path)
                        print(f"Added synthetic image: {img_path}")
                    else:
                        print(f"Warning: Mask not found for {img_name}")
        
        print(f"Total image files found: {len(self.image_files)}")
        print(f"Total mask files found: {len(self.mask_files)}")

    def load_data(self):
        """Load and preprocess training data"""
        images = []
        masks = []
        
        # Assuming your data is organized in folders:
        # data_dir/
        #   ├── images/  # Original frames
        #   └── masks/   # Corresponding watermark masks
        
        for img_path, mask_path in zip(self.image_files, self.mask_files):
            # Load and preprocess image
            img = cv2.imread(img_path)
            img = cv2.resize(img, (256, 256))
            img = img / 255.0  # Normalize
            images.append(img)
            
            # Load corresponding mask
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (256, 256))
            mask = mask / 255.0  # Normalize
            masks.append(mask)
        
        return np.array(images), np.array(masks)

def build_model():
    """Build the watermark detection model"""
    model = models.Sequential([
        # Input layer
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3), padding='same'),
        layers.MaxPooling2D((2, 2), padding='same'),
        
        # Hidden layers
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2), padding='same'),
        
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2), padding='same'),
        
        # Upsampling layers to get back to original size
        layers.Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same', activation='relu'),
        layers.Conv2DTranspose(32, (3, 3), strides=(2, 2), padding='same', activation='relu'),
        layers.Conv2DTranspose(1, (3, 3), strides=(2, 2), padding='same', activation='sigmoid')
    ])
    
    return model

def train():
    # Create dataset
    dataset = WatermarkDataset('training_data')
    images, masks = dataset.load_data()
    
    # Build model
    model = build_model()
    
    # Compile model
    model.compile(optimizer='adam',
                 loss='binary_crossentropy',
                 metrics=['accuracy'])
    
    # Train model
    history = model.fit(images, masks,
                       epochs=10,
                       batch_size=32,
                       validation_split=0.2)
    
    # Save the entire model
    model.save('watermark_detector_model.h5')
    
    # Save training history
    np.save('training_history.npy', history.history)
    
    print("Model trained and saved successfully!")

if __name__ == '__main__':
    train()