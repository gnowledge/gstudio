from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views import *
from gnowsys_ndf.settings import *

active_node = node_collection.collection.GSystem()
tags = []
group_id = '58bd05c45a162d0148f65c71'
active_node.fill_gstystem_values(tags = tags)
active_node.name = unicode('Photo_Slider')
active_node.group_set = [ObjectId('58bd05c45a162d0148f65c71')]
active_node.type_of = [ObjectId('58d24b6af9d307025372fda6')]
active_node.created_by = 1
active_node_content = '''
<script src="/static/ndf/js/slider.js"></script>
<script src="/static/ndf/bower_components/slick/slick.js"></script>
<!--script src="/static/ndf/bower_components/slick-carousel/slick/slick.js"></script>
<script src="/static/ndf/bower_components/slick-carousel/js/scripts.js"></script-->

<style>
html, body { 
            margin: 0;    
            padding: 0;   
          }   
    
          * {
            box-sizing: border-box;
          }
    
          .slider {
              width: 50%;
              margin: 100px auto;
          }
    
          .slick-slide {
            margin: 0px 20px;
          }
    
          .slick-slide img {
            width: 100%;
          }
    
          .slick-prev:before,
          .slick-next:before {
            color:  #713558;
            font-size: 2vw;
          }
    
    
          .slick-slide {
            transition: all ease-in-out .3s;
            opacity: .2;
          }
        
          .slick-active {
            opacity: 0.75;
          }
    
          .slick-current {
            opacity: 1;
          }
         // #slider_ul{
         //       @media screen and (min-width: 1024px) {
          //        width:calc(900px + 2vmin);
            //    }
             //   @media screen and (min-width: 768px) {
               //   width:calc(600px + 2vmin);
                //}
                //@media screen and (max-width:425px){
                 //  width:calc(300px + 2vmin);
                //}
          //}
          .slick-dots li button:before
{
    
    opacity: 1 !important; 
    color: white;

    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.slick-dots li.slick-active button:before
{
    opacity: 1 !important;
    color: white;
}
.slick-dots li.slick-active button::after
{
    opacity: 1 !important;
    color: white;
}
.slick-dots li{
  font-size:2vw !important;
}
.slick-dots li button::before {
  font-size: 1vw !important;
}
</style>
<!--section class="vertical-center slider" id="slider_ul" style="width:900px"></section-->
<section class="single-item slider" id="slider_ul">Sliders</section>
'''
#active_node_content = u'<style type="text/css">html, body {\r\nmargin: 0;\r\npadding: 0;\r\n}\r\n* {\r\nbox-sizing: border-box;\r\n}\r\n.slider {\r\nwidth: 50%;\r\nmargin: 100px auto;\r\n}\r\n.slick-slide {\r\nmargin: 0px 20px;\r\n}\r\n.slick-slide img {\r\nwidth: 100%;\r\n}\r\n.slick-prev:before,\r\n.slick-next:before {\r\ncolor: #713558;\r\n}\r\n\r\n.slick-slide {\r\ntransition: all ease-in-out .3s;\r\nopacity: .2;\r\n}\r\n.slick-active {\r\nopacity: .5;\r\n}\r\n.slick-current {\r\nopacity: 1;\r\n}\r\nsection{\r\n@media screen and (min-width: 1024px) {\r\nwidth:calc(900px + 2vmin);\r\n}\r\n@media screen and (min-width: 768px) {\r\nwidth:calc(600px + 2vmin);\r\n}\r\n@media screen and (max-width:425px){\r\nwidth:calc(300px + 2vmin);\r\n}\r\n}\r\n</style>\r\n<script>\r\nfunction image_list(){\r\nvar image = [\'/media/4/7/2/c31079fcc30ab3b6b7e34c15d15d192a6012cba11aac317ebf72cdb2cb5c0.png\',\'/media/a/2/c/73c197b755bd98fba342f66f10ecfee03c7d283bbdf258a7c3fef291fb2c7.png\'];\r\nvar i = 0;\r\nfor(i =0;i < image.length;i++){\r\n//var listitem_div = document.createElement(\'DIV\');\r\n//listitem_div.id = i;\r\nvar image_element = document.createElement(\'IMG\');\r\nimage_element.setAttribute(\'src\',image[i]);\r\n//listitem_div.appendChild(image_element);\r\ndocument.getElementById("slider_ul").appendChild(image_element);\r\n}\r\n//$( "#slider_ul" ).load(window.location.href + " #slider_ul" );\r\n// location.reload();\r\n}\r\n}\r\n</script><!--section class="vertical-center slider" id="slider_ul" style="width:900px"></section-->\r\n<section class="vertical-center slider" id="slider_ul">Sliders</section>\r\n<script>\r\n$(document).on(\'ready\', function() {\r\n$(".vertical-center").slick({\r\ndots: true,\r\nvertical: true,\r\ncenterMode: true,\r\n});\r\n});\r\n</script>'

active_node.content = unicode(active_node_content)
#active_node.content = active_node_content.encode('ascii', 'xmlcharrefreplace')
active_node.save(groupid = group_id)
print active_node


