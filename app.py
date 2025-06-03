import streamlit as st
import os
import re
from urllib.parse import urlparse, parse_qs
import requests
import json
import yt_dlp

st.set_page_config(page_title="MP4 Downloader", page_icon="🎥")

st.title("🎥 MP4 Video İndirici")
st.write("YouTube videolarını ve Shorts'ları MP4 formatında indirin!")

# YouTube API anahtarı
API_KEY = "AIzaSyBvVNuBZhM5N9AOFj1voNKbDlupbJ_nGRY"

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    if not url:
        return None
        
    # Handle youtu.be URLs
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
        
    # Handle youtube.com URLs
    if "youtube.com" in url:
        if "shorts" in url:
            return url.split("/shorts/")[1].split("?")[0]
        parsed_url = urlparse(url)
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
            
    return None

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    if not url:
        return False
    video_id = extract_video_id(url)
    return video_id is not None and len(video_id) == 11

def get_video_info(video_id):
    """Get video information using YouTube Data API."""
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet,contentDetails"
        response = requests.get(url)
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            video_data = data['items'][0]
            return {
                'title': video_data['snippet']['title'],
                'thumbnail': video_data['snippet']['thumbnails']['high']['url'],
                'duration': video_data['contentDetails']['duration']
            }
        return None
    except Exception as e:
        st.error(f"Video bilgileri alınamadı: {str(e)}")
        return None

def download_video(url, quality):
    """Download video using yt-dlp."""
    try:
        # Create a temporary directory for downloads
        download_dir = os.path.join(os.getcwd(), "temp_downloads")
        os.makedirs(download_dir, exist_ok=True)
        
        # Enhanced configuration for SABR streaming
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'verbose': True,
            'no_warnings': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['js', 'configs'],
                }
            },
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_color': True,
            'extract_flat': False,
            'quiet': False,
            'geo_bypass': True,
            'merge_output_format': 'mp4',
        }
        
        # First, try to get video info without downloading
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First attempt: just get info
                st.info("Video bilgileri alınıyor...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("Video bilgileri alınamadı")
                
                st.success("Video bilgileri başarıyla alındı!")
                
                # Second attempt: download the video
                st.info("Video indiriliyor...")
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise Exception("Video indirilemedi")
                
                # Try to find the downloaded file
                video_path = os.path.join(download_dir, f"{info['title']}.mp4")
                
                if os.path.exists(video_path):
                    st.success("Video başarıyla indirildi!")
                    return video_path
                else:
                    # If the exact path doesn't exist, find the downloaded file
                    files = os.listdir(download_dir)
                    if files:
                        st.success("Video başarıyla indirildi!")
                        return os.path.join(download_dir, files[0])
                    raise Exception("İndirilen video dosyası bulunamadı")
                    
            except Exception as e:
                st.error(f"İlk deneme başarısız: {str(e)}")
                
                # If first attempt fails, try with a different configuration
                st.info("Alternatif yöntem deneniyor...")
                ydl_opts.update({
                    'format': 'best',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                            'player_skip': ['js', 'configs'],
                            'skip': ['dash', 'hls'],
                        }
                    }
                })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                    info = ydl_retry.extract_info(url, download=True)
                    
                    if not info:
                        raise Exception("Video bilgileri alınamadı")
                    
                    video_path = os.path.join(download_dir, f"{info['title']}.mp4")
                    if os.path.exists(video_path):
                        st.success("Video başarıyla indirildi!")
                        return video_path
                    else:
                        files = os.listdir(download_dir)
                        if files:
                            st.success("Video başarıyla indirildi!")
                            return os.path.join(download_dir, files[0])
                        raise Exception("İndirilen video dosyası bulunamadı")
                
    except Exception as e:
        st.error(f"Video indirme hatası: {str(e)}")
        return None

# URL girişi
url = st.text_input("YouTube Video URL'sini yapıştırın:")

if url:
    if not is_valid_youtube_url(url):
        st.error("Lütfen geçerli bir YouTube URL'si girin!")
    else:
        try:
            # Video ID'yi çıkar
            video_id = extract_video_id(url)
            if not video_id:
                st.error("Video ID bulunamadı!")
                st.stop()

            # Video bilgilerini al
            video_info = get_video_info(video_id)
            if not video_info:
                st.error("Video bilgileri alınamadı!")
                st.stop()

            # Video bilgilerini göster
            st.image(video_info['thumbnail'], width=300)
            st.write(f"**Başlık:** {video_info['title']}")
            
            # Video kalitesi seçimi
            quality = st.selectbox(
                "Video kalitesini seçin:",
                options=['720p', '1080p', '480p', '360p']
            )

            if st.button("İndir"):
                with st.spinner("Video indiriliyor..."):
                    # Videoyu indir
                    download_path = download_video(url, quality)
                    
                    if download_path:
                        # İndirilen dosyayı kullanıcıya sun
                        with open(download_path, 'rb') as file:
                            st.download_button(
                                label="İndirilen videoyu kaydet",
                                data=file,
                                file_name=os.path.basename(download_path),
                                mime="video/mp4"
                            )
                        
                        # Geçici dosyayı sil
                        os.remove(download_path)
                        st.success("Video başarıyla indirildi!")
                    else:
                        st.error("Video indirilemedi!")

        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")
            st.write("Lütfen geçerli bir YouTube URL'si girdiğinizden emin olun.")
            st.write("Eğer sorun devam ederse, lütfen şunları kontrol edin:")
            st.write("1. İnternet bağlantınızın aktif olduğundan emin olun")
            st.write("2. Video'nun herkese açık olduğundan emin olun")
            st.write("3. URL'nin doğru kopyalandığından emin olun") 