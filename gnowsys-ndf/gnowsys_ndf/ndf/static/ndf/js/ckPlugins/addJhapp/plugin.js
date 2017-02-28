CKEDITOR.plugins.add('addJhapp',
{
    init: function(editor)
    {
        //plugin code goes here
        var pluginName = 'addJhapp';
        var groupId = editor.config.groupID.group_id;
        var nodeId = editor.config.nodeID.node_id;
        var url = "/" + groupId + "/ajax/get_jhapps";
        // var textAreaId = "textarea-"+nodeId;
        var textAreaId = editor.config.textarea_id;
        CKEDITOR.dialog.add(pluginName, this.path + 'plugin.js');
        editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));

        editor.addCommand("addJhapp", {
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

                          $(".button-hollow-purple").click(function(event){
                            var datasrc = $(this).attr("data-original-url");
                            completeURL = "/media"+ datasrc;
                            CKEDITOR.instances[textAreaId].insertHtml('<iframe style="border:none;width:100%;height:100%;min-height:800px;" src=' + completeURL +  '>' + '</img>');
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });


                        }
                    });
            }
        });

        editor.ui.addButton('addJhapp',
            {
                label: 'Add Jhapp from this Group',
                command: pluginName,
                icon: this.path + 'images/addJhapp.png'
            });

    }
});
