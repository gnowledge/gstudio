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


function isInGroup() {
    var url = window.location.pathname;
    var groupUrlArr = [ "/course/about/",
                        "/course/notebook/",
                        "/course/gallery/",
                        "/course/raw-material/",
                        "/course/content/",
                        "/course/asset_detail/",
                        "/course/activity_player/"];
    for (var i = groupUrlArr.length - 1; i >= 0; i--) {
        if(url.match(groupUrlArr[i])){
            return true
            break;
        }
    }
}


function getCookieValue(keyName) {
    // will return value of cookie of provided key
    var allCookiesList = document.cookie.split(';');
    for (var i = allCookiesList.length - 1; i >= 0; i--) {
        if(allCookiesList[i].indexOf(keyName) > -1){
            return allCookiesList[i].trim().split('=').pop()
            break;
        }
    }
}
