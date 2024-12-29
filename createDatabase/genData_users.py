import json
from datetime import datetime

def generate_user_data(filename, num_users):
    try:
        # Load existing users if file exists
        with open(filename, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        users = []

    # Determine starting point based on the last UserID in the file
    start_id = users[-1]["UserID"] + 1 if users else 1

    for i in range(num_users):
        user_id = start_id + i
        user = {
            "UserID": user_id,
            "Name": f"Nutzer{str(user_id).zfill(8)}",
            "Email": f"{str(user_id).zfill(8)}@example.com",
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        users.append(user)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    print(f"{num_users} users have been added to {filename}")

# Example usage with repetition
repetitions = 10  # Number of times to repeat the process
users_per_iteration = 100000

for _ in range(repetitions):
    try:
        generate_user_data("data/users.json", users_per_iteration)
    except Exception as e:
        print(f"An error occurred during this iteration: {e}")
