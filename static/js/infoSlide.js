document.addEventListener('DOMContentLoaded', function () {
    // Referenzen zu den DIVs
    const relationalDatabaseDiv = document.querySelector('.RelationalDatabase');
    const graphDatabaseDiv = document.querySelector('.GraphDatabase');

    // Funktion für die HomeScreen-Anzeige
    function showHomeScreen() {
        // Textänderungen
        relationalDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <h3>PostgreSQL</h3>
                <p>The function <code>fetch_postgreSQL_latest_posts_of_friends(user_id)</code> retrieves the latest five posts made by a user's friends from a PostgreSQL database.</p>
                <ul>
                    <li>
                    <strong>Input:</strong> takes <code>user_id</code>, representing the user whose friends posts will be fetched
                    </li>
                    <li>
                    <strong>Database Query:</strong>
                    <ul>
                        <li>references several tables: <code>friendship</code>, <code>user</code>, <code>post</code>, <code>like</code>, and <code>comment</code></li>
                        <li>Subqueries are used to count likes and gather detailed comment data (content, creation date, author's name)</li>
                        <li>main query joins subqueries with <code>post</code> table to fetch the necessary information, filtered by user's friends, and orders results for recent posts.</li>
                    </ul>
                    </li>
                    <li>
                    <strong>Output:</strong>
                    <ul>
                        <li>returns a structured list of posts, including:</li>
                        <ul>
                        <li>friends user ID and name, Post ID, content, creation date, like and comment count, latest comments with their authors</li>
                        </ul>
                    </ul>
                    </li>
                </ul>
                </div>
        `;
        graphDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <h3>Neo4j</h3>
                <p>The function <code>fetch_neo4j_latest_posts_of_friends(user_id)</code> retrieves the latest five posts made by a user's friends from a Neo4j database.</p>
                <ul>
                    <li>
                        <strong>Input:</strong> takes <code>user_id</code>, representing the user whose friends' posts will be fetched
                    </li>
                    <li>
                        <strong>Database Query:</strong>
                        <ul>
                            <li>matches the user and their friends through the <code>FRIEND</code> relationship</li>
                            <li>retrieves posts created by friends and counts likes and comments using <code>LIKED</code> and <code>ON</code> relationships</li>
                            <li>fetches up to 5 latest comments per post, including content, creation date, and author name</li>
                            <li>orders posts by descending <code>PostID</code> and limits results to 50</li>
                        </ul>
                    </li>
                    <li>
                        <strong>Output:</strong>
                        <ul>
                            <li>returns a structured list of posts, including:</li>
                            <ul>
                                <li>friend's user ID and name, Post ID, content, creation date, like and comment count, and latest comments with their authors</li>
                            </ul>
                        </ul>
                    </li>
                </ul>
            </div>
        `;
    }

    // Funktion für die NewPostScreen-Anzeige
    function showNewPostScreen() {
        relationalDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <h3>PostgreSQL</h3>
                <p>The function <code>create_post_postgresql(user_id, content)</code> creates a new post.</p>
                <ul>
                    <li>
                        <strong>Database Query:</strong>
                        <ul>
                            <li>fetches current highest <code>PostID</code> and increments it, inserts new post with provided user ID, content, and current timestamp</li>
                        </ul>
                    </li>
                    <li>
                        <strong>Output:</strong>
                        <ul>
                            <li>returns status, the new <code>PostID</code> and a success or error message</li>
                        </ul>
                    </li>
                </ul>
            </div>

            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <p>The function <code>fetch_postgresql_own_posts(user_id)</code> retrieves the users latest 50 posts.</p>
                <ul>
                    <li>
                        <strong>Database Query:</strong>
                        <ul>
                            <li>references tables: <code>user</code>, <code>post</code>, <code>like</code> and <code>comment</code>, uses subqueries to count likes,
                            retrieves comment data, fetches and orders the own, latest 50 posts by <code>PostID</code></li>
                        </ul>
                    </li>
                    <li>
                        <strong>Output:</strong>
                        <ul>
                            <li>returns a structured list of posts, including <code>PostID</code>, content, creation date, like and comment count, and latest comments with their authors</li>
                        </ul>
                    </li>
                </ul>
            </div>
        `;
        graphDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <h3>Neo4j</h3>
                <p>The function <code>create_post_neo4j(user_id, content)</code> creates a new post.</p>
                <ul>
                    <li>
                        <strong>Database Query:</strong>
                        <ul>
                            <li>fetches current highest <code>PostID</code> and increments it, creates new post with provided user ID, content, and current timestamp, and links it to the user</li>
                        </ul>
                    </li>
                    <li>
                        <strong>Output:</strong>
                        <ul>
                            <li>returns status, the new <code>PostID</code>, and a success or error message</li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div style="width: 96%; margin-left: 15px; margin-right: 15px; font-size: 15px">
                <p>The function <code>fetch_neo4j_own_posts(user_id)</code> retrieves the user's latest 50 posts.</p>
                <ul>
                    <li>
                        <strong>Database Query:</strong>
                        <ul>
                            <li>fetches posts created by the user, counts likes and comments, retrieves comment details, and orders the latest 50 posts by <code>PostID</code></li>
                        </ul>
                    </li>
                    <li>
                        <strong>Output:</strong>
                        <ul>
                            <li>returns a structured list of posts, including <code>PostID</code>, content, creation date, like and comment count, and latest comments with their authors</li>
                        </ul>
                    </li>
                </ul>
            </div>
        `;
    }

    // Funktion für die NewPostScreen-Anzeige
    function addFriendsScreen() {
        relationalDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px;">
                <h3>PostgreSQL</h3>
                coming soon...
            </div>
        `;
        graphDatabaseDiv.innerHTML = `
            <div style="width: 96%; margin-left: 15px; margin-right: 15px;">
                <h3>Neo4j</h3>
                coming soon...
            </div>
        `;
    }

    // Standardanzeige: HomeScreen wird direkt bei Seitenladen angezeigt
    showHomeScreen();

    // Event Listener für `call_homeScreen` (erneutes Anzeigen der HomeScreen-Inhalte)
    document.querySelector('.call_homeScreen').addEventListener('click', function () {
        showHomeScreen();
    });

    // Event Listener für `call_newpostScreen` (Anzeigen der NewPostScreen-Inhalte)
    document.querySelector('.call_newpostScreen').addEventListener('click', function () {
        showNewPostScreen();
    });

    // Event Listener für `call_newpostScreen` (Anzeigen der NewPostScreen-Inhalte)
    document.querySelector('.call_adduserScreen').addEventListener('click', function () {
        addFriendsScreen();
    });
});
