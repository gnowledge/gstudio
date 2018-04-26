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

// // after opening overlay node'sdescription should fetch from oid
// $('.overlay-description-by-oid-caller').click(function(){
// // alert(this.getAttribute('data-oid'));
// var oid = this.getAttribute('data-oid');
// document.getElementById('overlay-description-by-oid').setAttribute('caught-data-oid', oid);

// // wiping out #overlay-description-by-oid-content and overlay-description-by-oid-title
// document.getElementById('overlay-description-by-oid-content').textContent = ""
// document.getElementById('overlay-description-by-oid-title').textContent = ""
// });

// $(document).on('open', '#overlay-description-by-oid[data-reveal]', function () {
// var modal = this;
// var oid = modal.getAttribute('caught-data-oid');
// // var url = "/{{group_id}}/ajax/get_resource_by_oid/" + oid;

// if (!oid) {return};
// });

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


// // start of document.ready()
//   $(document).ready(function() {
//     try{
//         $("#help-canvas-menu").click(function(){
//             $("#help-canvas-menu").toggleClass("expanded");
//             // $("div").addClass("expanded");
//         });

//       // $('select option[value="{{request.LANGUAGE_CODE}}"]').attr("selected",true);

//       {% block document_ready %} {% endblock %}

//     }
//     finally{
//       // function defined in app.js to check the font and load it asynchronously.
//       checkOpenSansFont();
//     }

//     //function defined to inject
//     (function(win,doc,tag,script){
//       var element = doc.createElement(tag);
//       var ftag = doc.getElementsByTagName(tag)[0];
//       element.async = 1;
//       element.src = script;
//       ftag.parentNode.insertBefore(element,ftag)
//     })(window,document,'script','/static/ndf/js/analytics.js');
//   });



// // Toggles the display of main sidebar for 12 col article view
//   var toggleMainSidebar = function(){
//     $("main>aside").toggle();
//     $("main>article").toggleClass("large-9 large-12");
//   };

// // Hide broken image links
//   $('img').error(function(){
//     $(this).addClass("hide");
//     //$(this).attr('src', 'missing.png');
//   });

// // If on the home group, change group dropdown text to "Groups"
//   if($(".group a.active").html() == "home") {
//     $(".group a.active").html("Groups").removeClass("active");
//     $("#home-group").addClass("active");
//   }

// //Functions to automatically add an <i> element icon inside node spans

// /* Attaches user icon with gnow level color for every user link */
// $(".user").prepend(function(){return "<i class='fi-torso'></i>"});

// /* Attaches icon for node type */
// $(".card .course").prepend(function(){return "<i class='fi-book'></i>"});

// /* Attaches icon for node type */
// $(".card .quiz").prepend(function(){return "<i class='fi-graph-bar'></i>"});

// /* Attaches icon for node type */
// $(".card .forum").prepend(function(){return "<i class='fi-comments'></i>"});

// /* Attaches icon for node type */
// $(".card .group").prepend(function(){return "<i class='fi-torsos'></i>"});

//   /* Attaches icon for node type */
// $(".card .page").prepend(function(){return "<i class='fi-page'></i>"});

// /* Attaches icon for node type */
// $(".card .ebook").prepend(function(){return "<i class='fi-book'></i>"});

// /* Attaches icon for node type */
// $("aside.page").prepend(function(){return "<i class='fi-page'></i>"});

// //set language prefernce
//   $(document).on('click', "#savepref", function(){
//     var vpref=$("#pref").val();
//     var fb=$("#fallback").val();
//     var vurl='/{{group_id}}/userpreference/';

//     $.ajax({
//       url: vurl,
//       type: 'POST',
//       data: {pref:vpref,fallback:fb,csrfmiddlewaretoken: '{{ csrf_token }}'},

//       success:function(data){
//         alert("Successfully set the preferences");
//         location.reload();
//       }
//     }); //ajax closes
//   }); //document closes
