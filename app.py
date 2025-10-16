import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

# --- Configuration ---
app = Flask(__name__)
# IMPORTANT: Retrieve the SECRET_KEY from environment variables for production.
# Replace the fallback key with your generated, unique key for local testing.
app.secret_key = os.environ.get('SECRET_KEY') 

DOWNLOAD_DIR = 'downloads'
COOKIE_FILE = 'cookies.txt' 
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_media():
    """Handles the media download request."""
    media_url = request.form.get('url')
    format_selection = request.form.get('format_selection')

    if not media_url or not format_selection:
        flash("Please enter a valid URL and select a format.", 'error')
        return redirect(url_for('index'))

    try:
        file_type, quality = format_selection.split('-')
    except ValueError:
        flash("Invalid format selection.", 'error')
        return redirect(url_for('index'))

    # --- Configure yt-dlp options ---
    postprocessors = []
    
    if file_type == 'mp3':
        format_string = f'bestaudio/best'
        postprocessors = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': quality}]
        out_template = os.path.join(DOWNLOAD_DIR, '%(title)s.mp3')
    else: # Video (mp4)
        format_string = f'bestvideo[height<={quality}]+bestaudio/best'
        out_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    filepath = None
    try:
        ydl_opts = {
            'format': format_string,
            'outtmpl': out_template,
            'noplaylist': True,
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            
            # --- Cookies for Authentication (to bypass sign-in errors) ---
            'cookiefile': COOKIE_FILE,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        }

        # 1. Run the download (Blocks until download to server disk is complete)
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(media_url, download=True)
            filepath = ydl.prepare_filename(info_dict)

        # 2. Flash Success Message (Sent with the file stream as the download begins)
        flash(f"Download of '{os.path.basename(filepath)}' has STARTED in your browser. Check your downloads folder.", 'success')

        # 3. Serve the file to the user
        response = send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            max_age=0 
        )
        return response

    except DownloadError as e:
        error_msg = "Download Failed. The media may be private, restricted (e.g., age-gated), or the URL is not supported."
        flash(error_msg, 'error')
        if filepath and os.path.exists(filepath):
             os.remove(filepath)
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f"An unexpected server error occurred.", 'error')
        return redirect(url_for('index'))
    
    finally:
        # 4. Clean up the file (Crucial for server space)
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

if __name__ == '__main__':
    # Run locally (Note: Flask debug server is not for production)
    app.run(debug=True)
