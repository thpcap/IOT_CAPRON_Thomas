
let sensorChart = null;
let actualisationGraphique = null;
let chargementEnCours = false;

async function afficherGraphique(serialnumber) {

    if (actualisationGraphique) {
        clearInterval(actualisationGraphique);
    }

    document.getElementById("graphiqueContainer").style.display = "block";
    document.getElementById("graphiqueSN").textContent = serialnumber;

    await chargerDonneesGraphique(serialnumber);

    document.getElementById("graphiqueContainer")
        .scrollIntoView({ behavior: "smooth" });

    actualisationGraphique = setInterval(() => {
        chargerDonneesGraphique(serialnumber);
    }, 10000);
}

async function chargerDonneesGraphique(serialnumber) {

    if (chargementEnCours) return;
    chargementEnCours = true;

    try {
        const response = await fetch(
            `/api/sensors/${encodeURIComponent(serialnumber)}/readings`
        );

        if (!response.ok) {
            throw new Error(`Erreur HTTP : ${response.status}`);
        }

        const data = await response.json();

        console.log("Données reçues :", data);

        const temperatures = data.temperature.map(item => ({
            x: new Date(item.time.replace(" ", "T")).getTime(),
            y: Number(item.reading)
        }));

        const humidites = data.humidity.map(item => ({
            x: new Date(item.time.replace(" ", "T")).getTime(),
            y: Number(item.reading)
        }));

        if (sensorChart) {

            // Actualiser les données du graphique
            sensorChart.data.datasets[0].data = temperatures;
            sensorChart.data.datasets[1].data = humidites;
            sensorChart.update("none");

        } else {

            // Créer le graphique lors du premier chargement
            const ctx = document.getElementById("sensorChart");

            sensorChart = new Chart(ctx, {
                type: "line",
                data: {
                    datasets: [
                        {
                            label: "Température (°C)",
                            data: temperatures,
                            borderColor: "rgb(255, 99, 132)",
                            backgroundColor: "rgba(255, 99, 132, 0.1)",
                            tension: 0.3,
                            yAxisID: "yTemperature"
                        },
                        {
                            label: "Humidité (%)",
                            data: humidites,
                            borderColor: "rgb(54, 162, 235)",
                            backgroundColor: "rgba(54, 162, 235, 0.1)",
                            tension: 0.3,
                            
                            yAxisID: "yHumidity"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    parsing: false,
                    interaction: {
                        mode: "nearest",
                        intersect: false
                    },
                    scales: {
                        x: {
                            type: "time",
                            title: {
                                display: true,
                                text: "Date"
                            }
                        },
                        yTemperature: {
                            type: "linear",
                            position: "left",
                            min: 0,
                            max: 50,
                            title: {
                                display: true,
                                text: "Température (°C)"
                            }
                        },
                        yHumidity: {
                            type: "linear",
                            position: "right",
                            min: 0,
                            max: 100,
                            title: {
                                display: true,
                                text: "Humidité (%)"
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        }

    } catch (error) {
        console.error("Erreur graphique :", error);
    } finally {
        chargementEnCours = false;
    }
}
