function activerNombre() {
    let commande = document.getElementById("commande");
    let nombre = document.getElementById("value");

    let option = commande.options[commande.selectedIndex];

    let min = option.dataset.min;
    let max = option.dataset.max;

    if (min !== undefined || max !== undefined) {
        nombre.disabled = false;

        nombre.min = min ?? "";
        nombre.max = max ?? "";
        nombre.value = "";

    } else {
        nombre.disabled = true;
        nombre.value = "";
        nombre.removeAttribute("min");
        nombre.removeAttribute("max");
    }
}
