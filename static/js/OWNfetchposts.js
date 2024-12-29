document.addEventListener('DOMContentLoaded', function () {
    const postsContainer = document.getElementById('OWNpostsContainer');

    async function fetchOWNPosts() {
        try {
            // Abrufen der Daten von der API
            const response = await fetch('/OWNlatestPost');
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();

            console.log('Fetched Data:', data); // Debugging: Prüfen der Daten

            // Container leeren
            postsContainer.innerHTML = '';

            // Prüfen, ob es eigene Posts gibt
            if (!data.neo4j_own_posts || data.neo4j_own_posts.length === 0) {
                postsContainer.innerHTML = '<p>No posts available. Please try again later.</p>';
                return;
            }

            // Rendern der eigenen Posts
            data.neo4j_own_posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.classList.add('postcontent');

                // Verarbeite Kommentare
                const commentsHtml = post.LatestComments && post.LatestComments.length > 0
                    ? `
                        <div class="comments">
                            <ul>
                                ${post.LatestComments.filter(comment => comment.CommentID !== null).map(comment => `
                                    <li>
                                        <a><strong>${comment.AuthorName || 'Unknown'}</strong> wrote:</a>
                                        <br>
                                        <a>${comment.Content || 'No content available'}</a>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `
                    : `<a class="comments">No comments yet.</a>`;

                // Füge den Post in den Container ein
                postElement.innerHTML = `
                    <a>-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-&nbsp;-</a>
                    <br>
                    <a style="color: #403D39">Likes:</a>
                    <a class="postLiked">${post.Likes}</a>
                    <a style="color: #403D39">Content:</a>
                    <p>${post.Content || 'No content available'}</p>
                    <a style="color: #403D39">Comments (${post.CommentCount}):</a>
                    ${commentsHtml}
                `;
                postsContainer.appendChild(postElement);
            });
        } catch (error) {
            console.error('Error fetching posts:', error);
            postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
        }
    }

    // Event Listener für Klick auf .call_newpostScreen
    document.querySelector('.call_newpostScreen').addEventListener('click', function (event) {
        event.preventDefault(); // Verhindert das Neuladen der Seite
        fetchOWNPosts(); // Posts laden
    });
});
