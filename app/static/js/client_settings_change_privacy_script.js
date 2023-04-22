function select_current() {
    if ('{{ user_info['is_private'] }}' == "False") {
        document.getElementById("standard").style.color = "#ff0000";
    } else {
        document.getElementById("private").style.color = "#ff0000";
    }
}