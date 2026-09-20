"""
SpicyConverter - TikTok 120fps Quality Tool
120fps Ultra Smooth: Interpolate -> Denoise -> Sharpen pipeline
by Djani
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess, os, sys, threading, re, hashlib, hmac, time, struct, json
from pathlib import Path
from license_client import get_hardware_id, check_license, activate_license, LICENSE_DIR

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
        self.geometry("600x860")
        self.minsize(600, 860)
        self.maxsize(600, 860)
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
        self.selected_mode = "60fps"
        self.ffmpeg_proc = None

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
        self._methods()
        self._button()
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

    def _methods(self):
        # hidden - 120fps is always the default
        self.selected_mode = "120fps"

    def _button(self):
        bf = ctk.CTkFrame(self.content, fg_color="transparent")
        bf.pack(fill="x", pady=(12, 8))
        self.btn = ctk.CTkButton(bf, text="\u25b6  START PROCESSING", font=FONT_NAME(13, True),
            fg_color=P["green"], hover_color=P["green_dark"], corner_radius=10, height=46, cursor="hand2", command=self._start)
        self.btn.pack(fill="x")

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
        p = filedialog.askopenfilename(title="Select Video", filetypes=[("Video","*.mp4 *.mov *.avi *.mkv *.webm"),("All","*.*")])
        if p: self._set_file(p)

    def _set_file(self, path):
        self.selected_file = path
        name = os.path.basename(path)
        mb = os.path.getsize(path) / (1024*1024)
        self.file_name.configure(text=name)
        self.file_size.configure(text=f"{mb:.1f} MB  |  Ready")
        self.file_card.pack(fill="x", pady=(0, 14))
        self.drop_title.configure(text=name, text_color=P["text"])
        self.drop_sub.configure(text=f"{mb:.1f} MB  \u2022  Ready", text_color=P["green"])
        self.drop_inner.configure(border_color=P["green"])
        self.status.configure(text=f"Loaded: {name}", text_color=P["green"])

    # ============================================================
    #  PROCESSING
    # ============================================================
    def _start(self):
        if self.processing: return
        if not self.selected_file:
            messagebox.showinfo("No Video", "Select a video first."); return
        if not self._check_ffmpeg():
            messagebox.showerror("ffmpeg not found", "Install: winget install ffmpeg"); return

        self.processing = True
        self.btn.configure(text="\u23f3  PROCESSING...", fg_color=P["text_muted"], state="disabled")
        self.prog_frame.pack(fill="x", pady=(0, 6), after=self.btn.master)
        self.prog_bar.set(0)
        self.prog_label.configure(text="0%  |  Starting...")
        self.status.configure(text="Processing...", text_color=P["green"])
        self._clear_log()
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        inp = self.selected_file
        p = Path(inp)
        out_dir = p.parent
        dur = self._get_duration(inp)

        try:
            out = out_dir / f"{p.stem}_120fps.mp4"
            self.after(0, self._log, "[..] 120fps Ultra Smooth\n")
            cmd = self._cmd_120(inp, str(out))
            self._run_ffmpeg(cmd, dur, 0)

            self.after(0, self._log, f"[OK] Output: {out.name}")

            if os.path.exists(str(out)):
                size_mb = os.path.getsize(str(out)) / (1024*1024)
                self.after(0, self._done, str(out), size_mb)
            else:
                self.after(0, self._fail, "Output file not created")

        except Exception as e:
            self.after(0, self._fail, str(e))

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
    def _cmd_120(self, inp, out):
        """120fps single-pass: interpolate -> encode (clean, no effects)"""
        f = ff()
        vf = (
            "fps=120,"
            "minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:vsbmc=1"
            ":search_param=1024"
        )
        return (f'"{f}" -y -i "{inp}" '
                f'-vf "{vf}" '
                f'-c:v libx264 -preset veryslow -crf 10 -b:v 100M -maxrate 120M -bufsize 200M '
                f'-pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 '
                f'-c:a aac -b:a 320k -ar 48000 -movflags +faststart "{out}"')

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

    def _done(self, output, size_mb):
        self.processing = False
        self.prog_frame.pack_forget()
        self.btn.configure(text="\u25b6  START PROCESSING", fg_color=P["green"], state="normal")
        self._log(f"\n[OK] Done! Saved as: {os.path.basename(output)}")
        self._log("\nTIP: Upload via tiktok.com (not the mobile app)")
        self.status.configure(text=f"Done: {os.path.basename(output)}", text_color=P["green"])
        if messagebox.askyesno("Done!", f"Open {os.path.basename(output)}?"):
            os.startfile(output)

    def _fail(self, msg):
        self.processing = False
        self.prog_frame.pack_forget()
        self.btn.configure(text="\u25b6  START PROCESSING", fg_color=P["green"], state="normal")
        self._log(f"\n[ERROR] {msg}")
        self.status.configure(text="Error", text_color=P["fire"])

# ============================================================
#  LICENSE DIALOG
# ============================================================
class LicenseDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SpicyConverter - License")
        self.geometry("480x350")
        self.resizable(False, False)
        self.configure(fg_color="#0a0a0a")
        self.grab_set()
        self.result = False

        # Dark titlebar
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except: pass

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(f, text="\U0001f512", font=("Segoe UI", 36)).pack(pady=(0, 10))
        ctk.CTkLabel(f, text="License Required", font=("Bahnschrift", 20, "bold"), text_color="#f0e8ec").pack()
        ctk.CTkLabel(f, text="Enter your license key to activate SpicyConverter.",
            font=("Bahnschrift", 11), text_color="#7a6070").pack(pady=(4, 16))

        hwid = get_hardware_id()
        ctk.CTkLabel(f, text="Your Hardware ID:", font=("Bahnschrift", 9), text_color="#4a3545").pack()
        ctk.CTkLabel(f, text=hwid, font=("Cascadia Code", 10), text_color="#f97316").pack(pady=(0, 12))

        self.key_entry = ctk.CTkEntry(f, placeholder_text="XXXX-XXXXXXXX-XXXXXXXXXXXXXXXX",
            font=("Cascadia Code", 11), fg_color="#120e14", border_color="#3a1525",
            border_width=1, corner_radius=8, height=38)
        self.key_entry.pack(fill="x", pady=(0, 12))

        self.status = ctk.CTkLabel(f, text="", font=("Bahnschrift", 10), text_color="#ef4444")
        self.status.pack(pady=(0, 8))

        self.btn = ctk.CTkButton(f, text="Activate", font=("Bahnschrift", 13, "bold"),
            fg_color="#166534", hover_color="#14532d", corner_radius=8, height=40,
            command=self._activate)
        self.btn.pack(fill="x")

    def _activate(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status.configure(text="Please enter a license key.")
            return

        self.btn.configure(text="Validating...", state="disabled")
        self.status.configure(text="Connecting to server...", text_color="#f97316")

        def _do():
            ok, msg, hwid = activate_license(key)
            self.after(0, lambda: self._result(ok, msg))

        threading.Thread(target=_do, daemon=True).start()

    def _result(self, ok, msg):
        if ok:
            self.status.configure(text=msg, text_color="#22c55e")
            self.result = True
            self.after(500, self.destroy)
        else:
            self.status.configure(text=msg, text_color="#ef4444")
            self.btn.configure(text="Activate", state="normal")

# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    valid, msg, hwid = check_license()
    if valid:
        app = SpicyConverter()
        app.mainloop()
    else:
        root = ctk.CTk()
        root.withdraw()
        dialog = LicenseDialog(root)
        root.wait_window(dialog)
        if dialog.result:
            app = SpicyConverter()
            app.mainloop()
        root.destroy()
