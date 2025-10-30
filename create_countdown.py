import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import subprocess
import shutil

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    return shutil.which('ffmpeg') is not None

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
    
    # Load fonts
    try:
        timer_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 200)
        label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 60)
        church_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 72)
    except:
        try:
            timer_font = ImageFont.truetype("arial.ttf", 200)
            label_font = ImageFont.truetype("arial.ttf", 60)
            church_font = ImageFont.truetype("arial.ttf", 72)
        except:
            print("⚠️ Using default font (Arial not found)")
            timer_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            church_font = ImageFont.load_default()
    
    # Format time string
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Convert to RGBA for transparency effects
    img_rgba = img.convert("RGBA")
    draw = ImageDraw.Draw(img_rgba)
    
    # --- Add Church Logo (top center) ---
    logo_bottom_y = 80  # Track where logo ends
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            # Resize logo to reasonable size (max 250px wide)
            logo_max_width = 250
            logo_aspect = logo.height / logo.width
            if logo.width > logo_max_width:
                logo = logo.resize((logo_max_width, int(logo_max_width * logo_aspect)), Image.Resampling.LANCZOS)
            
            # Convert logo to RGBA if not already
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Position logo at top center
            logo_x = (width - logo.width) // 2
            logo_y = 80
            logo_bottom_y = logo_y + logo.height
            
            # Paste logo
            img_rgba.paste(logo, (logo_x, logo_y), logo)
            draw = ImageDraw.Draw(img_rgba)  # Refresh draw object
            
        except Exception as e:
            print(f"   ⚠️ Could not load logo: {e}")
    
    # --- Draw Church Name (below logo or at top) ---
    church_y = logo_bottom_y + 30  # Position below logo
    if church_name:
        church_bbox = draw.textbbox((0, 0), church_name, font=church_font)
        church_width = church_bbox[2] - church_bbox[0]
        church_x = (width - church_width) // 2
        
        # Draw church name with shadow
        draw.text((church_x + 3, church_y + 3), church_name, fill=(0, 0, 0, 180), font=church_font)
        draw.text((church_x, church_y), church_name, fill=text_color + (255,), font=church_font)
    
    # --- Draw countdown section (center of screen) ---
    # Draw translucent rounded rectangle behind countdown
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Calculate countdown box position (center of screen)
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
    
    # Draw label text
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
    """
    Create a countdown video using ffmpeg with optional background music and church branding.
    """
    
    if not check_ffmpeg():
        print("❌ ffmpeg not found!")
        print("Install with:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False
    
    print(f"🎬 Creating {duration//60} minute countdown video...")
    if church_name:
        print(f"⛪ Church: {church_name}")
    if logo_path:
        print(f"🏛️ Logo: {logo_path}")
    
    # Load theme colors if background exists
    bg_color_top = (0, 120, 200)
    bg_color_bottom = (0, 60, 130)
    
    if os.path.exists(theme_path):
        try:
            theme_img = Image.open(theme_path)
            bg_color_top = theme_img.getpixel((theme_img.width // 2, 100))
            bg_color_bottom = theme_img.getpixel((theme_img.width // 2, theme_img.height - 100))
            print(f"🎨 Using theme colors from {theme_path}")
        except:
            print(f"⚠️ Could not load theme, using default colors")
    
    # Create temporary directory for frames
    temp_dir = "temp_countdown_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
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
        
        # Save frame multiple times for the desired fps
        for _ in range(fps):
            frame_path = os.path.join(temp_dir, f"frame_{frame_count:06d}.jpg")
            frame.save(frame_path, "JPEG", quality=95)
            frame_count += 1
        
        if remaining % 30 == 0:
            print(f"  ⏱️  Generated up to {minutes:02d}:{seconds:02d}")
    
    print(f"✅ Generated {frame_count} frames")
    print(f"🎞️  Encoding video with ffmpeg...")
    
    # Build ffmpeg command with optional audio
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-framerate', str(fps),
        '-i', os.path.join(temp_dir, 'frame_%06d.jpg'),
    ]
    
    # Add audio if provided
    if audio_path and os.path.exists(audio_path):
        print(f"🎵 Adding background music: {audio_path}")
        ffmpeg_cmd.extend([
            '-i', audio_path,
            '-t', str(duration),
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
        ])
    else:
        if audio_path:
            print(f"⚠️ Audio file not found: {audio_path}, creating video without audio")
    
    # Video encoding settings
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
        print(f"❌ ffmpeg error: {e.stderr.decode()}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate countdown timer for church slides")
    parser.add_argument('--format', choices=['mp4', 'gif', 'images'], default='mp4',
                       help='Output format (default: mp4)')
    parser.add_argument('--duration', type=int, default=300,
                       help='Countdown duration in seconds (default: 300 = 5 minutes)')
    parser.add_argument('--theme', type=str, default='forgiveness',
                       help='Theme name for background colors (default: forgiveness)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output path (default: output/countdown.[format])')
    parser.add_argument('--fps', type=int, default=30,
                       help='Frames per second for video (default: 30)')
    parser.add_argument('--audio', type=str, default=None,
                       help='Path to background audio file (mp3, wav, etc.)')
    parser.add_argument('--church-name', type=str, default='Vernon United Methodist Church',
                       help='Church name to display (default: Vernon United Methodist Church)')
    parser.add_argument('--logo', type=str, default=None,
                       help='Path to church logo image (PNG with transparency recommended)')
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        if args.format == 'mp4':
            output_path = 'output/countdown.mp4'
        elif args.format == 'gif':
            output_path = 'output/countdown.gif'
        else:
            output_path = 'output/countdown_slides'
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'output', exist_ok=True)
    
    theme_path = f"backgrounds/{args.theme}/countdown.jpg"
    
    # Handle audio
    audio_path = args.audio
    if not audio_path and args.format == 'mp4':
        default_audio_paths = [
            'audio/countdown_music.mp3',
            'audio/church_music.mp3',
            'audio/calm_piano.mp3',
            'output/countdown_music.mp3'
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
            'logos/church_logo.png',
            'logos/methodist_logo.png',
            'logos/umc_logo.png',
            'images/logo.png',
            'assets/logo.png'
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
    if args.format == 'mp4':
        success = create_countdown_video(
            duration=args.duration,
            output_path=output_path,
            theme_path=theme_path,
            fps=args.fps,
            audio_path=audio_path,
            church_name=args.church_name,
            logo_path=logo_path
        )
    else:
        print(f"❌ Format '{args.format}' not fully implemented with church branding yet")
        print(f"   Use --format mp4 for now")
        return
    
    if success:
        print("\n✅ Done!")
        print(f"🎬 Video: {output_path}")
        if audio_path:
            print(f"🎵 Includes background music")
        if logo_path:
            print(f"🏛️ Includes church logo")
        print(f"\n💡 To embed in PowerPoint:")
        print(f"   The video will be automatically added to slide 1")
        print(f"   python simple_convert.py 2025-06-22")
    else:
        print("\n❌ Failed to create countdown")

if __name__ == "__main__":
    main()