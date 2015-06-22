// The Global variables
var Readstart;
var Unreadstart;
var typeOfMail; // 0 for the unread ones and 1 for the read ones
var mailbox_name;
var userName;
var CSRFtoken;
var countValue = 20;
function countInitialize(){
	Readstart = 0;
	Unreadstart = 0;
	typeOfMail = 0;
}

function increaseMailFetchCount(){
	if (typeOfMail == 0){
		Unreadstart = Unreadstart + countValue;
	}
	else{
		Readstart = Readstart + countValue;
	}
	// alert('Unread: ' + Unreadstart + ' Read: ' + Readstart);
	getMails();
}


function decreaseMailFetchCount(){
	if (typeOfMail == 0){
		Unreadstart = Unreadstart - countValue;
		if(Unreadstart < 0){
			Unreadstart = 0;
		}
	}
	else {
		Readstart = Readstart - countValue;
		if(Readstart < 0) { 
			Readstart = 0;
		}
	}
	// alert('Unread: ' + Unreadstart + ' Read: ' + Readstart);
	getMails();

}


function getMails(){
	var temp = 0;
	if(typeOfMail == 0){
		temp = Unreadstart;
	}
	else {
		temp = Readstart;
	}
	$.post( 'mailresponse/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'mail_type': typeOfMail, 'startFrom': temp}, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
}


// Function to put a POST request to fetch mails
function setMailBoxName(username, csrf_token, mailBoxName) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	/*code to set the 'mailbox_settings' url*/
	set_link=$("#set_box").attr("href");
	set_link=set_link.replace('dummy',mailBoxName);
	$("#set_box").attr("href", set_link);

	/*code to set the 'compose_mail' url*/
	new_mail_link=$("#compose_mail").attr("href");
	new_mail_link=new_mail_link.replace('dummy',mailBoxName);
	$("#compose_mail").attr("href", new_mail_link);

	mailbox_name = mailBoxName;
	userName = username;
	CSRFtoken = csrf_token;
	countInitialize();
	getMails();
}

function updateStatus(filename){
	alert(typeOfMail);
	if(typeOfMail == 0){
		alert('WORKED');
	$.post( 'mailstatuschange/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'mail_type': typeOfMail, 'file_name': filename}, function(data){		
		alert('SHIFTED!');
	});
	}
}

// <textarea name=\"editor1\" id=\"editor1\">&lt;p&gt;
// &lt;/p&gt;</textarea><script>CKEDITOR.replace( 'editor1' );</script>
function readBody(mail_id,text){
	var content = text;
    var elementName = "myModal" + mail_id;
    document.getElementById(elementName).innerHTML = content;    			
}

$(document).ready(function(){
	$("#unreadMailsLink").click(function(){
		Unreadstart = 0;
		typeOfMail = 0;
		getMails();
	});

	$("#readMailsLink").click(function(){
		Readstart = 0;
		typeOfMail = 1;
		getMails();
	});
});



