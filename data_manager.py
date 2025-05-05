import json
import os

DATA_FILE = "data.json"
data_cache = None  # Cache to avoid unnecessary file reads

def load_data():
    """Loads user data from the JSON file with caching."""
    global data_cache
    if data_cache is None:
        try:
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w") as f:
                    json.dump({}, f)
            with open(DATA_FILE, "r") as f:
                data_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            data_cache = {}  # Reset cache if an error occurs
    return data_cache

def save_data():
    """Saves cached user data to the JSON file."""
    global data_cache
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data_cache, f, indent=2)
    except IOError:
        print("Error saving data!")

def get_user(uid):
    """Retrieves a specific user's data."""
    return load_data().get(str(uid), {})

def save_user(uid, user_data):
    """Saves individual user data and updates the cache."""
    global data_cache
    data_cache[str(uid)] = user_data
    save_data()

def delete_user(uid):
    """Deletes a user from the database."""
    global data_cache
    if str(uid) in data_cache:
        del data_cache[str(uid)]
        save_data()

def all_users():
    """Returns all stored users."""
    return load_data()
