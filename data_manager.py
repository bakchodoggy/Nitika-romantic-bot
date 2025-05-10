import json
import os
import threading

DATA_FILE = "data.json"
data_lock = threading.Lock()  # Prevents race conditions in multi-threaded environments

def load_data():
    """Loads user data from the JSON file safely."""
    with data_lock:
        try:
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w") as f:
                    json.dump({}, f)
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Warning: Failed to load JSON data. Resetting...")
            return {}

def save_data(data):
    """Safely saves user data to the JSON file with thread safety."""
    with data_lock:
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            print("Error saving data!")

def load_user(uid):
    """Retrieves a specific user's data."""
    data = load_data()
    return data.get(str(uid), {})

def save_user(uid, user_data):
    """Saves individual user data securely."""
    data = load_data()
    data[str(uid)] = user_data
    save_data(data)

def delete_user(uid):
    """Deletes a user from the database safely."""
    data = load_data()
    if str(uid) in data:
        del data[str(uid)]
        save_data(data)

def all_users():
    """Returns all stored users."""
    return load_data()