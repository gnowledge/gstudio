CKEDITOR.plugins.add('addVideo',
{
    init: function(editor)
    {
        //plugin code goes here
        var pluginName = 'addVideo';
        var groupId = editor.config.groupID.group_id;
        var nodeId = editor.config.nodeID.node_id;
        var url = "/" + groupId + "/video";
        // var textAreaId = "textarea-"+nodeId;
        var textAreaId = editor.config.textarea_id;
        CKEDITOR.dialog.add(pluginName, this.path + 'plugin.js');
        editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));

        editor.addCommand("addVideo", {
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
                            var video_player_url = "/" + groupId + "/ajax/get_video_player";
                            var datasrc = $(this).children('img').attr("data-image-id");

                            $.ajax({
                                        type: "GET",
                                        url: video_player_url,
                                        datatype: "html",
                                        data:{
                                            datasrc:datasrc
                                        },
                                        success: function(data) {
                                            CKEDITOR.instances[textAreaId].insertHtml(data);
                                            $('#group_imgs_on_modal').foundation('reveal', 'close');

                                        }
                                });


                          });


                        }
                    });
            }
        });

        editor.ui.addButton('addVideo',
            {
                label: 'Add video from this Group',
                command: pluginName,
                icon: this.path + 'images/addVideo.png'
            });

    }
});
