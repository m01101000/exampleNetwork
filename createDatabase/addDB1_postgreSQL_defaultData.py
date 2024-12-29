import json
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import insert

# PostgreSQL connection
DATABASE_URI = 'postgresql://postgres:super@localhost:5432/db1_postgreSQL'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

def insert_data_postgresql():
    """
    Inserts JSON data into PostgreSQL using SQLAlchemy Core without models.
    """
    # Reflect the database schema
    metadata.reflect(bind=engine)
    
    # Open a connection
    with engine.connect() as conn:
        try:
            # Insert Users
            with open('data/users.json', 'r', encoding='utf-8') as f:
                users_table = metadata.tables['user']
                users = json.load(f)
                conn.execute(insert(users_table), users)

            # Insert Posts
            with open('data/posts.json', 'r', encoding='utf-8') as f:
                posts_table = metadata.tables['post']
                posts = json.load(f)
                conn.execute(insert(posts_table), posts)

            # Insert Comments
            with open('data/comments.json', 'r', encoding='utf-8') as f:
                comments_table = metadata.tables['comment']
                comments = json.load(f)
                conn.execute(insert(comments_table), comments)

            # Insert Likes
            with open('data/likes.json', 'r', encoding='utf-8') as f:
                likes_table = metadata.tables['like']
                likes = json.load(f)
                conn.execute(insert(likes_table), likes)

            # Insert Friendships
            with open('data/friendships.json', 'r', encoding='utf-8') as f:
                friendships_table = metadata.tables['friendship']
                friendships = json.load(f)
                conn.execute(insert(friendships_table), friendships)

            print("Data successfully inserted into PostgreSQL.")
        except Exception as e:
            print(f"Error inserting data into PostgreSQL: {e}")

# Run the function
if __name__ == "__main__":
    insert_data_postgresql()
