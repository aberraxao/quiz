$(function () {
    $("#mybutton").click(send_replies);
});

function send_replies(event) {
    event.preventDefault();

    //const urlParams = new URLSearchParams(window.location.search);
    //const myParam = urlParams.get('username');

    var data = $('form').serialize();
    $.post('/done', data);
}