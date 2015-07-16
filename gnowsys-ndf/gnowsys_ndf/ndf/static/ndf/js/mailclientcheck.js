var validName = 0;
var validID	  = 0;
var empty_check = '<p style="color:red">Empty Field</p>';
var mailBoxName;
var mailBoxId;
var edit_page;
var same;
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
	
	if($('#page_type')[0].innerHTML == 'edit'){
		edit_page = 1;
		mailBoxName=$('#mailboxname')[0].innerHTML;
		mailBoxId=$('#mailboxid')[0].innerHTML;
	}
	else{
		edit_page= 0;
	}

	// IMPORTANT : CSRF_TOKEN must always be passed with the key value as 'csrfmiddlewaretoken'

	$("#name_id").blur(function(){
		var val = $("#name_id").val();
		var shld = 0;
		if(edit_page == 1) {
			if(val==mailBoxName){
				shld = 0;
			}
			else{
				shld = 1;
			}
		}
		else{
			shld = 1;
		}
		if(shld == 1){
			$.post( 'uniqueMailboxName/', {'name_data':val,'csrfmiddlewaretoken': CSRF_token }, function(data){		
				var content = $(data).filter( '#message' );
				$( "#name_id_error" ).empty().append( content );

				content = $(data).filter( '#Button_data' );
				content = content[0].innerHTML;
				if(content=="1"){
					validName = 1;
				}
				else{
					validName = 0;
				}
			});
		}
		else{
			$( "#name_id_error" ).empty().append( '' );
		}
	});

	$("#email_id").blur(function(){
		var val = $("#email_id").val();
		var shld = 0;
		if(edit_page == 1) {
			if(val==mailBoxId){
				shld = 0;
			}
			else{
				shld = 1;
			}
		}
		else{
			shld = 1;
		}
		if(shld == 1){
			$.post( 'uniqueMailboxId/', {'email_data':val, 'csrfmiddlewaretoken':CSRF_token}, function(data){		
				var content = $(data).filter( '#message' );
				$( "#email_id_error" ).empty().append( content );

				content = $(data).filter( '#Button_data' );
				content = content[0].innerHTML;
				if(content=="1"){
					validID = 1;
				}
				else{
					validID = 0;
				}
			});
		}
		else{
			$( "#name_id_error" ).empty().append( '' );
		}
	});

	$("#form-edit-node").submit(function(event){
		var val = $("#name_id").val();
		var shld = 0;
		if(edit_page == 1) {
			if(val==mailBoxName){
				shld = 0;
			}
			else{
				shld = 1;
			}
		}
		else{
			shld = 1;
		}
		if(shld == 1){
			$.post( 'uniqueMailboxName/', {'name_data':val,'csrfmiddlewaretoken': CSRF_token }, function(data){		
				var content = $(data).filter( '#message' );
				$( "#name_id_error" ).empty().append( content );

				content = $(data).filter( '#Button_data' );
				content = content[0].innerHTML;
				if(content=="1"){
					validName = 1;
				}
				else{
					validName = 0;
				}
			});
		}
		else{
			$( "#name_id_error" ).empty().append( '' );
		}

		val = $("#email_id").val();
		shld = 0;
		if(edit_page == 1) {
			if(val==mailBoxId){
				shld = 0;
			}
			else{
				shld = 1;
			}
		}
		else{
			shld = 1;
		}
		if(shld == 1){
			$.post( 'uniqueMailboxId/', {'email_data':val, 'csrfmiddlewaretoken':CSRF_token}, function(data){		
				var content = $(data).filter( '#message' );
				$( "#email_id_error" ).empty().append( content );

				content = $(data).filter( '#Button_data' );
				content = content[0].innerHTML;
				if(content=="1"){
					validID = 1;
				}
				else{
					validID = 0;
				}
			});
		}
		else{
			$( "#name_id_error" ).empty().append( '' );
		}
		if(edit_page == 1){
			if(mailBoxName==$("#name_id").val() && mailBoxId==$("#email_id").val()){
				validName=1;
				validID=1;
			}
		}
		if(validID&validName){
			return;
		}		
		else{
			event.preventDefault();
		}
	});

});