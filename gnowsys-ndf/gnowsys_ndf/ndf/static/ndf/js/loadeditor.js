function saveforum(){
	var name=$("#forum_name").val();
	if (name=="" )
	{
		alert("Please enter forum name");
	}
	else
	{
		$("#forum").trigger('click');
	}
}
$(document).ready(function(){
	$("#orgitdown").change(function(){
		var content=$('#orgitdown').val()
		$('#forum_edit_cont').val(content);

	});


	$("#save_edit_cont").click(function(){
		$('a.close-reveal-modal').trigger('click');
	});
	$('#orgitdown').orgitdown(mySettings);


});
