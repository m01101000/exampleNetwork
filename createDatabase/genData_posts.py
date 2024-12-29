import json
from datetime import datetime
import random

def generate_post_data(filename, num_posts, user_id_range):
    try:
        # Load existing posts if file exists
        with open(filename, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        posts = []

    # Determine starting point based on the last PostID in the file
    start_id = posts[-1]["PostID"] + 1 if posts else 1

    # Sample lorem ipsum contents
    lorem_texts = [
        "example a",
        "example b",
        "example c"
    ]

    for i in range(num_posts):
        post_id = start_id + i
        user_id = random.randint(user_id_range[0], user_id_range[1])
        post = {
            "PostID": post_id,
            "UserID": user_id,
            "Content": random.choice(lorem_texts),
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        posts.append(post)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)

    print(f"{num_posts} posts have been added to {filename}")

# Example usage with repetition
repetitions = 1000  # Number of times to repeat the process
posts_per_iteration = 10000
user_id_range = (1, 100)

for _ in range(repetitions):
    try:
        generate_post_data("data/posts.json", posts_per_iteration, user_id_range)
    except Exception as e:
        print(f"An error occurred during this iteration: {e}")
