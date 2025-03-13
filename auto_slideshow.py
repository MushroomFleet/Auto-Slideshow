#!/usr/bin/env python3
"""
auto-slideshow.py - Create slideshows from images in a folder

This script takes a folder of images and creates a slideshow video with 
customizable transitions, duration, and other parameters.
"""

import os
import argparse
import configparser
import cv2
import numpy as np
import random
from glob import glob

# Define transition effects
TRANSITIONS = {
    "fade": 0,
    "wipe_left": 1,
    "wipe_right": 2,
    "wipe_up": 3,
    "wipe_down": 4,
    "zoom_in": 5,
    "zoom_out": 6,
    "slide_left": 7,
    "slide_right": 8,
}

def read_config(config_path="config.cfg"):
    """Read configuration from config file or use defaults"""
    config = configparser.ConfigParser()
    
    # Set defaults
    config["DEFAULT"] = {
        "transition_duration": "0.5",  # seconds
        "video_duration": "59",  # seconds
        "frame_rate": "25",  # FPS
        "transition_type": "random",  # Can be one of TRANSITIONS keys or "random"
        "image_duration": "3",  # seconds per image (used when no video_duration)
        "output_file": "slideshow.mp4"
    }
    
    # Read config file if it exists
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        # Create default config file
        with open(config_path, 'w') as f:
            config.write(f)
        print(f"Created default configuration file at {config_path}")
    
    return config["DEFAULT"]

def get_image_files(folder_path):
    """Get list of image files from folder"""
    # Supported image extensions
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']
    
    image_files = []
    for ext in extensions:
        image_files.extend(glob(os.path.join(folder_path, f"*{ext}")))
        image_files.extend(glob(os.path.join(folder_path, f"*{ext.upper()}")))
    
    # Sort files by name for consistent order
    image_files.sort()
    
    if not image_files:
        raise ValueError(f"No image files found in {folder_path}")
        
    return image_files

def resize_image(image, width, height):
    """Resize image to target dimensions while preserving aspect ratio"""
    # Determine if the image is already 16:9
    h, w = image.shape[:2]
    current_ratio = w / h
    target_ratio = width / height
    
    if abs(current_ratio - target_ratio) < 0.01:  # Close enough to target ratio
        return cv2.resize(image, (width, height))
    
    # Resize and crop to maintain aspect ratio and fill target dimensions
    if current_ratio > target_ratio:  # Image is wider
        new_h = height
        new_w = int(height * current_ratio)
        img_resized = cv2.resize(image, (new_w, new_h))
        # Crop to center
        start_x = (new_w - width) // 2
        return img_resized[:, start_x:start_x+width]
    else:  # Image is taller
        new_w = width
        new_h = int(width / current_ratio)
        img_resized = cv2.resize(image, (new_w, new_h))
        # Crop to center
        start_y = (new_h - height) // 2
        return img_resized[start_y:start_y+height, :]

def apply_transition(prev_frame, next_frame, transition_type, progress):
    """Apply transition effect between frames
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        transition_type: Integer indicating transition type (see TRANSITIONS)
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    if transition_type == 0:  # Fade
        return cv2.addWeighted(prev_frame, 1 - progress, next_frame, progress, 0)
    
    elif transition_type == 1:  # Wipe Left
        h, w = prev_frame.shape[:2]
        cut = int(w * progress)
        result = prev_frame.copy()
        result[:, :cut] = next_frame[:, :cut]
        return result
    
    elif transition_type == 2:  # Wipe Right
        h, w = prev_frame.shape[:2]
        cut = int(w * (1 - progress))
        result = prev_frame.copy()
        result[:, cut:] = next_frame[:, cut:]
        return result
    
    elif transition_type == 3:  # Wipe Up
        h, w = prev_frame.shape[:2]
        cut = int(h * progress)
        result = prev_frame.copy()
        result[:cut, :] = next_frame[:cut, :]
        return result
    
    elif transition_type == 4:  # Wipe Down
        h, w = prev_frame.shape[:2]
        cut = int(h * (1 - progress))
        result = prev_frame.copy()
        result[cut:, :] = next_frame[cut:, :]
        return result
    
    elif transition_type == 5:  # Zoom In
        h, w = prev_frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # For zoom in, start with next_frame small and grow it
        zoom_factor = progress
        if zoom_factor < 0.1:  # Avoid too small scaling
            zoom_factor = 0.1
            
        # Size of the scaled image
        scaled_w = int(w * zoom_factor)
        scaled_h = int(h * zoom_factor)
        
        # Ensure minimum size
        scaled_w = max(scaled_w, 10)
        scaled_h = max(scaled_h, 10)
        
        # Resize next_frame
        scaled_next = cv2.resize(next_frame, (scaled_w, scaled_h))
        
        # Create result with prev_frame as background
        result = prev_frame.copy()
        
        # Calculate position to place the scaled image centered
        start_x = max(0, center_x - scaled_w // 2)
        start_y = max(0, center_y - scaled_h // 2)
        end_x = min(w, start_x + scaled_w)
        end_y = min(h, start_y + scaled_h)
        
        # Account for partial image placement near edges
        scaled_start_x = 0
        scaled_start_y = 0
        if start_x == 0:
            scaled_start_x = (scaled_w - (end_x - start_x)) // 2
        if start_y == 0:
            scaled_start_y = (scaled_h - (end_y - start_y)) // 2
            
        # Place scaled image onto result
        try:
            result[start_y:end_y, start_x:end_x] = scaled_next[
                scaled_start_y:scaled_start_y + (end_y - start_y), 
                scaled_start_x:scaled_start_x + (end_x - start_x)
            ]
        except ValueError:
            # Fallback to fade if dimensions don't align
            return cv2.addWeighted(prev_frame, 1 - progress, next_frame, progress, 0)
        
        return result
        
    elif transition_type == 6:  # Zoom Out
        h, w = prev_frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # For zoom out, start with prev_frame full size and shrink it
        zoom_factor = 1 - progress
        if zoom_factor < 0.1:  # Avoid too small scaling
            zoom_factor = 0.1
            
        # Size of the scaled image
        scaled_w = int(w * zoom_factor)
        scaled_h = int(h * zoom_factor)
        
        # Ensure minimum size
        scaled_w = max(scaled_w, 10)
        scaled_h = max(scaled_h, 10)
        
        # Resize prev_frame
        scaled_prev = cv2.resize(prev_frame, (scaled_w, scaled_h))
        
        # Create result with next_frame as background
        result = next_frame.copy()
        
        # Calculate position to place the scaled image centered
        start_x = max(0, center_x - scaled_w // 2)
        start_y = max(0, center_y - scaled_h // 2)
        end_x = min(w, start_x + scaled_w)
        end_y = min(h, start_y + scaled_h)
        
        # Account for partial image placement near edges
        scaled_start_x = 0
        scaled_start_y = 0
        if start_x == 0:
            scaled_start_x = (scaled_w - (end_x - start_x)) // 2
        if start_y == 0:
            scaled_start_y = (scaled_h - (end_y - start_y)) // 2
            
        # Place scaled image onto result
        try:
            result[start_y:end_y, start_x:end_x] = scaled_prev[
                scaled_start_y:scaled_start_y + (end_y - start_y), 
                scaled_start_x:scaled_start_x + (end_x - start_x)
            ]
        except ValueError:
            # Fallback to fade if dimensions don't align
            return cv2.addWeighted(prev_frame, 1 - progress, next_frame, progress, 0)
        
        return result
    
    elif transition_type == 7:  # Slide Left
        h, w = prev_frame.shape[:2]
        offset = int(w * progress)
        
        result = np.zeros_like(prev_frame)
        # Place part of prev_frame
        if offset < w:
            result[:, :w-offset] = prev_frame[:, offset:]
        
        # Place part of next_frame
        if offset > 0:
            result[:, w-offset:] = next_frame[:, :offset]
            
        return result
        
    elif transition_type == 8:  # Slide Right  
        h, w = prev_frame.shape[:2]
        offset = int(w * progress)
        
        result = np.zeros_like(prev_frame)
        # Place part of prev_frame
        if offset < w:
            result[:, offset:] = prev_frame[:, :w-offset]
        
        # Place part of next_frame
        if offset > 0:
            result[:, :offset] = next_frame[:, w-offset:]
            
        return result
        
    else:
        # Default to simple crossfade if transition not recognized
        return cv2.addWeighted(prev_frame, 1 - progress, next_frame, progress, 0)

def create_slideshow(image_files, config):
    """Create slideshow video from images"""
    # Parse configuration
    transition_duration = float(config["transition_duration"])
    video_duration = float(config["video_duration"])
    frame_rate = int(config["frame_rate"])
    output_file = config["output_file"]
    
    # Determine transition type
    transition_type_config = config["transition_type"]
    if transition_type_config == "random":
        use_random_transitions = True
        transition_type = None  # Will be selected randomly for each transition
    else:
        use_random_transitions = False
        if transition_type_config in TRANSITIONS:
            transition_type = TRANSITIONS[transition_type_config]
        else:
            print(f"Warning: Unknown transition type '{transition_type_config}'. Using 'fade' instead.")
            transition_type = 0  # Default to fade
    
    # Calculate timing
    num_images = len(image_files)
    total_transitions = num_images - 1
    
    # Calculate image duration needed to achieve target video duration
    total_transition_time = total_transitions * transition_duration
    remaining_time = video_duration - total_transition_time
    
    if remaining_time <= 0:
        raise ValueError(f"Transition time ({total_transition_time}s) exceeds video duration ({video_duration}s)")
    
    image_duration = remaining_time / num_images
    print(f"Using {image_duration:.2f} seconds per image and {transition_duration:.2f} seconds per transition")
    
    # Open first image to get dimensions
    first_image = cv2.imread(image_files[0])
    if first_image is None:
        raise ValueError(f"Could not read image: {image_files[0]}")
    
    h, w = first_image.shape[:2]
    
    # Target 16:9 aspect ratio if not already
    target_w = w
    target_h = int(w * 9 / 16)
    if abs(target_h - h) > 5:  # If height differs significantly from 16:9
        print(f"Images are not 16:9. Will resize from {w}x{h} to {target_w}x{target_h}")
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use mp4v codec
    out = cv2.VideoWriter(output_file, fourcc, frame_rate, (target_w, target_h))
    
    if not out.isOpened():
        raise ValueError(f"Could not open output video file: {output_file}")
    
    # Process images
    prev_image = None
    frame_count = 0
    total_frames = int(video_duration * frame_rate)
    
    print(f"Creating slideshow with {num_images} images, {total_frames} frames...")
    
    for i, img_path in enumerate(image_files):
        # Read and resize current image
        curr_img = cv2.imread(img_path)
        if curr_img is None:
            print(f"Warning: Could not read image: {img_path}, skipping...")
            continue
            
        curr_img = resize_image(curr_img, target_w, target_h)
        
        # For the first image, no transition needed
        if i == 0:
            # Add frames for the first image duration
            frames_per_image = int(image_duration * frame_rate)
            for _ in range(frames_per_image):
                if frame_count < total_frames:
                    out.write(curr_img)
                    frame_count += 1
        else:
            # Choose transition for this pair of images
            if use_random_transitions:
                curr_transition = random.randint(0, 8)  # Random transition from 0-8
            else:
                curr_transition = transition_type
            
            # Add transition frames
            transition_frames = int(transition_duration * frame_rate)
            for j in range(transition_frames):
                if frame_count < total_frames:
                    progress = j / transition_frames
                    frame = apply_transition(prev_image, curr_img, curr_transition, progress)
                    out.write(frame)
                    frame_count += 1
            
            # Add frames for current image duration (after transition)
            frames_per_image = int(image_duration * frame_rate)
            for _ in range(frames_per_image):
                if frame_count < total_frames:
                    out.write(curr_img)
                    frame_count += 1
        
        # Update prev_image for next iteration
        prev_image = curr_img
        
        # Print progress
        progress_pct = min(100, int((frame_count / total_frames) * 100))
        print(f"Progress: {progress_pct}% ({frame_count}/{total_frames} frames)", end='\r')
    
    # Release resources
    out.release()
    print(f"\nSlideshow created successfully: {output_file}")
    print(f"Video duration: {frame_count/frame_rate:.2f} seconds, {frame_count} frames at {frame_rate} FPS")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Create a slideshow from images in a folder")
    parser.add_argument("folder", help="Folder containing the images")
    parser.add_argument("-c", "--config", default="config.cfg", help="Path to configuration file")
    parser.add_argument("-o", "--output", help="Output file path (overrides config)")
    args = parser.parse_args()
    
    # Verify folder exists
    if not os.path.isdir(args.folder):
        parser.error(f"Folder does not exist: {args.folder}")
    
    # Read configuration
    config = read_config(args.config)
    
    # Override output file if specified
    if args.output:
        config["output_file"] = args.output
    
    # Get list of image files
    try:
        image_files = get_image_files(args.folder)
        if len(image_files) < 2:
            print("Error: At least 2 images are required to create a slideshow")
            return 1
            
        print(f"Found {len(image_files)} images in {args.folder}")
        
        # Create slideshow
        create_slideshow(image_files, config)
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())