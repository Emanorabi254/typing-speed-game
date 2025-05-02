# 📁 file: data_handler.py

import json
import os

DATA_FILE = "data/user_data.json"
LEVEL_FILE = "data/level_status.json"

def load_user():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_user(username, nickname):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as file:
        json.dump({
            "username": username,
            "nickname": nickname,
            "best_score": 0,
            "scores": []
        }, file)

def save_score(username, score):
    data = load_user()
    data["scores"].append(score)
    if score > data.get("best_score", 0):
        data["best_score"] = score
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def initialize_levels():
    if not os.path.exists(LEVEL_FILE):
        levels = {
            "Easy": [ {"unlocked": i == 0, "progress": 0} for i in range(100)],
            "Medium": [ {"unlocked": i == 0, "progress": 0} for i in range(100)],
            "Hard": [ {"unlocked": i == 0, "progress": 0} for i in range(100)],
        }
        os.makedirs("data", exist_ok=True)
        with open(LEVEL_FILE, "w") as f:
            json.dump(levels, f)

def load_level_status():
    with open(LEVEL_FILE, "r") as f:
        return json.load(f)

def update_level_status(mode, level_index, progress_percent):
    data = load_level_status()
    data[mode][level_index]["progress"] = progress_percent
    if progress_percent >= 90 and level_index + 1 < 100:
        data[mode][level_index + 1]["unlocked"] = True
    with open(LEVEL_FILE, "w") as f:
        json.dump(data, f)
