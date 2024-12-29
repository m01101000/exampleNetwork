import json
from datetime import datetime
import random

def generate_like_data(filename, num_likes, user_id_range, post_id_range):
    try:
        # Load existing likes if file exists
        with open(filename, "r", encoding="utf-8") as f:
            likes = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        likes = []

    # Determine starting point based on the last LikeID in the file
    start_id = likes[-1]["LikeID"] + 1 if likes else 1

    for i in range(num_likes):
        like_id = start_id + i
        post_id = random.randint(post_id_range[0], post_id_range[1])
        user_id = random.randint(user_id_range[0], user_id_range[1])
        like = {
            "LikeID": like_id,
            "PostID": post_id,
            "UserID": user_id,
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        likes.append(like)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(likes, f, indent=4, ensure_ascii=False)

    print(f"{num_likes} likes have been added to {filename}")

# Example usage with repetition
repetitions = 10  # Number of times to repeat the process
likes_per_iteration = 10000
user_id_range = (1, 10000)
post_id_range = (1, 10000)

for _ in range(repetitions):
    try:
        generate_like_data("data/likes.json", likes_per_iteration, user_id_range, post_id_range)
    except Exception as e:
        print(f"An error occurred during this iteration: {e}")
