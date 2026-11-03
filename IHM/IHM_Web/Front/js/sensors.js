document.addEventListener("DOMContentLoaded",function(){

    const sensorForm = document.getElementById("sensorForm");

    sensorForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = {
            serialnumber: document.getElementById("serialnumber").value.trim(),
            name: document.getElementById("name").value.trim() || null,
        };

        try {
            const response = await fetch(`${API_URL}/api/sensors`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Erreur API");
            }

            console.log("Capteur créé :", result.sensor);
            alert("Capteur ajouté avec succès !");

            sensorForm.reset();
            chargerCapteurs();

        } catch (error) {
            console.error("Erreur :", error);
            alert("Impossible de contacter le serveur : " + error.message);
        }
    });
    chargerCapteurs();

});


async function chargerCapteurs() {
    const tbody = document.getElementById("capteurList");

    try {
        // Récupération des capteurs depuis le backend
        const response = await fetch(`${API_URL}/api/sensors`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP : ${response.status}`);
        }

        const data = await response.json();

        // Vide le tableau avant de le remplir
        tbody.innerHTML = "";

        // Parcourt tous les capteurs
        data.sensors.forEach(sensor => {
            const tr = document.createElement("tr");
            tr.classList.add(`capt_${sensor.serialnumber}`);

            tr.innerHTML = `
                <td>
                    <input
                        type="checkbox"
                        name="Capteurs"
                        value="${sensor.serialnumber}"
                    >
                </td>
                <td class="capt_id">${sensor.id}</td>
                <td class="capt_name">${sensor.name}</td>
                <td class="capt_sn">${sensor.serialnumber}</td>
                <td class="capt_v">${sensor.version ?? "Inconnue"}</td>
                <td>${sensor.autoimported}</td>
                <button type="button" onclick="afficherGraphique('${sensor.serialnumber}')">
                    Afficher le graphique
                </button>
            `;

            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Erreur lors du chargement des capteurs :", error);
        tbody.innerHTML = `
            <tr>
                <td colspan="6">Impossible de charger les capteurs.</td>
            </tr>
        `;
    }
}