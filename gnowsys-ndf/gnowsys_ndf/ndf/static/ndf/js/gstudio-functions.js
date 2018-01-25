
function get_group_id()
{
	
	 group_id = $(".group_id").val();
	 return  group_id        
}

function is_user_authenticated()
{
	
	 is_authenticated = $(".is_authenticated").val();
	 return  is_authenticated        
}

function is_contributor_list(node_id)
{
	
	 is_contributor = $(".is-contributor-"+node_id).val();
	 return  is_contributor        
}

function user_access_policy()
{
	
	 user_access_priv = $(".user_access_priv").val();
	 return  user_access_priv        
}


