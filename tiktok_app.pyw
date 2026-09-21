"""
SpicyConverter - 120fps Quality Tool
TikTok (clean) & YouTube (enhanced) modes
by Djani
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess, os, sys, threading, re, queue
from pathlib import Path

# FFMPEG
def get_ffmpeg():
    if getattr(sys, 'frozen', False):
        d = Path(sys._MEIPASS) / "ffmpeg_bin" / "ffmpeg.exe"
        if d.exists():
            return str(d.parent)
        meipass = Path(sys._MEIPASS)
        for item in meipass.iterdir():
            if item.is_dir() and "ffmpeg" in item.name.lower():
                if (item / "ffmpeg.exe").exists():
                    return str(item)
    local = Path(__file__).parent / "ffmpeg_bin" / "ffmpeg.exe"
    if local.exists():
        return str(local.parent)
    return None

FFMPEG = get_ffmpeg()
def ff(base="ffmpeg"):
    return os.path.join(FFMPEG, base) if FFMPEG else base

# THEME
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

P = {
    "bg":"#0a0a0a","card":"#1a1218","card_border":"#3a1525",
    "fire":"#f97316","fire_dark":"#c2410c",
    "text":"#f0e8ec","text_dim":"#7a6070","text_muted":"#4a3545",
    "green":"#166534","green_dark":"#14532d","input_bg":"#120e14",
}

# Font helper - use Bahnschrift for stylish look, Cascadia for log
def FONT_NAME(size=12, bold=False):
    weight = "bold" if bold else "normal"
    return ("Bahnschrift", size, weight)

def FONT_LOG(size=9):
    return ("Cascadia Code", size)

class SpicyConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SpicyConverter")
        self.geometry("600x950")
        self.minsize(600, 950)
        self.maxsize(600, 950)
        self.configure(fg_color=P["bg"])
        self.resizable(False, False)

        # Window icon
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "chili.ico")
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chili.ico")
        if os.path.exists(icon_path):
            try:
                import tkinter as tk
                icon_img = tk.PhotoImage(file=icon_path)
                self.tk.call('wm', 'iconphoto', self._w, True, icon_img)
            except:
                try:
                    self.iconbitmap(default=icon_path)
                except:
                    pass

        self.selected_file = None
        self.processing = False
        self.selected_mode = "tiktok"
        self.ffmpeg_proc = None
        self.cancel_flag = False

        # Queue system
        self.video_queue = queue.Queue()
        self.queue_list = []  # For UI display: [(path, status), ...]
        self.current_index = 0

        self._dark_titlebar()
        self._build()

    def _dark_titlebar(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except: pass

    def _build(self):
        self.grad = ctk.CTkCanvas(self, highlightthickness=0, bd=0, bg=P["bg"])
        self.grad.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_grad()

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
            scrollbar_button_color=P["card_border"], scrollbar_button_hover_color=P["green"])
        self.scroll.pack(fill="both", expand=True)

        self.content = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=28, pady=(20, 16))

        self._header()
        self._dropzone()
        self._file_info()
        self._mode_selector()
        self._queue_area()
        self._button_row()
        self._progress()
        self._log_area()
        self._footer()

    def _draw_grad(self):
        self.grad.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2: return
        for i in range(50):
            r = i / 50
            c = f"#{int(10+10*r):02x}{int(8+4*r):02x}{int(10+6*r):02x}"
            y = int(h * i / 50)
            self.grad.create_line(0, y, w, y, fill=c, width=1)

    def _header(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="x", pady=(0, 16))
        left = ctk.CTkFrame(f, fg_color="transparent")
        left.pack(side="left")
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(anchor="w")
        ctk.CTkLabel(row, text="\U0001f336", font=FONT_NAME(26)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(row, text="SpicyConverter", font=FONT_NAME(24, True), text_color=P["fire"]).pack(side="left")
        ctk.CTkLabel(f, text=" v1.0 ", font=FONT_NAME(9, True), text_color="white", fg_color=P["green"], corner_radius=8).pack(side="right", pady=(6, 0))

    def _dropzone(self):
        self.drop_card = ctk.CTkFrame(self.content, fg_color=P["card"], border_color=P["card_border"], border_width=1, corner_radius=16)
        self.drop_card.pack(fill="x", pady=(0, 14))
        self.drop_inner = ctk.CTkFrame(self.drop_card, fg_color=P["input_bg"], border_color=P["card_border"], border_width=2, corner_radius=12, cursor="hand2")
        self.drop_inner.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(self.drop_inner, text="\U0001f3ac", font=FONT_NAME(28), text_color=P["green"]).pack(pady=(16, 4))
        self.drop_title = ctk.CTkLabel(self.drop_inner, text="Browse Video", font=FONT_NAME(14, True), text_color=P["text"])
        self.drop_title.pack(pady=(0, 2))
        self.drop_sub = ctk.CTkLabel(self.drop_inner, text="MP4, MOV, AVI, MKV, WEBM", font=FONT_NAME(10), text_color=P["text_dim"])
        self.drop_sub.pack(pady=(0, 14))
        # Make entire area clickable
        def _click_all(e):
            self._browse()
        for w in [self.drop_inner, self.drop_title, self.drop_sub]:
            w.bind("<Button-1>", _click_all)
            w.configure(cursor="hand2")
        # Also bind children of drop_inner
        self.drop_inner.bind("<Enter>", lambda e: self.drop_inner.configure(border_color=P["green"]) if not self.processing else None)
        self.drop_inner.bind("<Leave>", lambda e: self.drop_inner.configure(border_color=P["card_border"]))

    def _file_info(self):
        self.file_card = ctk.CTkFrame(self.content, fg_color=P["card"], border_color=P["card_border"], border_width=1, corner_radius=14)
        self.file_card.pack(fill="x", pady=(0, 14))
        self.file_card.pack_forget()
        inner = ctk.CTkFrame(self.file_card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(inner, text="\U0001f3ac", font=FONT_NAME(18)).pack(side="left", padx=(0, 8))
        tf = ctk.CTkFrame(inner, fg_color="transparent")
        tf.pack(side="left", fill="x", expand=True)
        self.file_name = ctk.CTkLabel(tf, text="", font=FONT_NAME(12, True), text_color=P["text"], anchor="w")
        self.file_name.pack(anchor="w")
        self.file_size = ctk.CTkLabel(tf, text="", font=FONT_NAME(10), text_color=P["text_dim"], anchor="w")
        self.file_size.pack(anchor="w")

    def _mode_selector(self):
        """TikTok / YouTube mode selector"""
        card = ctk.CTkFrame(self.content, fg_color=P["card"], border_color=P["card_border"], border_width=1, corner_radius=14)
        card.pack(fill="x", pady=(0, 14))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(inner, text="\u2699\ufe0f", font=FONT_NAME(16)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(inner, text="Mode", font=FONT_NAME(13, True), text_color=P["text"]).pack(side="left")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=14, pady=(0, 10))

        self.btn_tiktok = ctk.CTkButton(btn_frame, text="\U0001f336  TikTok", font=FONT_NAME(12, True),
            fg_color=P["green"], hover_color=P["green_dark"], corner_radius=8, height=36,
            command=lambda: self._set_mode("tiktok"))
        self.btn_tiktok.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_youtube = ctk.CTkButton(btn_frame, text="\u25b6  YouTube", font=FONT_NAME(12, True),
            fg_color=P["text_muted"], hover_color="#5a4555", corner_radius=8, height=36,
            command=lambda: self._set_mode("youtube"))
        self.btn_youtube.pack(side="left", expand=True, fill="x", padx=(4, 0))

        # Mode description
        self.mode_desc = ctk.CTkLabel(card, text="Clean pipeline - no effects, pure 120fps interpolation",
            font=FONT_NAME(10), text_color=P["text_dim"], wraplength=500)
        self.mode_desc.pack(padx=14, pady=(0, 10))

    def _set_mode(self, mode):
        self.selected_mode = mode
        if mode == "tiktok":
            self.btn_tiktok.configure(fg_color=P["green"])
            self.btn_youtube.configure(fg_color=P["text_muted"])
            self.mode_desc.configure(text="Clean pipeline - no effects, pure 120fps interpolation")
        else:
            self.btn_youtube.configure(fg_color="#cc0000")
            self.btn_tiktok.configure(fg_color=P["text_muted"])
            self.mode_desc.configure(text="Maximum smoothness + crispy sharpen + cinematic color (optimal for YouTube)")

    def _queue_area(self):
        """Video queue display"""
        card = ctk.CTkFrame(self.content, fg_color=P["card"], border_color=P["card_border"], border_width=1, corner_radius=14)
        card.pack(fill="x", pady=(0, 14))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(header, text="\U0001f4cb", font=FONT_NAME(16)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(header, text="Queue", font=FONT_NAME(13, True), text_color=P["text"]).pack(side="left")

        self.queue_count_label = ctk.CTkLabel(header, text="0 videos", font=FONT_NAME(10), text_color=P["text_dim"])
        self.queue_count_label.pack(side="right")

        # Queue list container
        self.queue_frame = ctk.CTkFrame(card, fg_color=P["input_bg"], corner_radius=10)
        self.queue_frame.pack(fill="x", padx=10, pady=(0, 8))

        # Placeholder
        self.queue_placeholder = ctk.CTkLabel(self.queue_frame, text="No videos in queue - click Browse to add",
            font=FONT_NAME(10), text_color=P["text_muted"])
        self.queue_placeholder.pack(pady=12)

        self.queue_items_frame = ctk.CTkFrame(self.queue_frame, fg_color="transparent")
        self.queue_items_frame.pack(fill="x", padx=6, pady=(0, 4))

        # Add more button
        add_frame = ctk.CTkFrame(card, fg_color="transparent")
        add_frame.pack(fill="x", padx=14, pady=(0, 10))
        self.add_btn = ctk.CTkButton(add_frame, text="+ Add Video", font=FONT_NAME(11, True),
            fg_color=P["card_border"], hover_color="#5a2535", corner_radius=8, height=32,
            command=self._browse)
        self.add_btn.pack(side="left")
        self.clear_queue_btn = ctk.CTkButton(add_frame, text="Clear All", font=FONT_NAME(11),
            fg_color="transparent", hover_color="#3a1525", text_color=P["text_muted"],
            corner_radius=8, height=32, border_width=1, border_color=P["card_border"],
            command=self._clear_queue)
        self.clear_queue_btn.pack(side="right")

    def _update_queue_ui(self):
        """Refresh queue display"""
        # Clear old items
        for w in self.queue_items_frame.winfo_children():
            w.destroy()

        if not self.queue_list:
            self.queue_placeholder.pack(pady=12)
            self.queue_count_label.configure(text="0 videos")
            return

        self.queue_placeholder.pack_forget()
        self.queue_count_label.configure(text=f"{len(self.queue_list)} videos")

        for i, (path, status) in enumerate(self.queue_list):
            row = ctk.CTkFrame(self.queue_items_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            # Status icon + text
            if status == "pending":
                icon = "\u23f3"
                color = P["text_dim"]
                status_text = "Pending"
            elif status == "processing":
                icon = "\u26a1"
                color = P["fire"]
                status_text = "Processing..."
            elif status == "done":
                icon = "\u2705"
                color = P["green"]
                status_text = "Done"
            elif status == "error":
                icon = "\u274c"
                color = "#ef4444"
                status_text = "Failed"
            else:
                icon = "\u23f3"
                color = P["text_dim"]
                status_text = "Pending"

            ctk.CTkLabel(row, text=icon, font=FONT_NAME(11), text_color=color, width=24).pack(side="left")
            name = os.path.basename(path)
            if len(name) > 30:
                name = name[:27] + "..."
            ctk.CTkLabel(row, text=name, font=FONT_NAME(10), text_color=P["text"]).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=status_text, font=FONT_NAME(9, True), text_color=color).pack(side="left")

            # Remove button (only for pending)
            if status == "pending":
                rm = ctk.CTkButton(row, text="\u2716", font=FONT_NAME(10), width=24, height=24,
                    fg_color="transparent", hover_color="#3a1525", text_color=P["text_muted"],
                    command=lambda idx=i: self._remove_from_queue(idx))
                rm.pack(side="right")

    def _remove_from_queue(self, index):
        """Remove item from queue by index"""
        if index < len(self.queue_list):
            self.queue_list.pop(index)
            self._update_queue_ui()

    def _clear_queue(self):
        """Clear entire queue"""
        self.queue_list.clear()
        self._update_queue_ui()

    def _button_row(self):
        """Start + Cancel buttons"""
        bf = ctk.CTkFrame(self.content, fg_color="transparent")
        bf.pack(fill="x", pady=(4, 8))

        self.btn = ctk.CTkButton(bf, text="\u25b6  START PROCESSING", font=FONT_NAME(13, True),
            fg_color=P["green"], hover_color=P["green_dark"], corner_radius=10, height=46,
            cursor="hand2", command=self._start)
        self.btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.cancel_btn = ctk.CTkButton(bf, text="\u23f9  CANCEL", font=FONT_NAME(13, True),
            fg_color="#991b1b", hover_color="#7f1d1d", corner_radius=10, height=46, width=120,
            cursor="hand2", command=self._cancel, state="disabled")
        self.cancel_btn.pack(side="right")

    def _progress(self):
        self.prog_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.prog_frame.pack(fill="x", pady=(0, 6))
        self.prog_frame.pack_forget()
        self.prog_bar = ctk.CTkProgressBar(self.prog_frame, fg_color=P["input_bg"], progress_color=P["green"], corner_radius=6, height=8)
        self.prog_bar.pack(fill="x")
        self.prog_bar.set(0)
        self.prog_label = ctk.CTkLabel(self.prog_frame, text="0%", font=FONT_NAME(10), text_color=P["text_dim"])
        self.prog_label.pack(fill="x", pady=(6, 0))
        self.prog_msg = ctk.CTkLabel(self.prog_frame, text="Enhancing your video. This may take a moment...", font=FONT_NAME(10), text_color=P["text_muted"])
        self.prog_msg.pack(fill="x", pady=(2, 0))

    def _log_area(self):
        self.log_card = ctk.CTkFrame(self.content, fg_color=P["card"], border_color=P["card_border"], border_width=1, corner_radius=12)
        self.log_card.pack(fill="both", expand=True, pady=(0, 10))
        self.log_card.pack_forget()
        self.log_text = ctk.CTkTextbox(self.log_card, font=FONT_LOG(9), fg_color=P["input_bg"], text_color=P["text_dim"], corner_radius=10, border_width=0, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=3, pady=3)
        self.log_text.configure(state="disabled")

    def _log(self, msg):
        self.log_card.pack(fill="both", expand=True, pady=(0, 10), after=self.btn.master)
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _footer(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="x")
        self.status = ctk.CTkLabel(f, text="Ready", font=FONT_NAME(10), text_color=P["green"], anchor="w")
        self.status.pack(side="left")
        ctk.CTkLabel(f, text="by Djani", font=FONT_NAME(9), text_color=P["text_muted"]).pack(side="right")

    def _browse(self):
        p = filedialog.askopenfilenames(title="Select Video(s)", filetypes=[("Video","*.mp4 *.mov *.avi *.mkv *.webm"),("All","*.*")])
        if p:
            for path in p:
                self.queue_list.append((path, "pending"))
            self._update_queue_ui()
            # Set first as selected for display
            if not self.selected_file and p:
                self._set_file_display(p[0])

    def _set_file_display(self, path):
        """Just update the dropzone display, not the queue"""
        self.selected_file = path
        name = os.path.basename(path)
        mb = os.path.getsize(path) / (1024*1024)
        self.file_name.configure(text=name)
        self.file_size.configure(text=f"{mb:.1f} MB  |  Ready")
        self.file_card.pack(fill="x", pady=(0, 14))
        self.drop_title.configure(text=name, text_color=P["text"])
        self.drop_sub.configure(text=f"{mb:.1f} MB  \u2022  Ready", text_color=P["green"])
        self.drop_inner.configure(border_color=P["green"])
        self.status.configure(text=f"{len(self.queue_list)} video(s) in queue", text_color=P["green"])

    # ============================================================
    #  PROCESSING
    # ============================================================
    def _start(self):
        if self.processing: return
        if not self.queue_list:
            messagebox.showinfo("No Video", "Add videos to the queue first."); return
        if not self._check_ffmpeg():
            messagebox.showerror("ffmpeg not found", "Install: winget install ffmpeg"); return

        self.processing = True
        self.cancel_flag = False
        self.btn.configure(text="\u23f3  PROCESSING...", fg_color=P["text_muted"], state="disabled")
        self.cancel_btn.configure(state="normal")
        self.prog_frame.pack(fill="x", pady=(0, 6), after=self.btn.master)
        self.prog_bar.set(0)
        self.prog_label.configure(text="0%  |  Starting...")
        self.status.configure(text="Processing queue...", text_color=P["green"])
        self._clear_log()
        self.current_index = 0
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _cancel(self):
        """Cancel current processing"""
        self.cancel_flag = True
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.terminate()
            except:
                pass
        self.after(0, self._log, "\n[CANCELLED] Processing stopped by user")
        self.after(0, self._cancel_done)

    def _cancel_done(self):
        self.processing = False
        self.cancel_flag = False
        self.btn.configure(text="\u25b6  START PROCESSING", fg_color=P["green"], state="normal")
        self.cancel_btn.configure(state="disabled")
        self.prog_frame.pack_forget()
        self.status.configure(text="Cancelled", text_color="#ef4444")

    def _process_queue(self):
        """Process all videos in queue sequentially"""
        total = len(self.queue_list)
        success_count = 0
        fail_count = 0

        for i, (path, _) in enumerate(self.queue_list):
            if self.cancel_flag:
                break

            self.current_index = i
            self.queue_list[i] = (path, "processing")
            self.after(0, self._update_queue_ui)

            name = os.path.basename(path)
            self.after(0, self._log, f"\n{'='*40}")
            self.after(0, self._log, f"[{i+1}/{total}] {name}")
            self.after(0, self._log, f"{'='*40}\n")

            try:
                self._process_single(path, i, total)
                self.queue_list[i] = (path, "done")
                success_count += 1
            except Exception as e:
                self.queue_list[i] = (path, "error")
                fail_count += 1
                self.after(0, self._log, f"[ERROR] {str(e)}")

            self.after(0, self._update_queue_ui)

        # Done
        self.after(0, self._queue_done, success_count, fail_count, total)

    def _queue_done(self, success, fail, total):
        self.processing = False
        self.cancel_flag = False
        self.btn.configure(text="\u25b6  START PROCESSING", fg_color=P["green"], state="normal")
        self.cancel_btn.configure(state="disabled")
        self.prog_frame.pack_forget()
        self._log(f"\n{'='*40}")
        self._log(f"QUEUE COMPLETE: {success}/{total} succeeded")
        if fail > 0:
            self._log(f"{fail} failed")
        self._log(f"{'='*40}")
        self.status.configure(text=f"Done: {success}/{total}", text_color=P["green"])

    def _process_single(self, path, index, total):
        """Process a single video"""
        p = Path(path)
        out_dir = p.parent
        dur = self._get_duration(path)

        out = out_dir / f"{p.stem}_120fps.mp4"
        mode_name = "TikTok" if self.selected_mode == "tiktok" else "YouTube"
        self.after(0, self._log, f"[..] Mode: {mode_name} | 120fps Ultra Smooth\n")

        if self.selected_mode == "youtube":
            cmd = self._cmd_120_youtube(path, str(out))
        else:
            cmd = self._cmd_120_tiktok(path, str(out))

        # Calculate offset for overall progress
        offset = (index / total) * 100
        self._run_ffmpeg(cmd, dur, offset, total_passes=total)

        self.after(0, self._log, f"[OK] Output: {out.name}")

        if not os.path.exists(str(out)):
            raise Exception("Output file not created")

        size_mb = os.path.getsize(str(out)) / (1024*1024)
        self.after(0, self._log, f"[OK] Size: {size_mb:.1f} MB")

    def _run_ffmpeg(self, cmd, dur, offset_pct, pass_num=0, total_passes=1):
        """Run ffmpeg with real-time progress. ffmpeg writes progress with \\r, not \\n."""
        pass

        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        self.ffmpeg_proc = subprocess.Popen(
            cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
            creationflags=flags
        )

        pass_start = offset_pct
        buf = b""

        # Read raw bytes — ffmpeg uses \\r to overwrite progress lines
        while True:
            chunk = self.ffmpeg_proc.stderr.read(4096)
            if not chunk:
                break
            buf += chunk
            # Split on both \\r and \\n
            while b"\r" in buf or b"\n" in buf:
                idx_r = buf.find(b"\r")
                idx_n = buf.find(b"\n")
                if idx_r == -1: idx = idx_n
                elif idx_n == -1: idx = idx_r
                else: idx = min(idx_r, idx_n)
                line = buf[:idx].decode("utf-8", errors="replace").strip()
                buf = buf[idx+1:]
                if not line:
                    continue
                m = re.search(r"time=(\d+):(\d+):(\d+)\.(\d+)", line)
                if m:
                    h, mi, s, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                    current_time = h * 3600 + mi * 60 + s + ms / 100.0
                    if dur > 0:
                        local_pct = min(100, (current_time / dur) * 100)
                        total_pct = pass_start + (local_pct / total_passes)
                        self.after(0, self._update_progress, total_pct,
                            f"{total_pct:.0f}%")

        self.ffmpeg_proc.wait()
        ret = self.ffmpeg_proc.returncode
        self.ffmpeg_proc = None

        if ret != 0:
            raise Exception(f"ffmpeg error (code: {ret})")

    # ============================================================
    #  FFMPEG COMMANDS
    # ============================================================
    def _cmd_120_tiktok(self, inp, out):
        """TikTok: Clean 120fps - pure interpolation, no effects"""
        f = ff()
        vf = (
            "minterpolate=fps=120:mi_mode=blend"
        )
        return (f'"{f}" -y -i "{inp}" '
                f'-vf "{vf}" '
                f'-c:v libx264 -preset veryslow -crf 10 -b:v 100M -maxrate 120M -bufsize 200M '
                f'-pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 '
                f'-c:a aac -b:a 320k -ar 48000 -movflags +faststart "{out}"')

    def _cmd_120_youtube(self, inp, out):
        """YouTube Gaming Montage: Maximum smoothness + crispy + motion blur
        
        mi_mode=blend interpolates without motion estimation = no ghosting.
        Motion blur + sharpening for professional montage look.
        No color filter - keeps original colors.
        """
        f = ff()
        vf = (
            # Step 1: Blend interpolation - smooth frames without ghosting
            "minterpolate=fps=120:mi_mode=blend,"
            # Step 2: Strong motion blur - ultra smooth look
            "tblend=all_mode=average:all_opacity=0.18,"
            # Step 3: Adaptive sharpen - crispy detail
            "cas=0.8"
        )
        return (f'"{f}" -y -i "{inp}" '
                f'-vf "{vf}" '
                f'-c:v libx264 -preset veryslow -crf 8 -tune film '
                f'-b:v 120M -maxrate 150M -bufsize 240M '
                f'-profile:v high -level 5.1 '
                f'-g 60 -bf 2 -flags +cgop+ildct+ilme '
                f'-pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 '
                f'-c:a aac -b:a 384k -ar 48000 '
                f'-movflags +faststart "{out}"')

    def _check_ffmpeg(self):
        try:
            cmd = ff()
            result = subprocess.run([cmd, "-version"], capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            return result.returncode == 0
        except: return False

    def _get_duration(self, path):
        try:
            probe = ff("ffprobe")
            r = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            return float(r.stdout.strip())
        except: return 0.0

    def _update_progress(self, pct, text):
        self.prog_bar.set(pct / 100)
        self.prog_label.configure(text=text)

# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    app = SpicyConverter()
    app.mainloop()
