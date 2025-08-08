
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

Here’s the organized section for your README file, detailing the **Algorithm Overview** and how the **Thermal-to-Auditory Mapping** works:

---

## **Algorithm Overview**

### **Thermal-to-Auditory Mapping**

The **ThermalSense** system is designed to transform thermal images into auditory soundscapes, making heat and cold information accessible through sound . The system processes a thermal image to generate:

1. **A color-coded image**, where different temperature ranges are mapped to specific colors.
2. **A soundscape**, where different parts of the image correspond to musical notes, creating an auditory representation of thermal data.

The primary application is for sensory substitution, allowing users to perceive temperature through sound

---

### **Main Parts**

1. **Initialization (`__init__`)**

   * **Purpose**: Set up essential parameters for the system.
   * **Key Tasks**:

     * Defines audio sample rate, sound duration, and output saving locations.
     * Configures color and frequency ranges for temperature mapping (hot, cold, and neutral).
     * Allows customization by passing temperature ranges, color mappings, and frequency configurations.
     * Prepares output folders if images are to be saved.

---

 
---

2. **Image Processing (`process_image`)**

   * **Purpose**: The main function to process each thermal frame.
   * **Steps**:

     1. **Resizing**: The image is resized to 50x30 pixels for consistent processing and grayscale image generation for each thermal frame (image_acquisition). 
     2. **Cleaning**: Non-thermal artifacts (e.g., sensor reflections) are removed using inpainting techniques(remove_non_thermal).
     3. **Mirroring**: The image is flipped for correct orientation.
     4. **mapping **: it generates the colored thermal image (`generate_colored_thermal_image`).
        Convert the 2D temperature array into an RGB image, representing thermal data visually,Based on the temperature, the         pixel is assigned a specific color (e.g., **hot** = red, **cold** = blue).
     6. **Soundscape Creation**: Generates a corresponding soundscape based on the processed image (create_soundscape).
     7. **Saving**: Optionally saves the cleaned and color-coded images .
     8. **Return**: Outputs both the cleaned image and the generated sound.
     
  
---

3. **Sound Generation – Turning Image Into Music (`create_soundscape`)**

   * **Purpose**: Converts the processed thermal image into a stereo audio "soundscape".
   * **How It Works**:

     * The system scans the image column by column, from left to right.
     * For each row (vertical position), the pixel’s temperature determines its pitch, using `_pitch_from_y` to calculate the frequency.
     * The sound is then mapped to different musical tones based on whether the temperature is hot, cold, or neutral.
     * **Hot regions** use a brass-like tone, **cold regions** use a reed-like tone, and **neutral regions** are silent or based what the user entered in custom mode.
     * **Stereo Panning**: The left part of the image is panned more to the left speaker, and the right part is panned more to the right speaker.
     * **Full Audio**: After processing all columns, the entire soundscape is combined into one complete audio file.

---

4. **Pentatonic Quantization (The Musical Mapping)**

   * **Purpose**: Ensure harmonious sound by quantizing pitches to a pentatonic scale.
   * **Functions**:

     * **\_pitch\_from\_y**: Maps the row number to a specific frequency based on its vertical position in the image. Higher rows correspond to higher frequencies, and lower rows correspond to lower frequencies.
     * **\_quantize**: Takes the calculated frequency and snaps it to the nearest **pentatonic note** using a precomputed table of ratios ([1.0, 1.125, 1.25, 1.5, 1.875]) across four octaves (starting from A3 = 220 Hz).
   * **Result**: Ensures that all notes, even when played simultaneously, sound harmonious without clashing frequencies.

---

5. **Tone Generation**

   * **Purpose**: Generate distinct tones for cold and hot regions.
   * **Cold Tone** (`_generate_reed_tone`): Creates a reed-like sound with slight vibrato for cold regions.
   * **Hot Tone** (`_generate_brass_tone`): Generates a richer, brass-like sound for hot regions, emphasizing harmonics.

---

6. **Other Helper Functions**

   * **save\_audio**: Saves the final soundscape as a **stereo WAV file**.
   * **detect\_hot\_cold\_regions**: Identifies how many columns contain at least one "hot" or "cold" pixel, useful for analysis.

---

### **Signal Generation**

1. **Pitch Calculation**: Map each temperature reading to the nearest note in a five-note pentatonic scale, so every tone you hear is guaranteed to fit together musically.
2. **Sound Synthesis**: Generate each note as a simple sine wave—its frequency set by the pitch and its loudness (amplitude) scaled by how extreme the temperature is.
3. **Stereo Panning**: The sound is panned from left to right, corresponding to the X-position of thermal features in the image.
4. **Real-Time Playback**: Audio is generated and played back in real-time, ensuring immediate auditory feedback for the user.

---


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




