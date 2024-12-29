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
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Friendship) REQUIRE f.FriendshipID IS UNIQUE")

    def insert_friendship(self, friendship):
        with self.driver.session() as session:
            session.run("""
                MATCH (u1:User {UserID: $UserID1}), (u2:User {UserID: $UserID2})
                MERGE (u1)-[:FRIEND {CreatedAt: datetime($CreatedAt)}]->(u2)
            """, friendship)

# Freundschaften generieren und direkt in die Datenbanken einfügen
def generate_and_insert_friendships(num_friendships, repetitions, user_id_range):
    metadata.reflect(bind=engine)
    friendships_table = metadata.tables['friendship']
    
    loader = Neo4jDataLoader()
    loader.ensure_constraints()

    friendship_counter = 1
    total_friendships_inserted = 0
    existing_pairs = set()

    with engine.connect() as conn:
        for _ in range(repetitions):
            batch_count = 0
            for i in range(num_friendships):
                while True:
                    user_id1 = random.randint(user_id_range[0], user_id_range[1])
                    user_id2 = random.randint(user_id_range[0], user_id_range[1])
                    if user_id1 != user_id2 and (user_id1, user_id2) not in existing_pairs and (user_id2, user_id1) not in existing_pairs:
                        break

                friendship_id = friendship_counter
                friendship = {
                    "FriendshipID": friendship_id,
                    "UserID1": user_id1,
                    "UserID2": user_id2,
                    "CreatedAt": datetime.utcnow().isoformat()
                }

                # In PostgreSQL einfügen
                result = conn.execute(insert(friendships_table), [friendship])
                batch_count += result.rowcount

                # In Neo4j einfügen
                loader.insert_friendship(friendship)
                friendship_counter += 1
                existing_pairs.add((user_id1, user_id2))

            print(f"Batch completed: {batch_count} friendships added to PostgreSQL and Neo4j.")
            total_friendships_inserted += batch_count

    loader.close()
    print(f"Total friendships created: {total_friendships_inserted}")

# Ausführung des Skripts mit flexiblen Parametern
if __name__ == "__main__":
    NUM_FRIENDSHIPS_PER_BATCH = 100000  # Anzahl der Freundschaften pro Schleife
    REPETITIONS = 10  # Anzahl der Wiederholungen
    USER_ID_RANGE = (1, 100000)  # Benutzer-ID Bereich
    generate_and_insert_friendships(NUM_FRIENDSHIPS_PER_BATCH, REPETITIONS, USER_ID_RANGE)