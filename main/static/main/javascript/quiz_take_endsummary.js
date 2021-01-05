$(document).ready( function () {

function randomInRange(min, max) {
  return Math.random() * (max - min) + min;
}

var more_confetti = function(){
    var myCanvas = $('#emitter')[0];
    var myConfetti = confetti.create(myCanvas, { resize: true });
    myConfetti({
        angle: randomInRange(55, 125),
        spread: randomInRange(50, 70),
        particleCount: randomInRange(150, 300),
        origin: { y: 0.6 }
    });
}

more_confetti();

$('#confetti-button').click(function(){
    more_confetti();
});

});