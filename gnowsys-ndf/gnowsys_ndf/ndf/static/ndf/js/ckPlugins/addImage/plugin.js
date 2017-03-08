CKEDITOR.plugins.add('addImage',
{
    init: function(editor)
    {
        //plugin code goes here
        var pluginName = 'addImage';
        var groupId = editor.config.groupID.group_id;
        var nodeId = editor.config.nodeID.node_id;
        var url = "/" + groupId + "/image";
        // var textAreaId = "textarea-"+nodeId;
        var textAreaId = editor.config.textarea_id;
        CKEDITOR.dialog.add(pluginName, this.path + 'plugin.js');
        editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));

        editor.addCommand("addImage", {
            exec: function() {

                    $.ajax({
                        type: "GET",
                        url: url,
                        datatype: "html",
                        data:{

                        },
                        success: function(data) {
                          $("#group_imgs_on_modal").html(data);
                          $('#group_imgs_on_modal').foundation('reveal', 'open');

                          $(".card-image-wrapper").click(function(event){
                            var imageURL = $(this).children('img').attr("data-image-src");
                            var imageTitle = $(this).attr("title");
                            // var locationURL = 'http://' + location.host;
                            var locationURL = window.location.origin
                            var completeURL = imageURL
                            var width = prompt("Please enter width in px",'600');
                            if(width == null)
                            {
                                return false;
                            }
                            CKEDITOR.instances[textAreaId].insertHtml('<img width="'+  width + '"src=' + completeURL + ' '+ 'alt=' + imageTitle + '>' + '</img>');
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                        

                          });


                        }
                    });
            }
        });

        editor.ui.addButton('addImage',
            {
                label: 'Add Image from this Group',
                command: pluginName,
                icon: this.path + 'images/addImage.png'
            });

    }
});
