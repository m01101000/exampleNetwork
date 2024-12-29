from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import insert
from datetime import datetime
from neo4j import GraphDatabase
import random

# PostgreSQL connection
DATABASE_URI = 'postgresql://postgres:super@localhost:5432/db1_postgreSQL'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

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
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.PostID IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Like) REQUIRE l.LikeID IS UNIQUE")

    def insert_post(self, post):
        with self.driver.session() as session:
            session.run("""
                MERGE (p:Post {PostID: $PostID})
                SET p.UserID = $UserID, p.Content = $Content, p.CreatedAt = datetime($CreatedAt)
            """, post)
            session.run("""
                MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID})
                MERGE (u)-[:CREATED]->(p)
            """, post)

    def insert_like(self, like):
        with self.driver.session() as session:
            session.run("""
                MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID})
                MERGE (u)-[:LIKED {CreatedAt: datetime($CreatedAt)}]->(p)
            """, like)

# Like-Daten generieren und direkt in die Datenbanken einfügen
def generate_and_insert_likes(num_likes, repetitions, user_id_range, post_id_range):
    metadata.reflect(bind=engine)
    likes_table = metadata.tables['like']
    
    loader = Neo4jDataLoader()
    loader.ensure_constraints()

    like_counter = 1
    total_likes_inserted = 0

    with engine.connect() as conn:
        for _ in range(repetitions):
            batch_count = 0
            for i in range(num_likes):
                like_id = like_counter
                user_id = random.randint(user_id_range[0], user_id_range[1])
                post_id = random.randint(post_id_range[0], post_id_range[1])
                like = {
                    "LikeID": like_id,
                    "PostID": post_id,
                    "UserID": user_id,
                    "CreatedAt": datetime.utcnow().isoformat()
                }

                # In PostgreSQL einfügen
                result = conn.execute(insert(likes_table), [like])
                batch_count += result.rowcount

                # In Neo4j einfügen
                loader.insert_like(like)
                like_counter += 1

            print(f"Batch completed: {batch_count} likes added to PostgreSQL and Neo4j.")
            total_likes_inserted += batch_count

    loader.close()
    print(f"Total likes created: {total_likes_inserted}")

# Ausführung des Skripts mit flexiblen Parametern
if __name__ == "__main__":
    NUM_LIKES_PER_BATCH = 100000  # Anzahl der Likes pro Schleife
    REPETITIONS = 25  # Anzahl der Wiederholungen
    USER_ID_RANGE = (1, 100000)  # Benutzer-ID Bereich
    POST_ID_RANGE = (1, 100000)  # Post-ID Bereich
    generate_and_insert_likes(NUM_LIKES_PER_BATCH, REPETITIONS, USER_ID_RANGE, POST_ID_RANGE)
