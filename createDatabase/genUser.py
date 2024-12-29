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
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.UserID IS UNIQUE")

    def insert_user(self, user):
        with self.driver.session() as session:
            session.run("""
                MERGE (u:User {UserID: $UserID})
                SET u.Name = $Name, u.Email = $Email, u.CreatedAt = datetime($CreatedAt)
            """, user)

# Benutzer-Daten generieren und direkt in die Datenbanken einfügen
def generate_and_insert_users(num_users, repetitions):
    metadata.reflect(bind=engine)
    users_table = metadata.tables['user']
    
    loader = Neo4jDataLoader()
    loader.ensure_constraints()

    user_counter = 1
    total_users_inserted = 0

    with engine.connect() as conn:
        for _ in range(repetitions):
            batch_count = 0
            for i in range(num_users):
                user_id = user_counter
                user = {
                    "UserID": user_id,
                    "Name": f"Nutzer{str(user_id).zfill(8)}",
                    "Email": f"{str(user_id).zfill(8)}@example.com",
                    "CreatedAt": datetime.utcnow().isoformat()
                }

                # In PostgreSQL einfügen
                result = conn.execute(insert(users_table), [user])
                batch_count += result.rowcount

                # In Neo4j einfügen
                loader.insert_user(user)
                user_counter += 1

            print(f"Batch completed: {batch_count} users added to PostgreSQL and Neo4j.")
            total_users_inserted += batch_count

    loader.close()
    print(f"Total users created: {total_users_inserted}")

# Ausführung des Skripts mit flexiblen Parametern
if __name__ == "__main__":
    NUM_USERS_PER_BATCH = 10000  # Anzahl der Benutzer pro Schleife
    REPETITIONS = 10  # Anzahl der Wiederholungen
    generate_and_insert_users(NUM_USERS_PER_BATCH, REPETITIONS)
