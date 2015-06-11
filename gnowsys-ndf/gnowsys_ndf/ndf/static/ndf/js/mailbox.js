function setMailBoxName(username, csrf_token, mailBoxName,type) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	a=$("#edit_box").attr("href");
	a=a.replace('dummy',mailBoxName);
	$("#edit_box").attr("href", a);
	
	b=$("#delete_box").attr("href");
	b=b.replace('dummy',mailBoxName);
	$("#delete_box").attr("href", b);
	
	$.post( 'mailclient/mailresponse/', {'mailBoxName':mailBoxName, 'username': username, 'csrfmiddlewaretoken': csrf_token, 'type': type }, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
}

function alterHyperLink(username, csrf_token, mailBoxName,type){
	var newFunction1 = "setMailBoxName('" + username + "','" + csrf_token + "','" + mailBoxName + "'," + "1" + ")";
	var newFunction2 = "setMailBoxName('" + username + "','" + csrf_token + "','" + mailBoxName + "'," + "0" + ")";
	$("#unreadMailsLink").attr('onclick',newFunction1);
	$("#readMailsLink").attr('onclick',newFunction2);
}