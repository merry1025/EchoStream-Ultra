# EchoStream-Ultra
Advanced pronunciation training tool using PyTorch and librosa to visually match your speech intonation with YouTube videos and local media.

# EchoStream Ultra

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DYOUR_PATREON_USERNAME%26type%3Dpledges&style=for-the-badge)](https://patreon.com/YOUR_PATREON_USERNAME)

**EchoStream Ultra** is an advanced, open-source pronunciation training and language learning tool. It uses GPU-accelerated acoustic math to compare your voice against native speakers in movies, TV shows, and YouTube videos. 

Instead of just checking if you said the right words, EchoStream evaluates your **rhythm, pacing, and stress (intonation)**, visually overlaying your voice onto the actor's voice so you can perfectly mimic native speech patterns.

---

## Key Features

* **Harmonic Source Separation:** Automatically filters out background music, wind, and explosions from movie audio, isolating just the actor's voice for accurate comparison.
* **DTW Intonation Scoring:** Uses Dynamic Time Warping (DTW) and Mel-frequency cepstral coefficients (MFCCs) to score how perfectly your pronunciation rhythm and stress match the native speaker.
* **Live Blueprint Waveforms:** Instantly draws the actor's stress waveform on the screen as you read the subtitle, giving you a visual guide on where to place your emphasis *before* you speak.
* **Native YouTube Integration:** Paste a YouTube URL, and the app automatically downloads the highest-quality video and extracts the English subtitles (`.vtt` to `.srt` auto-conversion).
* **Smart Per-Video Favorites:** Save difficult sentences to your "Favorites." The app dynamically remembers which favorites belong to which video, allowing you to enter "Review Mode" and practice targeted loops.
* **"Play Both" Sync Engine:** Plays the actor's voice and your recorded voice simultaneously with a precisely calculated hardware delay, letting you hear exactly where your accent drifted.

---

## How It Works (The Acoustic Engine)

EchoStream Ultra acts as a strict vocal coach using a 4-step pipeline:
1. **Auto-Isolation (`librosa.effects.hpss`):** Extracts harmonic frequencies (human voice) and discards percussive noise (room tone/sound effects).
2. **Smart Trimming:** Uses RMS energy envelopes to surgically trim dead air, ensuring both audio clips start at the exact same `0.0s` mark.
3. **Tensor Mapping:** Converts the clean audio into 13-dimensional MFCC tensors using PyTorch, removing volume differences to focus purely on mouth movement and pitch.
4. **Pacing Penalty:** Calculates the Euclidean distance between the waveforms and applies a strict time-penalty if your syllable pacing lags behind the native speaker.

---

## Installation

### Prerequisites
1. **Python 3.8+**
2. **VLC Media Player** (Must be installed on your system for the Python-VLC bindings to render the video).
3. *(Optional but Recommended)* An NVIDIA GPU for PyTorch acceleration.

### Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/merry1025/EchoStream-Ultra.git](https://github.com/merry1025/EchoStream-Ultra.git)
   cd EchoStream-Ultra

### Create a virtual environment

python -m venv venv
venv\Scripts\activate  # On Windows

### Install the required dependencies

pip install -r requirements.txt

### Run the application

python "EchoStream Ultra.py"
