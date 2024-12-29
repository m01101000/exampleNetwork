from neo4j import GraphDatabase
import json

# Neo4j-Verbindung
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "db2_neo4j"

class Neo4jDataLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def ensure_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.UserID IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.PostID IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Comment) REQUIRE c.CommentID IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Like) REQUIRE l.LikeID IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Friendship) REQUIRE f.FriendshipID IS UNIQUE")

    def load_users(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as f:
                users = json.load(f)
                count = 0
                for user in users:
                    session.run("""
                        MERGE (u:User {UserID: $UserID})
                        SET u.Name = $Name, u.Email = $Email, u.CreatedAt = datetime($CreatedAt)
                    """, user)
                    count += 1
                print(f"{count} users added or updated.")

    def load_posts(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
                count = 0
                for post in posts:
                    session.run("""
                        MERGE (p:Post {PostID: $PostID})
                        SET p.UserID = $UserID, p.Content = $Content, p.CreatedAt = datetime($CreatedAt)
                    """, post)
                    session.run("""
                        MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID})
                        MERGE (u)-[:CREATED]->(p)
                    """, post)
                    count += 1
                print(f"{count} posts added or updated.")

    def load_comments(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as f:
                comments = json.load(f)
                count = 0
                for comment in comments:
                    session.run("""
                        MERGE (c:Comment {CommentID: $CommentID})
                        SET c.Content = $Content, c.CreatedAt = datetime($CreatedAt)
                    """, comment)
                    session.run("""
                        MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID}), (c:Comment {CommentID: $CommentID})
                        MERGE (u)-[:WROTE]->(c)
                        MERGE (c)-[:ON]->(p)
                    """, comment)
                    count += 1
                print(f"{count} comments added or updated.")

    def load_likes(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as f:
                likes = json.load(f)
                count = 0
                for like in likes:
                    session.run("""
                        MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID})
                        MERGE (u)-[:LIKED {CreatedAt: datetime($CreatedAt)}]->(p)
                    """, like)
                    count += 1
                print(f"{count} likes added.")

    def load_friendships(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as f:
                friendships = json.load(f)
                count = 0
                for friendship in friendships:
                    session.run("""
                        MATCH (u1:User {UserID: $UserID1}), (u2:User {UserID: $UserID2})
                        MERGE (u1)-[:FRIEND {CreatedAt: datetime($CreatedAt)}]->(u2)
                    """, friendship)
                    count += 1
                print(f"{count} friendships added.")

    def load_all_data(self):
        print("Ensuring constraints...")
        self.ensure_constraints()
        print("Loading users...")
        self.load_users('data/users.json')
        print("Loading posts...")
        self.load_posts('data/posts.json')
        print("Loading comments...")
        self.load_comments('data/comments.json')
        print("Loading likes...")
        self.load_likes('data/likes.json')
        print("Loading friendships...")
        self.load_friendships('data/friendships.json')
        print("All data successfully loaded into Neo4j.")

if __name__ == "__main__":
    loader = Neo4jDataLoader()
    try:
        loader.load_all_data()
    finally:
        loader.close()
