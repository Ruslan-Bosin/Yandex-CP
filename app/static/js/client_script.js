function on_load() {
    var qrcode = new QRCode("qrcode", {
        text: "{{ user_id }}",
        width: 250,
        height: 250,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
}