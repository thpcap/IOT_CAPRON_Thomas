
function toggleAdvanced() {
    const menu = document.getElementById("advancedConfig");
    const arrow = document.getElementById("advancedArrow");

    menu.classList.toggle("open");
    arrow.classList.toggle("rotated");
}

document.addEventListener("DOMContentLoaded", function () {

    const sensorForm = document.getElementById("sensorForm");

    sensorForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = {
            serialnumber: document.getElementById("serialnumber").value.trim(),
            name: document.getElementById("name").value.trim() || null,

            // Topics personnalisés
            TempTopic: document.getElementById("topicT").value.trim() || "",
            HumiTopic: document.getElementById("topicH").value.trim() || "",
            dateTopic: document.getElementById("topicDate").value.trim() || "",
            versTopic: document.getElementById("topicVersion").value.trim() || "",
            CommandTopic: document.getElementById("topicCommand").value.trim() || "",
            BlinkTopic: document.getElementById("topicBlink").value.trim() || "",
            BargraphTopic: document.getElementById("topicBargraph").value.trim() || ""
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

            // Refermer la configuration avancée
            document.getElementById("advancedConfig").classList.remove("open");
            document.getElementById("advancedArrow").classList.remove("rotated");

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
                <td hidden>${sensor.autoimported}</td>
                <td>
                    <button type="button" onclick="afficherGraphique('${sensor.serialnumber}')">
                        Afficher le graphique
                    </button>
                </td>
                <td>
                    <button type="button" onclick="supprimerCapteur('${sensor.serialnumber}')">
                        Supprimer
                    </button>
                </td>
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

async function supprimerCapteur(serialnumber) {

    if (!confirm(`Voulez-vous vraiment supprimer le capteur ${serialnumber} ?\nToutes ses mesures seront également supprimées.`)) {
        return;
    }

    try {
        const response = await fetch(
            `/api/sensors/${encodeURIComponent(serialnumber)}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erreur lors de la suppression");
        }

        alert("Capteur supprimé avec succès !");

        // Actualiser la liste des capteurs
        chargerCapteurs();

    } catch (error) {
        console.error("Erreur :", error);
        alert(error.message);
    }
}