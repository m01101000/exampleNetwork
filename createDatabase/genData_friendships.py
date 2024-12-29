import json
from datetime import datetime
import random

def generate_friendship_data(filename, num_friendships, user_id_range):
    try:
        # Load existing friendships if file exists
        with open(filename, "r", encoding="utf-8") as f:
            friendships = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        friendships = []

    # Determine starting point based on the last FriendshipID in the file
    start_id = friendships[-1]["FriendshipID"] + 1 if friendships else 1

    existing_pairs = {(f["UserID1"], f["UserID2"]) for f in friendships}

    for i in range(num_friendships):
        while True:
            user_id1 = random.randint(user_id_range[0], user_id_range[1])
            user_id2 = random.randint(user_id_range[0], user_id_range[1])
            if user_id1 != user_id2 and (user_id1, user_id2) not in existing_pairs and (user_id2, user_id1) not in existing_pairs:
                break

        friendship_id = start_id + i
        friendship = {
            "FriendshipID": friendship_id,
            "UserID1": user_id1,
            "UserID2": user_id2,
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        friendships.append(friendship)
        existing_pairs.add((user_id1, user_id2))

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(friendships, f, indent=4, ensure_ascii=False)

    print(f"{num_friendships} friendships have been added to {filename}")

# Example usage with repetition
repetitions = 10  # Number of times to repeat the process
friendships_per_iteration = 1000
user_id_range = (1, 10000)

for _ in range(repetitions):
    try:
        generate_friendship_data("data/friendships.json", friendships_per_iteration, user_id_range)
    except Exception as e:
        print(f"An error occurred during this iteration: {e}")
