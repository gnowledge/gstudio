function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }

$(document).ready(function(){

	var CSRF_token = getCookie("csrftoken");

	// IMPORTANT : CSRF_TOKEN must always be passed with the key value as 'csrfmiddlewaretoken'

	$("#name_id").blur(function(){
		var val = $("#name_id").val();
		$.post( 'uniqueMailboxName/', {'name_data':val,'csrfmiddlewaretoken': CSRF_token }, function(data){		
			// function body
			var content = $(data).filter( '#message' );
			$( "#name_id_error" ).empty().append( content );

			content = $(data).filter( '#Button_data' );
			$( "#saveButton" ).empty().append( content );
		});
	});

	$("#email_id").blur(function(){
		var val = $("#email_id").val();
		$.post( 'uniqueMailboxId/', {'email_data':val, 'csrfmiddlewaretoken':CSRF_token}, function(data){		
			// function body
			var content = $(data).filter( '#message' );
			$( "#email_id_error" ).empty().append( content );

			content = $(data).filter( '#Button_data' );
			$( "#saveButton" ).empty().append( content );
		});
	});
});