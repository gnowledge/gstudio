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
                            split_word = assessment_text_val.slice(0, 7) + ' style="min-height:100vh; min-width:100%" ' + assessment_text_val.slice(7);
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
                            
                            $("#insert_policequad_en").click(function(event){
                            

                            tool_val = "<a href='/policequad/en/' target='_blank'><img src='/static/ndf/images/PoliceQuad_pt33x.png' alt='Police quad thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_policequad_hi").click(function(event){
                            

                            tool_val = "<a href='/policequad/hi/' target='_blank'><img src='/static/ndf/images/PoliceQuad_pt33x.png' alt='Police quad thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          }); 
                            $("#insert_policequad_te").click(function(event){
                            

                            tool_val = "<a href='/policequad/te/' target='_blank'><img src='/static/ndf/images/PoliceQuad_pt33x.png' alt='Police quad thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_runkittyrun_en").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<a href='/runkittyrun/en/' target='_blank'><img src='/static/ndf/images/run_kitty_run.png' alt='Run Kitty Run' height='1000px' width='1000px' >"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_runkittyrun_hi").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<a href='/runkittyrun/hi/' target='_blank'><img src='/static/ndf/images/run_kitty_run.png' alt='Run Kitty Run' height='1000px' width='1000px' >"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_runkittyrun_te").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<a href='/runkittyrun/te/' target='_blank'><img src='/static/ndf/images/run_kitty_run.png' alt='Run Kitty Run' height='1000px' width='1000px' >"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_turtle").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<iframe src='/turtleblocksjs/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_geometric_reasoning").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<iframe src='/GeogebraGeometricReasoning/' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_physics-video-player").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<a href='/physics-video-player/' target='_blank'><img src='/static/ndf/images/physics_video_tool.jpg' alt='Physics Video Player' height='1000px' width='1000px' >"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_proportional_reasoning1").click(function(event){
                            tool_val = "<iframe src='/GeogebraProportionalReasoning1/' style='height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_proportional_reasoning2_a1_q1").click(function(event){
                            tool_val = "<iframe src='/GeogebraProportionalReasoning2/PR-unit2-activity1-q1/' style='height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_proportional_reasoning2_a1_q3").click(function(event){
                            tool_val = "<iframe src='/GeogebraProportionalReasoning2/PR-unit2-activity1-q3/' style='height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_geogebra_proportional_reasoning2_a2_q1").click(function(event){
                            tool_val = "<iframe src='/GeogebraProportionalReasoning2/PR-unit2-activity2-q1/' style='height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a1_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L1A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                                
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a2_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L1A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a3_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L1A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a4_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L1A4/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a1_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L2A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a2_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L2A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a3_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L2A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a4_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L2A4/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a1_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L3A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a2_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L3A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a3_en").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/en/L3A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a1_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L1A1/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a2_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L1A2/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a3_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L1A3/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a4_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L1A4/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a1_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L2A1/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a2_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L2A2/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a3_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L2A3/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a4_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L2A4/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a1_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L3A1/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a2_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L3A2/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a3_hi").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/hi/L3A3/' target='_blank'><img src='/static/ndf/images/fst_hi.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                             $("#insert_fst_l1_a1_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L1A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a2_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L1A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a3_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L1A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l1_a4_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L1A4/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a1_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L2A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a2_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L2A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a3_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L2A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l2_a4_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L2A4/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a1_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L3A1/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a2_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L3A2/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_fst_l3_a3_te").click(function(event){
                                tool_val = "<a href='/FoodSharingTool/te/L3A3/' target='_blank'><img src='/static/ndf/images/fst_en.png' alt='Food Sharing Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });


                            $("#insert_rp_l2a1").click(function(event){

                                tool_val = "<a href='/RatioPatterns/L2A1/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a2").click(function(event){
                                tool_val = "<a href='/RatioPatterns/L2A2/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a3").click(function(event){
                                tool_val = "<a href='/RatioPatterns/L2A3/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a4").click(function(event){
                                tool_val = "<a href='/RatioPatterns/L2A4/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a5").click(function(event){
                                tool_val = "<a href='/RatioPatterns/L2A5/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a6").click(function(event){
                                tool_val6 = "<a href='/RatioPatterns/L2A6/' target='_blank'><img src='/static/ndf/images/rp_en.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_rp_l2a1_hi").click(function(event){

                                tool_val = "<a href='/RatioPatterns/hi/L2A1/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a2_hi").click(function(event){
                                tool_val = "<a href='/RatioPatterns/hi/L2A2/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a3_hi").click(function(event){
                                tool_val = "<a href='/RatioPatterns/hi/L2A3/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a4_hi").click(function(event){
                                tool_val = "<a href='/RatioPatterns/hi/L2A4/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a5_hi").click(function(event){
                                tool_val = "<a href='/RatioPatterns/hi/L2A5/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a6_hi").click(function(event){
                                tool_val = "<a href='/RatioPatterns/hi/L2A6/' target='_blank'><img src='/static/ndf/images/rp_hi.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_rp_l2a1_te").click(function(event){

                                tool_val = "<a href='/RatioPatterns/te/L2A1/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a2_te").click(function(event){
                                tool_val = "<a href='/RatioPatterns/te/L2A2/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a3_te").click(function(event){
                                tool_val = "<a href='/RatioPatterns/te/L2A3/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a4_te").click(function(event){
                                tool_val = "<a href='/RatioPatterns/te/L2A4/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a5_te").click(function(event){
                                tool_val = "<a href='/RatioPatterns/te/L2A5/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_rp_l2a6_te").click(function(event){
                                tool_val = "<a href='/RatioPatterns/te/L2A6/' target='_blank'><img src='/static/ndf/images/rp_te.png' alt='Ratio Patterns Tool' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a1_en").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/en/L4A1/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a2_en").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/en/L4A2/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a1_hi").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/hi/L4A1/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a2_hi").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/hi/L4A2/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a1_te").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/te/L4A1/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                            $("#insert_icl_l4a2_te").click(function(event){
                                tool_val = "<a href='/IceCubesInLemonade/te/L4A2/' target='_blank'><img src='/static/ndf/images/icl_en.png' alt=' IceCubesInLemonade' height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_find_the_rate").click(function(event){
                                tool_val = "<iframe src='/FindTheRateProportionalReasoning/' style='min-height:100vh;width:100%'></iframe>"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });



                            
                          
                          $("#insert_starlogo_model1_en").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/en/Anemia1' target='_blank'><img src='/static/ndf/images/Anemia_english.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                          
                          $("#insert_starlogo_model2_en").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/en/Anemia2/' target='_blank'><img src='/static/ndf/images/Anemia_english.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                          $("#insert_starlogo_model1_hi").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/hi/Anemia1/' target='_blank'><img src='/static/ndf/images/Anemia_hindi.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_starlogo_model2_hi").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/hi/Anemia2/' target='_blank'><img src='/static/ndf/images/Anemia_hindi.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_starlogo_model1_te").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/te/Anemia1' target='_blank'><img src='/static/ndf/images/AnemeaTelugu.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_starlogo_model2_te").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/te/Anemia2' target='_blank'><img src='/static/ndf/images/AnemeaTelugu.png' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_starlogo_model3_en").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/en/FishAlgae' target='_blank'><img src='/static/ndf/images/FishAlgae-English.jpg' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });


                            $("#insert_starlogo_model3_hi").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/hi/FishAlgae' target='_blank'><img src='/static/ndf/images/FishAlgae-Hindi.jpg' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                            $("#insert_starlogo_model3_te").click(function(event){
                            

                            tool_val = "<a href='/starlogonova/te/FishAlgae' target='_blank'><img src='/static/ndf/images/FishAlgae-Telugu.jpg' alt='Star Logo Thumbnail'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });




                          $("#insert_AST_U1_L4_DA1_Ani_En").click(function(event){
                            

                            tool_val = "<a href='/Rotation_of_Earth_Animation/en/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth.jpg' alt='Rotation_of_Earth'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U1_L4_DA2_WTT_En").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Element_Hunt_Activity/en/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth.jpg' alt='Rotation_of_Earth'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA1_Ani_En").click(function(event){
                            

                            tool_val = "<a href='/Motions_of_the_Moon_Animation/en/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon.jpg' alt='Motions_of_Moon'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA2_MT_En").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Moon_Track/en/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon.jpg' alt='Motions_of_Moon'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA1_Ani_En").click(function(event){
                            

                            tool_val = "<a href='/Solar_System_Animation/en/' target='_blank'><img src='/static/ndf/images/Solar_System.jpg' alt='Solar_System'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA2_PT_En").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Planet_Trek_Activity/en/' target='_blank'><img src='/static/ndf/images/Solar_System.jpg' alt='Solar_System'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U1_L4_DA1_Ani_Hi").click(function(event){
                            

                            tool_val = "<a href='/Rotation_of_Earth_Animation/hi/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth_hi.png' alt=' Rotation_of_Earth_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U1_L4_DA2_WTT_Hi").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Element_Hunt_Activity/hi/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth_hi.png' alt='Rotation_of_Earth_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA1_Ani_Hi").click(function(event){
                            

                            tool_val = "<a href='/Motions_of_the_Moon_Animation/hi/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon_hi.png' alt='Motions_of_Moon_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA2_MT_Hi").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Moon_Track/hi/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon_hi.png' alt='Motions_of_Moon_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA1_Ani_Hi").click(function(event){
                            

                            tool_val = "<a href='/Solar_System_Animation/hi/' target='_blank'><img src='/static/ndf/images/Solar_System_hi.png' alt='Solar_System_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA2_PT_Hi").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Planet_Trek_Activity/hi/' target='_blank'><img src='/static/ndf/images/Solar_System_hi.png' alt='Solar_System_hi'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U1_L4_DA1_Ani_Te").click(function(event){
                            

                            tool_val = "<a href='/Rotation_of_Earth_Animation/te/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth_te.png' alt='Rotation_of_Earth_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U1_L4_DA2_WTT_Te").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Element_Hunt_Activity/te/' target='_blank'><img src='/static/ndf/images/Rotation_of_Earth_te.png' alt='Rotation_of_Earth_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA1_Ani_Te").click(function(event){
                            

                            tool_val = "<a href='/Motions_of_the_Moon_Animation/te/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon_te.png' alt='Motions_of_Moon_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U2_L8_DA2_MT_Te").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Moon_Track/te/' target='_blank'><img src='/static/ndf/images/Motions_of_Moon_te.png' alt='Motions_of_Moon_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA1_Ani_Te").click(function(event){
                            

                            tool_val = "<a href='/Solar_System_Animation/te/' target='_blank'><img src='/static/ndf/images/Solar_System_te.png' alt='Solar_System_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AST_U3_L11_DA2_PT_Te").click(function(event){
                            

                            tool_val = "<a href='/Astroamer_Planet_Trek_Activity/te/' target='_blank'><img src='/static/ndf/images/Solar_System_te.png' alt='Solar_System_te'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });


                          $("#insert_Build_An_Atom_en").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_An_Atom/en/Build_An_Atom.html' target='_blank'><img src='/static/ndf/images/BuildanAtom_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_Build_An_Atom_hi").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_An_Atom/hi/Build_An_Atom.html' target='_blank'><img src='/static/ndf/images/BuildanAtom_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_Build_An_Atom_te").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_An_Atom/te/Build_An_Atom.html' target='_blank'><img src='/static/ndf/images/BuildanAtom_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_Build_A_Molecule_en").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_A_Molecule/en/Build_A_Molecule.html' target='_blank'><img src='/static/ndf/images/BuildaMolecule_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_Build_A_Molecule_hi").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_A_Molecule/hi/Build_A_Molecule.html' target='_blank'><img src='/static/ndf/images/BuildaMolecule_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_Build_A_Molecule_te").click(function(event){
                            

                            tool_val = "<a href='/PhET-customized/Build_A_Molecule/te/Build_A_Molecule.html' target='_blank'><img src='/static/ndf/images/BuildaMolecule_en.png' alt='Build an Atom_en'  height='1000px' width='1000px' >"
                            
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_AGES_PUZZLE").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<iframe src='/ages_puzzle' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });

                          $("#insert_FACTORISATION_PUZZLE").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<iframe src='/factorisation' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
                            $('#group_imgs_on_modal').foundation('reveal', 'close');
                          });
                          $("#insert_COINS_PUZZLE").click(function(event){
                            //ost_text_gallery = $('#paste-ost-gallery').val();
                            //ost_text_file = $('#paste-ost-captions').val();
                            tool_val = "<iframe src='/coins_linear_eqn' style='height:100vh;width:100%'></iframe>"
                            // split_word = ost_text_val.slice(0, 18) + "gallery=" + ost_text_gallery + "&amp;file=/ost/" + ost_text_file+"'"+ ost_text_val.slice(18);
                            // alert(split_word)
                             CKEDITOR.instances[textAreaId].insertHtml(tool_val);
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
