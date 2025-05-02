
import tkinter as tk
import json
import os
from data_handler import load_user, save_user, load_level_status, initialize_levels
from game_engine import GameEngine
from graph import embed_score_graph
from PIL import Image, ImageTk

class TypingGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Game")
        self.root.configure(bg="#1e1e2f")
        self.root.resizable(True, True)

        self.username = ""
        self.nickname = ""
        self.frames = {}
        self.mode = ""
        self.levels_data = {}
        self.selected_level = 0

        self.bg = "#1d1745"
        self.fg = "#f8f8f2"
        self.accent = "#FFBF00"
        
        self.bg_images = {}
        self.bg_labels = {}
        self.resize_job = None   # to track resize job
        self.last_columns_count = None  # to track column change
        self.max_grid_columns = 13 # Maximum number of columns for level buttons
        self.root.bind("<Configure>", self.handle_resize_event)


        initialize_levels()
        self.init_user()

    def init_user(self):
        user = load_user()
        if not user:
            self.ask_username()
        else:
            self.username = user["username"]
            self.nickname = user.get("nickname", self.username)
            self.show_welcome_message()

    def ask_username(self):
        self.clear_frames()
        self.root.geometry("500x400")
        
        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["register"] = frame
        self.add_background(frame, "assets/Welcome.png", "welcome")

        tk.Label(frame, text="Enter your name:", font=("Arial", 12), fg=self.accent, bg=self.bg).pack(pady=5)
        name_entry = tk.Entry(frame, font=("Arial", 12), bg="#2d2d3a", fg="white", insertbackground="white")
        name_entry.pack(pady=5)

        tk.Label(frame, text="Choose your nickname:", font=("Arial", 12), fg=self.accent, bg=self.bg).pack(pady=5)
        nick_entry = tk.Entry(frame, font=("Arial", 12), bg="#2d2d3a", fg="white", insertbackground="white")
        nick_entry.pack(pady=5)

        tk.Button(frame, text="Start", command=lambda: self.save_user(name_entry.get(), nick_entry.get()), bg="#6272a4", fg="white").pack(pady=10)

    def save_user(self, name, nickname):
        if name and nickname:
            self.username = name
            self.nickname = nickname
            save_user(name, nickname)
            self.show_welcome_message()
            
    def add_background(self, frame, image_path, key):
        img = Image.open(image_path)
        self.bg_images[key] = img
        resized = img.resize((self.root.winfo_width(), self.root.winfo_height()))
        photo = ImageTk.PhotoImage(resized)
        
        label = tk.Label(frame, image=photo)
        label.image = photo
        label.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_labels[key] = label

    def show_welcome_message(self):
        self.clear_frames()
        self.root.geometry("500x400")


        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["welcome"] = frame

        self.add_background(frame, "assets/typing_bg.png", "welcome")
       
        tk.Label(frame, text=f"👋 Welcome {self.nickname}!", font=("Arial", 20, "bold"), fg=self.accent, bg=self.bg).pack(pady=60)
        tk.Button(frame, text="Enter Game", command=self.show_main_menu, bg="#6272a4", fg="white", width=20, height=2).pack(pady=20)

    def clear_frames(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames.clear()

    def show_main_menu(self):
        self.clear_frames()
        
        self.root.geometry("800x600")

        user = load_user()
        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["main"] = frame
        
        self.add_background(frame, "assets/typing_bg.png", "main")

        tk.Label(frame, text="Typing Speed Game", font=("Arial", 24, "bold"), fg=self.accent, bg=self.bg).pack(pady=30)
        tk.Label(frame, text=f"👤 {self.nickname}", font=("Arial", 14), fg=self.fg, bg=self.bg).pack(pady=5)
        tk.Label(frame, text=f"🏆 Best Score: {user['best_score']}", font=("Arial", 12), fg=self.accent, bg=self.bg).pack(pady=2)

        self.make_menu_button(frame, "Play Game", self.select_mode)
        self.make_menu_button(frame, "Profile", self.show_profile)
        self.make_menu_button(frame, "Instructions", self.show_instructions)
        self.make_menu_button(frame, "Exit", self.root.destroy)

        tk.Label(frame, text="Made with❤️by Eman Orabi❤️", font=("Arial", 10), fg=self.fg, bg=self.bg).pack(side="bottom", pady=10)
    def make_menu_button(self, frame, text, command):
        tk.Button(frame, text=text, width=20, height=2, bg="#6272a4", fg="white", font=("Arial", 12, "bold"), command=command).pack(pady=10)

    def show_instructions(self):
        self.clear_frames()
        self.root.geometry("800x600")

        canvas = tk.Canvas(self.root, bg=self.bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.frames["instructions"] = canvas

        # Elements
        title = canvas.create_text(400, 50, text="📝 Instructions", fill=self.accent,
                                font=("Arial", 24, "bold"), tags="centered")
        
        instructions = (
            "📘 How to Play:\n\n"
            "🎯 Choose a difficulty and unlock levels.\n\n"
            "⌨️ Type the shown word within 30 seconds.\n\n"
            "⏳ New word appears every 50s (or sooner if answered fast).\n\n"
            "✅ Correct answers = 50pts (+20 bonus if fast).\n\n"
            "🚀 Finish with 90%+ to unlock next level.\n\n"
            "🔙 You can exit levels anytime using the back button.\n\n"
        )

        body = canvas.create_text(400, 330, text=instructions, fill=self.fg,
                                font=("Arial", 13), width=600, justify="center", tags="centered")
        
        footer = canvas.create_text(400, 550, text="✨ Design made with ❤️ by Eman Orabi ✨",
                                    fill="white", font=("Arial", 11, "italic"), tags="centered")
        
        back_btn = tk.Button(self.root, text="⬅ Back", command=self.show_main_menu,
                            bg="#6272a4", fg="white", font=("Arial", 11, "bold"))
        back_window = canvas.create_window(400, 590, window=back_btn, tags="centered")

        # Update the canvas size to fit the content
        def center_all(event):
            canvas_width = event.width
            for tag in ["centered"]:
                items = canvas.find_withtag(tag)
                for item in items:
                    coords = canvas.coords(item)
                    if len(coords) == 2:
                        canvas.coords(item, canvas_width // 2, coords[1])

        canvas.bind("<Configure>", center_all)

    def select_mode(self):
        self.clear_frames()
        self.root.geometry("800x600")

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["mode"] = frame
        
        self.add_background(frame, "assets/choice.png", "mode")

        tk.Label(frame, text="Choose Difficulty", font=("Arial", 20, "bold"), fg=self.accent, bg=self.bg).pack(pady=20)

        for m in ["Easy", "Medium", "Hard"]:
            self.make_menu_button(frame, m, lambda d=m: self.show_levels(d))

        self.make_menu_button(frame, "⬅ Back", self.show_main_menu)

    def show_levels(self, mode):
        self.mode = mode
        self.last_columns_count = None  # to track column change

        self.clear_frames()
        self.root.geometry("800x600")

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["levels"] = frame

        # Back button in the top bar
        top_bar = tk.Frame(frame, bg=self.bg)
        top_bar.pack(fill="x", pady=(10, 0))
        tk.Button(top_bar, text="⬅ Back", command=self.select_mode,
                bg="#44475a", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Label(frame, text=f"{mode} Levels", font=("Arial", 18, "bold"),
                fg=self.accent, bg=self.bg).pack(pady=10)

        # Canvas zone
        canvas = tk.Canvas(frame, bg=self.bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Save scroll_frame to access it during resize
        self.levels_container = scroll_frame

        # Render buttons initially
        self.root.after_idle(self.render_levels)
        # Mouse wheel scroll support
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


    def render_levels(self):
        current_width = self.root.winfo_width()
        button_width = 110
        max_columns = max(3, current_width // button_width)

        # Skip if columns didn't change
        if self.last_columns_count == max_columns:
            return
        self.last_columns_count = max_columns

        for widget in self.levels_container.winfo_children():
            widget.destroy()

        levels_status = load_level_status()[self.mode]
        for i, level in enumerate(levels_status):
            status = level["unlocked"]
            progress = level["progress"]

            btn = tk.Button(
                self.levels_container,
                text=f"Level {i+1}\n{progress}%",
                width=10,
                height=3,
                bg="#F8D56C" if status else "#44475a",
                fg="black" if status else "#888888",
                state="normal" if status else "disabled",
                font=("Arial", 10, "bold"),
                command=lambda idx=i: self.start_level(idx)
            )
            row, col = divmod(i, max_columns)
            start_col = (self.max_grid_columns - max_columns) // 2
            btn.grid(row=row, column=col + start_col, padx=10, pady=10)

    def start_level(self, level_index):
        self.selected_level = level_index
        path = f"levels/{self.mode.lower()}.json"
        if not os.path.exists(path): return

        with open(path, "r") as file:
            all_levels = json.load(file)["levels"]

        if level_index >= len(all_levels): return

        level_words = all_levels[level_index]
        self.clear_frames()
        GameEngine(
            root=self.root,
            username=self.username,
            mode=self.mode,
            level_index=level_index,
            words=level_words,
            on_finish_callback=lambda: self.show_levels(self.mode)
        )

    def show_profile(self):
        user = load_user()
        self.clear_frames()
        self.root.geometry("800x600")

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="both", expand=True)
        self.frames["profile"] = frame

        tk.Label(frame, text="Your Profile", font=("Arial", 20, "bold"), fg=self.accent, bg=self.bg).pack(pady=10)
        tk.Label(frame, text=f"Name: {user['username']}", font=("Arial", 14), fg="white", bg=self.bg).pack()
        tk.Label(frame, text=f"Best Score: {user['best_score']}", font=("Arial", 14), fg="white", bg=self.bg).pack()
        if user["scores"]:
            tk.Label(frame, text=f"Last Score: {user['scores'][-1]}", font=("Arial", 14), fg="white", bg=self.bg).pack()

        tk.Label(frame, text="Progress Graph", font=("Arial", 12, "bold"), fg="white", bg=self.bg).pack(pady=5)
        embed_score_graph(frame, user["scores"])

        self.make_menu_button(frame, "⬅ Back", self.show_main_menu)
        
    def _do_resize_backgrounds(self):
        self.resize_job = None  # Reset job ID
        if not self.bg_images or not self.bg_labels:
            return

        for key in list(self.bg_images):
            try:
                img = self.bg_images[key]
                label = self.bg_labels.get(key)
                if not label or not label.winfo_exists():
                    continue  # make sure the label exists
                # Resize the image to fit the current window size
                resized = img.resize((self.root.winfo_width(), self.root.winfo_height()))
                photo = ImageTk.PhotoImage(resized)
                label.config(image=photo)
                label.image = photo
            except Exception as e:
                print(f"Resize error for {key}: {e}")

    def resize_all_backgrounds(self, event=None):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(200, self._do_resize_backgrounds)

    def handle_resize_event(self, event=None):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(200, self._resize_components)

    def _resize_components(self):
        self._do_resize_backgrounds()
        if "levels" in self.frames:
            self.render_levels()


# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingGameApp(root)
    root.mainloop()
