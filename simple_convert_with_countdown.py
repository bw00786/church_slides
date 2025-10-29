
import yaml
import os
import sys
import subprocess
from src.tools.pptx_creator_tool import create_powerpoint_manual

def generate_countdown_video(theme, output_path="output/countdown.mp4"):
    """Generate countdown video if it doesn't exist"""
    if os.path.exists(output_path):
        print(f"⏱️  Using existing countdown: {output_path}")
        return output_path
    
    print(f"⏱️  Generating countdown video...")
    theme_bg = f"backgrounds/{theme}/countdown.jpg"
    
    # Call the countdown generator
    cmd = [
        "python", "create_countdown.py",
        "--format", "mp4",
        "--duration", "300",
        "--theme", theme,
        "--output", output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError:
        print("⚠️  Could not generate countdown video, skipping...")
        return None

def simple_convert(service_date, include_countdown=True):
    """Direct YAML to PowerPoint conversion with optional countdown"""
    
    # Load YAML
    yaml_path = f"service_orders/{service_date}.yaml"
    if not os.path.exists(yaml_path):
        print(f"❌ File not found: {yaml_path}")
        return
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    theme = data.get('theme', 'default').lower().replace(' ', '_')
    backgrounds_path = f"backgrounds/{theme}"
    
    if not os.path.exists(backgrounds_path):
        backgrounds_path = "backgrounds/default"
        if not os.path.exists(backgrounds_path):
            print(f"⚠️ Warning: No backgrounds found at {backgrounds_path}")
    
    print(f"🎨 Using backgrounds: {backgrounds_path}")
    
    # Generate countdown video if first slide is countdown type
    countdown_video_path = None
    order_items = data.get('order', data.get('service_order', []))
    
    if order_items and include_countdown:
        first_item = order_items[0]
        if first_item.get('type') == 'countdown':
            countdown_video_path = generate_countdown_video(theme)
    
    # Convert YAML to slides
    slides = []
    for idx, item in enumerate(order_items):
        slide_type = item.get('type', 'text')
        title = item.get('title', '')
        content = item.get('content', '')
        
        # Add speaker/presenter info
        if 'speaker' in item:
            content = f"{content}\n\nSpeaker: {item['speaker']}" if content else f"Speaker: {item['speaker']}"
        elif 'presenter' in item:
            content = f"{content}\n\nPresenter: {item['presenter']}" if content else f"Presenter: {item['presenter']}"
        
        # Map slide type to background
        bg_map = {
            'countdown': 'countdown.jpg',
            'song': 'song.jpg',
            'hymn': 'hymn.jpg',
            'prayer': 'prayer.jpg',
            'scripture': 'scripture.jpg',
            'sermon': 'sermon.jpg',
            'communion': 'communion.jpg',
            'offering': 'offering.jpg',
            'children_message': 'children.jpg',
            'liturgy': 'liturgy.jpg',
            'text': 'general.jpg',
            'dismissal': 'general.jpg',
        }
        
        bg_file = bg_map.get(slide_type, 'general.jpg')
        bg_path = os.path.join(backgrounds_path, bg_file)
        
        slide_data = {
            'type': slide_type,
            'title': title,
            'content': content,
            'background_path': bg_path
        }
        
        # Add countdown video path to first slide if available
        if idx == 0 and countdown_video_path:
            slide_data['countdown_video'] = countdown_video_path
        
        slides.append(slide_data)
        print(f"  ✓ Added slide: {title} ({slide_type})")
    
    # Create PowerPoint
    theme_clean = theme.replace('_', '')
    output_path = f"output/{service_date}_{theme_clean}_ServiceSlides.pptx"
    os.makedirs("output", exist_ok=True)
    
    print(f"\n🎬 Creating PowerPoint presentation...")
    result = create_powerpoint_manual(slides, output_path, backgrounds_path)
    print(result)
    
    if countdown_video_path:
        print(f"\n💡 Note: Countdown video created at {countdown_video_path}")
        print(f"   It will be embedded in the first slide of your presentation")
    
    print(f"\n✅ Done! Open your presentation: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('service_date', help='Service date (YYYY-MM-DD)')
    parser.add_argument('--no-countdown', action='store_true', 
                       help='Skip countdown video generation')
    args = parser.parse_args()
    
    simple_convert(args.service_date, include_countdown=not args.no_countdown)