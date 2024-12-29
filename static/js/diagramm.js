
const ctx = document.getElementById('myChart').getContext('2d');
ctx.canvas.width = 1250;
ctx.canvas.height = 310;
let chart;

async function fetchData() {
    try {
        const response = await fetch('/data');
        const jsonData = await response.json();

        // Extrahiere die Messungen und Werte
        const labels = jsonData.ereignisse.map(event => event.messung);
        const dataset1 = jsonData.ereignisse.map(event => event.messwerte[0]);
        const dataset2 = jsonData.ereignisse.map(event => event.messwerte[1]);
        
        return { labels, dataset1, dataset2 };
    } catch (error) {
        console.error('Fehler beim Abrufen der Daten:', error);
    }
}

function getMaxValue(data) {
    // Ermittelt den höchsten Wert über alle Datensätze
    const allValues = [...data.dataset1, ...data.dataset2];
    return Math.max(...allValues);
}

// Verzögerungsfunktion
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function createChart() {
    // 2 Sekunden Verzögerung vor dem Abrufen der Daten
    await delay(4000);

    const data = await fetchData();
    if (!data) return;

    // Ermittelt den höchsten Wert in den Daten für die Y-Achsen-Skalierung
    const maxValue = getMaxValue(data);

    // Falls das Diagramm bereits existiert, zerstöre es
    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'PostgreSQL',
                    data: data.dataset1,
                    backgroundColor: 'rgba(255, 252, 242, 1)',
                    borderColor: 'rgba(255, 252, 242, 1)',
                    borderWidth: 4
                },
                {
                    label: 'Neo4j',
                    data: data.dataset2,
                    backgroundColor: 'rgba(235, 94, 40, 1)',
                    borderColor: 'rgba(235, 94, 40, 1)',
                    borderWidth: 4
                }
            ]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'query'
                    }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: maxValue,  // Skaliert die Y-Achse basierend auf dem höchsten Wert
                    title: {
                        display: true,
                        text: 'duration (s)'
                    }
                }
            }
        }
    });
}

// Funktion zum Neuladen des Diagramms, aufgerufen durch den Button
function reloadChart() {
    createChart();
}

// Initiales Laden des Diagramms
createChart();