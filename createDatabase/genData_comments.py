import json
from datetime import datetime
import random

def generate_comment_data(filename, num_comments, user_id_range, post_id_range):
    try:
        # Load existing comments if file exists
        with open(filename, "r", encoding="utf-8") as f:
            comments = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        comments = []

    # Determine starting point based on the last CommentID in the file
    start_id = comments[-1]["CommentID"] + 1 if comments else 1

    # Sample lorem ipsum contents for comments
    lorem_texts = [
        "Ut enim ad minim veniam, quis.",
        "Duis aute irure dolor.",
        "Excepteur sint occaecat cupidatat non proident."
    ]

    for i in range(num_comments):
        comment_id = start_id + i
        post_id = random.randint(post_id_range[0], post_id_range[1])
        user_id = random.randint(user_id_range[0], user_id_range[1])
        comment = {
            "CommentID": comment_id,
            "PostID": post_id,
            "UserID": user_id,
            "Content": random.choice(lorem_texts),
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        comments.append(comment)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)

    print(f"{num_comments} comments have been added to {filename}")

# Example usage with repetition
repetitions = 10  # Number of times to repeat the process
comments_per_iteration = 1000
user_id_range = (1, 10000)
post_id_range = (1, 10000)

for _ in range(repetitions):
    try:
        generate_comment_data("data/comments.json", comments_per_iteration, user_id_range, post_id_range)
    except Exception as e:
        print(f"An error occurred during this iteration: {e}")
