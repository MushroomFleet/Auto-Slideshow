# 🎬 Auto-Slideshow Generator 🎬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Create beautiful slideshows from your image collections with just one command! ✨

![Slideshow Demo](https://via.placeholder.com/800x450.png?text=Auto-Slideshow+Demo)

## 🌟 Features

- 📁 Processes entire folders of images automatically
- 🔄 8 stunning transition effects
- ⏱️ Customizable durations and timing
- 🎨 Works with any 16:9 images (auto-resizes others)
- 📺 Creates MP4 videos for easy sharing
- ⚙️ Highly configurable via config file
- 🚀 Simple command-line interface

## 📋 Requirements

- 🐍 Python 3.6 or higher
- 📚 OpenCV library
- 🧮 NumPy library

## 🔧 Installation

### Step 1: Clone this repository

```bash
git clone https://github.com/yourusername/auto-slideshow.git
cd auto-slideshow
```

### Step 2: Install dependencies

```bash
pip install opencv-python numpy
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

Create your first slideshow in seconds! 🎉

```bash
python auto-slideshow.py path/to/your/images
```

That's it! Your slideshow will be saved as `slideshow.mp4` in the current directory.

## 📘 Basic Usage

### Create a slideshow with default settings

```bash
python auto-slideshow.py my_vacation_photos
```

### Specify an output file

```bash
python auto-slideshow.py my_vacation_photos -o vacation_memories.mp4
```

### Use a custom configuration file

```bash
python auto-slideshow.py my_vacation_photos -c my_custom_config.cfg
```

## ⚙️ Configuration

The default settings are stored in `config.cfg`:

```ini
[DEFAULT]
# Duration of each transition in seconds
transition_duration = 0.5

# Total video duration in seconds
video_duration = 59

# Frames per second
frame_rate = 25

# Transition type (fade, wipe_left, wipe_right, wipe_up, wipe_down, zoom_in, zoom_out, slide_left, slide_right, or random)
transition_type = random

# Duration per image in seconds (used if calculating total video length)
image_duration = 3

# Output file name
output_file = slideshow.mp4
```

### 🔄 Available Transition Effects

1. 🌫️ **fade** - Smooth cross-dissolve between images
2. ⬅️ **wipe_left** - New image wipes in from right to left
3. ➡️ **wipe_right** - New image wipes in from left to right
4. ⬆️ **wipe_up** - New image wipes in from bottom to top
5. ⬇️ **wipe_down** - New image wipes in from top to bottom
6. 🔍 **zoom_in** - New image zooms in from center
7. 🔎 **zoom_out** - Current image zooms out to reveal new image
8. 👈 **slide_left** - Current image slides left, new image enters from right
9. 👉 **slide_right** - Current image slides right, new image enters from left

Set `transition_type = random` to use a different random effect for each transition! 🎲

## 🧙‍♂️ Advanced Usage Examples

### Create a very short slideshow (10 seconds)

```bash
# First, create a custom config file
echo "[DEFAULT]
transition_duration = 0.3
video_duration = 10
frame_rate = 30
transition_type = fade" > short.cfg

# Then run with this config
python auto-slideshow.py my_images -c short.cfg -o short_slideshow.mp4
```

### Create a slideshow with consistent zoom-in transitions

```bash
# First, create a custom config file
echo "[DEFAULT]
transition_duration = 0.7
video_duration = 120
frame_rate = 30
transition_type = zoom_in" > zoom_slideshow.cfg

# Then run with this config
python auto-slideshow.py wedding_photos -c zoom_slideshow.cfg
```

### Create a high-framerate slideshow for social media

```bash
# First, create a custom config file
echo "[DEFAULT]
transition_duration = 0.5
video_duration = 30
frame_rate = 60
transition_type = random" > social_media.cfg

# Then run with this config
python auto-slideshow.py vacation_highlights -c social_media.cfg -o instagram_story.mp4
```

## 📝 Tips and Tricks

- 🖼️ For best results, use images with the same aspect ratio (ideally 16:9)
- 📏 The script will automatically resize/crop images if they don't match the first image's dimensions
- 📁 Images are processed in alphabetical order by filename
- 🎮 To control the exact order, rename your files with numerical prefixes (e.g., 01_beach.jpg, 02_sunset.jpg)
- 🎵 Use video editing software to add music to your slideshow after creation

## 📊 Performance Notes

- 💻 Creating slideshows with many high-resolution images can be memory-intensive
- ⏱️ Processing time depends on the number of images, transition effects, and video length
- 🔄 The script shows a progress indicator while creating your slideshow

## 🤝 Contributing

Contributions are welcome! 🙌 Feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- 🎥 OpenCV team for the amazing computer vision library
- 🧮 NumPy developers for the numerical computing tools
- 🌟 All the awesome contributors to this project

---

Made with ❤️ by [Your Name]

🎬 Happy Slideshow Creating! 🎬
