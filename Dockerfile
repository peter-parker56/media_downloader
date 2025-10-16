FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py
ENV PORT 8000

# Install ffmpeg (system dependency)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (including app.py, templates, and cookies.txt)
COPY . .

RUN mkdir -p downloads

EXPOSE 8000

# Start Gunicorn production server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
