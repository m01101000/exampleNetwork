// Funktion zum Ausblenden aller Panels
function hideAllPanels() {
    document.querySelector('.homeScreen').style.display = 'none';
    document.querySelector('.newpostScreen').style.display = 'none';
    document.querySelector('.adduserScreen').style.display = 'none';
}

// Funktion zum Anzeigen des ausgewählten Panels
function showPanel(targetClass) {
    hideAllPanels(); // Zuerst alle ausblenden
    document.querySelector(`.${targetClass}`).style.display = 'block'; // Nur das gewählte anzeigen
}

// Event Listener für das Home-Menü
document.querySelector('.call_homeScreen').addEventListener('click', function() {
    showPanel('homeScreen'); // Zeigt nur .homeScreen an
});

// Event Listener für das Newpost-Menü
document.querySelector('.call_newpostScreen').addEventListener('click', function() {
    showPanel('newpostScreen'); // Zeigt nur .newpostScreen an
});

// Event Listener für das Adduser-Menü
document.querySelector('.call_adduserScreen').addEventListener('click', function() {
    showPanel('adduserScreen'); // Zeigt nur .adduserScreen an
});