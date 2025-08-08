
# ThermalSense – Real-Time Thermal-to-Audio Perception System

**ThermalSense** is a sensory substitution system designed to translate thermal camera data into sound, enabling users to "hear" temperature differences in their surroundings. This system is particularly useful for  research applications in human-computer interaction.

The system works by mapping the temperature values captured by infrared sensors (like the MLX90640) to audio cues, providing real-time auditory feedback. Hotter regions correspond to higher-pitched sounds, while cooler areas are represented with lower tones.

This README serves as a comprehensive guide to the **ThermalSense Core System**, detailing the system's architecture, algorithms, and implementation steps based on the principles outlined in the related paper **"ThermalSense: A Sensory Substitution System for Enabling Perception of Thermal Information"** https://drive.google.com/file/d/1dFGBmDBlz_y5wf21syICkZNWN9OCk4tf/view?usp=drive_link


---

## Table of Contents

* [Introduction](#introduction)
* [System Architecture](#system-architecture)

  * [Class Structure](#class-structure)
  * [Data Flow](#data-flow)
* [Algorithm Overview](#algorithm-overview)

  * [Thermal-to-Auditory Mapping](#thermal-to-auditory-mapping)
  * [Signal Generation](#signal-generation)
* [Installation Guide](#installation-guide)
* [Running the System](#running-the-system)
* [Key Features](#key-features)
* [Use Cases](#use-cases)
* [Project Structure](#project-structure)

---

## Introduction

**ThermalSense** extends human sensory capabilities by converting thermal information into auditory cues. Inspired by visual-to-auditory systems like *EyeMusic*, it leverages the *EyeMusic* algorithm to create soundscapes from thermal data. Users can perceive temperature variations and localize heat sources through sound.

This system can  have applications in:

* **Assistive Technology**: Enabling visually impaired users to "hear" heat sources.
* **Education**: Teaching about thermal imaging and perception.
* **Research**: Exploring human-computer interaction and multisensory integration.

---

## System Architecture

The system is composed of four main classes, each handling a distinct part of the process:

* **ThermalSenseGUI/MAIN**: The main user interface for setting parameters and controlling the system.
* **ObjectThermalSenseRunner**: The orchestrator, managing data acquisition, processing, and output.
* **ThermalSenseInput**: The interface for reading data from the MLX90640 thermal camera.
* **ThermalSense**: The core class for processing thermal images, generating the audio output, and saving results.

### Class Structure

* **Main/ThermalSenseGUI**:

  * Responsible for displaying the GUI, gathering user input (e.g., custom temperature ranges), and starting or stopping the system, when you hit Run, it launches a ObjectThermalSenseRunner in the background

* **ObjectThermalSenseRunner**:

  * Coordinates real-time cycles of acquiring, processing, and outputting thermal data. It interacts with both `ThermalSenseInput` and `ThermalSense`,In a tight loop it: Grabs frames from the camera via ThermalSenseInput
Hands each frame to ThermalSense for cleaning, color‐mapping, and sonification
Plays back the generated audio, updates the GUI plot, and writes logs/files.


* **ThermalSenseInput**:

  * Handles the I2C connection with the MLX90640 sensor, reading temperature data in real-time.

* **ThermalSense**:

  * provides all the thermal image processing - resizing , cleaning, gray scale , mapping to color , and the core soundscape generation .

---

## Data Flow

### 1. **ThermalSenseInput – Frame Acquisition**

* Initializes I²C connection with the MLX90640 sensor.
* Captures a thermal frame  representing temperature data.

### 2. **ObjectThermalSenseRunner – Frame Handling**

* Acquires each new thermal frame.
* Reshapes the data for processing, updating the frame at a set sample rate.

### 3. **ThermalSense – Image Processing and Sound Generation**

* The frame is processed to clean non-thermal data.
* A heatmap is generated, mapping temperature ranges to specific sound frequencies.
* The audio cues are generated based on the vertical position (pitch) and temperature (volume/timbre).

### 4. **ObjectThermalSenseRunner – Output and Feedback**

* Saves images and audio files to a result directory.
* Logs statistics (e.g., temperature, location of heat sources).
* Plays back the generated soundscapes in real-time and updates the GUI.

### 5. **ThermalSenseGUI – User Control**

User Interface: The ThermalSenseGUI provides a control panel where users can:

Choose Custom Mode: Users can define up to 7 custom temperature ranges, each with its own temperature thresholds, frequency, and color.

Enable/Disable Sound: Users can choose whether they want to hear the generated sounds.
Enable/Disable Real-Time Visualization: Users can toggle live visual updates on the GUI (using Matplotlib).
Enable/Disable Logging: Users can choose to log  CSV file.
Enable/Disable Logging: Users can choose to frame sound save .
Enable/Disable Logging: Users can choose to frame capture saving .

Default Mode: In this mode, the temperature ranges are pre-configured, and users do not need to adjust settings. The ranges are:

Cold (0-20°C): Blue, 200 Hz, Reed sound.

Neutral (21-29°C): Black,0 Hz, silent.

Hot (30-70°C): Red, 500 Hz, Brass sound.

Control Buttons: Users can:

Start the operation (initiate the real-time processing loop).

Stop the operation (halt the loop ).

Exit the operation 

Modify settings at any time to adjust the ranges or toggles (sound, visualization, etc.).

---

## Algorithm Overview

### Thermal-to-Auditory Mapping

This code defines a class called ThermalSense.
Its job is to take a thermal image (showing hot and cold spots), process it, and create:
1.	A color-coded image (where different temperature ranges get different colors)
2.	A “soundscape” (music-like audio, where different parts of the image play different notes)
The main application is for sensory substitution, making heat and cold information accessible through sound.
________________________________________
Main Parts
1. Initialization (__init__)
•	Sets up parameters: audio sample rate, duration, where to save output, color and frequency ranges for hot/cold/neutral.
•	Allows customization: You can pass your own temperature ranges, color, and frequency mappings.
•	Prepares output folders if images will be saved.
________________________________________
2. Color Mapping
generate_colored_thermal_image
•	What it does: Converts the 2D temperature array into a 3-channel RGB image.
•	How: For each pixel, checks which range (“Hot”, “Cold”, “Neutral”, or custom) it belongs to, and colors it accordingly (e.g., “hot” = red, “cold” = blue).
•	Helper function: _color_to_rgb translates color names/hex codes into [R, G, B] arrays.
________________________________________
3. Image Processing
process_image
•	What it does: Main function called to process each thermal frame.
•	Steps:
1.	Loads and resizes the image to 50x30 pixels grayscale.
2.	Removes non-thermal artifacts (e.g., reflections) using in-painting.
3.	Flips the image (mirroring).
4.	Creates a soundscape from the image.
5.	Optionally saves images (cleaned and color-coded).
6.	Returns the cleaned image and the generated sound.
________________________________________
4. Sound Generation – Turning Image Into Music
create_soundscape
•	What it does: Converts the processed thermal image into stereo audio (a “soundscape”).
•	How it works:
o	Goes column by column across the image (left to right).
o	For each column:
	Allocates a slice of time in the audio (like a “window” sweeping left-to-right).
	For each row (vertical position) in that column:
	Looks up the pixel’s temperature.
	Decides if it’s “hot”, “cold”, or “neutral” (based on predefined or custom ranges).
	If it’s “hot” or “cold”, calculates a pitch/frequency using _pitch_from_y, and then generates a short sound (like a musical note).
	Different instruments (brass or reed) are used for “hot” or “cold” (for variety).
	Combines (adds up) the notes for that column into the audio.
	Stereo panning: Notes from the left part of the image play more in the left speaker, and right parts in the right speaker.
o	Combines everything into a full audio “soundscape” for the whole image.
________________________________________

5. Pentatonic Quantization (The Musical Mapping)
_pitch_from_y and _quantize
•	_pitch_from_y:
o	Takes a row number (y) and maps it to a frequency.
o	Bottom row → low frequency, top row → high frequency, all within a defined range.
o	Calls _quantize to “snap” that frequency to the nearest pentatonic note.
•	_quantize:
o	Has a table of all pentatonic notes (using ratios over 4 octaves from A3 = 220 Hz).
o	Finds the closest note to the frequency calculated by _pitch_from_y.
o	Why? So even if image rows map to “in-between” values, you always get a proper pentatonic note (never a “clashing” frequency).
o	Ratios used: [1.0, 1.125, 1.25, 1.5, 1.875] over four octaves.
o	Result: All notes played at once will always sound harmonious (never dissonant).
________________________________________
6. Tone Generation
•	_generate_reed_tone (for cold):
Generates a sound that mimics a reed instrument, with slight vibrato.
•	_generate_brass_tone (for hot):
Generates a richer, “brassier” musical sound, with harmonics.
________________________________________
7. Other Helpers
•	save_audio: Writes the final audio as a stereo WAV file.
•	detect_hot_cold_regions: Counts how many columns contain at least one “hot” or “cold” pixel (used for basic analysis).
________________________________________


### Signal Generation

1. **Pitch Calculation**: Temperature is mapped to a pentatonic scale for harmonious tones.
2. **Sound Synthesis**: Each note is generated using a sine wave formula, modulated by temperature values.
3. **Stereo Panning**: Audio is panned left-to-right based on the X-position of thermal features.
4. **Real-Time Playback**: Audio is generated in real-time, ensuring immediate auditory feedback for the user.

---

## Key Features

* **Real-Time Thermal-to-Audio Conversion**
  Continuously captures MLX90640 frames and immediately sonifies them into stereo “thermal soundscapes,” so you can literally hear heat patterns as they occur.

* **Default vs. Custom Mode**

  * **Default Mode** auto-computes hot/cold thresholds (μ ± σ) for a zero-config quick start (custom UI disabled).
  * **Custom Mode** lets you define up to 7 named temperature ranges, each with its own low/high bounds, display color (CSS name or hex RGB), and base tone frequency.

* **Range Management UI**

  * Add or remove up to 7 custom ranges
  * Specify **Name**, **Low \[°C]**, **High \[°C]**, **Color** (text or RGB), **Frequency \[Hz]**
  * “Validate Data” button enforces that low < high, color names are valid, and frequencies are non-negative before starting

* **Comprehensive Logging & Saving**

  * **Enable/Disable**: image saving (PNG), CSV logging, frame capture, audio file output (WAV)
  * Each run creates a timestamped folder under `Results/ThermalSense-<YYYY-MM-DD_HH-MM-SS>/`
  * CSV output includes frame number, mean temperature, heat category, file paths, and hot/cold counts

* **Real-Time Visualization Controls**

  * **Enable/Disable** live Matplotlib display
  * Overlays show current hot/cold/total column counts on the thermal image
  * Smooth fade-in/out transitions for splash and stop backgrounds

* **Stereo Panning & Musical Mapping**

  * Scans left-to-right: horizontal position → time & stereo pan
  * Vertical position quantized to a pentatonic scale for harmonious chords
  * “Hot” ranges use a brass-like timbre, “Cold” ranges use a reed-like timbre, “Neutral” can be silent

* **Modular, OOP Design**

  * **ThermalSenseGUI**: user interface & control panel
  * **ThermalSenseRunner**: threaded orchestration of capture → process → output → log
  * **ThermalSenseInput**: MLX90640 I²C handling & display update
  * **ThermalSense** (in `Dependencies/ThermalSense`): core image cleaning, color mapping & soundscape synthesis

* **Safe Threading & Shutdown**

  * Start/Stop buttons launch or terminate the runner thread cleanly
  * All resources (I²C bus, open files, Matplotlib figures) are released on exit

---

## Installation Guide

### Requirements

* **Raspberry Pi** or **Linux PC**
* **Python 3.8+**
* **MLX90640 Thermal Camera**

### Steps to Install:

1. Clone the repository:

   ```bash
   git clone https://github.com/NoraTanous/Thermal-Sense.git
   cd Thermal-Sense
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Enable I2C on Raspberry Pi:

   ```bash
   sudo raspi-config
   ```

---

## Running the System

To start the system, run:

```bash
python main.py
```

This will launch the **ThermalSenseGUI**, where you can configure settings and begin the real-time thermal-to-audio mapping.

---

## Use Cases

* **Assistive Technology**: Helping the visually impaired perceive temperature differences in their environment.
* **Educational Tool**: Demonstrating how thermal imaging works and how humans perceive temperature.
* **Research and Development**: Exploring sensory substitution, multisensory integration, and human-computer interaction.

---

## Project Structure

```
ThermalSense/
├── __pycache__/
├── Backup/
├── Dependencies/
│   └── ThermalSense/
├── Pictures/
│   ├── Welcome.png
│   └── ThermalSenseResults.png
├── Results/
│   └── ThermalSense-<timestamp>/
│       ├── cleaned/
│       ├── thermal/
│       ├── audio/
│       └── ThermalSense-<timestamp>.csv
├── venv/
├── .gitignore
├── LICENSE
├── main.py
├── ObjectThermalSenseRunner.py
├── README.md
├── ThermalSenseInput.py
└── ThermalSense/
```




