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
    
    # Convert YAML to slides
    slides = []
    for item in order_items:
        slide_type = item.get('type', 'text')
        title = item.get('title', '')
        
        # Get content - could be 'content' or 'reference' for scripture
        content = item.get('content', '')
        if not content and 'reference' in item:
            content = item.get('reference', '')
        
        # Add speaker/presenter info if present
        if 'speaker' in item:
            if content:
                content += f"\n\nSpeaker: {item['speaker']}"
            else:
                content = f"Speaker: {item['speaker']}"
        elif 'presenter' in item:
            if content:
                content += f"\n\nPresenter: {item['presenter']}"
            else:
                content = f"Presenter: {item['presenter']}"
        
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
        
        slides.append({
            'type': slide_type,
            'title': title,
            'content': content,
            'background_path': bg_path
        })
        
        print(f"  ✓ Added slide: {title} ({slide_type})")
    
    # Create PowerPoint
    theme_clean = theme.replace('_', '')
    output_path = f"output/{service_date}_{theme_clean}_ServiceSlides.pptx"
    os.makedirs("output", exist_ok=True)
    
    print(f"\n🎬 Creating PowerPoint presentation...")
    result = create_powerpoint_manual(slides, output_path, backgrounds_path)
    print(result)
    print(f"\n✅ Done! Open your presentation: {output_path}")

if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else "2025-10-12"
    simple_convert(date)