# Rule of Thirds Video Overlay CLI Tool

A Python script to overlay a **Rule of Thirds grid** on videos with:

- Support for **pausing and resuming** processing safely
- Automatic **audio restoration** from the original video using FFmpeg
- Robust handling of interruptions without losing progress
- Progress bars for visual feedback during processing

---

## Features

- Draws a white Rule of Thirds grid on every frame of your video
- Resumes video processing from where it left off if interrupted (only from finalized output files)
- Automatically restores original audio after processing video frames
- Supports common video formats (MP4, MKV, AVI, etc.)
- Uses `tqdm` for progress bars during processing
- Requires FFmpeg installed and available in your system PATH

---

## Requirements

- Python 3.7 or higher
- [OpenCV](https://pypi.org/project/opencv-python/)
- [tqdm](https://pypi.org/project/tqdm/)
- [FFmpeg](https://ffmpeg.org/) (must be installed and accessible from the command line)

---

## Installation

1. **Clone the repository** (or download the script):

   ```
   git clone https://github.com/yourusername/rule-of-thirds-overlay.git
   cd rule-of-thirds-overlay
   ```

2. **Install Python dependencies:**

   ```
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**

   - **macOS:**
     ```
     brew install ffmpeg
     ```
   - **Ubuntu/Debian:**
     ```
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **Windows:**  
     Download from [FFmpeg official site](https://ffmpeg.org/download.html) and add to your PATH.

   Verify installation by running:

   ```
   ffmpeg -version
   ```

---

## Usage

Run the script with your input video file:

`python3 rule_of_thirds_overlay.py "input_video.mp4`

### Resume Processing After Interruption

If the script is interrupted (e.g., Ctrl+C), you can safely resume processing with:

`python3 rule_of_thirds_overlay.py --continue "input_video.mp4`

The script will:

- Resume video processing from the last finalized output file
- If video processing is complete but audio muxing was interrupted, it will resume adding audio

### Output Files

- `output_<input_video>` - Video with the Rule of Thirds grid overlay, **without audio**
- `final_<input_video>` - Final video with the overlay **and original audio restored**

---

## Docker Usage

You can run this script anywhere with Docker, no Python or FFmpeg installation required on your host.

### 1. Build the Docker Image

Clone this repo and build the image:

```
git clone https://github.com/yourusername/rule-of-thirds-overlay.git
cd rule-of-thirds-overlay
docker build -t thirds-overlay .
```

### 2. Run the Script with Docker

Mount your video folder as a volume (replace `/path/to/videos` with your actual path):

```
docker run --rm -v /path/to/videos:/data thirds-overlay python rule_of_thirds_overlay.py /data/your_video.mp4
```

To **resume processing** after interruption:

```
docker run --rm -v /path/to/videos:/data thirds-overlay python rule_of_thirds_overlay.py --continue /data/your_video.mp4
```

- All output files will appear in your local `/path/to/videos` directory.

### 3. Notes

- You can use any folder on your host for videos and results.
- The Docker image includes Python, OpenCV, tqdm, and FFmpeg.
- If you update the script or requirements, rebuild the image (`docker build ...`).

---

## Included Files

##### `requirements.txt`

```
opencv-python
tqdm
```

##### `Dockerfile`

```
# Use official Python image
FROM python:3.10-slim

# Install ffmpeg and OpenCV dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script(s) into the container
COPY rule_of_thirds_overlay.py .

# Default command (can be overridden)
CMD ["python", "rule_of_thirds_overlay.py", "--help"]
```

---

## How It Works

1. **Video Processing:**  
   The script processes frames, draws the grid, and writes to a temporary file.  
   On completion, it replaces the output file with the temp file.

2. **Resuming:**

   - Resumes only from the finalized output file (never from temp files to avoid corruption).
   - If no output file exists, it starts fresh.

3. **Audio Restoration:**  
   Uses FFmpeg to mux the original audio track with the processed video, producing the final output.

---

## Sample Output

- todo

## Future Features

- Batch processing
- IINA Plugin
- Parallel processing

## Troubleshooting

- **Temp file corruption:**  
  If the script is interrupted, the temp file may be incomplete and unreadable. The script deletes temp files on startup to prevent errors.

- **FFmpeg errors:**  
  Ensure FFmpeg is installed and in your system PATH. Run `ffmpeg -version` to verify.

- **Unsupported video formats:**  
  OpenCV supports most common formats, but some codecs may not be supported. Convert your video to MP4 (H.264) if you encounter issues.

- **Performance:**  
  Processing large videos can be CPU-intensive. Consider running on a machine with sufficient resources.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open a GitHub issue or submit a pull request.

---

## Acknowledgments

- [OpenCV](https://opencv.org/) for video processing
- [tqdm](https://github.com/tqdm/tqdm) for progress bars
- [FFmpeg](https://ffmpeg.org/) for audio muxing

---

**Enjoy!** 🎥✨
