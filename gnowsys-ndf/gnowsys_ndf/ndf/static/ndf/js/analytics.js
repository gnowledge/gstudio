
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

function registerEvent(obj, properties, action) {
    /*
        obj : 
            this is the object to which user performs the activity
            It is a dictionary that takes the name of activity as key whose value is a dictionary containing activity attributes

        properties : 
            dictionary containing the attribute values of the object

        action : 
            this is action that the user performs on the object
            It is a dictionary that have two fields
                'key' : one word recognition for the activity
                'phrase' : phrase that defines how the action will be used in a sentence
    */

    parameters = { 'group_id' : window.location.pathname.split("/")[1],
            'obj' : obj, 
            'obj_properties' : JSON.stringify(properties), 
            'action' : JSON.stringify(action)
     }

	$.ajax({
		url : '/analytics/custom_event/',
        data : parameters,
		method : 'POST',
		headers: {
	        "X-CSRFToken":csrftoken
	    },
		success : function(data) {
			//console.log(data);
		}
	});
}

