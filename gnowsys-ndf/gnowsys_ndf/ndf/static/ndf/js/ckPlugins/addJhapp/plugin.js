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
                            

                            pq_text_val = "<a href='/policequad' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/PoliceQuad_pt33x.png' alt='Police quad thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(pq_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_runkittyrun").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            bm_text_val = "<a href='/runkittyrun/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RKR.jpg' alt='Run Kitty Run' height='1000px' width='1000px' >"
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
                            tjs_text_val = "<a href='/physics-video-player/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/physics-video-player.jpg' alt='Physics Video Player' height='1000px' width='1000px' >"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tjs_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_proportional_reasoning").click(function(event){
                            gpr_text_val = "<iframe src='/Geogebra-Proportional-Reasoning/' style='height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(gpr_text_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a1").click(function(event){
                                fst_val_a1 = "<a href='/FoodSharingTool/en/L1A1/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/FST.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                                
                            
                             CKEDITOR.instances[textAreaId].insertHtml(fst_val_a1);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a2").click(function(event){
                                fst_val_a2 = "<a href='/FoodSharingTool/en/L1A2/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/FST.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(fst_val_a2);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a3").click(function(event){
                                fst_val_a3 = "<a href='/FoodSharingTool/en/L1A3/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/FST.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(fst_val_a3);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a4").click(function(event){
                                fst_val_a4 = "<a href='/FoodSharingTool/en/L1A4/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/FST.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(fst_val_a4);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a1").click(function(event){
                                rp_val_l2a1 = "<a href='/RatioPattens/en/L2A1/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a2").click(function(event){
                                rp_val_l2a2 = "<a href='/RatioPattens/en/L2A2/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a2);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a3").click(function(event){
                                rp_val_l2a3 = "<a href='/RatioPattens/en/L2A3/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a3);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a4").click(function(event){
                                rp_val_l2a4 = "<a href='/RatioPattens/en/L2A4/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a4);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a5").click(function(event){
                                rp_val_l2a5 = "<a href='/RatioPattens/en/L2A5/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a5);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a6").click(function(event){
                                rp_val_l2a6 = "<a href='/RatioPattens/en/L2A6/' onclick='javascript:opneinnewindow() return false;' target='_blank'><img src='/static/ndf/images/RP.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(rp_val_l2a6);
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
