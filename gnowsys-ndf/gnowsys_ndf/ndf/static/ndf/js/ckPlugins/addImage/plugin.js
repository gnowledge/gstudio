CKEDITOR.plugins.add('addImage',
{
    init: function(editor)
    {
        //plugin code goes here
        var pluginName = 'addImage';
        var groupId = editor.config.groupID.group_id;
        var nodeId = editor.config.nodeID.node_id;
        var url = "/" + groupId + "/image";
        var textAreaId = "textarea-"+nodeId;
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
                          $("#myID").html(data);
                          $('#myID').foundation('reveal', 'open');

                          $(".card-image-wrapper").click(function(event){
                            var imageURL = $(this).children('img').attr("data-image-src");
                            var locationURL = 'http://' + location.host;
                            var completeURL = locationURL + imageURL
                            var width = prompt("width for image");
                            CKEDITOR.instances[textAreaId].insertHtml('<img width="'+  width + '"src=' + completeURL +  '>' + '</img>');
                            $('#myID').foundation('reveal', 'close');
                            return false;

                          });


                        }
                    });
            }
        });

        editor.ui.addButton('addImage',
            {
                label: 'add Image',
                command: pluginName,
                icon: this.path + 'images/addImage.png'
            });

    }
});
