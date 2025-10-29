#!/usr/bin/env python3
"""
Convert a Word document service order to YAML format for church slides.
Usage: python word_to_yaml.py <input.docx>
"""

import sys
import os
import re
from datetime import datetime
import mammoth

def extract_text_from_docx(docx_path):
    """Extract text from Word document"""
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            return result.value
    except Exception as e:
        print(f"❌ Error reading Word document: {e}")
        sys.exit(1)

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
    
    print("⚠️ Could not parse service date from document")
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
    """
    Determine if a line is likely a header for a service item.
    More aggressive detection to ensure each item gets its own slide.
    """
    line = line.strip()
    
    if not line:
        return False
    
    # Definite headers
    known_headers = [
        'countdown', 'opening praise', 'closing praise', 'announcements',
        "children's message", 'children message', 'call to worship',
        'opening prayer', 'closing prayer', 'hymn of praise', 'scripture',
        'sermon', 'message', 'holy communion', 'communion', "lord's prayer",
        'prayers for the community', 'offering', 'doxology', 'dismissal',
        'benediction', 'responsive reading', 'liturgy'
    ]
    
    line_lower = line.lower().rstrip(':')
    
    # Check against known headers
    for header in known_headers:
        if header in line_lower:
            return True
    
    # Pattern: "X Minute Countdown"
    if re.match(r'^\d+\s+Minute\s+Countdown', line, re.IGNORECASE):
        return True
    
    # Pattern: Short line ending with colon (max 50 chars)
    if line.endswith(':') and len(line) < 50:
        return True
    
    # Pattern: "Scripture: Reference"
    if re.match(r'^Scripture:\s*.+', line, re.IGNORECASE):
        return True
    
    # Pattern: Single capitalized line that's not too long
    # AND is followed by content (not another header)
    if (re.match(r'^[A-Z]', line) and 
        len(line) < 40 and 
        ':' not in line and
        not line.startswith('-')):
        
        # Check if next line looks like content
        if next_lines:
            next_line = next_lines[0].strip()
            # Content indicators: starts with -, L:, P:, #, or is long, or is empty
            if (next_line.startswith('-') or 
                next_line.startswith('L:') or 
                next_line.startswith('P:') or
                next_line.startswith('#') or
                len(next_line) > 60 or
                not next_line):
                return True
    
    return False

def parse_service_order(text):
    """Parse the order of service section with improved header detection"""
    # Find the "Order of Service" section
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
        
        # Get next few lines for lookahead
        next_lines = lines[i+1:i+4] if i+1 < len(lines) else []
        
        # Skip separator lines
        if re.match(r'^[~=\-]{3,}$', line.strip()):
            i += 1
            continue
        
        # Empty line - might separate items
        if not line.strip():
            i += 1
            continue
        
        # Check if this is a header
        if is_likely_header(line, next_lines):
            # Save previous item if exists
            if current_title:
                content_str = '\n'.join(current_content).strip()
                items.append({
                    'title': current_title,
                    'content': content_str,
                    'metadata': current_metadata
                })
                print(f"  📌 Parsed: {current_title}")
            
            # Start new item
            current_title = line.rstrip(':').strip()
            current_content = []
            current_metadata = {}
        else:
            # This is content
            stripped = line.strip()
            
            # Check for presenter/speaker lines (start with -)
            if stripped.startswith('-'):
                presenter = stripped.lstrip('-').strip()
                current_metadata['presenter'] = presenter
            elif stripped:  # Not empty
                current_content.append(line)
        
        i += 1
    
    # Don't forget the last item
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
        
        # Determine slide type
        slide_type = identify_slide_type(title, content)
        
        yaml_lines.append(f"  - type: {slide_type}")
        yaml_lines.append(f"    title: {title}")
        
        # Add presenter/speaker if present
        if 'presenter' in metadata:
            yaml_lines.append(f"    presenter: {metadata['presenter']}")
        elif 'speaker' in metadata:
            yaml_lines.append(f"    speaker: {metadata['speaker']}")
        
        # Handle scripture references
        if slide_type == 'scripture':
            ref_match = re.search(r':\s*(.+)$', title)
            if ref_match:
                yaml_lines.append(f"    reference: {ref_match.group(1)}")
        
        # Add content if present
        if content:
            if '\n' in content or len(content) > 60:
                # Multi-line content
                yaml_lines.append("    content: |")
                for line in content.split('\n'):
                    yaml_lines.append(f"      {line}")
            else:
                # Single line content
                yaml_lines.append(f'    content: "{content}"')
    
    return '\n'.join(yaml_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python word_to_yaml.py <input.docx>")
        print("\nOr run interactively:")
        docx_path = input("Enter path to Word document: ").strip()
    else:
        docx_path = sys.argv[1]
    
    if not os.path.exists(docx_path):
        print(f"❌ File not found: {docx_path}")
        sys.exit(1)
    
    print(f"📄 Reading {docx_path}...")
    
    # Extract text from Word document
    text = extract_text_from_docx(docx_path)
    
    # Parse the document
    print("🔍 Parsing document...")
    service_date = parse_service_date(text)
    theme = parse_theme(text)
    speaker = parse_speaker(text)
    
    print("\n📋 Extracting service items:")
    items = parse_service_order(text)
    
    print(f"\n📅 Service Date: {service_date}")
    print(f"🎨 Theme: {theme}")
    if speaker:
        print(f"🎤 Speaker: {speaker}")
    print(f"✅ Found {len(items)} service items")
    
    # Create YAML
    yaml_content = create_yaml_structure(service_date, theme, speaker, items)
    
    # Save to file
    output_filename = f"service_orders/{service_date}.yaml"
    os.makedirs("service_orders", exist_ok=True)
    
    with open(output_filename, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Created: {output_filename}")
    print("\n📝 Preview:")
    print("=" * 60)
    print(yaml_content[:800])
    if len(yaml_content) > 800:
        print("...\n(truncated)")
    print("=" * 60)
    
    # Ask if user wants to generate slides immediately
    response = input("\n🎬 Generate PowerPoint slides now? (y/n): ").strip().lower()
    if response == 'y':
        print("\n🚀 Generating slides...")
        os.system(f"python simple_convert.py {service_date}")

if __name__ == "__main__":
    main()