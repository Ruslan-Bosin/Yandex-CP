var error_message = document.getElementById("error_message");
var submit_button = document.getElementById("submit_button");


function validator() {
    var email_text = document.getElementById("email").value;
    var message = "";

    if (email_text.indexOf('@') == -1) {message = "Неверный формат почты"}

    error_message.innerText = message;
    if (message == "") {submit_button.disabled = false;}
    else {submit_button.disabled = true;}
}


function validator_with_error_message_checker() {

    document.getElementById("email").value = '{{ user_info["email"] }}';

    if (error_message.innerText == "") {
        validator()
    }
}
