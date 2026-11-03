document.addEventListener("DOMContentLoaded",function(){
    const form = document.getElementById("commandForm");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Récupération des capteurs cochés
        const capteurs = Array.from(
            document.querySelectorAll('input[name="Capteurs"]:checked')
        ).map(input => input.value);

        // Récupération de la commande
        const commande = document.getElementById("commande").value;

        // Récupération de la valeur supplémentaire
        const valueInput = document.getElementById("value");
        const value = valueInput.value;

        // Vérifications
        if (capteurs.length === 0) {
            alert("Veuillez sélectionner au moins un capteur.");
            return;
        }

        if (!commande) {
            alert("Veuillez sélectionner une commande.");
            return;
        }

        if (["6", "7"].includes(commande) && value === "") {
            alert("Veuillez saisir une valeur.");
            return;
        }

        // Construction des données
        const data = {
            capteurs: capteurs,
            commande: commande,
            value: value === "" ? null : value
        };

        try {
            const response = await fetch(`${API_URL}/api/send-command`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Erreur lors de l'envoi.");
            }

            alert(result.message);

        } catch (error) {
            console.error(error);
            alert("Erreur : " + error.message);
        }
    });
});
  