function setMailBoxName(username, csrf_token, mailBoxName,mailbox_id) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	a=$("#edit_box").attr("href");
	a=a.replace('dummy',mailBoxName);
	$("#edit_box").attr("href", a);
	
	b=$("#delete_box").attr("href");
	b=b.replace('dummy',mailBoxName);
	$("#delete_box").attr("href", b);
	
	$.post( 'mailresponse/', {'mailBoxName':mailBoxName, 'username': username, 'csrfmiddlewaretoken': csrf_token }, function(data){
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
}