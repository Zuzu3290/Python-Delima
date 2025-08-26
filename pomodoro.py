
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer (Tkinter)
- Work / Short Break / Long Break cycles
- Start / Pause / Resume / Reset / Skip
- Session counter and progress
- Configurable durations
- Fully responsive UI
- No external dependencies
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
import time

# ---------------------------- CONFIG ---------------------------- #
WORK_MIN = 25  # default work duration (minutes)
SHORT_BREAK_MIN = 5 # default short break (minutes)
LONG_BREAK_MIN = 15  # default long break (minutes)
SESSIONS_BEFORE_LONG_BREAK = 4 # long break after this many work sessions

APP_TITLE = "Pomodoro Timer"
ACCENT = "#ef4444"# red-500
BG = "#0b1220" # near-black
CARD = "#111827" # slate-900
TEXT = "#e5e7eb"# gray-200
MUTED = "#9ca3af"  # gray-400

# ---------------------------- APP ---------------------------- #
class PomodoroApp(tk.Tk):
     def __init__(self):
          super().__init__()
          self.title(APP_TITLE)
          self.configure(bg=BG)
          self.resizable(True, True)   # Make the window resizable
          self.geometry("480x480") # Set a default starting size
          # State
          self.is_running = False
          self.is_paused = False
          self.remaining = 0
          self.completed_work_sessions = 0
          self.current_mode = "WORK"  # WORK / SHORT / LONG
          self._after_id = None
          self.start_time = None

         # Define fonts dynamically for resizing
          self.timer_font = font.Font(family="Consolas", size=44, weight="bold")
          self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
          self.mode_font = font.Font(family="Segoe UI", size=12)
          self.muted_font = font.Font(family="Segoe UI", size=10)

          self._build_ui()
          self._set_mode("WORK", minutes=WORK_MIN) # Bind the resize event to our font resizing function
          self.bind('<Configure>', self._on_resize)

 # ---- UI ----
    def _build_ui(self):
          self.columnconfigure(0, weight=1)
          self.rowconfigure(0, weight=1)
          wrapper = ttk.Frame(self)
          wrapper.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
          self._apply_style()
          wrapper.columnconfigure(0, weight=1)
          wrapper.rowconfigure(0, weight=1)

          card = ttk.Frame(wrapper, padding=16, style="Card.TFrame")
          card.grid(row=0, column=0, sticky="nsew")
          for i in range(8):
              card.rowconfigure(i, weight=1, minsize=40)
          for i in range(4):
              card.columnconfigure(i, weight=1, minsize=60)
          card.grid_propagate(False) # Prevent the card from shrinking to fit widgets

         # Title
          self.title_lbl = ttk.Label(card, text=APP_TITLE, style="Title.TLabel", font=self.title_font)
          self.title_lbl.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0, 8))

         # Mode label
          self.mode_lbl = ttk.Label(card, text="Mode: WORK", style="Mode.TLabel", font=self.mode_font)
          self.mode_lbl.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 12))

         # Timer display
          self.time_lbl = ttk.Label(card, text="25:00", style="Timer.TLabel", font=self.timer_font)
          self.time_lbl.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(0, 12))

        # Progress (sessions)
        self.progress_lbl = ttk.Label(card, text="Work sessions: 0", style="Muted.TLabel", font=self.muted_font)
        self.progress_lbl.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(0, 12))

        # Controls
        self.start_btn = ttk.Button(card, text="Start", command=self.start_timer, style="Accent.TButton")
        self.pause_btn = ttk.Button(card, text="Pause", command=self.pause_timer, state="disabled")
        self.reset_btn = ttk.Button(card, text="Reset", command=self.reset_timer)
        self.skip_btn = ttk.Button(card, text="Skip", command=self.skip_session)

        self.start_btn.grid(row=4, column=0, padx=4, pady=6, sticky="ew")
        self.pause_btn.grid(row=4, column=1, padx=4, pady=6, sticky="ew")
        self.reset_btn.grid(row=4, column=2, padx=4, pady=6, sticky="ew")
        self.skip_btn.grid(row=4, column=3, padx=4, pady=6, sticky="ew")

        # Settings
        sep = ttk.Separator(card)
        sep.grid(row=5, column=0, columnspan=4, pady=12, sticky="ew")

        ttk.Label(card, text="Work (min):", style="Muted.TLabel", font=self.muted_font).grid(row=6, column=0, sticky="w")
        ttk.Label(card, text="Short break (min):", style="Muted.TLabel", font=self.muted_font).grid(row=6, column=1, sticky="w")
        ttk.Label(card, text="Long break (min):", style="Muted.TLabel", font=self.muted_font).grid(row=6, column=2, sticky="w")
        ttk.Label(card, text="Sessions until long break:", style="Muted.TLabel", font=self.muted_font).grid(row=6, column=3, sticky="w")

        self.work_var = tk.IntVar(value=WORK_MIN)
        self.short_var = tk.IntVar(value=SHORT_BREAK_MIN)
        self.long_var = tk.IntVar(value=LONG_BREAK_MIN)
        self.until_long_var = tk.IntVar(value=SESSIONS_BEFORE_LONG_BREAK)

        self.work_spin = ttk.Spinbox(card, from_=1, to=180, textvariable=self.work_var, width=8, command=self._apply_settings)
        self.short_spin = ttk.Spinbox(card, from_=1, to=120, textvariable=self.short_var, width=8, command=self._apply_settings)
        self.long_spin = ttk.Spinbox(card, from_=1, to=240, textvariable=self.long_var, width=8, command=self._apply_settings)
        self.until_long_spin = ttk.Spinbox(card, from_=1, to=12, textvariable=self.until_long_var, width=8, command=self._apply_settings)

        self.work_spin.grid(row=7, column=0, sticky="ew", padx=4, pady=2)
        self.short_spin.grid(row=7, column=1, sticky="ew", padx=4, pady=2)
        self.long_spin.grid(row=7, column=2, sticky="ew", padx=4, pady=2)
        self.until_long_spin.grid(row=7, column=3, sticky="ew", padx=4, pady=2)

    def _apply_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Card.TFrame", background=CARD, relief="flat")
        style.configure("Title.TLabel", background=CARD, foreground=TEXT)
        style.configure("Mode.TLabel", background=CARD, foreground=MUTED)
        style.configure("Timer.TLabel", background=CARD, foreground=TEXT)
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED)
        style.configure("TButton", padding=8)
        style.configure("Accent.TButton", foreground="white", background=ACCENT)
        style.map("Accent.TButton", background=[("active", "#dc2626")])
        self.option_add("*TFrame.background", CARD)
        self.option_add("*Label.background", CARD)

    def _on_resize(self, event):
        """Dynamically adjusts fonts and padding based on window size."""
        # Use a base size to calculate proportional font sizes
        base_size = min(self.winfo_width(), self.winfo_height())
        
        # Adjust font sizes proportionally
        self.timer_font.configure(size=int(base_size / 6))
        self.title_font.configure(size=int(base_size / 18))
        self.mode_font.configure(size=int(base_size / 24))
        self.muted_font.configure(size=int(base_size / 30))

    # ---- Logic ----
    def _set_mode(self, mode: str, minutes: int):
        self.current_mode = mode
        self.mode_lbl.config(text=f"Mode: {mode}")
        self.remaining = int(minutes * 60)
        self._update_time_label()
        self._update_title()
        self.progress_lbl.config(text=f"Work sessions: {self.completed_work_sessions}")

    def _apply_settings(self):
        if not self.is_running and not self.is_paused:
            if self.current_mode == "WORK":
                self.remaining = int(self.work_var.get() * 60)
            elif self.current_mode == "SHORT":
                self.remaining = int(self.short_var.get() * 60)
            else:
                self.remaining = int(self.long_var.get() * 60)
            self._update_time_label()
            self._update_title()

    def _format_time(self, seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        if not self.is_running:
            return

        if self.remaining > 0:
            self.remaining -= 1
            self._update_time_label()
            self._update_title()
            self._after_id = self.after(1000, self._tick)
        else:
            self._notify_session_end()
            self._advance_session()

    def _notify_session_end(self):
        try:
            self.bell()
        except Exception:
            pass

    def _advance_session(self):
        if self.current_mode == "WORK":
            self.completed_work_sessions += 1
            if self.completed_work_sessions % self.until_long_var.get() == 0:
                self._set_mode("LONG", minutes=self.long_var.get())
            else:
                self._set_mode("SHORT", minutes=self.short_var.get())
        else:
            self._set_mode("WORK", minutes=self.work_var.get())

        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self._tick()

    def _update_time_label(self):
        self.time_lbl.config(text=self._format_time(self.remaining))

    def _update_title(self):
        self.title(f"{self._format_time(self.remaining)} • {self.current_mode} • {APP_TITLE}")

     # ---- Controls ----
   def start_timer(self):
        if self.is_running and not self.is_paused:
           return
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.start_btn.config(text="Resume", state="disabled")
        self.pause_btn.config(state="normal")
        self._tick()

    def pause_timer(self):
        if not self.is_running:
           return
        self.is_running = False
        self.is_paused = True
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.start_btn.config(text="Resume", state="normal")
        self.pause_btn.config(state="disabled")

    def reset_timer(self):
         if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.is_running = False
        self.is_paused = False
        self.completed_work_sessions = 0
        self._set_mode("WORK", minutes=self.work_var.get())
        self.start_btn.config(text="Start", state="normal")
        self.pause_btn.config(state="disabled")

    def skip_session(self):
         if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.is_running = False
        self._advance_session()

# ---------------------------- MAIN ---------------------------- #
def main():
    app = PomodoroApp()
    app.mainloop()

if __name__ == "__main__":
    main()
