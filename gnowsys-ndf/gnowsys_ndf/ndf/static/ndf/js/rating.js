

function add_ratings(this_val){
    
    var js = document.createElement("script");
    slected_rating_id = $(this_val).attr('data-node-id')
    slected_rating_val = $(this_val).attr('value')
    js.type = "text/javascript";
    js.src = '/static/ndf/js/gstudio-functions.js';

    document.head.appendChild(js);
    group_id =  get_group_id()
    user_access_priv = user_access_policy()
    user = is_user_authenticated();
        if (user == "True"){
            if(user_access_priv == "allow"){
                updateRating(group_id,slected_rating_val,slected_rating_id);
                
            }
        }
        else{
            alert("Please login to rate this resource");
            return false;
        }       
}

function updateRating(group_id,user_rating,rating_id) {
        csrf_token = $(".csrf_token").val();
        is_contributor = is_contributor_list(rating_id);
        
        if(is_contributor == "True"){

            alert("You cannot rate your own resource");
            return false;
        }
        else{

            var rating_url = "/" +  group_id + "/ratings/add_ratings/" + rating_id;
            
            $.ajax({
                    url: rating_url,
                    type: 'POST',
                    data: {
                        rating: user_rating,
                        node: rating_id,
                        csrfmiddlewaretoken: csrf_token,
                        if_comments: "True",
                    },

                    success: function(data){
                       //Replace rating bar with new values
                       //'rating_template' is a div.class of parent template
                       // $(".rating_template").html(data);
                       // console.log(data)
                       data = JSON.parse(data)
                       setRating(data,rating_id);
                    }
            });
        }

    }

function setRating(data_dict,rating_id){
    userRating = data_dict['user_rating']
    avgRating = data_dict['avg']

    if(userRating){
        setStars(userRating,rating_id);
    }
    // else{
    //     setStars( Math.round(avgRating) );
    //     $(".rating-bar").addClass("unrated");
    // }
    //Update the average value text
    
    $('#avg-rating-'+rating_id).html("Avg. : &nbsp;"+ avgRating+" by "+data_dict['tot']+"<i class='fi-torsos'></i>");
    $('#avg-rating-'+rating_id).removeClass("lbl_tag").addClass("rating-lbl")
}

function setStars(stars,rating_id){
        if(stars){            
            $("#rating-"+Math.floor(stars)+"-"+rating_id).prop("checked",true);
        }
    
}

