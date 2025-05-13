import cv2
import sys
import time
import os
from tqdm import tqdm
import argparse
import shutil

def draw_rule_of_thirds(frame):
    height, width = frame.shape[:2]
    third_w = width // 3
    third_h = height // 3
    color = (255, 255, 255)
    thickness = 2
    cv2.line(frame, (third_w, 0), (third_w, height), color, thickness)
    cv2.line(frame, (2 * third_w, 0), (2 * third_w, height), color, thickness)
    cv2.line(frame, (0, third_h), (width, third_h), color, thickness)
    cv2.line(frame, (0, 2 * third_h), (width, 2 * third_h), color, thickness)
    return frame

def count_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total

def main():
    parser = argparse.ArgumentParser(
        description="Overlay a rule of thirds grid on a video. Use --continue to resume processing after interruption. Progress is saved in a .progress file next to the output."
    )
    parser.add_argument("input_video", help="Input video file (mp4, mkv, avi, etc.)")
    parser.add_argument("--continue", dest="continue_run", action="store_true",
                        help="Resume processing from last saved frame if interrupted and append to previous output.")
    args = parser.parse_args()

    input_path = args.input_video
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    output_filename = "output_" + input_filename
    output_path = os.path.join(input_dir, output_filename)
    temp_output_path = os.path.join(input_dir, "temp_" + output_filename)

    cap_in = cv2.VideoCapture(input_path)
    if not cap_in.isOpened():
        print("Error opening input video file.")
        sys.exit(1)

    total_frames = int(cap_in.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap_in.get(cv2.CAP_PROP_FPS)
    width = int(cap_in.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap_in.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_frame = 0
    if args.continue_run and os.path.exists(output_path):
        # Count frames already processed in output video
        start_frame = count_video_frames(output_path)
        print(f"Resuming: {start_frame} frames already processed in {output_path}.")
    else:
        print("Starting from scratch.")

    # Prepare temporary output file
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

    # If resuming, copy already processed frames from old output
    if start_frame > 0:
        cap_out = cv2.VideoCapture(output_path)
        for i in tqdm(range(start_frame), desc="Copying previous output", unit="frame"):
            ret, frame = cap_out.read()
            if not ret:
                break
            out.write(frame)
        cap_out.release()

    # Skip processed frames in input video
    cap_in.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    start_time = time.time()
    with tqdm(total=total_frames, initial=start_frame, desc="Processing video", unit="frame") as pbar:
        frame_idx = start_frame
        while True:
            ret, frame = cap_in.read()
            if not ret:
                break
            frame = draw_rule_of_thirds(frame)
            out.write(frame)
            frame_idx += 1
            pbar.update(1)

    cap_in.release()
    out.release()

    # Replace old output with new complete file
    shutil.move(temp_output_path, output_path)

    elapsed = time.time() - start_time
    print(f"\nOverlay video saved to {output_path}")
    print(f"Total processing time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
