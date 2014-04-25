$("body>header").hover(function() {
    // Top bar animation on hover
    $("nav.top-bar").animate({
        top:"0"
    },50);
},function() {
    // Top bar animation on hover
    $("nav.top-bar").animate({
        top:"-30px"
    },500);
}
                      );