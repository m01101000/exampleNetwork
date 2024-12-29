document.addEventListener('DOMContentLoaded', async function () {
    const postsContainer = document.getElementById('postsContainer');

    async function fetchPosts() {
        try {
            // Abrufen der Daten von der API
            const response = await fetch('/latestPostofFriends');
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            // Container leeren, bevor neue Posts hinzugefügt werden
            postsContainer.innerHTML = '';

            // Prüfen, ob es Neo4j-Posts gibt
            if (!data.neo4j_latest_posts || data.neo4j_latest_posts.length === 0) {
                postsContainer.innerHTML = '<p>No posts available. Please try again later.</p>';
                return;
            }

            // Rendern der Neo4j-Posts
            data.neo4j_latest_posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.classList.add('postcontent');

                postElement.innerHTML = `
                    <a>-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-</a>
                    <br>
                    <a>by</a>
                    <a class="postedby">${post.FriendName}</a>
                    <a>|</a>
                    <a class="postLiked"><img class="likeimg" src="/static/images/like.png" alt="like">&nbsp;${post.Likes}</a>
                    <br>
                    <a>-</a>
                    <br>
                    <a>${post.Content}</a>
                    <br>
                    <a>-</a>
                    <br>
                    <a class="action"><img class="commentimg" src="/static/images/comment.png" alt="comment"></a>
                    <a class="comments">${post.CommentCount}</a>
                    <br>
                    ${
                        post.CommentCount > 0
                            ? `
                                <div class="comments">
                                    <a>Comments:</a>
                                    <ul>
                                        ${post.LatestComments.map(comment => `
                                            <li>
                                                <a><strong>${comment.AuthorName}</strong> wrote:</a>
                                                <br>
                                                <a>${comment.Content}</a>
                                                <br>
                                            </li>
                                        `).join('')}
                                    </ul>
                                </div>
                            `
                            : `<a class="comments">No comments yet.</a>`
                    }
                `;
                postsContainer.appendChild(postElement);
            });
        } catch (error) {
            console.error('Error fetching latest posts:', error);
            postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
        }
    }

    // Abrufen und Rendern der Posts
    await fetchPosts();

    // Event Listener für Home-Screen hinzufügen
    document.querySelector('.call_homeScreen').addEventListener('click', function () {
        fetchPosts(); // Posts erneut laden
    });
});
