from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine, MetaData, Table, func, text
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
from time import perf_counter
import json
import os
from datetime import datetime
import atexit

app = Flask(__name__)

AppUser = 1
############################################################################
############################################################################
############################################################################
############################################################################
############################################################################
# Database 1 | PostgreSQL

# SQLAlchemy-Verbindungsdetails
DATABASE_URI = "postgresql+psycopg2://postgres:super@localhost:5432/db1_postgreSQL"

# SQLAlchemy Engine erstellen
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
metadata = MetaData(bind=engine)
metadata.reflect()

# Tabelle definieren
user_table = Table("user", metadata, autoload_with=engine)

def warm_up_postgresql():
    """
    Führt eine minimale Abfrage aus, um PostgreSQL zu "wecken".
    """
    session = Session()
    try:
        session.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Fehler beim PostgreSQL-Warm-Up: {e}")
    finally:
        session.close()

def fetch_postgresql_friends(user_id):
    """
    Abfrage der Freunde eines Nutzers aus PostgreSQL.
    :param user_id: Die UserID des Nutzers, dessen Freunde abgefragt werden.
    :return: Liste der Freunde.
    """
    session = Session()
    try:
        # PostgreSQL Warm-Up durchführen
        warm_up_postgresql()

        friendship_table = metadata.tables['friendship']
        user_table = metadata.tables['user']
        start_time = perf_counter()  # High-precision timer
        # Abfrage der Freunde eines Nutzers
        query = session.execute(
            friendship_table.select().where(friendship_table.c.UserID1 == user_id)
        ).fetchall()

        # Hole die Details der Freunde aus der `user`-Tabelle
        friends = [
            dict(session.execute(user_table.select().where(user_table.c.UserID == row.UserID2)).fetchone())
            for row in query
        ]
        end_time = perf_counter()
        runtime = end_time - start_time  # Calculate runtime in seconds
        return {
            "friends": friends,
            "fetch_postgresql_friends_off_user_runtime": runtime
        }
    finally:
        session.close()


def fetch_postgreSQL_latest_posts_of_friends(user_id):
    """
    Holt die 50 neuesten Posts der Freunde eines Nutzers aus PostgreSQL,
    inklusive Anzahl der Likes, Anzahl der Kommentare und den letzten 5 Kommentaren mit Autoren.
    :param user_id: Die UserID des Nutzers, dessen Freunde abgefragt werden.
    :return: Liste der 50 neuesten Posts mit den zugehörigen Autoren.
    """
    session = Session()
    try:
        # PostgreSQL Warm-Up durchführen
        warm_up_postgresql()

        # Tabellen referenzieren
        friendship_table = metadata.tables['friendship']
        user_table = metadata.tables['user']
        post_table = metadata.tables['post']
        like_table = metadata.tables['like']
        comment_table = metadata.tables['comment']

        start_time = perf_counter()  # Startzeit messen

        # Direkte SQLAlchemy-Abfrage mit Subqueries
        # Likes-Subquery
        like_count_subquery = (
            session.query(
                like_table.c.PostID,
                func.count(like_table.c.LikeID).label("Likes")
            )
            .group_by(like_table.c.PostID)
            .subquery()
        )

        # Kommentare-Subquery
        comment_count_subquery = (
            session.query(
                comment_table.c.PostID,
                func.count(comment_table.c.CommentID).label("CommentCount"),
                func.array_agg(
                    func.json_build_object(
                        "CommentID", comment_table.c.CommentID,
                        "Content", comment_table.c.Content,
                        "CreatedAt", comment_table.c.CreatedAt,
                        "AuthorName", user_table.c.Name
                    )
                ).label("LatestComments")
            )
            .join(user_table, user_table.c.UserID == comment_table.c.UserID)
            .group_by(comment_table.c.PostID)
            .subquery()
        )

        # Hauptabfrage
        query = (
            session.query(
                post_table.c.PostID,
                post_table.c.Content,
                post_table.c.CreatedAt,
                user_table.c.UserID.label("FriendID"),
                user_table.c.Name.label("FriendName"),
                func.coalesce(like_count_subquery.c.Likes, 0).label("Likes"),
                func.coalesce(comment_count_subquery.c.CommentCount, 0).label("CommentCount"),
                func.coalesce(comment_count_subquery.c.LatestComments, []).label("LatestComments"),
            )
            .join(friendship_table, friendship_table.c.UserID2 == post_table.c.UserID)
            .join(user_table, user_table.c.UserID == post_table.c.UserID)
            .outerjoin(like_count_subquery, like_count_subquery.c.PostID == post_table.c.PostID)
            .outerjoin(comment_count_subquery, comment_count_subquery.c.PostID == post_table.c.PostID)
            .filter(friendship_table.c.UserID1 == user_id)
            .order_by(post_table.c.PostID.desc())
            .limit(50)
        ).all()

        end_time = perf_counter()  # Endzeit messen
        runtime = end_time - start_time

        # Ergebnisse strukturieren
        latest_posts = [
            {
                "posted_by_UserID": row.FriendID,
                "FriendName": row.FriendName,
                "PostID": row.PostID,
                "Content": row.Content,
                "CreatedAt": row.CreatedAt.strftime('%Y-%m-%d %H:%M:%S'),
                "Likes": row.Likes,
                "CommentCount": row.CommentCount,
                "LatestComments": row.LatestComments
            }
            for row in query
        ]

        return {
            "postgreSQL_latest_posts": latest_posts,
            "fetch_postgreSQL_latest_posts_runtime": runtime
        }
    finally:
        session.close()

def create_post_postgresql(user_id, content):
    """
    Erstellt einen neuen Post mit der nächsten PostID (höchste vorhandene + 1) in der PostgreSQL-Datenbank.
    
    :param user_id: Die ID des Nutzers, der den Post erstellt.
    :param content: Der Inhalt des Posts.
    :return: Ein Dictionary mit dem Status und der neuen PostID.
    """
    engine = create_engine(DATABASE_URI)
    
    try:
        # PostgreSQL Warm-Up durchführen
        warm_up_postgresql()

        with engine.connect() as connection:
            # Abfrage der höchsten aktuellen PostID
            query_get_max_post_id = 'SELECT COALESCE(MAX("PostID"), 0) AS MaxPostID FROM post'
            max_post_id = connection.execute(text(query_get_max_post_id)).scalar()
            new_post_id = max_post_id + 1
            
            start_time = perf_counter()  # Startzeit messen

            # Einfügen des neuen Posts
            query_create_post = """
            INSERT INTO post ("PostID", "UserID", "Content", "CreatedAt")
            VALUES (:PostID, :UserID, :Content, :CreatedAt)
            """
            connection.execute(
                text(query_create_post),
                {
                    "PostID": new_post_id,
                    "UserID": user_id,
                    "Content": content,
                    "CreatedAt": datetime.utcnow()
                }
            )

            end_time = perf_counter()  # Endzeit messen
            runtime = end_time - start_time
            
            return {
                "status": "success",
                "PostID": new_post_id,
                "message": f"Post {new_post_id} successfully created by user {user_id}.",
                "runtime": runtime
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "PostID": None
        }

def fetch_postgresql_own_posts(user_id):
    """
    Holt die 50 neuesten eigenen Posts eines Nutzers aus PostgreSQL,
    inklusive Anzahl der Likes, Anzahl der Kommentare und den letzten 5 Kommentaren mit Autoren.
    :param user_id: Die UserID des Nutzers, dessen Posts abgefragt werden.
    :return: Liste der 50 neuesten eigenen Posts mit zugehörigen Informationen.
    """
    session = Session()
    try:
        # PostgreSQL Warm-Up durchführen
        warm_up_postgresql()
        
        # Tabellen referenzieren
        user_table = metadata.tables['user']
        post_table = metadata.tables['post']
        like_table = metadata.tables['like']
        comment_table = metadata.tables['comment']

        start_time = perf_counter()  # Startzeit messen

        # Likes-Subquery
        like_count_subquery = (
            session.query(
                like_table.c.PostID,
                func.count(like_table.c.LikeID).label("Likes")
            )
            .group_by(like_table.c.PostID)
            .subquery()
        )

        # Kommentare-Subquery
        comment_count_subquery = (
            session.query(
                comment_table.c.PostID,
                func.count(comment_table.c.CommentID).label("CommentCount"),
                func.array_agg(
                    func.json_build_object(
                        "CommentID", comment_table.c.CommentID,
                        "Content", comment_table.c.Content,
                        "CreatedAt", comment_table.c.CreatedAt,
                        "AuthorName", user_table.c.Name
                    )
                ).label("LatestComments")
            )
            .join(user_table, user_table.c.UserID == comment_table.c.UserID)
            .group_by(comment_table.c.PostID)
            .subquery()
        )

        # Hauptabfrage
        query = (
            session.query(
                post_table.c.PostID,
                post_table.c.Content,
                post_table.c.CreatedAt,
                func.coalesce(like_count_subquery.c.Likes, 0).label("Likes"),
                func.coalesce(comment_count_subquery.c.CommentCount, 0).label("CommentCount"),
                func.coalesce(comment_count_subquery.c.LatestComments, []).label("LatestComments"),
            )
            .filter(post_table.c.UserID == user_id)  # Nur eigene Posts
            .outerjoin(like_count_subquery, like_count_subquery.c.PostID == post_table.c.PostID)
            .outerjoin(comment_count_subquery, comment_count_subquery.c.PostID == post_table.c.PostID)
            .order_by(post_table.c.PostID.desc())
            .limit(50)
        ).all()

        end_time = perf_counter()  # Endzeit messen
        runtime = end_time - start_time

        # Ergebnisse strukturieren
        own_posts = [
            {
                "PostID": row.PostID,
                "Content": row.Content,
                "CreatedAt": row.CreatedAt.strftime('%Y-%m-%d %H:%M:%S'),
                "Likes": row.Likes,
                "CommentCount": row.CommentCount,
                "LatestComments": row.LatestComments
            }
            for row in query
        ]

        return {
            "postgreSQL_own_posts": own_posts,
            "fetch_postgresql_own_posts_runtime": runtime
        }
    finally:
        session.close()

############################################################################
############################################################################
############################################################################
############################################################################
############################################################################
############################################################################
# Database 2 | neo4j

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "db2_neo4j"

# Erstellen einer globalen Driver-Instanz
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Schließen des Drivers beim Beenden des Programms
atexit.register(driver.close)

def fetch_neo4j_friends(user_id):
    """
    Abfrage der Freunde eines Nutzers aus Neo4j.
    :param user_id: Die UserID des Nutzers, dessen Freunde abgefragt werden.
    :return: Liste der Freunde.
    """
    try:
        with driver.session() as session:
            # Warm-Up durchführen
            session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            start_time = perf_counter()  # High-precision timer
            query = """
            MATCH (u:User {UserID: $UserID})-[:FRIEND]->(friend:User)
            RETURN friend.UserID AS UserID, friend.Name AS Name, friend.Email AS Email, friend.CreatedAt AS CreatedAt
            """
            result = session.run(query, {"UserID": user_id})
            end_time = perf_counter()
            runtime = end_time - start_time  # Calculate runtime in seconds
            # Konvertiere das Ergebnis in eine Liste von Dictionaries
            friends = [
                {
                    "UserID": record["UserID"],
                    "Name": record["Name"],
                    "Email": record["Email"],
                    "CreatedAt": str(record["CreatedAt"])  # Konvertiere datetime zu String
                }
                for record in result
            ]            
            return {
                "friends": friends,
                "fetch_neo4j_friends_off_user_runtime": runtime
            }
    except Exception as e:
        return {"error": str(e)}

def fetch_neo4j_latest_posts_of_friends(user_id):
    """
    Holt die 50 neuesten Posts der Freunde eines Nutzers aus Neo4j, inklusive Anzahl der Likes, Anzahl der Kommentare,
    und den letzten 50 Kommentaren jedes Posts (mit Name des Verfassers).
    """
    
    try:
        with driver.session() as session:
            # Warm-Up durchführen
            session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            start_time = perf_counter()

            query = """
            MATCH (u:User {UserID: $UserID})-[:FRIEND]->(friend:User)-[:CREATED]->(post:Post)
            OPTIONAL MATCH (post)<-[:LIKED]-(like:User)  // Likes zählen
            OPTIONAL MATCH (post)<-[:ON]-(comment:Comment)  // Kommentare abrufen
            OPTIONAL MATCH (comment)<-[:WROTE]-(commentAuthor:User)  // Verfasser des Kommentars abrufen
            WITH DISTINCT friend, post, like, comment, commentAuthor
            WITH friend, post, count(DISTINCT like) AS likeCount, count(DISTINCT comment) AS commentCount,
                 collect(DISTINCT {
                     CommentID: comment.CommentID, 
                     Content: comment.Content, 
                     CreatedAt: comment.CreatedAt, 
                     AuthorName: commentAuthor.Name
                 })[0..5] AS latestComments
            RETURN friend.UserID AS FriendID, friend.Name AS Name, post.PostID AS PostID,
                   post.Content AS Content, post.CreatedAt AS CreatedAt, likeCount, commentCount,
                   latestComments
            ORDER BY post.PostID DESC
            LIMIT 50
            """
            result = session.run(query, {"UserID": user_id})
            end_time = perf_counter()
            runtime = end_time - start_time

            # Ergebnisse strukturieren
            latest_posts = [
                {
                    "posted_by_UserID": record["FriendID"],
                    "FriendName": record["Name"],
                    "PostID": record["PostID"],
                    "Content": record["Content"],
                    "CreatedAt": str(record["CreatedAt"]),
                    "Likes": record["likeCount"],
                    "CommentCount": record["commentCount"],
                    "LatestComments": None if record["latestComments"] is None else [
                        {
                            "CommentID": comment["CommentID"],
                            "Content": comment["Content"],
                            "CreatedAt": str(comment["CreatedAt"]),
                            "AuthorName": comment["AuthorName"]
                        }
                        for comment in record["latestComments"]
                    ]
                }
                for record in result
            ]

            return {
                "neo4j_latest_posts": latest_posts,
                "fetch_neo4j_latest_posts_runtime": runtime
            }
    except Exception as e:
        return {"error": str(e)}

def create_post_neo4j(user_id, content):
    """
    Erstellt einen neuen Post mit der nächsten PostID (höchste vorhandene + 1) in der Neo4j-Datenbank.
    
    :param user_id: Die ID des Nutzers, der den Post erstellt.
    :param content: Der Inhalt des Posts.
    :return: Ein Dictionary mit dem Status und der neuen PostID.
    """
    
    try:
        with driver.session() as session:
            # Warm-Up durchführen
            session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            # Abfrage der höchsten aktuellen PostID
            start_time = perf_counter()
            query_get_max_post_id = """
            MATCH (p:Post)
            RETURN coalesce(MAX(p.PostID), 0) AS MaxPostID
            """
            result = session.run(query_get_max_post_id)
            max_post_id = result.single()["MaxPostID"]
            new_post_id = max_post_id + 1
            
            # Erstellen des neuen Posts und Verknüpfung mit dem Nutzer
            query_create_post = """
            MATCH (u:User {UserID: $UserID})
            CREATE (p:Post {PostID: $PostID, Content: $Content, CreatedAt: datetime()})
            MERGE (u)-[:CREATED]->(p)
            """
            session.run(query_create_post, {
                "UserID": user_id,
                "PostID": new_post_id,
                "Content": content
            })

            end_time = perf_counter()
            runtime = end_time - start_time
            return {
                "status": "success",
                "PostID": new_post_id,
                "message": f"Post {new_post_id} successfully created by user {user_id}.",
                "runtime": runtime
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "PostID": None
        }

def fetch_neo4j_own_posts(user_id):
    """
    Holt die 50 neuesten eigenen Posts eines Nutzers aus Neo4j, inklusive Anzahl der Likes, Anzahl der Kommentare,
    und den letzten 50 Kommentaren jedes Posts (mit Name des Verfassers).
    """
    try:
        with driver.session() as session:
            # Warm-Up durchführen
            session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            start_time = perf_counter()

            query = """
            MATCH (u:User {UserID: $UserID})-[:CREATED]->(post:Post)
            OPTIONAL MATCH (post)<-[:LIKED]-(like:User)  // Likes zählen
            OPTIONAL MATCH (post)<-[:ON]-(comment:Comment)  // Kommentare abrufen
            OPTIONAL MATCH (comment)<-[:WROTE]-(commentAuthor:User)  // Verfasser des Kommentars abrufen
            WITH DISTINCT post, like, comment, commentAuthor
            WITH post, count(DISTINCT like) AS likeCount, count(DISTINCT comment) AS commentCount,
                 collect(DISTINCT {
                     CommentID: comment.CommentID, 
                     Content: comment.Content, 
                     CreatedAt: comment.CreatedAt, 
                     AuthorName: commentAuthor.Name
                 })[0..5] AS latestComments
            RETURN post.PostID AS PostID, post.Content AS Content, post.CreatedAt AS CreatedAt,
                   likeCount, commentCount, latestComments
            ORDER BY post.PostID DESC
            LIMIT 50
            """
            
            result = session.run(query, {"UserID": user_id})
            end_time = perf_counter()
            runtime = end_time - start_time

            # Ergebnisse strukturieren
            own_posts = [
                {
                    "PostID": record["PostID"],
                    "Content": record["Content"],
                    "CreatedAt": str(record["CreatedAt"]),
                    "Likes": record["likeCount"],
                    "CommentCount": record["commentCount"],
                    "LatestComments": None if record["latestComments"] is None else [
                        {
                            "CommentID": comment["CommentID"],
                            "Content": comment["Content"],
                            "CreatedAt": str(comment["CreatedAt"]),
                            "AuthorName": comment["AuthorName"]
                        }
                        for comment in record["latestComments"]
                    ]
                }
                for record in result
            ]

            return {
                "neo4j_own_posts": own_posts,
                "fetch_neo4j_own_posts_runtime": runtime
            }
    except Exception as e:
        return {"error": str(e)}

############################################################################
############################################################################
############################################################################
############################################################################
############################################################################

def load_existing_data():
    """
    Lädt bestehende Messdaten aus der Datei oder gibt eine leere Liste zurück.
    """
    file_path = "runtimes.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

# Combine Both Databases in a Single Route
@app.route('/combined_users', methods=['GET'])
def compare_performance():

    #postgreSQLfriends = fetch_postgresql_friends(AppUser)
    #neo4jFriends = fetch_neo4j_friends(AppUser)
    postgreSQL_postByFriends = fetch_postgreSQL_latest_posts_of_friends(1413)
    neo4j_postByFriends = fetch_neo4j_latest_posts_of_friends(1413)
    #abc = fetch_neo4j_own_posts(AppUser)
    #ccc = fetch_postgresql_own_posts(AppUser)

    return jsonify(postgreSQL_postByFriends, neo4j_postByFriends)

############################################################################
############################################################################
############################################################################
############################################################################
############################################################################

@app.route('/', methods=["GET", "POST"])
def index():
    global AppUser  # Zugriff auf die globale Variable
    
    if request.method == "POST":
        # Zahl aus dem Formular abrufen (oder Standardwert 1 verwenden)
        number = request.form.get("number", "1")
        
        # Überprüfen, ob die Eingabe eine Zahl ist
        if number.isdigit():
            AppUser = int(number)  # Globale Variable aktualisieren
        else:
            return render_template("index.html", result="error")
    return render_template('dashboard.html', result=AppUser)

#own latest posts
@app.route('/OWNlatestPost')
def get_OWNlatestPost():
    postgreSQL_own_posts = fetch_postgresql_own_posts(AppUser)
    neo4j_own_posts = fetch_neo4j_own_posts(AppUser)

    #########################################
    #########################################
    #########################################
    # Extrahiere Runtimes
    postgreSQL_own_posts_runtime = postgreSQL_own_posts.get("fetch_postgresql_own_posts_runtime", 0)
    neo4j_own_posts_runtime = neo4j_own_posts.get("fetch_neo4j_own_posts_runtime", 0)
    # Formatiere die Runtimes im gewünschten JSON-Format
    runtime_data = {
        "messung": f"latest own posts",
        "messwerte": [round(postgreSQL_own_posts_runtime, 3), round(neo4j_own_posts_runtime, 3)]
    }
    # JSON-Datei-Pfad
    file_path = "createDatabase/data/runtimes.json"
    # Lade vorhandene Daten oder initialisiere leere Liste
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = []
    # Neue Messung hinzufügen
    data.append(runtime_data)
    # Aktualisierte Daten in die Datei schreiben
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    #########################################
    #########################################
    #########################################
    data = neo4j_own_posts
    # Rückgabe im passenden Format
    return jsonify(data)

#latestposts
@app.route('/latestPostofFriends')
def get_latestPostofFriends():
    postgreSQL_postByFriends = fetch_postgreSQL_latest_posts_of_friends(AppUser)
    neo4j_postByFriends = fetch_neo4j_latest_posts_of_friends(AppUser)

    #########################################
    #########################################
    #########################################
    # Extrahiere Runtimes
    postgres_runtime = postgreSQL_postByFriends.get("fetch_postgreSQL_latest_posts_runtime", 0)
    neo4j_runtime = neo4j_postByFriends.get("fetch_neo4j_latest_posts_runtime", 0)
    # Formatiere die Runtimes im gewünschten JSON-Format
    runtime_data = {
        "messung": f"latest 50 posts",
        "messwerte": [round(postgres_runtime, 3), round(neo4j_runtime, 3)]
    }
    # JSON-Datei-Pfad
    file_path = "createDatabase/data/runtimes.json"
    # Lade vorhandene Daten oder initialisiere leere Liste
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = []
    # Neue Messung hinzufügen
    data.append(runtime_data)
    # Aktualisierte Daten in die Datei schreiben
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    #########################################
    #########################################
    #########################################
    data = neo4j_postByFriends
    # Rückgabe im passenden Format
    return jsonify(data)

#diagrammdata
@app.route('/data')
def get_data():
    file_path = "createDatabase/data/runtimes.json"
    
    # Sicherstellen, dass die Datei existiert
    if not os.path.exists(file_path):
        return jsonify({"ereignisse": []})

    with open(file_path, "r") as f:
        data = json.load(f)

    # Rückgabe im passenden Format
    return jsonify({"ereignisse": data})

from flask import request, jsonify

#createPosts
@app.route('/createPosts', methods=['POST'])
def createPosts():
    try:
        # Hole den JSON-Inhalt
        data = request.get_json()
        content = data.get('content')
        if not content:
            return jsonify({"status": "error", "message": "Content is required"}), 400

        # Rufe die Funktionen für PostgreSQL und Neo4j auf
        result = create_post_postgresql(user_id=AppUser, content=content)
        result1 = create_post_neo4j(user_id=AppUser, content=content)
        #########################################
        #########################################
        #########################################
        # Extrahiere Runtimes
        result_postgreSQL_runtime = result.get("runtime", 0)
        result_neo4j_runtime = result1.get("runtime", 0)
        # Formatiere die Runtimes im gewünschten JSON-Format
        runtime_data = {
            "messung": f"createPost",
            "messwerte": [round(result_postgreSQL_runtime, 3), round(result_neo4j_runtime, 3)]
        }
        # JSON-Datei-Pfad
        file_path = "createDatabase/data/runtimes.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
        else:
            data = []
        # Neue Messung hinzufügen
        data.append(runtime_data)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        #########################################
        #########################################
        #########################################
        return jsonify({
            "status": "success",
            "postgreSQLresult": result,
            "neo4j": result1,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/pdf')
def pdf():
    return render_template('pdf.html')

############################################################################
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8080)
