# Prayer Times CLI

A command-line interface tool that displays Islamic prayer times for your location with a beautiful terminal UI. The script automatically detects your location or allows manual input for more accuracy.

## Features

- 🕌 Displays all prayer times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha)
- 🌍 Automatic location detection with manual override option
- ⏰ Shows time remaining until next prayer
- 📅 Displays both Gregorian and Hijri dates
- 💾 Saves your location preferences for future use
- 🎨 Beautiful colored terminal output

## Installation

1. Clone or download this repository:
```bash
git clone https://github.com/Omar-Elhorbity/prayer_time.git
```

2. Install the required dependencies:
```bash
pip install requests
```

3. Make the script executable:
```bash
chmod +x prayer_time.py
```

4. To run it from anywhere in your terminal, add the script's directory to your PATH by adding this line to your `~/.bashrc`:
```bash
export PATH=$PATH:/media/omar/EXTERNAL/Scripts/prayer_time
```

5. Apply the changes:
```bash
source ~/.bashrc
```

## Usage

### Basic Usage
From any directory in your terminal:
```bash
prayer_time.py
```

### Force Manual Location Input
If you want to manually enter your location:
```bash
prayer_time.py --manual
```

### Location Settings
- The first time you run the script, it will attempt to detect your location automatically
- You can choose to accept the detected location or enter it manually
- Your manual location is saved in `~/.prayer_location` for future use

## Data Sources

- Prayer times are fetched from the Aladhan API
- Location detection uses multiple services for accuracy
- Hijri date conversion is handled by the Aladhan API

## Requirements

- Python 3.x
- `requests` library
- Internet connection for fetching prayer times and location data

## License

This project is open source and available under the MIT License. 

Ⓒ Originally made by [Hassan Ezz](https://github.com/hasssanezzz)
