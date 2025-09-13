import os
import subprocess
from pathlib import Path

def concat_audio_files(input_files, output_file):
    """
    Concatenate multiple audio files into one
    
    Args:
        input_files (list): List of paths to input audio files
        output_file (str): Path for the output audio file
    """
    try:
        # Create a temporary file listing all input files
        temp_list = 'temp_file_list.txt'
        
        # Write the file list
        with open(temp_list, 'w') as f:
            for audio_file in input_files:
                f.write(f"file '{audio_file}'\n")
        
        # Construct the ffmpeg command
        command = [
            'ffmpeg',
            '-f', 'concat',           # Use concat demuxer
            '-safe', '0',             # Don't restrict file paths
            '-i', temp_list,          # Input from the list file
            '-c', 'copy',             # Copy streams without re-encoding
            output_file               # Output file
        ]
        
        # Execute the command
        print("Starting audio concatenation...")
        subprocess.run(command, check=True)
        print(f"Successfully concatenated audio files to: {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while concatenating: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_list):
            os.remove(temp_list)

def main():
    print("Audio File Concatenation Tool")
    print("-" * 30)
    
    # Get input files
    input_files = []
    while True:
        file_path = input("Enter path to audio file (or press Enter to finish): ").strip()
        if not file_path:
            break
        
        if os.path.exists(file_path):
            input_files.append(file_path)
        else:
            print(f"Warning: File '{file_path}' does not exist. Skipping.")
    
    if not input_files:
        print("No valid input files provided.")
        return
    
    # Get output file path
    output_file = input("Enter the output file path: ").strip()
    if not output_file:
        print("No output file specified.")
        return
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Perform concatenation
    concat_audio_files(input_files, output_file)

if __name__ == "__main__":
    main()
