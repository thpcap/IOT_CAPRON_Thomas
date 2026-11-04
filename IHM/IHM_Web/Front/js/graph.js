
let sensorChart = null;
let actualisationGraphique = null;
let chargementEnCours = false;

let capteurActuel = null;
let heureDebut = null;
let heureFin = null;

function formaterDateInput(date) {
    const annee = date.getFullYear();
    const mois = String(date.getMonth() + 1).padStart(2, "0");
    const jour = String(date.getDate()).padStart(2, "0");
    const heures = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${annee}-${mois}-${jour}T${heures}:${minutes}`;
}

async function afficherGraphique(serialnumber) {

    if (actualisationGraphique) {
        clearInterval(actualisationGraphique);
        actualisationGraphique = null;
    }

    capteurActuel = serialnumber;

    heureDebut = null;
    heureFin = null;

    document.getElementById("heureDebut").value = "";
    document.getElementById("heureFin").value = "";

    document.getElementById("graphiqueContainer").style.display = "block";
    document.getElementById("graphiqueSN").textContent = serialnumber;

    await chargerDonneesGraphique(serialnumber);

    document.getElementById("graphiqueContainer")
        .scrollIntoView({ behavior: "smooth" });

    actualisationGraphique = setInterval(() => {
        chargerDonneesGraphique(serialnumber);
    }, 10000);
}

async function appliquerPeriodeGraphique() {

    const debut = document.getElementById("heureDebut").value;
    const fin = document.getElementById("heureFin").value;

    heureDebut = debut ? new Date(debut) : null;
    heureFin = fin ? new Date(fin) : null;

    if (heureDebut && isNaN(heureDebut.getTime())) {
        alert("Date de début invalide.");
        return;
    }

    if (heureFin && isNaN(heureFin.getTime())) {
        alert("Date de fin invalide.");
        return;
    }

    if (heureDebut && heureFin && heureDebut >= heureFin) {
        alert("La date de début doit être antérieure à la date de fin.");
        return;
    }

    await chargerDonneesGraphique(capteurActuel);
}

async function reinitialiserPeriodeGraphique() {

    document.getElementById("heureDebut").value = "";
    document.getElementById("heureFin").value = "";

    heureDebut = null;
    heureFin = null;

    await chargerDonneesGraphique(capteurActuel);
}

async function chargerDonneesGraphique(serialnumber) {

    if (chargementEnCours || !serialnumber) return;

    chargementEnCours = true;

    try {

        const debut = document.getElementById("heureDebut").value;
        const fin = document.getElementById("heureFin").value;

        const params = new URLSearchParams();

        if (debut) {
            params.append("heure_debut", debut + ":00");
        }

        if (fin) {
            params.append("heure_fin", fin + ":00");
        }

        const url =
            `/api/sensors/${encodeURIComponent(serialnumber)}/readings` +
            (params.toString() ? `?${params.toString()}` : "");

        console.log("Requête API :", url);

        const response = await fetch(url);

        if (!response.ok) {
            const erreur = await response.text();
            throw new Error(`Erreur HTTP ${response.status} : ${erreur}`);
        }

        const data = await response.json();

        console.log("Données reçues :", data);

        if (
            !data ||
            !Array.isArray(data.temperature) ||
            !Array.isArray(data.humidity)
        ) {
            throw new Error("Réponse API invalide.");
        }

        const temperatures = data.temperature.map(item => ({
            x: new Date(item.time.replace(" ", "T")).getTime(),
            y: Number(item.reading)
        }));

        const humidites = data.humidity.map(item => ({
            x: new Date(item.time.replace(" ", "T")).getTime(),
            y: Number(item.reading)
        }));

        if (
            temperatures.some(item => !Number.isFinite(item.x) || !Number.isFinite(item.y)) ||
            humidites.some(item => !Number.isFinite(item.x) || !Number.isFinite(item.y))
        ) {
            throw new Error("Certaines mesures reçues sont invalides.");
        }

        if (sensorChart) {

            sensorChart.data.datasets[0].data = temperatures;
            sensorChart.data.datasets[1].data = humidites;

            sensorChart.update("none");

        } else {

            const ctx = document.getElementById("sensorChart");

            if (!ctx) {
                throw new Error("Canvas sensorChart introuvable.");
            }

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
                            pointRadius: 3,
                            yAxisID: "yTemperature"
                        },
                        {
                            label: "Humidité (%)",
                            data: humidites,
                            borderColor: "rgb(54, 162, 235)",
                            backgroundColor: "rgba(54, 162, 235, 0.1)",
                            tension: 0.3,
                            pointRadius: 3,
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

        console.log("Graphique actualisé avec succès.");

    } catch (error) {

        console.error("Erreur graphique :", error);

    } finally {

        chargementEnCours = false;
    }
}
