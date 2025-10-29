# Church Slides Generator

Automatically generate PowerPoint presentations for church services from Word documents or YAML files. Features AI-powered parsing, customizable backgrounds, and support for multiple service formats.

## Features

✨ **Word Document to Slides** - Convert service orders from Word documents to PowerPoint  
🎨 **Custom Backgrounds** - Generate themed gradient backgrounds for different slide types  
🤖 **AI-Powered Parsing** - Intelligent detection of service items (songs, prayers, scripture, etc.)  
📊 **Multiple Slide Types** - Support for countdown, songs, prayers, scripture, sermons, communion, and more  
🔄 **Flexible Workflow** - Use AI agents or direct conversion for reliability  

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Slide Types](#slide-types)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/church-slides.git
cd church-slides
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install ffmpeg (Required for countdown videos)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add to PATH

**Verify installation:**
```bash
ffmpeg -version
```

### Step 5: Install Ollama (Optional - for AI agents)

Only needed if you want to use the AI agent workflow (`src/main.py`).

**macOS:**
```bash
brew install ollama
ollama serve
ollama pull gemma3
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull gemma3
```

**Windows:**
- Download from [https://ollama.ai](https://ollama.ai)
- Install and run
- Execute: `ollama pull gemma3`

### Step 5: Create Required Directories

```bash
mkdir -p service_orders backgrounds/default output
```

## Quick Start

### Option 1: From Plain Text (Recommended for Testing)

```bash
# Test the parser with sample data
python test_text_to_yaml_fixed.py
```

This will:
1. Parse sample service order text
2. Create `service_orders/2025-06-22.yaml`
3. Optionally generate PowerPoint slides

### Option 2: From Word Document

```bash
# Convert Word doc to YAML
python word_to_yaml.py "path/to/your/service_order.docx"

# Generate slides
python simple_convert.py 2025-06-22
```

### Option 3: From Existing YAML

```bash
# If you already have a YAML file in service_orders/
python simple_convert.py 2025-10-12
```

## Usage

### 1. Generate Background Images

Create themed backgrounds for your slides:

```bash
# Generate backgrounds for a theme
python generate_backgrounds.py forgiveness

# Generate with custom colors
python generate_backgrounds.py easter \
  --colors countdown:"(255,192,203),(255,105,180)" \
           sermon:"(135,206,235),(70,130,180)"

# Adjust transparency and rounded corners
python generate_backgrounds.py christmas --opacity 150 --radius 40
```

This creates images in `backgrounds/themename/`:
- countdown.jpg
- song.jpg
- hymn.jpg
- prayer.jpg
- scripture.jpg
- sermon.jpg
- communion.jpg
- offering.jpg
- children.jpg
- liturgy.jpg
- general.jpg

### 2. Create Service Order YAML

#### Format Example

Create a file `service_orders/2025-06-22.yaml`:

```yaml
date: 2025-06-22
theme: Disciples Making Disciples
speaker: Pastor Megan

order:
  - type: countdown
    title: 5 Minute Countdown
  
  - type: song
    title: Opening Praise
    content: "Amazing Grace"
  
  - type: children_message
    title: Children's Message
    presenter: Pastor Megan
  
  - type: liturgy
    title: Call to Worship
    content: |
      Leader: We are called to be God's children.
      People: God's love has been poured on us through Jesus Christ!
  
  - type: scripture
    title: Scripture Reading
    reference: Matthew 6:14-15
    content: |
      For if you forgive others their trespasses,
      your heavenly Father will also forgive you
  
  - type: sermon
    title: Sermon Title
    speaker: Pastor Name
  
  - type: communion
    title: Holy Communion
  
  - type: offering
    title: Offering with Doxology
  
  - type: dismissal
    title: Dismissal
```

### 3. Generate PowerPoint

```bash
python simple_convert.py 2025-06-22
```

Output will be saved to: `output/2025-06-22_themename_ServiceSlides.pptx`

### 4. Convert Word Document to YAML

```bash
python word_to_yaml.py "Service_June_22.docx"
```

**Word Document Format:**

```
Service Date: June 22, 2025
Theme: Disciples Making Disciples
Speaker: Pastor Megan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Order of Service

5 Minute Countdown (Regular)

Opening Praise:
Amazing Grace

Announcements

Children's Message
-Pastor Megan

Call to Worship
L: We are called to be God's children.
P: God's love has been poured on us through Jesus Christ!

Opening Prayer:
Lord of Light and Mercy, be with us this day...

Scripture: Acts 3:11-19
11 While the man held on to Peter and John...

Sermon:
Pastor Megan

Holy Communion

Dismissal
```

## File Structure

```
church-slides/
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore file
│
├── src/                              # Main application (AI agent workflow)
│   ├── __init__.py
│   ├── main.py                       # CrewAI workflow
│   ├── service_crew.py               # Agent definitions
│   ├── manual_execution.py           # Manual execution
│   └── tools/
│       ├── __init__.py
│       └── pptx_creator_tool.py      # PowerPoint creation
│
├── simple_convert.py                 # Direct YAML→PPTX (recommended)
├── test_text_to_yaml_fixed.py        # Test parser without Word doc
├── word_to_yaml.py                   # Word→YAML converter
├── generate_backgrounds.py           # Background generator
│
├── service_orders/                   # YAML service files
│   ├── 2025-06-22.yaml
│   └── 2025-10-12.yaml
│
├── backgrounds/                      # Background images by theme
│   ├── forgiveness/
│   ├── easter/
│   └── default/
│
└── output/                           # Generated PowerPoint files
    └── *.pptx
```

## Slide Types

The application supports the following slide types:

| Type | Description | Background |
|------|-------------|------------|
| `countdown` | Pre-service countdown timer | countdown.jpg |
| `song` | Worship songs | song.jpg |
| `hymn` | Traditional hymns | hymn.jpg |
| `prayer` | Prayer segments | prayer.jpg |
| `scripture` | Bible readings | scripture.jpg |
| `sermon` | Sermon/message | sermon.jpg |
| `communion` | Communion/Eucharist | communion.jpg |
| `offering` | Offering time | offering.jpg |
| `children_message` | Children's message | children.jpg |
| `liturgy` | Liturgical readings | liturgy.jpg |
| `text` | General announcements | general.jpg |
| `dismissal` | Benediction/dismissal | general.jpg |

## Customization

### Custom Themes

1. Generate new background set:
```bash
python generate_backgrounds.py "my_theme_name"
```

2. Use in YAML:
```yaml
theme: My Theme Name
```

### Custom Colors

```bash
python generate_backgrounds.py "ocean_theme" \
  --colors countdown:"(0,105,148),(0,52,89)" \
           song:"(64,224,208),(0,139,139)" \
           sermon:"(25,25,112),(0,0,128)"
```

### Modify Slide Layout

Edit `src/tools/pptx_creator_tool.py` to customize:
- Font sizes and styles
- Text positioning
- Background transparency
- Box styling

## Troubleshooting

### "module yaml not found"

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows

# Reinstall PyYAML
pip install PyYAML
```

### "No module named 'src'"

```bash
# Create __init__.py files
touch src/__init__.py
touch src/tools/__init__.py
```

### "Background image not found"

```bash
# Generate backgrounds for your theme
python generate_backgrounds.py your_theme_name

# Or use default theme
python generate_backgrounds.py default
```

### YAML Parsing Errors

Check your YAML file for:
- Proper indentation (2 spaces)
- Quoted strings with special characters (colons, quotes)
- Use `|` for multi-line content

### Ollama Connection Issues

```bash
# Make sure Ollama is running
ollama serve

# Check if model is installed
ollama list

# Pull model if missing
ollama pull gemma3
```

### Font Issues (Background Generation)

The script tries multiple font paths. If Arial isn't found:
- **macOS**: Should work automatically
- **Linux**: `sudo apt-get install ttf-mscorefonts-installer`
- **Windows**: Arial included by default

## Workflows

### Recommended: Direct Conversion (No AI)

Fast, reliable, deterministic:

```bash
python word_to_yaml.py service.docx
python simple_convert.py 2025-06-22
```

### Advanced: AI Agent Workflow

Uses CrewAI agents for parsing (requires Ollama):

```bash
python -m src.main --service-date 2025-06-22
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [python-pptx](https://python-pptx.readthedocs.io/)
- AI agents powered by [CrewAI](https://www.crewai.com/)
- LLM support via [LiteLLM](https://litellm.ai/)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [Troubleshooting](#troubleshooting) section
- Review existing issues for solutions

---

Made with ❤️ for church media teams