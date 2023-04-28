var error_message = document.getElementById("error_message");
var submit_button = document.getElementById("submit_button");

var f = true;
var pass1 = document.getElementById("password")
var pass2 = document.getElementById("password_confirmation")
var long_arrow_icon = document.getElementById("long_arrow_icon")
document.addEventListener("click", function(e) {
//   alert(e.target.className)
  if ((e.target.className=="change_fill") || (e.target.className=="icon long_arrow")) {

    if (f == true) {
        long_arrow_icon.style.transform = "scale(-1, 1)";
        pass1.style.display = "none";
        pass2.style.display = "inline-block";
        f = false;
    } else {
        long_arrow_icon.style.transform = "scale(1, 1)";
        pass1.style.display = "inline-block";
        pass2.style.display = "none";
        f = true;
    }
  }
});

function validator() {
    var name_text = document.getElementById("name").value;
    var email_text = document.getElementById("email").value;
    var password_text = document.getElementById("password").value;
    var password_confirmation_text = document.getElementById("password_confirmation").value;
    var message = "Данные введены корректно";

    if (password_confirmation_text != password_text) {message = "Пароли не совпадают"}
    if (password_text.length < 8) {message = "Неверный формат пароля"}
    if (email_text.indexOf('@') == -1) {message = "Неверный формат почты"}
    // TODO: name_text validator
    // TODO: починить отображение error message в html

    error_message.innerText = message;
    if (message == "Данные введены корректно") {submit_button.disabled = false;}
    else {submit_button.disabled = true;}
}


function validator_with_error_message_checker() {
    if (error_message.innerText == "") {
        validator()
    }
}
