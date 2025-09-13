import subprocess
import os
import json

def get_duration(file_path):
    """
    Get the duration of a media file using ffprobe
    """
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        file_path
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def merge_video_audio(video_path, audio_path, output_path):
    """
    Merge video and audio files using ffmpeg, with audio loop if needed
    
    Args:
        video_path (str): Path to the video file
        audio_path (str): Path to the audio file
        output_path (str): Path for the output video
    """
    try:
        # Get durations
        video_duration = get_duration(video_path)
        audio_duration = get_duration(audio_path)
        
        # Calculate how many times to loop the audio
        loop_times = int(video_duration / audio_duration + 0.5)  # Round to nearest integer
        
        print(f"Video duration: {video_duration:.2f} seconds")
        print(f"Audio duration: {audio_duration:.2f} seconds")
        print(f"Will loop audio {loop_times} times")
        
        # Construct the ffmpeg command with audio loop
        command = [
            'ffmpeg',
            '-i', video_path,    # Input video
            '-stream_loop', str(loop_times - 1),  # Loop times minus 1 (0 means play once)
            '-i', audio_path,    # Input audio
            '-c:v', 'copy',      # Copy the video stream without re-encoding
            '-c:a', 'aac',       # Convert audio to AAC codec
            '-shortest',         # Cut off at shortest input
            '-strict', 'experimental',
            output_path
        ]
        
        # Execute the command
        subprocess.run(command, check=True)
        print(f"Successfully merged video and audio to: {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while merging: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    # Get input from user
    video_path = input("Enter the path to the video file (.mp4): ")
    audio_path = input("Enter the path to the audio file (.mp3): ")
    output_path = input("Enter the path for output file (.mp4): ")
    
    # Validate input files exist
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' does not exist")
        return
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' does not exist")
        return
    
    # Merge video and audio
    merge_video_audio(video_path, audio_path, output_path)

if __name__ == "__main__":
    main()
