# Setting Up Countdown Video to Auto-Play

The countdown video has been added to your PowerPoint with church branding and optional music, but you need to set it to auto-play manually.

## What's Included in Your Countdown

✅ Church name (e.g., "Vernon United Methodist Church")  
✅ Church logo (if provided)  
✅ 5-minute countdown timer (5:00 to 0:00)  
✅ Background music (if audio file was provided)  
✅ Theme-matched gradient background  

## Quick Setup (30 seconds)

1. **Open your PowerPoint file**
   - Open `output/2025-XX-XX_XXXXX_ServiceSlides.pptx`

2. **Go to Slide 1**
   - Click on slide 1 in the sidebar

3. **Click on the video**
   - You should see the countdown video in the center of the slide
   - Click it once to select it

4. **Set to Auto-Play**
   - Look for the **Playback** tab in the ribbon (it appears when video is selected)
   - Find the **Start** dropdown
   - Change it from "On Click" to **"Automatically"**

5. **Optional: Full Screen Mode**
   - Still in Playback tab
   - Check **"Play Full Screen"** if you want it to fill the screen
   - Check **"Loop until Stopped"** if you want it to repeat (not recommended for countdown)
   - Check **"Hide During Show"** to hide video controls
   - Adjust **Volume** slider if needed

6. **Save**
   - Press Ctrl+S (Windows) or Cmd+S (Mac)
   - Close and reopen to test

## Test the Countdown

1. Press **F5** to start the slideshow from beginning
2. OR click **Slide Show** > **From Beginning**
3. The video should automatically start playing
4. You should see:
   - Your church name at top
   - Church logo (if included)
   - "Service begins in"
   - Countdown timer (5:00 → 0:00)
   - Hear background music (if included)

## Troubleshooting

### Video doesn't appear

**Solution:**
- Make sure `output/countdown.mp4` exists
- Try manually inserting: Insert > Video > Video on My PC
- Select `output/countdown.mp4`

### Video appears but won't play

**Solution:**
- Make sure you set Start to "Automatically" in Playback tab
- Check that video file hasn't been moved
- Try playing the video file directly to ensure it works

### No audio in countdown video

**Solution:**
```bash
# Add audio to existing video
python add_audio_to_countdown.py --audio path/to/music.mp3

# Or regenerate countdown with audio
python create_countdown.py --format mp4 --audio audio/countdown_music.mp3

# Then regenerate PowerPoint
python simple_convert.py 2025-06-22
```

### Church logo doesn't appear

**Solution:**
- Logo must be placed before generating countdown
- Check: `ls logos/church_logo.png`
- See LOGO_SETUP.md for detailed instructions
- Regenerate countdown with logo:
```bash
python create_countdown.py --format mp4 --logo logos/methodist_logo.png
python simple_convert.py 2025-06-22
```

### Video is too small/large

**Solution:**
- Click the video and drag corners to resize
- Hold Shift while dragging to maintain aspect ratio
- Recommended: Fill most of the slide but leave some margin

### Video quality is poor

**Solution:**
The video is generated at 1920x1080 HD resolution. If it looks poor:
- Check your display resolution
- Make sure you're viewing in Slide Show mode (F5)
- The video may compress when editing but looks better in presentation mode

## Alternative: Manual Video Insert

If the video wasn't embedded automatically:

1. Go to slide 1
2. **Insert** > **Video** > **Video on My PC...**
3. Navigate to `output/countdown.mp4`
4. Click **Insert**
5. Follow steps 3-6 above to set autoplay

## Customizing the Countdown

### Change Church Name
```bash
python create_countdown.py --format mp4 \
  --church-name "First United Methodist Church"
python simple_convert.py 2025-06-22
```

### Change Logo
```bash
# Place new logo
cp new_logo.png logos/church_logo.png

# Regenerate
python create_countdown.py --format mp4 --logo logos/church_logo.png
python simple_convert.py 2025-06-22
```

### Change Background Music
```bash
# Replace audio file
cp new_music.mp3 audio/countdown_music.mp3

# Add to existing video (fast)
python add_audio_to_countdown.py

# Or regenerate everything
python create_countdown.py --format mp4
python simple_convert.py 2025-06-22
```

### Change Duration
```bash
# 3-minute countdown
python create_countdown.py --format mp4 --duration 180
python simple_convert.py 2025-06-22

# 10-minute countdown
python create_countdown.py --format mp4 --duration 600
python simple_convert.py 2025-06-22
```

## Best Practices

✅ **Test before service** - Always run through the slideshow before the service  
✅ **Volume check** - Test audio volume in your church's system  
✅ **Backup plan** - Have a manual countdown or start time ready  
✅ **Early arrival** - Start countdown at least 5 minutes before service  
✅ **Autoplay setup** - Set up autoplay once, save the file as a template  

## Quick Reference Card

**Auto-play Setup:**
1. Click video in slide 1
2. Playback tab
3. Start: Automatically
4. Save (Ctrl+S / Cmd+S)

**Test:**
- Press F5
- Video should play automatically

**Regenerate:**
```bash
python create_countdown.py --format mp4
python simple_convert.py 2025-06-22
```

---

For more help, see:
- README.md - Full documentation
- LOGO_SETUP.md - Church logo instructions
- AUDIO_SETUP.md - Background music sources
