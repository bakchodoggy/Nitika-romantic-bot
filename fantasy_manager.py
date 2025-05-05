import random

def get_random_fantasy_image():
    """Returns a random fantasy-themed image URL."""
    images = [
        "https://example.com/fantasy1.jpg",
        "https://example.com/fantasy2.jpg",
        "https://example.com/fantasy3.jpg"
    ]
    return random.choice(images)
