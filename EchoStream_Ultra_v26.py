import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import vlc
import pysrt
import sounddevice as sd
import numpy as np
import librosa
import torch
import torchaudio
import torchaudio.transforms as T
from scipy.io.wavfile import write, read
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip

# YOUTUBE DOWNLOADER
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

import threading
import time
import os
import re
import json

class EchoStreamUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("EchoStream Ultra | YouTube Smart-Caption Edition")
        self.root.geometry("1200x980")
        self.root.configure(bg="#121212")

        # Hardware & Audio
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fs = 22050
        
        # Directories
        self.fav_dir = "favorite"
        self.yt_dir = "YouTube"
        os.makedirs(self.fav_dir, exist_ok=True)
        os.makedirs(self.yt_dir, exist_ok=True) 
        
        self.current_fav_file = None 
        
        # High-performance VLC args for RTX 3090
        vlc_args = [
            '--no-xlib', '--quiet', '--no-video-title-show', 
            '--vout=direct3d11', '--avcodec-hw=dxva2',
            '--file-caching=1000', '--network-caching=1000'
        ]
        self.instance = vlc.Instance(vlc_args)
        self.player = self.instance.media_player_new()
        
        # State Variables
        self.video_path = ""
        self.all_subtitles = []
        self.favorite_subs = []
        self.current_idx = 0
        self.normal_mode_idx = 0  
        self.review_mode = False
        
        self.is_recording = False 
        self.playback_id = 0
        self.preload_id = 0 
        
        # SMART CACHE
        self.current_ref_idx = -1
        self.y_ref_iso_cache = None 
        
        # Timeline State
        self.slider_pressed = False

        self.setup_ui()
        self.setup_hotkeys()
        
        # Start the UI Polling Loop
        self.update_slider_loop()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#121212")
        header.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(header, text="ECHOSTREAM ULTRA", font=("Impact", 24), fg="#00aaff", bg="#121212").pack(side=tk.LEFT)
        self.mode_label = tk.Label(header, text="NORMAL MODE", font=("Segoe UI", 10, "bold"), fg="#888888", bg="#121212")
        self.mode_label.pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"RTX 3090: {self.device.type.upper()}", font=("Segoe UI", 10, "bold"), fg="#39FF14", bg="#121212").pack(side=tk.RIGHT)

        self.video_frame = tk.Frame(self.root, bg="black", highlightthickness=1, highlightbackground="#444444")
        self.video_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.sub_text = tk.StringVar(value="[Ctrl+O] Load Media | [Y] Download YouTube")
        self.sub_label = tk.Label(self.root, textvariable=self.sub_text, font=("Segoe UI", 20, "bold"), fg="#FFFFFF", bg="#121212", wraplength=1000, pady=20)
        self.sub_label.pack()

        # High Contrast Graph Setup
        self.fig = plt.Figure(figsize=(10, 3), dpi=100, facecolor='#121212')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#000000')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.X, padx=20)

        # UI Container for Slider + Buttons
        controls_container = tk.Frame(self.root, bg="#121212")
        controls_container.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=15)

        # PROGRESS SLIDER SETUP
        self.slider_var = tk.DoubleVar()
        self.progress_slider = ttk.Scale(controls_container, variable=self.slider_var, from_=0, to=100, orient=tk.HORIZONTAL)
        self.progress_slider.pack(fill=tk.X, pady=(0, 15))
        
        # Bind Mouse Events for Slider
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Buttons Footer
        footer = tk.Frame(controls_container, bg="#121212")
        footer.pack(fill=tk.X)
        
        self.score_text = tk.StringVar(value="MIMIC SCORE: --%")
        self.score_label = tk.Label(footer, textvariable=self.score_text, font=("Segoe UI", 26, "bold"), fg="#00FFCC", bg="#121212")
        self.score_label.pack(side=tk.LEFT)

        self.btn_frame = tk.Frame(footer, bg="#121212")
        self.btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(self.btn_frame, text="YOUTUBE (Y)", command=self.download_youtube, bg="#FF0000", fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.rec_btn = tk.Button(self.btn_frame, text="RECORD (R)", command=self.record_and_score, bg="#1a73e8", fg="white", font=("Segoe UI", 10, "bold"), padx=15)
        self.rec_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_speak_btn = tk.Button(self.btn_frame, text="STOP SPEAK (S)", command=self.stop_recording_early, bg="#FF3B30", fg="white", font=("Segoe UI", 10, "bold"), padx=15)
        
        tk.Button(self.btn_frame, text="LISTEN (P)", command=self.play_segment, bg="#333", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="REPLAY ME (H)", command=self.playback_user, bg="#333", fg="#00FFCC", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="PLAY BOTH (B)", command=self.play_both, bg="#333", fg="#FF9900", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="SAVE (F)", command=self.save_favorite, bg="#333", fg="gold", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="MODE (M)", command=self.toggle_review_mode, bg="#444", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="DEL", command=self.delete_current_favorite, bg="#442222", fg="#ff6666", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

    def setup_hotkeys(self):
        self.root.bind("<Control-o>", lambda e: self.load_files())
        self.root.bind("<space>", lambda e: self.play_segment())
        self.root.bind("<Right>", lambda e: self.move_sub(1))
        self.root.bind("<Left>", lambda e: self.move_sub(-1))
        self.root.bind("<r>", lambda e: self.record_and_score())
        self.root.bind("<s>", lambda e: self.stop_recording_early())
        self.root.bind("<p>", lambda e: self.play_segment())
        self.root.bind("<h>", lambda e: self.playback_user())
        self.root.bind("<b>", lambda e: self.play_both())
        self.root.bind("<y>", lambda e: self.download_youtube())
        self.root.bind("<f>", lambda e: self.save_favorite())
        self.root.bind("<m>", lambda e: self.toggle_review_mode())
        self.root.bind("<Delete>", lambda e: self.delete_current_favorite())
        self.root.bind("<Button-3>", lambda e: self.move_sub(1))

    def get_mic_device(self):
        try:
            default_device = sd.default.device[0]
            device_info = sd.query_devices(default_device)
            if any(mix_word in device_info['name'].lower() for mix_word in ['mix', 'what u hear', '立体声混音', 'cable']):
                for i, dev in enumerate(sd.query_devices()):
                    if dev['max_input_channels'] > 0 and any(mic_word in dev['name'].lower() for mic_word in ['mic', '麦克风']):
                        return i
            return default_device
        except:
            return None

    def update_slider_loop(self):
        if not self.slider_pressed and self.player.get_length() > 0:
            pos = self.player.get_position()
            if pos >= 0:
                self.slider_var.set(pos * 100)
        self.root.after(300, self.update_slider_loop)

    def on_slider_press(self, event):
        self.slider_pressed = True

    def on_slider_release(self, event):
        self.slider_pressed = False
        self.playback_id += 1 
        
        if self.player.get_length() > 0:
            percentage = self.slider_var.get() / 100.0
            new_time_ms = int(percentage * self.player.get_length())
            self.player.set_time(new_time_ms)
            self.sync_subtitle_to_time(new_time_ms)
            self.player.play()

    def sync_subtitle_to_time(self, current_time_ms):
        if not self.current_subs_list: return
        for i, sub in enumerate(self.current_subs_list):
            if sub['start'].ordinal <= current_time_ms <= sub['end'].ordinal:
                self.current_idx = i
                self.update_view()
                return
            elif sub['start'].ordinal > current_time_ms:
                self.current_idx = max(0, i - 1)
                self.update_view()
                return
        self.current_idx = len(self.current_subs_list) - 1
        self.update_view()

    @property
    def current_subs_list(self):
        return self.favorite_subs if self.review_mode else self.all_subtitles

    # --- CORE REFACTOR: Universal Load Media Function ---
    def _load_media(self, v_path, s_path):
        self.video_path = v_path
        raw_subs = pysrt.open(s_path)
        self.all_subtitles = self.reconstruct_sentences(raw_subs)
        self.player.set_media(self.instance.media_new(v_path))
        self.player.set_hwnd(self.video_frame.winfo_id())
        
        video_filename = os.path.basename(self.video_path)
        self.current_fav_file = os.path.join(self.fav_dir, f"{video_filename}.fav.json")
        
        self.review_mode = False
        self.mode_label.config(text="NORMAL MODE", fg="#888888")
        
        self.current_idx = 0
        self.normal_mode_idx = 0
        self.root.update()
        self.update_view()

    def load_files(self):
        v = filedialog.askopenfilename(title="Select Video")
        s = filedialog.askopenfilename(title="Select SRT")
        if v and s:
            self._load_media(v, s)

    # --- YOUTUBE INTEGRATION LOGIC ---
    def download_youtube(self):
        if not YT_DLP_AVAILABLE:
            messagebox.showerror("Dependency Missing", "Please run 'pip install yt-dlp' in your terminal first.")
            return

        url = simpledialog.askstring("Download YouTube", "Paste YouTube Video URL:")
        if not url: return

        self.score_label.config(fg="#FFA500")
        self.score_text.set("⏳ DOWNLOADING YOUTUBE...")
        self.sub_text.set("Please wait. Fetching video and subtitles...")
        self.root.update()

        threading.Thread(target=self._run_youtube_download, args=(url,), daemon=True).start()

    def _convert_vtt_to_srt(self, vtt_path):
        """Converts YouTube's rolling WebVTT format into clean, deduplicated SRT."""
        srt_path = vtt_path.rsplit('.', 1)[0] + ".srt"
        try:
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blocks = re.split(r'\n\n+', content)
            unique_lines = []
            
            for block in blocks:
                if "-->" not in block: continue
                
                lines = block.strip().split('\n')
                ts_line = [l for l in lines if "-->" in l][0]
                
                # Extract start and end times, removing positioning data
                start_time, end_time = ts_line.split("-->")
                start_time = start_time.strip().split(' ')[0].replace('.', ',')
                end_time = end_time.strip().split(' ')[0].replace('.', ',')
                
                text_lines = [l for l in lines if "-->" not in l and not re.match(r'^\d+$', l.strip())]
                
                for line in text_lines:
                    # Strip WebVTT timestamp tags e.g., <00:00:00.240> and styling tags e.g., <c>
                    clean_line = re.sub(r'<[^>]+>', '', line).strip()
                    # Clean zero-width spaces YouTube sometimes inserts
                    clean_line = clean_line.replace('\u200b', '').replace('\u200c', '').strip()
                    
                    if not clean_line: continue
                    
                    # DEDUPLICATION LOGIC:
                    # If this text is exactly the same as the last line added, 
                    # it's a scrolling continuation. Just extend the end time of the last line.
                    if unique_lines and unique_lines[-1]['text'] == clean_line:
                        unique_lines[-1]['end'] = end_time
                    else:
                        unique_lines.append({
                            'start': start_time,
                            'end': end_time,
                            'text': clean_line
                        })
                        
            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(unique_lines):
                    f.write(f"{i+1}\n")
                    f.write(f"{entry['start']} --> {entry['end']}\n")
                    f.write(f"{entry['text']}\n\n")
                    
            return srt_path
        except Exception as e:
            print(f"VTT Parse Error: {e}")
            return vtt_path

    def _run_youtube_download(self, url):
        try:
            import yt_dlp
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(self.yt_dir, '%(title)s.%(ext)s'),
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB'],
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                v_path = ydl.prepare_filename(info)
                
            base_name = os.path.splitext(v_path)[0]
            
            s_path = None
            for ext in ['.en.srt', '.en-US.srt', '.en-GB.srt', '.en.vtt', '.en-US.vtt', '.en-GB.vtt']:
                temp_path = f"{base_name}{ext}"
                if os.path.exists(temp_path):
                    s_path = temp_path
                    break
                    
            if s_path and s_path.endswith('.vtt'):
                s_path = self._convert_vtt_to_srt(s_path)

            if os.path.exists(v_path) and s_path and os.path.exists(s_path):
                self.root.after(0, lambda: self._load_media(v_path, s_path))
                self.root.after(0, lambda: [self.score_label.config(fg="#888888"), self.score_text.set("YOUTUBE READY")])
            else:
                self.root.after(0, lambda: [self.score_label.config(fg="#FF3B30"), self.score_text.set("ERR: NO EN SUBTITLE FOUND")])
                self.root.after(0, lambda: self.sub_text.set("Video downloaded, but could not find English subtitles."))
                
        except Exception as e:
            self.root.after(0, lambda: [self.score_label.config(fg="#FF3B30"), self.score_text.set("ERR: DOWNLOAD FAILED")])
            print(f"YT-DLP Error: {e}")

    def reconstruct_sentences(self, subs):
        reconstructed = []
        temp_text, start_time = "", None
        for sub in subs:
            if start_time is None: start_time = sub.start
            clean = re.sub(r'<[^>]*>', '', sub.text).replace('\n', ' ').strip()
            temp_text += " " + clean
            if any(clean.endswith(p) for p in ['.', '!', '?', '"']) or len(temp_text) > 100:
                reconstructed.append({'text': temp_text.strip(), 'start': start_time, 'end': sub.end})
                temp_text, start_time = "" , None
        return reconstructed

    def update_view(self):
        lst = self.current_subs_list
        if lst:
            self.sub_text.set(lst[self.current_idx]['text'])
            self.trigger_preload()

    def trigger_preload(self):
        if not self.current_subs_list: return
        self.preload_id += 1
        current_id = self.preload_id
        
        if self.current_idx == self.current_ref_idx and self.y_ref_iso_cache is not None:
            self._draw_single_wave(self.y_ref_iso_cache, current_id)
        else:
            self.ax.clear()
            self.canvas.draw()
            self.score_label.config(fg="#FFA500")
            self.score_text.set("⏳ LOADING WAVEFORM...")
            threading.Thread(target=self._run_preload, args=(current_id,), daemon=True).start()

    def _run_preload(self, preload_id):
        sub = self.current_subs_list[self.current_idx]
        t_start, t_end = sub['start'].ordinal / 1000.0, sub['end'].ordinal / 1000.0
        
        try:
            temp_wav = f"tv_ref_preload_{preload_id}.wav"
            with VideoFileClip(self.video_path) as video:
                method = getattr(video, "subclipped", getattr(video, "subclip", None))
                clip = method(t_start, t_end)
                clip.audio.write_audiofile(temp_wav, fps=self.fs, logger=None)
            
            if self.preload_id != preload_id: 
                if os.path.exists(temp_wav): os.remove(temp_wav)
                return
            
            sr_ref, y_ref_raw = read(temp_wav)
            if os.path.exists(temp_wav): os.remove(temp_wav)
            
            if y_ref_raw.dtype != np.float32:
                y_ref_raw = y_ref_raw.astype(np.float32) / np.iinfo(y_ref_raw.dtype).max
            if len(y_ref_raw.shape) > 1: 
                y_ref_raw = y_ref_raw.mean(axis=1)
            
            y_ref_iso = self.auto_isolate_speech(y_ref_raw, self.fs)
            
            if self.preload_id != preload_id: return
            
            self.y_ref_iso_cache = y_ref_iso
            self.current_ref_idx = self.current_idx
            
            self.root.after(0, lambda: self._draw_single_wave(y_ref_iso, preload_id))
        except Exception as e:
            print(f"Preload error: {e}")

    def _draw_single_wave(self, y_ref, preload_id=None):
        if preload_id is not None and self.preload_id != preload_id: return
        
        if len(y_ref) < 500:
            self.score_label.config(fg="#FF3B30")
            self.score_text.set("ERR: AUDIO TOO SHORT")
            return
            
        hop = 256
        env_ref = librosa.feature.rms(y=y_ref, hop_length=hop)[0]
        env_ref = env_ref / (np.max(env_ref) + 1e-8)
        time_ref = librosa.frames_to_time(np.arange(len(env_ref)), sr=self.fs, hop_length=hop)
        dur_ref = len(y_ref) / self.fs
        
        self.ax.clear()
        self.ax.fill_between(time_ref, -env_ref, env_ref, color='#00aaff', alpha=0.5, label='Actor Stress Blueprint')
        self.ax.set_title(f"REFERENCE WAVEFORM (CYAN=ACTOR: {dur_ref:.1f}s)", color='#FFFFFF', fontsize=10)
        self.ax.axis('off')
        self.ax.legend(loc='upper right', facecolor='#121212', edgecolor='#444444', labelcolor='white')
        self.canvas.draw()
        
        self.score_label.config(fg="#888888")
        self.score_text.set("READY TO RECORD")

    def play_segment(self):
        if not self.current_subs_list: return
        
        self.playback_id += 1
        current_id = self.playback_id
        
        sub = self.current_subs_list[self.current_idx]
        self.player.set_time(sub['start'].ordinal)
        self.player.play()
        
        threading.Thread(target=self._strict_pause_monitor, args=(sub['end'].ordinal, current_id), daemon=True).start()

    def _strict_pause_monitor(self, end_ms, monitor_id):
        while self.playback_id == monitor_id:
            current_time = self.player.get_time()
            if current_time >= end_ms or current_time == -1:
                self.player.set_pause(1)
                break
            time.sleep(0.001)

    def record_and_score(self):
        if not self.current_subs_list: return
        
        self.player.set_pause(1)
        self.playback_id += 1 
        
        self.is_recording = True
        sub = self.current_subs_list[self.current_idx]
        t_start, t_end = sub['start'].ordinal / 1000.0, sub['end'].ordinal / 1000.0
        
        self.rec_btn.pack_forget()
        self.stop_speak_btn.pack(side=tk.LEFT, padx=5)
        
        self.score_label.config(fg="#FF3B30") 
        self.score_text.set(">>> SPEAK NOW <<<")
        self.root.update()
        
        threading.Thread(target=self._run_recording, args=(t_start, t_end,), daemon=True).start()

    def _run_recording(self, t_start, t_end):
        max_duration = t_end - t_start + 1.5
        mic_id = self.get_mic_device()
        
        rec_data = sd.rec(int(max_duration * self.fs), samplerate=self.fs, channels=1, dtype='float32', device=mic_id)
        start_time = time.time()
        
        while self.is_recording and (time.time() - start_time) < max_duration:
            time.sleep(0.1)
        
        sd.stop()
        actual_len = int((time.time() - start_time) * self.fs)
        
        audio_array = rec_data[:actual_len].flatten()
        audio_array = np.nan_to_num(audio_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        write("user_attempt.wav", self.fs, audio_array)
        self.is_recording = False
        self.root.after(0, lambda: self.finish_analysis(t_start, t_end, audio_array))

    def stop_recording_early(self):
        self.is_recording = False

    def finish_analysis(self, t_start, t_end, y_user):
        self.stop_speak_btn.pack_forget()
        self.rec_btn.pack(side=tk.LEFT, padx=5)
        
        self.score_label.config(fg="#888888")
        self.score_text.set("PROCESSING...")
        self.root.update()
        
        threading.Thread(target=self.calculate_gpu_score, args=(t_start, t_end, y_user), daemon=True).start()

    def auto_isolate_speech(self, y, sr, buffer_sec=0.15):
        y_harm, _ = librosa.effects.hpss(y)
        y_emph = librosa.effects.preemphasis(y_harm)
        rms = librosa.feature.rms(y=y_emph, frame_length=2048, hop_length=512)[0]
        threshold = np.max(rms) * 0.12
        active_frames = np.where(rms > threshold)[0]
        
        if len(active_frames) == 0:
            return y 
            
        start_sample = librosa.frames_to_samples(active_frames[0], hop_length=512)
        end_sample = librosa.frames_to_samples(active_frames[-1], hop_length=512)
        
        buffer_samples = int(buffer_sec * sr)
        start_sample = max(0, start_sample - buffer_samples)
        end_sample = min(len(y), end_sample + buffer_samples)
        
        return y[start_sample:end_sample]

    def calculate_gpu_score(self, t_start, t_end, y_user):
        try:
            if self.current_idx != self.current_ref_idx or self.y_ref_iso_cache is None:
                self.root.after(0, lambda: [self.score_label.config(fg="#FFA500"), self.score_text.set("⏳ EXTRACTING MEDIA...")])
                
                with VideoFileClip(self.video_path) as video:
                    method = getattr(video, "subclipped", getattr(video, "subclip", None))
                    clip = method(t_start, t_end)
                    clip.audio.write_audiofile("tv_ref_fallback.wav", fps=self.fs, logger=None)

                sr_ref, y_ref_raw = read("tv_ref_fallback.wav")
                if os.path.exists("tv_ref_fallback.wav"): os.remove("tv_ref_fallback.wav")
                
                if y_ref_raw.dtype != np.float32:
                    y_ref_raw = y_ref_raw.astype(np.float32) / np.iinfo(y_ref_raw.dtype).max
                if len(y_ref_raw.shape) > 1: 
                    y_ref_raw = y_ref_raw.mean(axis=1)
                
                self.y_ref_iso_cache = self.auto_isolate_speech(y_ref_raw, self.fs)
                self.current_ref_idx = self.current_idx

            y_ref = self.y_ref_iso_cache.copy()
            y_user = self.auto_isolate_speech(y_user, self.fs)

            if len(y_user) < 500 or len(y_ref) < 500:
                self.root.after(0, lambda: [self.score_label.config(fg="#FF3B30"), self.score_text.set("ERR: AUDIO TOO SHORT")])
                return

            w_ref = torch.from_numpy(y_ref).float().unsqueeze(0).to(self.device)
            w_user = torch.from_numpy(y_user).float().unsqueeze(0).to(self.device)

            xform = T.MFCC(sample_rate=self.fs, n_mfcc=13, melkwargs={"n_fft":400, "hop_length":160}).to(self.device)
            mfcc_ref = xform(w_ref).squeeze(0).cpu().numpy()
            mfcc_user = xform(w_user).squeeze(0).cpu().numpy()

            mfcc_ref = (mfcc_ref - np.mean(mfcc_ref)) / (np.std(mfcc_ref) + 1e-8)
            mfcc_user = (mfcc_user - np.mean(mfcc_user)) / (np.std(mfcc_user) + 1e-8)

            mfcc_ref = np.nan_to_num(mfcc_ref, nan=0.0, posinf=0.0, neginf=0.0)
            mfcc_user = np.nan_to_num(mfcc_user, nan=0.0, posinf=0.0, neginf=0.0)

            D, wp = librosa.sequence.dtw(X=mfcc_ref, Y=mfcc_user, metric='euclidean')
            
            normalized_cost = D[-1, -1] / len(wp)
            base_score = 110 - (normalized_cost * 20) 
            
            dur_ref = len(y_ref) / self.fs
            dur_user = len(y_user) / self.fs
            time_diff_seconds = abs(dur_ref - dur_user)
            
            pacing_penalty = time_diff_seconds * 10
            score = max(0, min(100, int(base_score - pacing_penalty))) 
            
            hop = 256
            env_ref = librosa.feature.rms(y=y_ref, hop_length=hop)[0]
            env_user = librosa.feature.rms(y=y_user, hop_length=hop)[0]

            env_ref = env_ref / (np.max(env_ref) + 1e-8)
            env_user = env_user / (np.max(env_user) + 1e-8)

            time_ref = librosa.frames_to_time(np.arange(len(env_ref)), sr=self.fs, hop_length=hop)
            time_user = librosa.frames_to_time(np.arange(len(env_user)), sr=self.fs, hop_length=hop)

            def update_gui():
                self.score_label.config(fg="#00FFCC")
                self.score_text.set(f"MIMIC SCORE: {score}%")
                self.ax.clear()
                
                self.ax.fill_between(time_ref, -env_ref, env_ref, color='#00aaff', alpha=0.5, label='Actor Stress')
                self.ax.fill_between(time_user, -env_user, env_user, color='#39FF14', alpha=0.6, label='Your Stress')
                
                self.ax.set_title(f"STRESS WAVEFORM (CYAN=ACTOR: {dur_ref:.1f}s | NEON=YOU: {dur_user:.1f}s)", color='#FFFFFF', fontsize=10)
                self.ax.axis('off')
                self.ax.legend(loc='upper right', facecolor='#121212', edgecolor='#444444', labelcolor='white')
                
                self.canvas.draw()
                
            self.root.after(0, update_gui)
            
        except Exception as e:
            err_msg = str(e).upper()[:30]
            self.root.after(0, lambda: [self.score_label.config(fg="#FF3B30"), self.score_text.set(f"ERR: {err_msg}...")])
            print(f"CRITICAL GPU ERROR: {e}")

    def play_both(self):
        if not self.current_subs_list: return
        if not os.path.exists("user_attempt.wav"):
            messagebox.showinfo("No Record", "You need to record yourself speaking first!")
            return

        self.playback_user()

        def delayed_video():
            time.sleep(0.09) 
            self.play_segment()
            
        threading.Thread(target=delayed_video, daemon=True).start()

    def move_sub(self, delta):
        lst = self.current_subs_list
        if lst:
            self.current_idx = max(0, min(len(lst)-1, self.current_idx + delta))
            self.update_view()
            self.play_segment()

    def save_favorite(self):
        if not self.all_subtitles or not self.current_fav_file or self.review_mode: return
        sub = self.all_subtitles[self.current_idx]
        entry = {
            "timestamp": f"{time.time()}", 
            "video": os.path.basename(self.video_path), 
            "text": sub['text'], 
            "start_ms": sub['start'].ordinal, 
            "end_ms": sub['end'].ordinal
        }
        data = json.load(open(self.current_fav_file)) if os.path.exists(self.current_fav_file) else []
        data.append(entry)
        json.dump(data, open(self.current_fav_file, "w"), indent=4)
        messagebox.showinfo("Saved", "Added to favorites for this video!")

    def toggle_review_mode(self):
        if not self.current_fav_file or not os.path.exists(self.current_fav_file) or os.stat(self.current_fav_file).st_size == 0: 
            messagebox.showinfo("Empty", "No favorites saved for this video yet!")
            return
            
        if not self.review_mode:
            self.normal_mode_idx = self.current_idx  
            self.review_mode = True
            data = json.load(open(self.current_fav_file))
            self.favorite_subs = [{'text': i['text'], 'start': pysrt.SubRipTime(milliseconds=i['start_ms']), 'end': pysrt.SubRipTime(milliseconds=i['end_ms']), 'id': i['timestamp']} for i in data]
            self.current_idx = 0  
        else:
            self.review_mode = False
            self.current_idx = self.normal_mode_idx  

        self.mode_label.config(text="REVIEW MODE ACTIVE" if self.review_mode else "NORMAL MODE", fg="#00aaff" if self.review_mode else "#888888")

        if self.current_subs_list:
            self.player.set_time(self.current_subs_list[self.current_idx]['start'].ordinal)

        self.update_view()

    def delete_current_favorite(self):
        if not self.review_mode or not self.current_fav_file: return
        
        data = [i for i in json.load(open(self.current_fav_file)) if i['timestamp'] != self.favorite_subs[self.current_idx]['id']]
        json.dump(data, open(self.current_fav_file, "w"), indent=4)
        
        if len(data) == 0:
            self.review_mode = False
            self.current_idx = self.normal_mode_idx
            self.mode_label.config(text="NORMAL MODE", fg="#888888")
            if self.current_subs_list:
                self.player.set_time(self.current_subs_list[self.current_idx]['start'].ordinal)
            self.update_view()
            messagebox.showinfo("Empty", "All favorites deleted. Returning to Normal Mode.")
        else:
            self.favorite_subs = [{'text': i['text'], 'start': pysrt.SubRipTime(milliseconds=i['start_ms']), 'end': pysrt.SubRipTime(milliseconds=i['end_ms']), 'id': i['timestamp']} for i in data]
            self.current_idx = min(self.current_idx, len(self.favorite_subs) - 1)
            self.player.set_time(self.current_subs_list[self.current_idx]['start'].ordinal)
            self.update_view()

    def playback_user(self):
        if os.path.exists("user_attempt.wav"):
            d, f = librosa.load("user_attempt.wav", sr=self.fs)
            sd.play(d, f)

if __name__ == "__main__":
    app = EchoStreamUltra(tk.Tk())
    app.root.mainloop()