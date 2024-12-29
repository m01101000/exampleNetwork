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

# Post-Daten generieren und direkt in die Datenbanken einfügen
def generate_and_insert_posts(num_posts, repetitions, user_id_range):
    metadata.reflect(bind=engine)
    posts_table = metadata.tables['post']
    
    loader = Neo4jDataLoader()
    loader.ensure_constraints()

    post_counter = 1
    total_posts_inserted = 0

    lorem_texts = ["example a", "example b", "example c"]

    with engine.connect() as conn:
        for _ in range(repetitions):
            batch_count = 0
            for i in range(num_posts):
                post_id = post_counter
                user_id = random.randint(user_id_range[0], user_id_range[1])
                post = {
                    "PostID": post_id,
                    "UserID": user_id,
                    "Content": random.choice(lorem_texts),
                    "CreatedAt": datetime.utcnow().isoformat()
                }

                # In PostgreSQL einfügen
                result = conn.execute(insert(posts_table), [post])
                batch_count += result.rowcount

                # In Neo4j einfügen
                loader.insert_post(post)
                post_counter += 1

            print(f"Batch completed: {batch_count} posts added to PostgreSQL and Neo4j.")
            total_posts_inserted += batch_count

    loader.close()
    print(f"Total posts created: {total_posts_inserted}")

# Ausführung des Skripts mit flexiblen Parametern
if __name__ == "__main__":
    NUM_POSTS_PER_BATCH = 10000  # Anzahl der Posts pro Schleife
    REPETITIONS = 100  # Anzahl der Wiederholungen
    USER_ID_RANGE = (1, 100000)  # Benutzer-ID Bereich
    generate_and_insert_posts(NUM_POSTS_PER_BATCH, REPETITIONS, USER_ID_RANGE)
