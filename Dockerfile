# 1. Base Image: Use a lightweight Python image
FROM python:3.10-slim

# 2. Set Environment Variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py
ENV PORT 3000

# 3. Install System Dependencies (Crucial for yt-dlp/Merging)
# Install ffmpeg and other necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
       git \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the Working Directory in the container
WORKDIR /usr/src/app

# 5. Copy Requirements and Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire application code
# This includes app.py, templates/, etc.
COPY . .

# 7. Create the temporary downloads directory
RUN mkdir -p downloads

# 8. Expose the port where Gunicorn will run
EXPOSE 3000

# 9. Define the command to run the application (Gunicorn)
# Use the SECRET_KEY from the environment (passed during 'docker run' or in deployment config)
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]
