function setMailBoxName(username, csrf_token, mailBoxName) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	$.post( 'mailclient/mailresponse/', {'mailBoxName':mailBoxName, 'username': username, 'csrfmiddlewaretoken': csrf_token }, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});	
		//.filter() is used because it is a top level-tag and if not use .find()
}
