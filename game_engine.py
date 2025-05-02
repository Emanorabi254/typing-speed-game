# 📁 file: Game_engine.py

import tkinter as tk
import os
import json
import random
import time
from tkinter import ttk
from data_handler import save_score, update_level_status
from sounds import play_sound

class GameEngine:
    def __init__(self, root, username, mode, level_index, words, on_finish_callback):
        self.root = root
        self.username = username
        self.mode = mode
        self.level_index = level_index
        self.original_words = words.copy()
        self.words_pool = random.sample(words, len(words))
        self.callback = on_finish_callback

        self.correct_count = 0
        self.score = 0
        self.current_word = ""
        self.word_start_time = 0
        self.timer_running = True
        self.current_word_visible = True
        self.hide_word_job = None

        self.bg = "#1d1745"
        self.fg = "#f8f8f2"
        self.accent = "#FFBF00"

        base_time = {"Easy": 120, "Medium": 150, "Hard": 180}
        self.level_time = base_time.get(self.mode, 120)
        if self.level_index >= 40:
            self.level_time += 30
        self.time_left = self.level_time

        self.frame = tk.Frame(self.root, bg=self.bg)
        self.frame.pack(fill="both", expand=True)

        self.word_label = tk.Label(self.frame, text="", font=("Arial", 22, "bold"), fg=self.accent, bg=self.bg)
        self.word_label.pack(pady=20)

        self.entry = tk.Entry(self.frame, font=("Arial", 18), bg="#2d2d3a", fg="white", insertbackground="white", justify="center")
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_word)

        self.score_label = tk.Label(self.frame, text="Score: 0", font=("Arial", 14), fg="white", bg=self.bg)
        self.score_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.frame, length=300, mode='determinate')
        self.progress.pack(pady=20)

        self.top_label = tk.Label(self.frame, text="", font=("Arial", 12, "bold"), fg="white", bg=self.bg)
        self.top_label.pack()

        self.back_button = tk.Button(self.frame, text="Exit Level", command=self.exit_level, bg="#44475a", fg="white", font=("Arial", 10, "bold"))
        self.back_button.pack(pady=10)

        self.total_shown = 0
        self.update_timer()
        self.next_word()

    def update_timer(self):
        if not self.timer_running:
            return

        self.time_left -= 1
        self.top_label.config(text=f"\U0001F464 {self.username}   |   ⏱️ Time Left: {self.time_left}s")

        if self.time_left <= 0:
            play_sound("timeout")
            self.finish_level()
        else:
            self.root.after(1000, self.update_timer)

    def next_word(self):
        if not self.timer_running or self.time_left <= 0 or not self.words_pool:
            return

        self.current_word = self.words_pool.pop(0)
        self.total_shown += 1
        self.progress.config(maximum=self.total_shown)

        self.current_word_visible = True
        self.word_start_time = time.time()
        self.word_label.config(text=self.current_word)
        self.entry.delete(0, tk.END)

        self.hide_word_job = self.root.after(10000, self.hide_word_if_not_typed)

    def check_word(self, event=None):
        if not self.timer_running:
            return

        if self.hide_word_job:
            self.root.after_cancel(self.hide_word_job)

        typed = self.entry.get().strip()
        correct = typed.lower() == self.current_word.lower()

        if correct:
            elapsed = time.time() - self.word_start_time
            bonus = 20 if elapsed < 10 else 0
            self.score += 50 + bonus
            self.correct_count += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.progress["value"] = self.correct_count
            play_sound("beep_correct")
        else:
            play_sound("beep_wrong")

        self.next_word()

    def hide_word_if_not_typed(self):
        if not self.timer_running or not self.current_word_visible:
            return

        self.current_word_visible = False
        typed = self.entry.get().strip().lower()

        if typed != self.current_word.lower():
            self.word_label.config(text="(Time's up)")
            play_sound("beep_wrong")
            self.root.after(1000, self.next_word)

    def finish_level(self):
        self.timer_running = False
        total_attempted = max(1, self.total_shown)
        percent = round((self.correct_count / total_attempted) * 100)
        update_level_status(self.mode, self.level_index, percent)
        save_score(self.username, self.score)
        self.frame.destroy()

        result_frame = tk.Frame(self.root, bg=self.bg)
        result_frame.pack(fill="both", expand=True)

        if percent >= 90:
            icon = "\U0001F389"
            title = "Congratulations!"
            subtitle = f"You passed with {percent}% accuracy \U0001F3AF"
            color = "#FCD150"
        else:
            icon = "\U0001F622"
            title = "Try Again!"
            subtitle = f"You reached {percent}% accuracy"
            color = "#9F7A0E"

        tk.Label(result_frame, text=icon, font=("Arial", 32), bg=self.bg).pack(pady=10)
        tk.Label(result_frame, text=title, font=("Arial", 20, "bold"), fg=color, bg=self.bg).pack()
        tk.Label(result_frame, text=subtitle, font=("Arial", 14), fg="white", bg=self.bg).pack(pady=10)
        tk.Label(result_frame, text=f"Score: {self.score}", font=("Arial", 12), fg="white", bg=self.bg).pack()

        btn_frame = tk.Frame(result_frame, bg=self.bg)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="⬅ Back", command=lambda: [result_frame.destroy(), self.callback()],
                  bg="#44475a", fg="white", width=15).pack(side="left", padx=10)

        if percent >= 90:
            tk.Button(btn_frame, text="Next Level", command=lambda: [result_frame.destroy(), self.start_next_level()],
          bg="#6272a4", fg="white", width=15).pack(side="right", padx=10)

            
        else:
            tk.Button(btn_frame, text="Retry", command=lambda: [result_frame.destroy(), self.retry_level()],
                      bg="#44475a", fg="white", width=15).pack(pady=5)

    def start_next_level(self):
        next_index = self.level_index + 1
        path = f"levels/{self.mode.lower()}.json"

        if not os.path.exists(path):
            print("❌ Level file not found.")
            return

        with open(path, "r") as file:
            levels = json.load(file)["levels"]

        if next_index >= len(levels):
            print("✅ No more levels.")
            self.callback()
            return

        next_words = levels[next_index]

        GameEngine(
            root=self.root,
            username=self.username,
            mode=self.mode,
            level_index=next_index,
            words=next_words,
            on_finish_callback=self.callback
        )
        

    def retry_level(self):
        GameEngine(
            root=self.root,
            username=self.username,
            mode=self.mode,
            level_index=self.level_index,
            words=self.original_words,
            on_finish_callback=self.callback
        )

    def exit_level(self):
        self.timer_running = False
        if self.hide_word_job:
            self.root.after_cancel(self.hide_word_job)
        self.frame.destroy()
        self.callback()
