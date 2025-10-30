import yaml
import os
import sys
from src.tools.pptx_creator_tool import create_powerpoint_manual

def simple_convert(service_date):
    """Direct YAML to PowerPoint conversion without AI agents"""
    
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
    
    # Convert YAML to slides - handle both 'order' and 'service_order' keys
    order_items = data.get('order', data.get('service_order', []))
    
    if not order_items:
        print("❌ No service order found in YAML file!")
        print("   Looking for 'order:' or 'service_order:' key")
        return
    
    print(f"📋 Found {len(order_items)} items in service order")
    
    # Check if we need to generate countdown video
    countdown_video_path = None
    if order_items and order_items[0].get('type') == 'countdown':
        countdown_video_path = 'output/countdown.mp4'
        
        if not os.path.exists(countdown_video_path):
            print(f"\n⏱️  Generating 5-minute countdown video...")
            print(f"   This will take about 30 seconds...")
            
            import subprocess
            try:
                subprocess.run([
                    'python', 'create_countdown.py',
                    '--format', 'mp4',
                    '--theme', theme,
                    '--output', countdown_video_path
                ], check=True, capture_output=True)
                print(f"✅ Countdown video generated: {countdown_video_path}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Could not generate countdown video: {e}")
                print(f"   Video will need to be added manually")
                countdown_video_path = None
            except FileNotFoundError:
                print(f"⚠️ create_countdown.py not found - skipping video generation")
                countdown_video_path = None
        else:
            print(f"✅ Using existing countdown video: {countdown_video_path}")
    
    # Convert YAML to slides
    slides = []
    for idx, item in enumerate(order_items):
        slide_type = item.get('type', 'text')
        title = item.get('title', '')
        
        # Get content - could be 'content' or 'reference' for scripture
        content = item.get('content', '')
        if not content and 'reference' in item:
            content = item.get('reference', '')
        
        # Special handling for SERMON slides
        if slide_type == 'sermon':
            # Build sermon slide content
            sermon_parts = []
            
            # Add the sermon title
            if title:
                sermon_parts.append(title)
            
            # Add speaker information
            if 'speaker' in item:
                sermon_parts.append("")  # Blank line
                sermon_parts.append(item['speaker'])
            elif 'presenter' in item:
                sermon_parts.append("")  # Blank line
                sermon_parts.append(item['presenter'])
            
            # Combine into content
            content = '\n'.join(sermon_parts)
            
            # Use "Sermon" as the title for the slide (displays at top)
            title = "Sermon"
        
        # Handle other slide types with speaker/presenter info
        elif 'speaker' in item or 'presenter' in item:
            presenter_name = item.get('speaker') or item.get('presenter')
            
            if content:
                content += f"\n\n{presenter_name}"
            else:
                content = presenter_name
        
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
        
        # Add countdown video to first slide if it's a countdown type
        if idx == 0 and slide_type == 'countdown' and countdown_video_path:
            slide_data['countdown_video'] = countdown_video_path
        
        slides.append(slide_data)
        
        # Enhanced logging for sermon slides
        if slide_type == 'sermon':
            print(f"  ✓ Added slide: Sermon - {item.get('title', 'Untitled')} ({slide_type})")
        else:
            print(f"  ✓ Added slide: {title} ({slide_type})")
    
    # Create PowerPoint
    theme_clean = theme.replace('_', '')
    output_path = f"output/{service_date}_{theme_clean}_ServiceSlides.pptx"
    os.makedirs("output", exist_ok=True)
    
    print(f"\n🎬 Creating PowerPoint presentation...")
    result = create_powerpoint_manual(slides, output_path, backgrounds_path)
    print(result)
    
    # Display video setup instructions if countdown video exists
    if countdown_video_path and os.path.exists(countdown_video_path):
        print(f"\n" + "="*70)
        print("🎥 COUNTDOWN VIDEO SETUP")
        print("="*70)
        print(f"\n✅ Video has been added to slide 1!")
        print(f"\n📍 To make it auto-play:")
        print(f"   1. Open the PowerPoint file")
        print(f"   2. Click on the video in slide 1")
        print(f"   3. Go to 'Playback' tab")
        print(f"   4. Change 'Start' to 'Automatically'")
        print(f"   5. (Optional) Check 'Play Full Screen'")
        print(f"   6. Save the file")
        print(f"\n📖 See setup_countdown_autoplay.md for detailed instructions")
        print("="*70)
    
    print(f"\n✅ Done! Open your presentation: {output_path}")

if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else "2025-10-12"
    simple_convert(date)