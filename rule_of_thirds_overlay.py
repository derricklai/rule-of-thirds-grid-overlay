import cv2
import sys
import time
import os
from tqdm import tqdm
import argparse
import shutil
import subprocess

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

def video_is_complete(video_path, total_frames):
    frames = count_video_frames(video_path)
    return frames >= total_frames

def restore_audio(processed_video, original_video, output_with_audio):
    print("\nRestoring audio using FFmpeg...")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", processed_video,
        "-i", original_video,
        "-c", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_with_audio
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio restored: {output_with_audio}")
        return True
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed to add audio. Please ensure FFmpeg is installed and in your PATH.")
        print(e.stderr.decode())
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Overlay a rule of thirds grid on a video. "
                    "Safe to interrupt and resume: "
                    "resumes video processing or audio muxing as needed."
    )
    parser.add_argument("input_video", help="Input video file (mp4, mkv, avi, etc.)")
    parser.add_argument("--continue", dest="continue_run", action="store_true",
                        help="Resume processing from last saved frame or audio muxing if interrupted.")
    args = parser.parse_args()

    input_path = args.input_video
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    output_filename = "output_" + input_filename
    temp_output_filename = "temp_" + output_filename
    final_output_with_audio = os.path.join(input_dir, "final_" + input_filename)
    output_path = os.path.join(input_dir, output_filename)
    temp_output_path = os.path.join(input_dir, temp_output_filename)

    # Get video info
    cap_in = cv2.VideoCapture(input_path)
    if not cap_in.isOpened():
        print("Error opening input video file.")
        sys.exit(1)
    total_frames = int(cap_in.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap_in.get(cv2.CAP_PROP_FPS)
    width = int(cap_in.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap_in.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_in.release()

    # If temp file exists, delete it (likely corrupt)
    if os.path.exists(temp_output_path):
        print(f"Deleting leftover temp file: {temp_output_path} (likely corrupt from previous interruption)")
        os.remove(temp_output_path)

    # Resume logic: only from finalized output file
    start_frame = 0
    video_done = False

    if os.path.exists(final_output_with_audio):
        if video_is_complete(final_output_with_audio, total_frames):
            print(f"Final video with audio already exists and is complete: {final_output_with_audio}")
            print("Nothing to do.")
            return
        else:
            print(f"Final video with audio exists but is incomplete. Will attempt to resume.")
            os.remove(final_output_with_audio)

    if args.continue_run and os.path.exists(output_path):
        # Resume from finalized output file
        start_frame = count_video_frames(output_path)
        if start_frame > 0:
            print(f"Resuming: {start_frame} frames already processed in {output_path}.")
            if start_frame >= total_frames:
                print("All video frames already processed.")
                video_done = True
        else:
            print(f"{output_path} exists but contains no frames. Starting from scratch.")
            start_frame = 0
    elif args.continue_run:
        print("No existing output file found. Starting from scratch.")
        start_frame = 0
    else:
        print("Starting from scratch.")
        start_frame = 0

    # If video is done but audio is not, just mux audio
    if args.continue_run and os.path.exists(output_path) and video_is_complete(output_path, total_frames):
        print("Video processing is already complete. Restoring audio if needed...")
        if restore_audio(output_path, input_path, final_output_with_audio):
            print(f"Final video with audio: {final_output_with_audio}")
        return

    # If video is not done, process video
    if not video_done:
        cap_in = cv2.VideoCapture(input_path)
        cap_in.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

        # If resuming, copy already processed frames from output file
        if args.continue_run and os.path.exists(output_path) and start_frame > 0:
            cap_out = cv2.VideoCapture(output_path)
            for i in tqdm(range(start_frame), desc="Copying previous output", unit="frame"):
                ret, frame = cap_out.read()
                if not ret:
                    print(f"Warning: Could not read frame {i} from {output_path}.")
                    break
                out.write(frame)
            cap_out.release()

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

        # Replace (or create) output file with new complete file
        shutil.move(temp_output_path, output_path)

        elapsed = time.time() - start_time
        print(f"\nOverlay video saved to {output_path}")
        print(f"Total processing time: {elapsed:.2f} seconds")

    # Restore audio using FFmpeg (if not already done)
    if not os.path.exists(final_output_with_audio) or not video_is_complete(final_output_with_audio, total_frames):
        restore_audio(output_path, input_path, final_output_with_audio)
        print(f"Final video with audio: {final_output_with_audio}")

if __name__ == "__main__":
    main()
