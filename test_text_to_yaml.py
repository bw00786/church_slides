#!/usr/bin/env python3
"""
Test the YAML parser with plain text input (no Word document needed)
Usage: python test_text_to_yaml.py
"""

import os
import re
from datetime import datetime

# Import the parsing functions from word_to_yaml
# But we'll redefine them here for standalone use

def parse_service_date(text):
    """Extract service date from text"""
    date_pattern = r'Service Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})'
    match = re.search(date_pattern, text, re.IGNORECASE)
    
    if match:
        date_str = match.group(1)
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            return date_obj.strftime("%Y-%m-%d")
        except:
            pass
    
    return datetime.now().strftime("%Y-%m-%d")

def parse_theme(text):
    """Extract theme from text"""
    theme_pattern = r'Theme:\s*(.+?)(?:\n|Speaker:|~)'
    match = re.search(theme_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Sunday Service"

def parse_speaker(text):
    """Extract speaker from text"""
    speaker_pattern = r'Speaker:\s*(.+?)(?:\n|~)'
    match = re.search(speaker_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def identify_slide_type(title, content):
    """Determine slide type based on title and content"""
    title_lower = title.lower()
    
    if 'countdown' in title_lower:
        return 'countdown'
    elif 'communion' in title_lower or 'holy communion' in title_lower:
        return 'communion'
    elif 'offering' in title_lower:
        return 'offering'
    elif 'dismissal' in title_lower or 'benediction' in title_lower:
        return 'dismissal'
    elif "children's message" in title_lower or 'children message' in title_lower:
        return 'children_message'
    elif 'sermon' in title_lower or 'message' in title_lower:
        return 'sermon'
    elif 'scripture' in title_lower or 'reading' in title_lower:
        return 'scripture'
    elif 'hymn' in title_lower or (title_lower.startswith('#') or '#' in title):
        return 'hymn'
    elif 'praise' in title_lower or 'song' in title_lower or 'worship' in title_lower:
        return 'song'
    elif 'prayer' in title_lower:
        return 'prayer'
    elif 'call to worship' in title_lower or 'responsive' in title_lower:
        return 'liturgy'
    elif 'announcement' in title_lower:
        return 'text'
    else:
        if content and ('L:' in content or 'P:' in content or 'Leader:' in content):
            return 'liturgy'
        return 'text'

def is_likely_header(line, next_lines):
    """Determine if a line is likely a header for a service item"""
    line = line.strip()
    
    if not line:
        return False
    
    known_headers = [
        'countdown', 'opening praise', 'closing praise', 'announcements',
        "children's message", 'children message', 'call to worship',
        'opening prayer', 'closing prayer', 'hymn of praise', 'scripture',
        'sermon', 'message', 'holy communion', 'communion', "lord's prayer",
        'prayers for the community', 'offering', 'doxology', 'dismissal',
        'benediction', 'responsive reading', 'liturgy'
    ]
    
    line_lower = line.lower().rstrip(':')
    
    for header in known_headers:
        if header in line_lower:
            return True
    
    if re.match(r'^\d+\s+Minute\s+Countdown', line, re.IGNORECASE):
        return True
    
    if line.endswith(':') and len(line) < 50:
        return True
    
    if re.match(r'^Scripture:\s*.+', line, re.IGNORECASE):
        return True
    
    if (re.match(r'^[A-Z]', line) and 
        len(line) < 40 and 
        ':' not in line and
        not line.startswith('-')):
        
        if next_lines:
            next_line = next_lines[0].strip()
            if (next_line.startswith('-') or 
                next_line.startswith('L:') or 
                next_line.startswith('P:') or
                next_line.startswith('#') or
                len(next_line) > 60 or
                not next_line):
                return True
    
    return False

def parse_service_order(text):
    """Parse the order of service section"""
    order_start = re.search(r'Order of Service', text, re.IGNORECASE)
    if not order_start:
        print("⚠️ Could not find 'Order of Service' section")
        return []
    
    service_text = text[order_start.end():].strip()
    lines = [l.rstrip() for l in service_text.split('\n')]
    
    items = []
    current_title = None
    current_content = []
    current_metadata = {}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        next_lines = lines[i+1:i+4] if i+1 < len(lines) else []
        
        if re.match(r'^[~=\-]{3,}$', line.strip()):
            i += 1
            continue
        
        if not line.strip():
            i += 1
            continue
        
        if is_likely_header(line, next_lines):
            if current_title:
                content_str = '\n'.join(current_content).strip()
                items.append({
                    'title': current_title,
                    'content': content_str,
                    'metadata': current_metadata
                })
                print(f"  📌 Parsed: {current_title}")
            
            current_title = line.rstrip(':').strip()
            current_content = []
            current_metadata = {}
        else:
            stripped = line.strip()
            
            if stripped.startswith('-'):
                presenter = stripped.lstrip('-').strip()
                current_metadata['presenter'] = presenter
            elif stripped:
                current_content.append(line)
        
        i += 1
    
    if current_title:
        content_str = '\n'.join(current_content).strip()
        items.append({
            'title': current_title,
            'content': content_str,
            'metadata': current_metadata
        })
        print(f"  📌 Parsed: {current_title}")
    
    return items

def create_yaml_structure(service_date, theme, speaker, items):
    """Create the YAML structure"""
    yaml_lines = []
    yaml_lines.append(f"date: {service_date}")
    yaml_lines.append(f"theme: {theme}")
    if speaker:
        yaml_lines.append(f"speaker: {speaker}")
    yaml_lines.append("")
    yaml_lines.append("order:")
    
    for item in items:
        title = item['title']
        content = item['content']
        metadata = item['metadata']
        
        slide_type = identify_slide_type(title, content)
        
        yaml_lines.append(f"  - type: {slide_type}")
        yaml_lines.append(f"    title: {title}")
        
        if 'presenter' in metadata:
            yaml_lines.append(f"    presenter: {metadata['presenter']}")
        elif 'speaker' in metadata:
            yaml_lines.append(f"    speaker: {metadata['speaker']}")
        
        if slide_type == 'scripture':
            ref_match = re.search(r':\s*(.+)$', title)
            if ref_match:
                yaml_lines.append(f"    reference: {ref_match.group(1)}")
        
        if content:
            if '\n' in content or len(content) > 60:
                yaml_lines.append("    content: |")
                for line in content.split('\n'):
                    yaml_lines.append(f"      {line}")
            else:
                yaml_lines.append(f'    content: "{content}"')
    
    return '\n'.join(yaml_lines)

# Sample text for testing
SAMPLE_TEXT = """Service Date: June 22, 2025
Theme:  Disciples Making Disciples
Speaker: Pastor Megan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Order of Service
5 Minute Countdown (Regular)
Opening Praise:
And All The People Said Amen
Announcements
Children's Message
-Pastor Megan
Call to Worship
L: We are called to be God's children.
P: God's love has been poured on us through Jesus Christ!
L: Fear and doubt are gone!
P: Joy and Celebration ring in our hearts!
L: Come, let us raise our voices in song!
P: Let us offer our hearts and souls to God in prayer and praise. AMEN.
Opening Prayer:
Lord of Light and Mercy, be with us this day as we again hear the stories of faith and sight. Help us to believe in your abiding presence with us, both in our darkness and in the light which you bring. Give us courage and strength to witness to your resurrection. For we offer this in Jesus' Name, AMEN.
Hymn of Praise: 
#399 Take My Life and Let it Be
Scripture: Acts 3:11-19
11 While the man held on to Peter and John, all the people were astonished and came running to them in the place called Solomon's Colonnade. 12 When Peter saw this, he said to them: "Fellow Israelites, why does this surprise you? Why do you stare at us as if by our own power or godliness we had made this man walk?
Sermon:  
Pastor Megan
Holy Communion
Lord's Prayer
Prayers for the Community
Offering with Doxology
Closing Praise: 
My Lighthouse
Dismissal
"""

def main():
    print("🧪 Testing YAML Parser\n")
    
    # Parse the sample text
    print("🔍 Parsing sample text...")
    service_date = parse_service_date(SAMPLE_TEXT)
    theme = parse_theme(SAMPLE_TEXT)
    speaker = parse_speaker(SAMPLE_TEXT)
    
    print(f"\n📅 Service Date: {service_date}")
    print(f"🎨 Theme: {theme}")
    if speaker:
        print(f"🎤 Speaker: {speaker}")
    
    print("\n📋 Extracting service items:")
    items = parse_service_order(SAMPLE_TEXT)
    
    print(f"\n✅ Found {len(items)} service items\n")
    
    # Show what was parsed
    print("=" * 60)
    print("PARSED ITEMS:")
    print("=" * 60)
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['title']} ({identify_slide_type(item['title'], item['content'])})")
        if item['metadata']:
            print(f"   Metadata: {item['metadata']}")
        if item['content']:
            preview = item['content'][:50].replace('\n', ' ')
            if len(item['content']) > 50:
                preview += "..."
            print(f"   Content: {preview}")
    print("=" * 60)
    
    # Create YAML
    yaml_content = create_yaml_structure(service_date, theme, speaker, items)
    
    # Save to file
    output_filename = f"service_orders/{service_date}.yaml"
    os.makedirs("service_orders", exist_ok=True)
    
    with open(output_filename, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Created: {output_filename}\n")
    print("📝 Full YAML Output:")
    print("=" * 60)
    print(yaml_content)
    print("=" * 60)
    
    # Ask if user wants to generate slides
    response = input("\n🎬 Generate PowerPoint slides now? (y/n): ").strip().lower()
    if response == 'y':
        print("\n🚀 Generating slides...")
        os.system(f"python simple_convert.py {service_date}")

if __name__ == "__main__":
    main()