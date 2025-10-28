import os
import sys
from PIL import Image, ImageDraw, ImageFont
import argparse
import re


def parse_color_pair(pair_str):
    """Parse a string like '(0,120,200),(0,60,130)' into two RGB tuples."""
    matches = re.findall(r"\((\d+),(\d+),(\d+)\)", pair_str)
    if len(matches) != 2:
        raise ValueError(f"Invalid color pair format: {pair_str}")
    top = tuple(map(int, matches[0]))
    bottom = tuple(map(int, matches[1]))
    return top, bottom


def create_slide_image(text, color_top, color_bottom, save_path, opacity=130, radius=30):
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), color_top)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for i in range(height):
        ratio = i / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

    # Text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Translucent rounded box behind text
    padding_x, padding_y = 50, 25
    box_coords = [
        (x - padding_x, y - padding_y),
        (x + text_width + padding_x, y + text_height + padding_y)
    ]

    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(box_coords, radius=radius, fill=(0, 0, 0, opacity))
    img_rgba = Image.alpha_composite(img_rgba, overlay)

    # Draw text (with soft shadow)
    draw_rgba = ImageDraw.Draw(img_rgba)
    draw_rgba.text((x + 3, y + 3), text, fill=(0, 0, 0, 180), font=font)
    draw_rgba.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    img_rgb = img_rgba.convert("RGB")
    img_rgb.save(save_path, "JPEG")
    print(f"✅ Created {save_path}")


def generate_backgrounds(theme_name, color_map, opacity, radius):
    base = r"C:\Users\Lis30\Documents\church_slides\backgrounds"
    folder = os.path.join(base, theme_name)
    os.makedirs(folder, exist_ok=True)

    if not color_map:
        print("⚠️ No colors provided; using default set.")
        color_map = {
            "countdown": ((0, 120, 200), (0, 60, 130)),
            "scripture": ((150, 210, 210), (60, 120, 120)),
            "sermon": ((0, 80, 120), (0, 40, 70)),
            "prayer": ((50, 150, 180), (20, 80, 100)),
            "general": ((100, 130, 160), (40, 60, 80)),
        }

    for name, (top, bottom) in color_map.items():
        text = name.capitalize()
        save_path = os.path.join(folder, f"{name}.jpg")
        create_slide_image(text, top, bottom, save_path, opacity, radius)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate themed gradient backgrounds with text overlays."
    )
    parser.add_argument("theme", help="Theme name (used as output folder name)")
    parser.add_argument(
        "--colors",
        nargs="*",
        help="Optional color pairs for slides, e.g. countdown:(0,120,200),(0,60,130)",
    )
    parser.add_argument("--opacity", type=int, default=130, help="Box opacity (0-255)")
    parser.add_argument("--radius", type=int, default=30, help="Corner radius of box")

    args = parser.parse_args()

    color_map = {}
    if args.colors:
        for color_str in args.colors:
            if ":" not in color_str:
                print(f"⚠️ Invalid color spec '{color_str}', skipping.")
                continue
            name, pair_str = color_str.split(":", 1)
            try:
                color_map[name] = parse_color_pair(pair_str)
            except ValueError as e:
                print(f"❌ Error parsing {name}: {e}")

    generate_backgrounds(args.theme, color_map, args.opacity, args.radius)
