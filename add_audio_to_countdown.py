#!/usr/bin/env python3
"""
Add background audio to existing countdown video
"""

import os
import sys
import subprocess

def add_audio_to_video(video_path, audio_path, output_path=None):
    """Add audio to an existing video file"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio not found: {audio_path}")
        print(f"\n💡 Download free music from:")
        print(f"   - YouTube Audio Library: https://studio.youtube.com")
        print(f"   - Pixabay: https://pixabay.com/music/")
        print(f"   - Search for: 'calm piano' or 'peaceful ambient'")
        return False
    
    if not output_path:
        # Create output name
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_with_audio{ext}"
    
    print(f"🎵 Adding audio to countdown video...")
    print(f"   Video: {video_path}")
    print(f"   Audio: {audio_path}")
    print(f"   Output: {output_path}")
    
    # Get video duration
    duration_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    try:
        result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        print(f"   Duration: {int(duration)} seconds")
    except:
        duration = 300  # Default to 5 minutes
        print(f"   Assuming duration: {duration} seconds")
    
    # Add audio to video
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-t', str(duration),
        '-c:v', 'copy',  # Don't re-encode video
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]
    
    try:
        print(f"\n⏳ Processing (this may take 10-30 seconds)...")
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        print(f"\n✅ Success! Video with audio created:")
        print(f"   {output_path}")
        
        # Get file sizes
        orig_size = os.path.getsize(video_path) / (1024 * 1024)
        new_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n📊 File sizes:")
        print(f"   Original: {orig_size:.1f} MB")
        print(f"   With audio: {new_size:.1f} MB")
        
        # Ask if user wants to replace original
        response = input("\n🔄 Replace original video? (y/n): ").strip().lower()
        if response == 'y':
            import shutil
            shutil.move(output_path, video_path)
            print(f"✅ Replaced: {video_path}")
            print(f"\n💡 Now regenerate your PowerPoint:")
            print(f"   python simple_convert.py 2025-06-22")
        else:
            print(f"\n💡 To use the new video, run:")
            print(f"   mv {output_path} {video_path}")
            print(f"   python simple_convert.py 2025-06-22")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.decode()}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add audio to countdown video")
    parser.add_argument('--video', default='output/countdown.mp4',
                       help='Path to video file')
    parser.add_argument('--audio', default=None,
                       help='Path to audio file')
    parser.add_argument('--output', default=None,
                       help='Output path (optional)')
    
    args = parser.parse_args()
    
    # Find audio file
    audio_path = args.audio
    if not audio_path:
        # Check default locations
        default_paths = [
            'audio/countdown_music.mp3',
            'audio/church_music.mp3',
            'audio/calm_piano.mp3',
            'output/countdown_music.mp3'
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                audio_path = path
                print(f"🎵 Found audio: {audio_path}")
                break
    
    if not audio_path:
        print("❌ No audio file specified or found")
        print("\n📖 Usage:")
        print("   python add_audio_to_countdown.py --audio path/to/music.mp3")
        print("\n📂 Or place audio file at one of these locations:")
        for path in default_paths:
            print(f"   - {path}")
        sys.exit(1)
    
    add_audio_to_video(args.video, audio_path, args.output)
