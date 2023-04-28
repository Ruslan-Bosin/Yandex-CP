function select_current() {
    if ('{{ user_info['is_private'] }}' == "False") {
        document.getElementById("standard").style.border = "1px solid #007AFF";
    } else {
        document.getElementById("private").style.border = "1px solid #007AFF";
    }
}