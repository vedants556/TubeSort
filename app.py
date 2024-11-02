import requests
import json
import os
import re
from flask import Flask, render_template, redirect, url_for, request, flash
from pytube import YouTube
import yt_dlp

app = Flask(__name__)
app.secret_key = '1321'  # Needed for session management (flash messages)

DATA_FILE = 'videos.json'

def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_videos(videos):
    with open(DATA_FILE, 'w') as file:
        json.dump(videos, file)

videos = load_videos()

@app.route('/')
def index():
    filter_category = request.args.get('filter')
    filtered_videos = videos if not filter_category else [video for video in videos if video['category'] == filter_category]
    return render_template('index.html', videos=filtered_videos)

@app.route('/upload', methods=['POST'])
def upload():
    youtube_url = request.form['youtube_url']
    category = request.form['category']
    
    video_id = extract_video_id(youtube_url)
    if not video_id:
        flash('Invalid YouTube URL. Please check the format and try again.', 'error')
        return redirect(url_for('index'))

    video_info = get_video_info(video_id)
    if video_info:
        videos.append({
            'title': video_info['title'],
            'thumbnail': video_info['thumbnail'],
            'url': youtube_url,
            'category': category
        })
        save_videos(videos)
        flash('Video added successfully!', 'success')
    else:
        flash('Failed to retrieve video information. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:video_index>', methods=['POST'])
def delete(video_index):
    if 0 <= video_index < len(videos):
        videos.pop(video_index)
        save_videos(videos)
        flash('Video removed successfully!', 'success')
    return redirect(url_for('index'))

def extract_video_id(url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if match:
        return match.group(1)
    return None

def get_video_info(video_id):
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'noplaylist': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail')
            }
        except Exception as e:
            print(f"Error retrieving video info: {e}")
    
    return None

if __name__ == '__main__':
    app.run(debug=True)
