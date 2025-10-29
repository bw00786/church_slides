#!/usr/bin/env python3
"""
Generate a 5-minute countdown video for church service slides.
Can create either MP4 video or animated GIF.

Usage:
    python create_countdown.py --format mp4 --theme forgiveness
    python create_countdown.py --format gif --duration 300
"""

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
                          text_color=(255, 255, 255)):
    """Create a single countdown frame"""
    
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
        # Try to load a large font for the timer
        timer_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 200)
        label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 60)
    except:
        try:
            timer_font = ImageFont.truetype("arial.ttf", 200)
            label_font = ImageFont.truetype("arial.ttf", 60)
        except:
            print("⚠️ Using default font (Arial not found)")
            timer_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
    
    # Format time string
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Draw translucent rounded rectangle behind text
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Calculate text size
    timer_bbox = draw.textbbox((0, 0), time_str, font=timer_font)
    timer_width = timer_bbox[2] - timer_bbox[0]
    timer_height = timer_bbox[3] - timer_bbox[1]
    
    label_text = "Service begins in"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    
    # Box dimensions
    box_padding = 80
    box_width = max(timer_width, label_width) + (box_padding * 2)
    box_height = timer_height + 150
    box_x = (width - box_width) // 2
    box_y = (height - box_height) // 2
    
    # Draw rounded rectangle
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
                          fps=30):
    """
    Create a countdown video using ffmpeg.
    
    Args:
        duration: Countdown duration in seconds (default 300 = 5 minutes)
        output_path: Where to save the video
        theme_path: Path to background image for color extraction
        fps: Frames per second (30 recommended)
    """
    
    if not check_ffmpeg():
        print("❌ ffmpeg not found!")
        print("Install with:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False
    
    print(f"🎬 Creating {duration//60} minute countdown video...")
    
    # Load theme colors if background exists
    bg_color_top = (0, 120, 200)
    bg_color_bottom = (0, 60, 130)
    
    if os.path.exists(theme_path):
        try:
            theme_img = Image.open(theme_path)
            # Sample colors from top and bottom
            bg_color_top = theme_img.getpixel((theme_img.width // 2, 100))
            bg_color_bottom = theme_img.getpixel((theme_img.width // 2, theme_img.height - 100))
            print(f"🎨 Using theme colors from {theme_path}")
        except:
            print(f"⚠️ Could not load theme, using default colors")
    
    # Create temporary directory for frames
    temp_dir = "temp_countdown_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"📸 Generating {duration * fps} frames...")
    
    frame_count = 0
    for remaining in range(duration, -1, -1):
        minutes = remaining // 60
        seconds = remaining % 60
        
        # Generate one frame per second (repeat for fps)
        frame = create_countdown_frame(
            minutes, seconds, 
            bg_color_top=bg_color_top,
            bg_color_bottom=bg_color_bottom
        )
        
        # Save frame multiple times for the desired fps
        for _ in range(fps):
            frame_path = os.path.join(temp_dir, f"frame_{frame_count:06d}.jpg")
            frame.save(frame_path, "JPEG", quality=95)
            frame_count += 1
        
        if remaining % 30 == 0:  # Progress update every 30 seconds
            print(f"  ⏱️  Generated up to {minutes:02d}:{seconds:02d}")
    
    print(f"✅ Generated {frame_count} frames")
    print(f"🎞️  Encoding video with ffmpeg...")
    
    # Use ffmpeg to create video from frames
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file
        '-framerate', str(fps),
        '-i', os.path.join(temp_dir, 'frame_%06d.jpg'),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"✅ Video created: {output_path}")
        
        # Get file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"📦 File size: {size_mb:.1f} MB")
        
        # Cleanup
        print("🧹 Cleaning up temporary frames...")
        shutil.rmtree(temp_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg error: {e.stderr.decode()}")
        return False

def create_countdown_gif(duration=300, output_path="output/countdown.gif"):
    """
    Create an animated GIF countdown (Warning: Large file size!)
    
    Args:
        duration: Countdown duration in seconds
        output_path: Where to save the GIF
    """
    
    print(f"🎬 Creating {duration//60} minute countdown GIF...")
    print("⚠️  Warning: GIF files can be very large!")
    
    frames = []
    
    for remaining in range(duration, -1, -1):
        minutes = remaining // 60
        seconds = remaining % 60
        
        frame = create_countdown_frame(minutes, seconds)
        frames.append(frame)
        
        if remaining % 30 == 0:
            print(f"  ⏱️  Generated up to {minutes:02d}:{seconds:02d}")
    
    print(f"💾 Saving GIF with {len(frames)} frames...")
    
    # Save as GIF (1 frame per second)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1000ms = 1 second per frame
        loop=0
    )
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ GIF created: {output_path}")
    print(f"📦 File size: {size_mb:.1f} MB")
    
    return True

def create_countdown_images(duration=300, output_dir="output/countdown_slides"):
    """
    Create individual countdown images (one per second) for manual slide creation
    
    Args:
        duration: Countdown duration in seconds
        output_dir: Directory to save images
    """
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"🎬 Creating {duration//60} minute countdown images...")
    
    for remaining in range(duration, -1, -1):
        minutes = remaining // 60
        seconds = remaining % 60
        
        frame = create_countdown_frame(minutes, seconds)
        output_path = os.path.join(output_dir, f"countdown_{minutes:02d}_{seconds:02d}.jpg")
        frame.save(output_path, "JPEG", quality=95)
        
        if remaining % 30 == 0:
            print(f"  ⏱️  Created {minutes:02d}:{seconds:02d}")
    
    print(f"✅ Created {duration + 1} images in {output_dir}")
    return True

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
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'output', exist_ok=True)
    
    # Theme background path
    theme_path = f"backgrounds/{args.theme}/countdown.jpg"
    
    # Generate countdown based on format
    if args.format == 'mp4':
        success = create_countdown_video(
            duration=args.duration,
            output_path=output_path,
            theme_path=theme_path,
            fps=args.fps
        )
    elif args.format == 'gif':
        success = create_countdown_gif(
            duration=args.duration,
            output_path=output_path
        )
    else:  # images
        success = create_countdown_images(
            duration=args.duration,
            output_dir=output_path
        )
    
    if success:
        print("\n✅ Done!")
        if args.format == 'mp4':
            print(f"💡 Tip: You can embed this video in slide 1 of your PowerPoint")
            print(f"   Insert > Video > Video on My PC... > {output_path}")
    else:
        print("\n❌ Failed to create countdown")

if __name__ == "__main__":
    main()