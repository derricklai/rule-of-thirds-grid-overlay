import cv2
import sys
import time
import os
from tqdm import tqdm
import argparse

def draw_rule_of_thirds(frame):
    height, width = frame.shape[:2]
    third_w = width // 3
    third_h = height // 3
    color = (255, 255, 255)  # White color
    thickness = 2
    # Vertical lines
    cv2.line(frame, (third_w, 0), (third_w, height), color, thickness)
    cv2.line(frame, (2 * third_w, 0), (2 * third_w, height), color, thickness)
    # Horizontal lines
    cv2.line(frame, (0, third_h), (width, third_h), color, thickness)
    cv2.line(frame, (0, 2 * third_h), (width, 2 * third_h), color, thickness)
    return frame

def get_progress_file(output_path):
    return output_path + ".progress"

def save_progress(progress_file, frame_idx):
    with open(progress_file, 'w') as f:
        f.write(str(frame_idx))

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            return int(f.read())
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Overlay a rule of thirds grid on a video. "
                    "Use --continue to resume processing after interruption. "
                    "Progress is saved in a .progress file next to the output."
    )
    parser.add_argument("input_video", help="Input video file (mp4, mkv, avi, etc.)")
    parser.add_argument("--continue", dest="continue_run", action="store_true",
                        help="Resume processing from last saved frame if interrupted")
    args = parser.parse_args()

    input_path = args.input_video
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    output_filename = "output_" + input_filename
    output_path = os.path.join(input_dir, output_filename)
    progress_file = get_progress_file(output_path)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error opening video file.")
        sys.exit(1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Determine where to start
    start_frame = load_progress(progress_file) if args.continue_run else 0

    if start_frame >= total_frames:
        print("All frames have already been processed.")
        sys.exit(0)

    # Open output video (overwrite or append new frames)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # If resuming, skip frames in input and output
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    start_time = time.time()
    with tqdm(total=total_frames, initial=start_frame, desc="Processing video", unit="frame") as pbar:
        frame_idx = start_frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = draw_rule_of_thirds(frame)
            out.write(frame)
            frame_idx += 1
            # Save progress every 10 frames for efficiency
            if frame_idx % 10 == 0 or frame_idx == total_frames:
                save_progress(progress_file, frame_idx)
            pbar.update(1)

    cap.release()
    out.release()

    # Remove progress file when done
    if frame_idx >= total_frames and os.path.exists(progress_file):
        os.remove(progress_file)

    elapsed = time.time() - start_time
    print(f"\nOverlay video saved to {output_path}")
    print(f"Total processing time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
