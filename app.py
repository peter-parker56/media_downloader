import os
import json
from flask import Flask, render_template, request, send_file, redirect, url_for, flash

# yt-dlp requires the `youtube_dl` name for compatibility with older imports
from yt_dlp import YoutubeDL 
from yt_dlp.utils import DownloadError

app = Flask(__name__)
# IMPORTANT: Flash messages require a secret key
app.secret_key = os.environ.get('SECRET_KEY')

# Configure a temporary directory to store downloads
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    """Renders the main page."""
    # We pass the flash messages to the template
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_media():
    """Handles the media download request."""
    media_url = request.form.get('url')
    format_selection = request.form.get('format_selection') # e.g., 'mp4-720' or 'mp3-192'

    if not media_url or not format_selection:
        flash("Please enter a valid URL and select a format.", 'error')
        return redirect(url_for('index'))

    # Split the selection into type and quality
    parts = format_selection.split('-')
    file_type = parts[0]
    quality = parts[1]

    # --- 1. Configure yt-dlp options based on selection ---
    postprocessors = []
    
    if file_type == 'mp3':
        # Audio extraction options
        format_string = f'bestaudio/best'
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality, # quality is the bitrate (e.g., 192)
        }]
        out_template = os.path.join(DOWNLOAD_DIR, '%(title)s.mp3')
    else: # Video (mp4) options
        # Select best video stream up to the specified height, and merge with best audio
        format_string = f'bestvideo[height<={quality}]+bestaudio/best'
        out_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    filepath = None
    try:
        ydl_opts = {
            'format': format_string,
            'outtmpl': out_template,
            'noplaylist': True,
            'postprocessors': postprocessors,
            # Suppress console output for a cleaner terminal
            'quiet': True,
            'no_warnings': True,
        }

        # 2. Run the download
        with YoutubeDL(ydl_opts) as ydl:
            # We must pass download=True here for the file to be saved
            info_dict = ydl.extract_info(media_url, download=True)
            # Get the actual final path of the downloaded file
            filepath = ydl.prepare_filename(info_dict)

        # 3. Serve the file to the user
        response = send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            # Set a high expiry time, but the file is deleted immediately after
            max_age=0 
        )
        
        # 4. Success message (this will appear on the next redirect)
        flash(f"Download of '{os.path.basename(filepath)}' has started in your browser.", 'success')
        return response

    except DownloadError as e:
        error_msg = f"Download Failed: The URL is not supported or the media is unavailable."
        flash(error_msg, 'error')
        # On download failure, delete any partial file that might have been created
        if filepath and os.path.exists(filepath):
             os.remove(filepath)
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"Server Error: {e}")
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        return redirect(url_for('index'))
    
    finally:
        # 5. Clean up the file immediately after sending it (Crucial for server space)
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Cleaned up temporary file: {filepath}")
            except OSError as e:
                # Handle case where file might still be in use by send_file
                print(f"Cleanup warning: Could not remove file {filepath}: {e}")

if __name__ == '__main__':
    app.run(debug=True)
