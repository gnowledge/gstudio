// The Global variables
var Readstart;
var Unreadstart;
var typeOfMail; // 0 for the unread ones and 1 for the read ones
var mailbox_name;
var userName;
var CSRFtoken;
var countValue = 20;
var fileName;

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

function toolbarDisplay(){
	var type = 'inline-block';
	$("#set_box")[0].style.display = type;
	$("#compose_mail")[0].style.display = type;
	$("#down_count")[0].style.display = type;
	$("#up_count")[0].style.display = type;
	$("#unreadMailsLink")[0].style.display = type;
	$("#readMailsLink")[0].style.display = type;
	$("#tab1").css("background-color", "#DCDCDC");
	$("#go1")[0].style.display = "none";
	$("#go2")[0].style.display = "none";
	$("#go3")[0].style.display = "none";
}

// Function to put a POST request to fetch mails
function setMailBoxName(username, csrf_token, mailBoxName, emailid) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	document.getElementById( 'emailIdBox' ).innerHTML = emailid;
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
	fileName = filename;
	var temp = 0;
	if(typeOfMail == 0){
		temp = Unreadstart;
	}
	else {
		temp = Readstart;
	}
	if(typeOfMail == 0){
	$.post( 'mailstatuschange/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'mail_type': typeOfMail, 'file_name': filename, 'startFrom': temp }, function(data){		
		var content = $(data).filter( '#mailContent' );
		console.log(content[0].innerHTML);
		$( ".mailBoxContent" ).empty().append( content );
	});
	}
}

// <a id=\"reply_mail\" href=\"#\" onclick=\"replyToMail();\" class=\"button small\" >Reply</a>
function readBody(filename, attached_files, Attachments){
	
	$.post( 'mail_body/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'mail_type': typeOfMail, 'file_name': filename}, function(data){		

	var content = '<a class="close-reveal-modal" >&#215;</a>';
	var attach_count = 0;

	content += data;
	
	for(n in Attachments){
		attach_count+=1;
	}
	
	if(attach_count>0){
	content += '<br> <h3> Attachments: </h3>';
	}
    
    var elementName = "myModal";
    var n;
    for(n in attached_files){
    	var link = "/" + userName + '/file/readDoc/download';
    	var href = link + Attachments[n];
    	content += "<br><a href=\"" + href + "\" download=\"" + attached_files[n] + "\">" + attached_files[n] + "</a>";
    }

    content+="<br>";
    content+="<form data-abide id=\"reply_mail\" enctype=\"multipart/form-data\" method=\"POST\" action=\"new_mail/"+mailbox_name+"/\">";
    content+="<input type=\"hidden\" name=\"csrfmiddlewaretoken\" id=\"file_name\" value=\""+ CSRFtoken + "\">";
    content+="<input type=\"hidden\" name=\"file_name\" id=\"file_name\" value=\""+ filename + "\">";
    content+="<input type=\"hidden\" name=\"mailBoxName\" id=\"mailBoxName\" value=\""+ mailbox_name + "\">";
    content+="<input type=\"hidden\" name=\"username\" id=\"username\" value=\""+ userName + "\">";
    content+="<input type=\"submit\" id=\"reply_mail\" value=\"Reply\" class=\"button small\"/>";
    content+="</form>";
    document.getElementById(elementName).innerHTML = content;    			

 	});   
}

function replyToMail(){
	$.post( 'new_mail/'+mailbox_name+'/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'file_name': fileName});
}

$(document).ready(function(){
	$("#unreadMailsLink").click(function(){
		Unreadstart = 0;
		typeOfMail = 0;
		$("#tab1").css("background-color", "#DCDCDC");
		$("#tab2").css("background-color", "#FFFFFF");
		getMails();
	});

	$("#readMailsLink").click(function(){
		Readstart = 0;
		typeOfMail = 1;
		getMails();
		$("#tab1").css("background-color","#FFFFFF");
		$("#tab2").css("background-color","#DCDCDC");
	});
});
