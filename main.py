import flet as ft
import yt_dlp
from pathlib import Path
import threading

def main(page: ft.Page):
    # Page settings
    page.title = "YST Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = ft.colors.BLACK
    page.window_width = 500
    page.window_height = 600
    
    # Download directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # UI Elements
    title = ft.Text("🎯 YST Downloader", size=24, color=ft.colors.BLUE_400)
    
    url_input = ft.TextField(
        label="Enter YouTube URL here...",
        width=400,
        border_color=ft.colors.BLUE_400,
        prefix_icon=ft.icons.LINK
    )
    
    # Quality buttons
    quality_buttons = ft.Row([
        ft.ElevatedButton("360p", on_click=lambda e: download_video("360p")),
        ft.ElevatedButton("480p", on_click=lambda e: download_video("480p")),
        ft.ElevatedButton("720p", on_click=lambda e: download_video("720p")),
        ft.ElevatedButton("1080p", on_click=lambda e: download_video("1080p")),
        ft.ElevatedButton("MP3", on_click=lambda e: download_video("MP3")),
    ], spacing=8, wrap=True)
    
    progress_bar = ft.ProgressBar(width=400, visible=False, color=ft.colors.BLUE_400)
    status_text = ft.Text("🔵 Ready to download...", size=16, color=ft.colors.GREEN_400)
    file_info = ft.Text("", size=12, color=ft.colors.GREY_400)
    
    def download_video(quality):
        url = url_input.value.strip()
        
        if not url:
            show_message("⚠️ Please enter a YouTube URL")
            return
        
        # Update UI
        progress_bar.visible = True
        status_text.value = f"⏬ Downloading {quality}..."
        status_text.color = ft.colors.BLUE_400
        page.update()
        
        # Start download in background thread
        threading.Thread(target=download_thread, args=(url, quality), daemon=True).start()
    
    def download_thread(url, quality):
        try:
            # Download settings
            if quality == "MP3":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                quality_map = {
                    "360p": "360", 
                    "480p": "480", 
                    "720p": "720", 
                    "1080p": "1080"
                }
                ydl_opts = {
                    'format': f'best[height<={quality_map[quality]}]',
                    'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
                }
            
            # Real download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                file_info.value = f"Downloading: {video_title}"
                page.update()
                
                ydl.download([url])
            
            # Success
            status_text.value = f"✅ Download complete ({quality})"
            status_text.color = ft.colors.GREEN_400
            file_info.value = f"Saved: {video_title}"
            show_message("🎉 Download completed!")
            
        except Exception as e:
            # Error
            status_text.value = f"❌ Download failed"
            status_text.color = ft.colors.RED_400
            file_info.value = f"Error: {str(e)}"
            show_message(f"❌ Error: {str(e)}")
        
        finally:
            progress_bar.visible = False
            page.update()
    
    def show_message(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=ft.colors.BLUE_400,
        )
        page.snack_bar.open = True
        page.update()
    
    # Add all elements to page
    page.add(
        ft.Column([
            title,
            ft.Divider(height=20),
            url_input,
            ft.Divider(height=20),
            quality_buttons,
            ft.Divider(height=20),
            progress_bar,
            status_text,
            file_info,
            ft.Container(height=20),
            ft.Text("YST Downloader v1.0.0", size=12, color=ft.colors.GREY_600),
        ])
    )

# Run the app
ft.app(target=main, view=ft.FLET_APP)
