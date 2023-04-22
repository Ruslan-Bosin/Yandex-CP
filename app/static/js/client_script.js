function on_load() {
    var qrcode = new QRCode("qrcode", {
        text: "{{ user_id }}",
        width: 128,
        height: 128,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
}