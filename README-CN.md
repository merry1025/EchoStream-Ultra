# EchoStream-Ultra
基于 PyTorch 和 librosa 的进阶发音训练工具，可将您的语音语调与 YouTube 视频和本地媒体进行直观的可视化比对。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DBonBonTV%26type%3Dpledges&style=for-the-badge)](https://patreon.com/BonBonTV)

**EchoStream Ultra** 是一款高级、开源的发音训练和语言学习工具。它利用 GPU 加速的声学算法，将您的声音与电影、电视节目和 YouTube 视频中的母语者进行比对。

EchoStream 不仅能检查您说的词对不对，它还能精准评估您的**节奏、语速和重音（语调）**，通过将您的声音波形与演员的波形直观地叠加在一起，帮助您完美模仿母语者的说话模式。

## 界面截图

<img width="1195" height="1000" alt="Screenshot01" src="https://github.com/user-attachments/assets/1457d077-8376-494b-9167-b22a24b9665f" />

---

## 核心功能

* **谐波源分离 (Harmonic Source Separation)：** 自动过滤电影音频中的背景音乐、风声和爆炸声，精准提取纯净的演员人声以供比对。
* **DTW 语调评分：** 利用动态时间规整（DTW）和梅尔频率倒谱系数（MFCCs）为您的发音节奏和重音还原度进行打分。
* **实时声纹蓝图：** 在您朗读字幕时，瞬间在屏幕上绘制出演员的重音波形，在开口前为您提供发音重点的视觉指引。
* **YouTube 原生支持：** 只需粘贴 YouTube 链接，软件会自动下载最高画质的视频并提取英文字幕（支持 `.vtt` 自动转 `.srt`）。
* **智能单视频收藏夹：** 将有难度的句子存入“收藏夹”。软件能动态记忆属于该特定视频的专属收藏，让您能在“复习模式 (Review Mode)”下进行针对性循环练习。
* **“双音轨同放”同步引擎：** 通过精准计算的硬件延迟，同时播放演员还原声和您的录音，让您立刻听出自己的口音在哪里出现了偏差。

---

## 工作原理（声学引擎）

EchoStream Ultra 就像一位严格的声乐导师，采用 4 步处理流程：
1. **自动人声提取 (`librosa.effects.hpss`)：** 提取谐波频率（人声）并剔除打击乐类噪音（环境音/特效音）。
2. **智能裁剪：** 利用 RMS 能量包络图精准裁剪无效静音，确保参照和录音均在精确的 `0.0s` 处对齐起跑。
3. **张量映射：** 利用 PyTorch 将纯净音频转换为 13 维 MFCC 张量，剔除音量大小的干扰，纯粹聚焦于发音口型运动和音高起伏。
4. **语速惩罚：** 计算波形间的欧氏距离（Euclidean distance），如果您读每个音节的节奏慢于母语者，将触发严格的扣分机制。

---

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

