# EchoStream-Ultra
Advanced pronunciation training tool using PyTorch and librosa to visually match your speech intonation with YouTube videos and local media.


[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DBonBonTV%26type%3Dpledges&style=for-the-badge)](https://patreon.com/BonBonTV)

[![Stars](https://img.shields.io/github/stars/merry1025/EchoStream-Ultra?style=social)](https://github.com/merry1025/EchoStream-Ultra/stargazers)
[![Forks](https://img.shields.io/github/forks/merry1025/EchoStream-Ultra?style=social)](https://github.com/merry1025/EchoStream-Ultra/network/members)
[![Pull Requests](https://img.shields.io/github/issues-pr/merry1025/EchoStream-Ultra?style=flat)](https://github.com/merry1025/EchoStream-Ultra/pulls)

中文介绍请看这里 https://github.com/merry1025/EchoStream-Ultra/blob/main/README-CN.md

**EchoStream Ultra** is an advanced, open-source pronunciation training and language learning tool. It uses GPU-accelerated acoustic math to compare your voice against native speakers in movies, TV shows, and YouTube videos. 

Instead of just checking if you said the right words, EchoStream evaluates your **rhythm, pacing, and stress (intonation)**, visually overlaying your voice onto the actor's voice so you can perfectly mimic native speech patterns.

## Screenshot

<img width="1192" height="1002" alt="Screenshot02" src="https://github.com/user-attachments/assets/8f2dba19-a250-4d78-b5fa-49eb74387f9e" />


---

## ✨ What's New in V2.0 (The AI Upgrade)

EchoStream Ultra has been completely rebuilt from the ground up with a state-of-the-art Deep Learning pipeline.

* ** Deep Learning Audio Isolation:** Powered by Facebook's **Demucs** neural network. It no longer just filters frequencies; it structurally rips the actor's pure vocals out of the movie, completely ignoring explosions, wind, and background music.
* ** AI Silence Trimming:** Integrates **Silero VAD** (Voice Activity Detection) to surgically trim dead air and hesitation from your microphone recordings before scoring, ensuring perfect alignment.
* ** Smart Tutor "Shadow Mode":** An automated, hands-free practice loop. The app plays a sentence, opens your mic, and scores you. If your Pitch/Pronunciation > 60% and Rhythm/Stress > 80%, it praises you and moves to the next sentence. If you fail, it loops the sentence until you get it right!
* ** Triple-Metric Scoring:** The old unified score is gone. You now receive precise, independent grades for **Pitch & Pronunciation** (MFCC + DTW Melody), **Rhythm** (Pacing penalties), and **Stress** (Logarithmic RMS envelope).
* ** Global YouTube Support:** A new dropdown menu allows you to easily select your target language (English, French, Spanish, Italian, Japanese, etc.). Just paste a YouTube link, and the app fetches the right video and subtitles automatically.
* ** True Pitch Tracking:** Using `librosa.pyin`, the app now tracks and draws the actual Fundamental Frequency (F0) melody of the actor's voice (Gold Line) and your voice (Magenta Line) so you can visually match their intonation.

EchoStream Ultra 经过了从头到尾的彻底重构，采用了最先进的深度学习 (Deep Learning) 引擎管线。

* **深度学习音频分离：** 由 Facebook 的 **Demucs** 神经网络提供支持。它不再仅仅是过滤频率；它能从电影中结构性地精准剥离出演员的纯净人声，完全无视爆炸声、风声和背景音乐。
* **AI 静音裁剪：** 集成了 **Silero VAD**（语音活动检测），在打分前如同外科手术般精准裁剪掉你麦克风录音中的空白死角和犹豫停顿，确保波形的完美对齐。
* **智能导师“影子模式 (Shadow Mode)”：** 一个自动化的免提跟读循环。软件会播放一个句子，自动打开麦克风，并为你打分。如果你的音高/发音 (Pitch/Pronunciation) > 60% 且 节奏/重音 (Rhythm/Stress) > 80%，它会给出表扬并自动进入下一句。如果没有达标，它会循环播放该句子，直到你读对为止！
* **三重指标打分：** 旧的单一综合评分已成为历史。你现在会获得精确、独立的单项评分，包括：**音高与发音 (Pitch & Pronunciation)**（MFCC + DTW 旋律算法）、**节奏 (Rhythm)**（语速惩罚机制）以及 **重音 (Stress)**（对数 RMS 包络）。
* **全球 YouTube 支持：** 全新的下拉菜单让你能够轻松选择目标语言（英语、法语、西班牙语、意大利语、日语等）。只需粘贴 YouTube 链接，软件便会自动抓取对应的视频和字幕。
* **真实音高追踪：** 借助 `librosa.pyin`，软件现在可以追踪并绘制出演员原声（金线）和你自己声音（品红线）的真实基频 (F0) 旋律，让你可以直观地在视觉上比对和纠正语调。

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

### 推荐使用一键安装法:
* **下载 https://github.com/merry1025/EchoStream-Ultra/releases/download/v2.0/EchoStream_Ultra_Release.zip
* **解压缩
* **运行Start_EchoStream.bat

### Suggested one-click installation:
* **Download https://github.com/merry1025/EchoStream-Ultra/releases/download/v2.0/EchoStream_Ultra_Release.zip
* **Unzip
* **Run: Start_EchoStream.bat

OR / 或者：

### Prerequisites
1. **Python 3.8+**
2. **VLC Media Player** (Must be installed on your system for the Python-VLC bindings to render the video).
3. *(Optional but Recommended)* An NVIDIA GPU for PyTorch acceleration.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/merry1025/EchoStream-Ultra.git
   cd EchoStream-Ultra

### Create a virtual environment

python -m venv venv
venv\Scripts\activate  # On Windows

### Install the required dependencies

pip install -r requirements.txt

### Run the application

python EchoStream_Ultra_v26.py

## Usage Guide & Hotkeys

EchoStream Ultra is designed to be used completely hands-free once your video is loaded, allowing you to focus entirely on your pronunciation. 

| Action | Hotkey / Control | Description |
| :--- | :--- | :--- |
| **Load Media** | `Ctrl + O` | Manually select a local video file (MP4/MKV) and its matching SRT subtitle file. |
| **Play Segment** | `Space` or `P` | Plays the video for the current subtitle sentence. |
| **Next Subtitle** | `Right Arrow` | Skips to the next subtitle sentence. You can also **Right-Click** anywhere on the app to quickly skip forward. |
| **Previous Subtitle** | `Left Arrow` | Goes back to the previous subtitle sentence. |
| **Record** | `R` | Starts your microphone. Speak the sentence naturally. The recording stops automatically based on the sentence length. |
| **Stop Recording**| `S` | Manually stops the microphone recording early if you finish speaking before the auto-cutoff. |
| **Replay Me** | `H` | Plays back your last recorded microphone attempt so you can hear yourself. |
| **Play Both** | `B` | Plays the actor's voice and your recorded voice simultaneously (with an auto-synced delay) to hear the exact overlap. |
| **Save Favorite** | `F` | Saves the current sentence to a dedicated "Favorites" list for this specific video. |
| **Mode Toggle** | `M` | Switches between **Normal Mode** (going through the whole video) and **Review Mode** (only looping through your saved favorites). |
| **Delete Favorite**| `Delete` | Removes the current sentence from your favorites list (only works while in Review Mode). |

## ️ 安装说明

### 前置要求
1. **Python 3.8+**
2. **VLC Media Player** (您的电脑上必须安装 VLC 播放器，以便 Python-VLC 组件能够渲染视频界面)。
3. *(可选但强烈推荐)* 配备 NVIDIA 显卡以获得 PyTorch 硬件加速。

### 部署步骤
1. 克隆代码仓库：

   git clone [https://github.com/merry1025/EchoStream-Ultra.git](https://github.com/merry1025/EchoStream-Ultra.git)
   
   cd EchoStream-Ultra
   
3. 创建并激活虚拟环境：

   python -m venv venv
   
   venv\Scripts\activate  # Windows 用户使用此命令
   
5. 安装所需依赖包：

   pip install -r requirements.txt

6. 运行程序：
   python EchoStream_Ultra_v26.py
   
## 使用指南与快捷键

视频加载完成后，EchoStream Ultra 完全支持“免提”操作，让您能全神贯注于发音练习。

| 操作 | 快捷键 / 鼠标 | 功能说明 |
| :--- | :--- | :--- |
| **加载本地媒体** | `Ctrl + O` | 手动选择本地视频文件 (MP4/MKV) 及其对应的 SRT 字幕文件。 |
| **播放当前片段** | `空格 (Space)` 或 `P` | 播放当前字幕对应的一段视频。 |
| **下一句字幕** | `右方向键` | 跳到下一句字幕。您也可以在程序界面任意位置 **右键单击** 快速跳到下一句。 |
| **上一句字幕** | `左方向键` | 退回到上一句字幕。 |
| **开始录音** | `R` | 开启麦克风录音。自然地朗读出句子即可。录音会根据原句子的长度自动停止。 |
| **提前停止录音** | `S` | 如果您在自动停止前就读完了，可以手动提前结束麦克风录音。 |
| **回放我的录音** | `H` | 播放您刚刚录制的声音，听听自己的表现。 |
| **同步对比播放** | `B` | 同时播放演员的原声和您的录音（系统会自动同步音频延迟），让您听出精确的口音重合度。 |
| **收藏当前句子** | `F` | 将当前句子保存到当前视频专属的“收藏夹”列表中。 |
| **切换复习模式** | `M` | 在 **普通模式**（按顺序播放整个视频）和 **复习模式**（仅循环播放您收藏的难点句子）之间切换。 |
| **删除当前收藏** | `Delete` | 从收藏夹列表中移除当前句子（仅在“复习模式”下有效）。 |



# Buy me a coffee on Patreon
[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DBonBonTV%26type%3Dpledges&style=for-the-badge)](https://patreon.com/BonBonTV)
