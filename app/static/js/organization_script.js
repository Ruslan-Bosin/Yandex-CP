function on_load() {
    document.getElementById("id").value = "";
}

function change_button_color() {
    if (document.getElementById("id").value.length > 0) {
        document.getElementById("submit_button").style.background = "#007AFF";
    } else {
        document.getElementById("submit_button").style.background = "#D4D4D4";
    }
}