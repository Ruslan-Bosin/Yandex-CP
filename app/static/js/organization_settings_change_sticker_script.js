var error_message = document.getElementById("error_message");
var submit_button = document.getElementById("submit_button");


function validator() {
    var sticker_text = document.getElementById("sticker").value;
    var message = "";

    console.log(sticker_text.length)
    if (sticker_text.length > 2) {message = "Введите один стикер"}

    error_message.innerText = message;
    if (message == "") {submit_button.disabled = false;}
    else {submit_button.disabled = true;}
}


function validator_with_error_message_checker() {

    document.getElementById("sticker").value = '{{ user_info["sticker"] }}';

    if (error_message.innerText == "") {
        validator()
    }
}
