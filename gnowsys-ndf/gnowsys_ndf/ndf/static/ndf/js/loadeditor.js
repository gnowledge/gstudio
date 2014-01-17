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
$('#orgitdown').orgitdown(mySettings);
$("#orgitdown").change(function(){
var content=$('#orgitdown').val()
$('#editor_content').val(content);
});
$("#savecontent").click(function(){
$('a.close-reveal-modal').trigger('click');
});
});
