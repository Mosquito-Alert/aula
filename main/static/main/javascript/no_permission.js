$(document).ready(function() {
    var timeleft = 5;
    var downloadTimer = setInterval(function(){
        if(timeleft <= 0){
            clearInterval(downloadTimer);
            window.location.href = "/";
        }
        $(".timer").text(timeleft);
        timeleft -= 1;
    }, 1000);
});