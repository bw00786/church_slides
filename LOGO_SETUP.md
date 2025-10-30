# Adding Church Logo to Countdown Video

## Quick Setup

### Step 1: Get Your Methodist Church Logo

**Option A: Download Official UMC Logo**
1. Visit: https://www.resourceumc.org/en/agencies/communications/brand-resources
2. Download the official United Methodist Church Cross & Flame logo
3. Save as PNG format (for transparency)

**Option B: Use Your Church's Custom Logo**
- Use your church's existing logo file
- PNG format with transparent background works best
- JPG is also supported

### Step 2: Place Logo in Project
```bash
# Create logos directory
mkdir -p logos

# Copy your logo file
cp ~/Downloads/umc_logo.png logos/church_logo.png

# Or use specific UMC logo name
cp ~/Downloads/cross_flame.png logos/methodist_logo.png
```

### Step 3: Generate Countdown with Logo
```bash
# Automatic (looks for logos/church_logo.png)
python create_countdown.py --format mp4

# Or specify custom location
python create_countdown.py --format mp4 --logo path/to/your/logo.png

# With custom church name
python create_countdown.py --format mp4 \
  --church-name "Vernon United Methodist Church" \
  --logo logos/umc_logo.png
```

## Default Logo Locations

The script automatically checks these locations (in order):
1. `logos/church_logo.png`
2. `logos/methodist_logo.png`
3. `logos/umc_logo.png`
4. `images/logo.png`
5. `assets/logo.png`

Place your logo in any of these locations for automatic use!

## Logo Specifications

**Recommended:**
- Format: PNG with transparent background
- Size: 250-500px wide (will be auto-resized)
- Aspect Ratio: Any (maintains original proportions)
- Color: White or light colors work best on gradient backgrounds

**Also Supported:**
- JPG files (no transparency)
- Any size (will be scaled proportionally)

## Complete Example
```bash
# 1. Download UMC logo
# Visit https://www.resourceumc.org and download Cross & Flame

# 2. Setup
mkdir -p logos audio
cp ~/Downloads/umc_cross_flame.png logos/methodist_logo.png
cp ~/Downloads/calm_music.mp3 audio/countdown_music.mp3

# 3. Generate countdown with everything
python create_countdown.py --format mp4 \
  --church-name "Vernon United Methodist Church" \
  --logo logos/methodist_logo.png \
  --audio audio/countdown_music.mp3 \
  --theme forgiveness

# 4. Create slides
python simple_convert.py 2025-06-22
```

## Layout Preview
```
┌──────────────────────────────────────┐
│                                      │
│          [UMC LOGO]                  │
│                                      │
│   Vernon United Methodist Church     │
│                                      │
│                                      │
│       Service begins in              │
│                                      │
│            05:00                     │
│                                      │
│                                      │
└──────────────────────────────────────┘
```

## Troubleshooting

**Logo doesn't appear:**
```bash
# Check if logo file exists
ls -la logos/church_logo.png

# Verify path
python create_countdown.py --logo logos/church_logo.png
```

**Logo is too large/small:**
- The script auto-resizes to max 250px wide
- For custom sizing, edit the logo file before use

**Logo has white background:**
- Convert to PNG with transparency using online tools:
  - https://remove.bg (removes background)
  - Or use GIMP/Photoshop to save with transparency

**Logo colors don't match:**
- Edit the logo to use white/light colors
- Or adjust the gradient background colors to complement your logo

## Creating Transparency (If Needed)

If your logo has a white background, remove it:

### Online Tools:
1. https://remove.bg - Upload and download
2. https://www.photoroom.com - Free background removal

### Using GIMP (Free):
1. Open logo in GIMP
2. Layer → Transparency → Add Alpha Channel
3. Select by Color tool → Click white background
4. Press Delete
5. Export as PNG

### Using Preview (Mac):
1. Open logo in Preview
2. Click Markup toolbar icon
3. Click Instant Alpha tool
4. Click white area to remove
5. Export as PNG
