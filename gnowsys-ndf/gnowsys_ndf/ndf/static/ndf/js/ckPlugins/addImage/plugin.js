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
                             var oToScroll = document.getElementById("group_imgs_on_modal");
                             oToScroll.onscroll = checkReading;

                        function checkReading () {
                              tmp = this.scrollHeight - this.scrollTop === this.clientHeight;
                              console.log(tmp);
                            }


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
