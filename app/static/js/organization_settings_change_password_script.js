var error_message = document.getElementById("error_message");
var submit_button = document.getElementById("submit_button");


function validator() {
    var password_text = document.getElementById("password").value;
    var message = "";

    if (password_text.length < 8) {message = "Неверный формат пароля"}

    error_message.innerText = message;
    if (message == "") {submit_button.disabled = false;}
    else {submit_button.disabled = true;}
}


function validator_with_error_message_checker() {
    if (error_message.innerText == "") {
        validator()
    }
}
