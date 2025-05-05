from datetime import datetime

def format_profile(user_data):
    lines = ["**Your Profile**"]
    keys = ["name", "mood", "fantasy", "heartbeats", "gems", "referrals"]

    for key in keys:
        value = user_data.get(key, "Not set" if key == "name" else "0" if key in ["heartbeats", "gems", "referrals"] else "Not selected")
        lines.append(f"{key.capitalize()}: {value}")

    if "joined" in user_data:
        lines.append(f"Joined: {user_data['joined']}")

    return "\n".join(lines)

def now_date():
    return datetime.now().strftime("%Y-%m-%d")
