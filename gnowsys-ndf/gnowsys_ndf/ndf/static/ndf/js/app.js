function addFont()
{
	var style = document.createElement('style');
	style.textContent = localStorage.openSansNormalFont;
	style.rel = 'stylesheet';
	document.head.appendChild(style);
}


// function to check font and load it in async way.
function checkOpenSansFont()
{

	try {
		if (localStorage.openSansNormalFont) {
	            // The font is in localStorage, we can load it directly
	            addFont();
	        } else {
	            // We have to first load the font file asynchronously
	            var request = new XMLHttpRequest();
	            request.open('GET', '/static/ndf/css/open-sans-normal-font.css', true);

	            request.onload = function() {
	            	if (request.status >= 200 && request.status < 400) {
	                    // We save the file in localStorage
	                    localStorage.openSansNormalFont = request.responseText;

	                    // ... and load the font
	                    addFont();
	                }
	            }

	            request.send();
	        }
    }
    catch(ex) {
        // maybe load the font synchronously for woff-capable browsers
        // to avoid blinking on every request when localStorage is not available
    }
}

 // $("nav.top-bar").delay(1000).animate({
 //        top:"-40px"
 //    },500);

// $("body>header").hover(function() {
//     // Top bar animation on hover
//     $("nav.top-bar").animate({
//         top:"0"
//     },50);
// },function() {
//     // Top bar animation on hover
//     $("nav.top-bar").delay(500).animate({
//         top:"-40px"
//     },500);
// }
                      // );