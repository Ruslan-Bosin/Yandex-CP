var error_message = document.getElementById("error_message");
var submit_button = document.getElementById("submit_button");


function validator() {
    var name_text = document.getElementById("name").value;
    var message = "";

    if (name_text.indexOf('aa') != -1) {message = "Неверное имя"}
    // TODO: name_text validator

    error_message.innerText = message;
    if (message == "") {submit_button.disabled = false;}
    else {submit_button.disabled = true;}
}


function validator_with_error_message_checker() {

    document.getElementById("name").value = '{{ user_info["name"] }}';

    if (error_message.innerText == "") {
        validator()
    }
}
