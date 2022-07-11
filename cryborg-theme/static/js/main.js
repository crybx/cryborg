$(function () {
    // $('nav a').textillate({ in: { effect: 'fadeIn', delayScale: 1, delay: 100 } });
    // $('.carat').textillate({ in: { effect: 'fadeIn', delayScale: 0.5 } });

    $('nav li').lettering().children().css("opacity", 0).each(function(index) {
        // $(this).delay(index * 40).fadeIn(50);
        $(this).delay(index * 40).animate({"opacity": 1}, 50);
    });


});