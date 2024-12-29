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
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Comment) REQUIRE c.CommentID IS UNIQUE")

    def insert_comment(self, comment):
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Comment {CommentID: $CommentID})
                SET c.Content = $Content, c.CreatedAt = datetime($CreatedAt)
            """, comment)
            session.run("""
                MATCH (u:User {UserID: $UserID}), (p:Post {PostID: $PostID}), (c:Comment {CommentID: $CommentID})
                MERGE (u)-[:WROTE]->(c)
                MERGE (c)-[:ON]->(p)
            """, comment)

# Kommentare generieren und direkt in die Datenbanken einfügen
def generate_and_insert_comments(num_comments, repetitions, user_id_range, post_id_range):
    metadata.reflect(bind=engine)
    comments_table = metadata.tables['comment']
    
    loader = Neo4jDataLoader()
    loader.ensure_constraints()

    comment_counter = 1
    total_comments_inserted = 0
    lorem_texts = [
        "Ut enim ad minim veniam, quis.",
        "Duis aute irure dolor.",
        "Excepteur sint occaecat cupidatat non proident."
    ]

    with engine.connect() as conn:
        for _ in range(repetitions):
            batch_count = 0
            for i in range(num_comments):
                comment_id = comment_counter
                user_id = random.randint(user_id_range[0], user_id_range[1])
                post_id = random.randint(post_id_range[0], post_id_range[1])
                comment = {
                    "CommentID": comment_id,
                    "UserID": user_id,
                    "PostID": post_id,
                    "Content": random.choice(lorem_texts),
                    "CreatedAt": datetime.utcnow().isoformat()
                }

                # In PostgreSQL einfügen
                result = conn.execute(insert(comments_table), [comment])
                batch_count += result.rowcount

                # In Neo4j einfügen
                loader.insert_comment(comment)
                comment_counter += 1

            print(f"Batch completed: {batch_count} comments added to PostgreSQL and Neo4j.")
            total_comments_inserted += batch_count

    loader.close()
    print(f"Total comments created: {total_comments_inserted}")

# Ausführung des Skripts mit flexiblen Parametern
if __name__ == "__main__":
    NUM_COMMENTS_PER_BATCH = 50000  # Anzahl der Kommentare pro Schleife
    REPETITIONS = 10  # Anzahl der Wiederholungen
    USER_ID_RANGE = (1, 100000)  # Benutzer-ID Bereich
    POST_ID_RANGE = (1, 100000)  # Post-ID Bereich
    generate_and_insert_comments(NUM_COMMENTS_PER_BATCH, REPETITIONS, USER_ID_RANGE, POST_ID_RANGE)
