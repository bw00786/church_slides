#!/usr/bin/env python3
"""
Generate a 5-minute countdown video for church service slides.
Cross-platform compatible (Windows, Mac, Linux)

Usage:
    python create_countdown.py --format mp4 --theme forgiveness
    python create_countdown.py --format gif --duration 300
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
import subprocess
import shutil

# Import cross-platform utilities
try:
    from path_utils import get_font_path, normalize_path, join_paths, ensure_directory
except ImportError:
    # Fallback if path_utils not available
    def get_font_path():
        if sys.platform == 'darwin':
            return '/System/Library/Fonts/Supplemental/Arial.ttf'
        elif sys.platform == 'win32':
            return 'C:\\Windows\\Fonts\\arial.ttf'
        else:
            return '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    def normalize_path(p):
        return os.path.normpath(p)
    
    def join_paths(*parts):
        return os.path.join(*parts)
    
    def ensure_directory(p):
        os.makedirs(p, exist_ok=True)

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    return shutil.which('ffmpeg') is not None

def get_system_fonts():
    """Get list of possible font paths for current system"""
    if sys.platform == 'darwin':  # macOS
        return [
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Helvetica.ttc',
        ]
    elif sys.platform == 'win32':  # Windows
        windows_fonts = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        return [
            os.path.join(windows_fonts, 'arial.ttf'),
            os.path.join(windows_fonts, 'Arial.ttf'),
            os.path.join(windows_fonts, 'ARIAL.TTF'),
            'arial.ttf',  # Try current directory
        ]
    else:  # Linux
        return [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
        ]

def load_font(size):
    """Load font with fallback for different systems"""
    font_paths = get_system_fonts()
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    
    print(f"⚠️ Using default font (Arial not found on {sys.platform})")
    return ImageFont.load_default()

def create_countdown_frame(minutes, seconds, width=1920, height=1080, 
                          bg_color_top=(0, 120, 200), bg_color_bottom=(0, 60, 130),
                          text_color=(255, 255, 255),
                          church_name="Vernon United Methodist Church",
                          logo_path=None):
    """Create a single countdown frame with church branding"""
    
    # Create gradient background
    img = Image.new("RGB", (width, height), bg_color_top)
    draw = ImageDraw.Draw(img)
    
    # Draw gradient
    for i in range(height):
        ratio = i / height
        r = int(bg_color_top[0] * (1 - ratio) + bg_color_bottom[0] * ratio)
        g = int(bg_color_top[1] * (1 - ratio) + bg_color_bottom[1] * ratio)
        b = int(bg_color_top[2] * (1 - ratio) + bg_color_bottom[2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Load fonts with cross-platform support
    timer_font = load_font(200)
    label_font = load_font(60)
    church_font = load_font(72)
    
    # Format time string
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Convert to RGBA for transparency effects
    img_rgba = img.convert("RGBA")
    draw = ImageDraw.Draw(img_rgba)
    
    # --- Add Church Logo (top center) ---
    logo_bottom_y = 80
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            logo_max_width = 250
            logo_aspect = logo.height / logo.width
            if logo.width > logo_max_width:
                logo = logo.resize((logo_max_width, int(logo_max_width * logo_aspect)), Image.Resampling.LANCZOS)
            
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            logo_x = (width - logo.width) // 2
            logo_y = 80
            logo_bottom_y = logo_y + logo.height
            
            img_rgba.paste(logo, (logo_x, logo_y), logo)
            draw = ImageDraw.Draw(img_rgba)
            
        except Exception as e:
            print(f"   ⚠️ Could not load logo: {e}")
    
    # --- Draw Church Name ---
    church_y = logo_bottom_y + 30
    if church_name:
        church_bbox = draw.textbbox((0, 0), church_name, font=church_font)
        church_width = church_bbox[2] - church_bbox[0]
        church_x = (width - church_width) // 2
        
        draw.text((church_x + 3, church_y + 3), church_name, fill=(0, 0, 0, 180), font=church_font)
        draw.text((church_x, church_y), church_name, fill=text_color + (255,), font=church_font)
    
    # --- Draw countdown section ---
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    timer_bbox = draw.textbbox((0, 0), time_str, font=timer_font)
    timer_width = timer_bbox[2] - timer_bbox[0]
    timer_height = timer_bbox[3] - timer_bbox[1]
    
    label_text = "Service begins in"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    
    box_padding = 80
    box_width = max(timer_width, label_width) + (box_padding * 2)
    box_height = timer_height + 150
    box_x = (width - box_width) // 2
    box_y = (height - box_height) // 2
    
    overlay_draw.rounded_rectangle(
        [(box_x, box_y), (box_x + box_width, box_y + box_height)],
        radius=40,
        fill=(0, 0, 0, 130)
    )
    
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    draw = ImageDraw.Draw(img_rgba)
    
    # Draw label
    label_x = (width - label_width) // 2
    label_y = box_y + 30
    draw.text((label_x + 3, label_y + 3), label_text, fill=(0, 0, 0, 180), font=label_font)
    draw.text((label_x, label_y), label_text, fill=text_color + (255,), font=label_font)
    
    # Draw timer
    timer_x = (width - timer_width) // 2
    timer_y = label_y + 80
    draw.text((timer_x + 4, timer_y + 4), time_str, fill=(0, 0, 0, 180), font=timer_font)
    draw.text((timer_x, timer_y), time_str, fill=text_color + (255,), font=timer_font)
    
    return img_rgba.convert("RGB")

def create_countdown_video(duration=300, output_path="output/countdown.mp4", 
                          theme_path="backgrounds/forgiveness/countdown.jpg",
                          fps=30, audio_path=None,
                          church_name="Vernon United Methodist Church",
                          logo_path=None):
    """Create countdown video - cross-platform compatible"""
    
    if not check_ffmpeg():
        print("❌ ffmpeg not found!")
        print("Install with:")
        if sys.platform == 'darwin':
            print("  macOS: brew install ffmpeg")
        elif sys.platform == 'win32':
            print("  Windows: Download from https://ffmpeg.org/download.html")
            print("           Or use: winget install ffmpeg")
        else:
            print("  Linux: sudo apt-get install ffmpeg")
        return False
    
    print(f"🎬 Creating {duration//60} minute countdown video...")
    print(f"💻 Platform: {sys.platform}")
    if church_name:
        print(f"⛪ Church: {church_name}")
    if logo_path:
        print(f"🏛️ Logo: {logo_path}")
    
    # Load theme colors
    bg_color_top = (0, 120, 200)
    bg_color_bottom = (0, 60, 130)
    
    theme_path = normalize_path(theme_path)
    if os.path.exists(theme_path):
        try:
            theme_img = Image.open(theme_path)
            bg_color_top = theme_img.getpixel((theme_img.width // 2, 100))
            bg_color_bottom = theme_img.getpixel((theme_img.width // 2, theme_img.height - 100))
            print(f"🎨 Using theme colors from {theme_path}")
        except:
            print(f"⚠️ Could not load theme, using default colors")
    
    # Create temp directory with OS-appropriate path
    temp_dir = normalize_path("temp_countdown_frames")
    ensure_directory(temp_dir)
    
    print(f"📸 Generating frames...")
    
    frame_count = 0
    for remaining in range(duration, -1, -1):
        minutes = remaining // 60
        seconds = remaining % 60
        
        frame = create_countdown_frame(
            minutes, seconds, 
            bg_color_top=bg_color_top,
            bg_color_bottom=bg_color_bottom,
            church_name=church_name,
            logo_path=logo_path
        )
        
        for _ in range(fps):
            frame_path = join_paths(temp_dir, f"frame_{frame_count:06d}.jpg")
            frame.save(frame_path, "JPEG", quality=95)
            frame_count += 1
        
        if remaining % 30 == 0:
            print(f"  ⏱️  Generated up to {minutes:02d}:{seconds:02d}")
    
    print(f"✅ Generated {frame_count} frames")
    print(f"🎞️  Encoding video with ffmpeg...")
    
    # Build ffmpeg command
    frame_pattern = join_paths(temp_dir, 'frame_%06d.jpg')
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-framerate', str(fps),
        '-i', frame_pattern,
    ]
    
    if audio_path and os.path.exists(audio_path):
        print(f"🎵 Adding background music: {audio_path}")
        audio_path = normalize_path(audio_path)
        ffmpeg_cmd.extend([
            '-i', audio_path,
            '-t', str(duration),
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
        ])
    
    output_path = normalize_path(output_path)
    ffmpeg_cmd.extend([
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        output_path
    ])
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"✅ Video created: {output_path}")
        
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"📦 File size: {size_mb:.1f} MB")
        
        print("🧹 Cleaning up temporary frames...")
        shutil.rmtree(temp_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate countdown timer for church slides")
    parser.add_argument('--format', choices=['mp4', 'gif', 'images'], default='mp4')
    parser.add_argument('--duration', type=int, default=300)
    parser.add_argument('--theme', type=str, default='forgiveness')
    parser.add_argument('--output', type=str, default=None)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--audio', type=str, default=None)
    parser.add_argument('--church-name', type=str, default='Vernon United Methodist Church')
    parser.add_argument('--logo', type=str, default=None)
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = normalize_path(args.output)
    else:
        output_path = join_paths('output', 'countdown.mp4')
    
    ensure_directory(os.path.dirname(output_path) if os.path.dirname(output_path) else 'output')
    
    theme_path = join_paths('backgrounds', args.theme, 'countdown.jpg')
    
    # Handle audio
    audio_path = args.audio
    if not audio_path:
        default_audio_paths = [
            join_paths('audio', 'countdown_music.mp3'),
            join_paths('audio', 'church_music.mp3'),
            join_paths('audio', 'calm_piano.mp3'),
        ]
        for path in default_audio_paths:
            if os.path.exists(path):
                audio_path = path
                print(f"🎵 Found default audio: {audio_path}")
                break
    
    # Handle logo
    logo_path = args.logo
    if not logo_path:
        default_logo_paths = [
            join_paths('logos', 'church_logo.png'),
            join_paths('logos', 'methodist_logo.png'),
            join_paths('logos', 'umc_logo.png'),
        ]
        for path in default_logo_paths:
            if os.path.exists(path):
                logo_path = path
                print(f"🏛️ Found logo: {logo_path}")
                break
    
    if logo_path and not os.path.exists(logo_path):
        print(f"⚠️ Logo not found: {logo_path}")
        logo_path = None
    
    # Generate countdown
    success = create_countdown_video(
        duration=args.duration,
        output_path=output_path,
        theme_path=theme_path,
        fps=args.fps,
        audio_path=audio_path,
        church_name=args.church_name,
        logo_path=logo_path
    )
    
    if success:
        print("\n✅ Done!")
        print(f"🎬 Video: {output_path}")
        if audio_path:
            print(f"🎵 Includes background music")
        if logo_path:
            print(f"🏛️ Includes church logo")
    else:
        print("\n❌ Failed to create countdown")

if __name__ == "__main__":
    main()
