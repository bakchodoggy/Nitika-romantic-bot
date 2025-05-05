from datetime import datetime

def format_profile(user_data):
    lines = []
    lines.append(f"**Your Profile**")
    lines.append(f"Name: {user_data.get('name', 'Not set')}")
    lines.append(f"Mood: {user_data.get('mood', 'Not selected')}")
    lines.append(f"Fantasy: {user_data.get('fantasy', 'Off')}")
    lines.append(f"Heartbeats: {user_data.get('heartbeats', 0)}")
    lines.append(f"Gems: {user_data.get('gems', 0)}")
    lines.append(f"Referrals: {user_data.get('referrals', 0)}")
    joined = user_data.get('joined')
    if joined:
        lines.append(f"Joined: {joined}")
    return "\n".join(lines)

def now_date():
    return datetime.now().strftime("%Y-%m-%d")
