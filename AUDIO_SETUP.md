# Adding Background Music to Countdown Videos

## Quick Setup

### Option 1: Use Your Own Music

```bash
# Place your audio file in the audio directory
mkdir -p audio
cp /path/to/your/music.mp3 audio/countdown_music.mp3

# Generate countdown with music
python create_countdown.py --format mp4 --theme forgiveness
```

### Option 2: Specify Custom Audio File

```bash
python create_countdown.py --format mp4 --audio /path/to/music.mp3
```

## Recommended Music Sources (Royalty-Free)

### 1. Free Music Archive
- Website: https://freemusicarchive.org
- Search for: "piano calm" or "ambient peaceful"
- License: Look for CC0 or CC BY licenses
- Download as MP3

### 2. YouTube Audio Library
- Website: https://www.youtube.com/audiolibrary
- Filter by: Mood → Calm, Inspirational
- Genre: Ambient, Classical
- All music is free to use

### 3. Pixabay Music
- Website: https://pixabay.com/music
- Search: "calm piano", "peaceful", "meditation"
- All content is free for commercial use
- No attribution required

### 4. Incompetech
- Website: https://incompetech.com/music
- Search: "Calm" or "Peaceful"
- Free with attribution (or purchase license)
- High quality compositions

### 5. Purple Planet Music
- Website: https://www.purple-planet.com
- Genre: Ambient, Peaceful
- Free with attribution
- Download MP3 directly

## Recommended Search Terms

When looking for church-appropriate music:
- "calm piano"
- "peaceful ambient"
- "meditation music"
- "gentle instrumental"
- "soft classical"
- "worship background"
- "contemplative"

## File Format Requirements

- **Format**: MP3, WAV, M4A, or OGG
- **Length**: At least 5 minutes (or your countdown duration)
- **Volume**: Moderate level (will be mixed with video)
- **Style**: Instrumental (no vocals) works best

## Step-by-Step: Download from YouTube Audio Library

1. Go to https://studio.youtube.com/channel/UC/music
2. Click on "Audio Library" in left sidebar
3. Filter by:
   - Mood: Calm
   - Genre: Ambient or Classical
4. Preview tracks by clicking play
5. Click download icon (⬇️) to download as MP3
6. Save to `audio/countdown_music.mp3`

## Example: Download Calm Piano Track

```bash
# Create audio directory
mkdir -p audio

# Download a calm track (example using curl - adjust URL)
# You'll need to manually download from the websites above

# Once downloaded, move it:
mv ~/Downloads/calm-piano-track.mp3 audio/countdown_music.mp3

# Test it
python create_countdown.py --format mp4
```

## Audio Specifications

The script will automatically:
- ✅ Trim audio to match video length (5 minutes)
- ✅ Encode as AAC at 192kbps
- ✅ Mix with video properly
- ✅ Handle different audio formats

## Troubleshooting

### "Audio file not found"
```bash
# Check the file exists
ls -la audio/countdown_music.mp3

# Make sure the path is correct
python create_countdown.py --audio audio/countdown_music.mp3
```

### "Audio doesn't play"
- Make sure ffmpeg is installed: `ffmpeg -version`
- Try converting to MP3: `ffmpeg -i input.wav output.mp3`

### "Audio is too loud/quiet"
Use ffmpeg to adjust volume:
```bash
# Reduce volume by 50%
ffmpeg -i input.mp3 -filter:a "volume=0.5" output.mp3

# Increase volume by 50%
ffmpeg -i input.mp3 -filter:a "volume=1.5" output.mp3
```

## Recommended Free Tracks

Here are some specific recommendations (all royalty-free):

1. **"Peaceful Piano" genre** - YouTube Audio Library
   - Calm, meditative piano pieces
   - Perfect for pre-service

2. **"Ambient Meditation"** - Pixabay
   - Soft, peaceful background music
   - No distracting melodies

3. **"Ascending"** by Audionautix (Incompetech)
   - Gentle, uplifting
   - Free with attribution

4. **"Meditation Impromptu 01"** - Purple Planet
   - Contemplative piano
   - Very church-appropriate

## Legal Note

⚠️ **Always check licensing requirements**
- Some free music requires attribution
- Read the license terms before using
- If in doubt, use CC0 (public domain) tracks

## Default Behavior

If you place a file at `audio/countdown_music.mp3`, it will be automatically used:

```bash
# Just run normally - audio will be included automatically
python create_countdown.py --format mp4
```

The script checks these locations in order:
1. `audio/countdown_music.mp3`
2. `audio/church_music.mp3`
3. `audio/calm_piano.mp3`
4. `output/countdown_music.mp3`

Place your music file in any of these locations for automatic use!