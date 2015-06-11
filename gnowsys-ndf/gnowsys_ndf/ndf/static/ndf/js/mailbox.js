function setMailBoxName(username, csrf_token, mailBoxName,type) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	// tyep 1 : Unread Mails ::::::::::::::::::::  type 2 : Read Mails
	$.post( 'mailclient/mailresponse/', {'mailBoxName':mailBoxName, 'username': username, 'csrfmiddlewaretoken': csrf_token, 'type': type }, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
		//.filter() is used because it is a top level-tag and if not use .find()
}

/*function fetchReadMails(username, csrf_token, mailBoxName) {
	$.post('mailclient/mailresponse')
} */