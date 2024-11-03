import datetime
import subprocess


"""""
Collection of all functions related to dealing with images and videos
"""

def get_video_creation_time(path):
    try:
        result = subprocess.run(['exiftool', '-CreateDate', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting creation date: {e}")
        return None


def extract_and_convert_create_date(exif_output):
    """Extract and convert 'Create Date' from 'Create Date : YYYY:MM:DD HH:MM:SS' to 'DD-MM-YYYY HH:MM:SS'."""
    try:
        date_string = exif_output.split(':', 1)[-1].strip()

        # Parse the date string assuming the format is 'YYYY:MM:DD HH:MM:SS'
        original_format = datetime.datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")

        # Reformat to 'DD-MM-YYYY HH:MM:SS'
        new_format = original_format.strftime("%d-%m-%Y %H:%M:%S")

        return new_format
    except (ValueError, IndexError) as e:
        print(f"Error processing date: {e}")
        return None

