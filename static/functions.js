function grow(start, end, steps) {
    var stepSize = (end - start) / steps
    start += stepSize;
    $("#linguist").css({
        fontSize: start
    });
    if (steps--) {
        window.setTimeout(function(){
            grow(start, end, steps);
        }, 10);
    }
};

function growth(start, end) {
    start += 0.05
    $("#linguist").css({
        fontSize: start
    });
    if (start <= end) {
        window.setTimeout(function(){
            growth(start, end);
        }, 10);
    }
};
