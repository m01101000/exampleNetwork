document.getElementById("submitPost").addEventListener("click", async function (e) {
    e.preventDefault(); // Verhindert das Standardverhalten des Buttons

    const postContent = document.getElementById("postContent");
    const content = postContent.value.trim();

    // Entferne alte Klassen
    postContent.classList.remove("success", "error");

    if (!content) {
        // Fehler: Inhalt fehlt
        postContent.classList.add("error");
        setTimeout(() => postContent.classList.remove("error"), 2000); // Entferne Fehlerklasse
        return;
    }

    try {
        // Button deaktivieren, während der Post verarbeitet wird
        const button = document.getElementById("submitPost");
        button.disabled = true;

        // Sende den Inhalt mit einem POST-Request an den Server
        const response = await fetch("/createPosts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                content: content
            })
        });

        const result = await response.json();

        if (result.status === "success") {
            // Erfolg: Grüne Umrandung, Textfeld leeren und Home-Screen anzeigen
            postContent.classList.add("success");
            postContent.value = ""; // Textfeld zurücksetzen
            setTimeout(() => postContent.classList.remove("success"), 300);

            // Nach 2 Sekunden Home-Screen anzeigen
            setTimeout(() => {
                document.querySelector('.call_newpostScreen').click();
            }, 200);
        } else {
            // Fehler: Rote Umrandung
            postContent.classList.add("error");
            setTimeout(() => postContent.classList.remove("error"), 500); // Entferne Fehlerklasse
        }
    } catch (error) {
        console.error("Error:", error);
        postContent.classList.add("error");
        setTimeout(() => postContent.classList.remove("error"), 500); // Entferne Fehlerklasse
    } finally {
        // Button wieder aktivieren
        document.getElementById("submitPost").disabled = false;
    }
});
