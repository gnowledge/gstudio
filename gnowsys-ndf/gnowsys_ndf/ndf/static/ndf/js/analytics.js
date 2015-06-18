
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function registerEvent(action, resource) {
	$.ajax({
		url : '/analytics/page_view/',
		data : {'action' : action, 'resource' : resource},
		method : 'POST',
		headers: {
	        "X-CSRFToken":csrftoken
	    },
		success : function(data) {
			console.log(data);
		}
	});
}

registerEvent('link', location.pathname);