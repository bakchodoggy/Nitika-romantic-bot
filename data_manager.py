import json
import os

DATA_FILE = "data.json"

# Cache loaded data to prevent excessive file reads
data_cache = None

def load_data():
    global data_cache
    if data_cache is None:  # Load only once to optimize performance
        try:
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w") as f:
                    json.dump({}, f)
            with open(DATA_FILE, "r") as f:
                data_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            data_cache = {}  # Reset cache on error
    return data_cache

def save_data():
    global data_cache
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data_cache, f, indent=2)
    except IOError:
        print("Error saving data to file!")

def get_user(uid):
    data = load_data()
    return data.get(str(uid), {})

def save_user(uid, user_data):
    global data_cache
    data_cache = load_data()  # Ensure cache is up-to-date
    data_cache[str(uid)] = user_data
    save_data()

def delete_user(uid):
    global data_cache
    data_cache = load_data()
    if str(uid) in data_cache:
        del data_cache[str(uid)]
        save_data()

def all_users():
    return load_data()