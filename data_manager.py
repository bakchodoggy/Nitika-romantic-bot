import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(uid):
    data = load_data()
    return data.get(str(uid), {})

def save_user(uid, user_data):
    data = load_data()
    data[str(uid)] = user_data
    save_data(data)

def delete_user(uid):
    data = load_data()
    if str(uid) in data:
        del data[str(uid)]
        save_data(data)

def all_users():
    data = load_data()
    return data
