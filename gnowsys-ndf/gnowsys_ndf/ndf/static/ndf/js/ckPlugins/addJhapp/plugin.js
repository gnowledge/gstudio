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
                            $("#insert_assessment").click(function(event){
                            assessment_text_val = $('#paste-area-assessment').val();
                            split_word = assessment_text_val.slice(0, 7) + ' style="height:100vh;width:100%" ' + assessment_text_val.slice(7);
                             CKEDITOR.instances[textAreaId].insertHtml(split_word);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_ost").click(function(event){
                            var ost_files_name = prompt("Please enter OST file name");
                            ost_files_name  = ost_files_name.trim();
                            ost_text_val = "<iframe src='/openstorytool/?gallery="+ost_files_name+"&amp;file=/openstorytool/"+ost_files_name+".csst' style='border:none\
;width:100%;height:100vh;min-height:800px;' ></iframe>"
                             CKEDITOR.instances[textAreaId].insertHtml(ost_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_policequad").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            pq_text_val = "<iframe src='/policequad/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(pq_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_runkittyrun").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            bm_text_val = "<iframe src='/runkittyrun/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(bm_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_turtle").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tjs_text_val = "<iframe src='/turtleblocksjs/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tjs_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_physics-video-player").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tjs_text_val = "<iframe src='/physics-video-player/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tjs_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_earth_rotation").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            ert_text_val = "<iframe src='/rotation/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(ert_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });


                        }
                    });
            }
        });

        editor.ui.addButton('addJhapp',
            {
                label: 'Embed Tools',
                command: pluginName,
                icon: this.path + 'images/addJhapp.png'
            });

    }
});
