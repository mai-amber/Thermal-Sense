
# ThermalSense – Real-Time Thermal-to-Audio Perception System

**ThermalSense** is a sensory substitution system designed to translate thermal camera data into sound, enabling users to "hear" temperature differences in their surroundings. This system is particularly useful for the visually impaired, educational purposes, or research applications in human-computer interaction.

The system works by mapping the temperature values captured by infrared sensors (like the MLX90640) to audio cues, providing real-time auditory feedback. Hotter regions correspond to higher-pitched sounds, while cooler areas are represented with lower tones.

This README serves as a comprehensive guide to the **ThermalSense Core System**, detailing the system's architecture, algorithms, and implementation steps based on the principles outlined in the related paper **"ThermalSense: A Sensory Substitution System for Enabling Perception of Thermal Information"** (link to paper).

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

This system has applications in:

* **Assistive Technology**: Enabling visually impaired users to "hear" heat sources.
* **Education**: Teaching about thermal imaging and perception.
* **Research**: Exploring human-computer interaction and multisensory integration.

---

## System Architecture

The system is composed of four main classes, each handling a distinct part of the process:

* **ThermalSenseGUI**: The main user interface for setting parameters and controlling the system.
* **ThermalSenseRunner**: The orchestrator, managing data acquisition, processing, and output.
* **ThermalSenseInput**: The interface for reading data from the MLX90640 thermal camera.
* **ThermalSense**: The core class for processing thermal images, generating the audio output, and saving results.

### Class Structure

* **ThermalSenseGUI**:

  * Responsible for displaying the GUI, gathering user input (e.g., custom temperature ranges), and starting or stopping the system.

* **ThermalSenseRunner**:

  * Coordinates real-time cycles of acquiring, processing, and outputting thermal data. It interacts with both `ThermalSenseInput` and `ThermalSense`.

* **ThermalSenseInput**:

  * Handles the I²C connection with the MLX90640 sensor, reading temperature data in real-time.

* **ThermalSense**:

  * Processes the thermal data, cleans it, maps temperature ranges to sound, and generates audio cues.

---

## Data Flow

### 1. **ThermalSenseInput – Frame Acquisition**

* Initializes I²C connection with the MLX90640 sensor.
* Captures a thermal frame (768 values) representing temperature data.

### 2. **ThermalSenseRunner – Frame Handling**

* Acquires each new thermal frame.
* Reshapes the data for processing, updating the frame at a set sample rate.

### 3. **ThermalSense – Image Processing and Sound Generation**

* The frame is processed to clean non-thermal data.
* A heatmap is generated, mapping temperature ranges to specific sound frequencies.
* The audio cues are generated based on the vertical position (pitch) and temperature (volume/timbre).

### 4. **ThermalSenseRunner – Output and Feedback**

* Saves images and audio files to a result directory.
* Logs statistics (e.g., temperature, location of heat sources).
* Plays back the generated soundscapes in real-time and updates the GUI.

### 5. **ThermalSenseGUI – User Control**

* The GUI allows the user to adjust settings such as mode (default or custom ranges), logging options, and visualization display.
* Users can start, stop, or modify the operation at any time.

---

## Algorithm Overview

### Thermal-to-Auditory Mapping

* **Vertical Position** (Y-axis): Mapped to pitch, with higher positions (hotter regions) corresponding to higher notes.
* **Horizontal Position** (X-axis): Determines the timing and stereo panning of the audio.
* **Temperature Mapping**: Divides temperature ranges into categories (e.g., cold, neutral, hot) and maps them to specific instruments or sounds.

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




