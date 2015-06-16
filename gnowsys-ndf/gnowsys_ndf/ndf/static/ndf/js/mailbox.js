function setMailBoxName(username, csrf_token, mailBoxName,type) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;

	/*code to set the 'mailbox_settings' url*/
	set_link=$("#set_box").attr("href");
	set_link=set_link.replace('dummy',mailBoxName);
	$("#set_box").attr("href", set_link);

	/*code to set the 'compose_mail' url*/
	new_mail_link=$("#compose_mail").attr("href");
	new_mail_link=new_mail_link.replace('dummy',mailBoxName);
	$("#compose_mail").attr("href", new_mail_link);
	
	$.post( 'mailclient/mailresponse/', {'mailBoxName':mailBoxName, 'username': username, 'csrfmiddlewaretoken': csrf_token, 'type': type }, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
}

function alterHyperLink(username, csrf_token, mailBoxName,type){
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	var newFunction1 = "setMailBoxName('" + username + "','" + csrf_token + "','" + mailBoxName + "'," + "1" + ")";
	var newFunction2 = "setMailBoxName('" + username + "','" + csrf_token + "','" + mailBoxName + "'," + "0" + ")";
	$("#unreadMailsLink").attr('onclick',newFunction1);
	$("#readMailsLink").attr('onclick',newFunction2);
}