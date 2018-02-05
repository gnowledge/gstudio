import os
import zipfile
import json
import shutil
import re
from datetime import datetime
from bs4 import BeautifulSoup, CData
from html import HTML
import urlparse
from django.template.defaultfilters import slugify
from gnowsys_ndf.settings import GSTUDIO_EPUBS_LOC_PATH
from gnowsys_ndf.ndf.models import node_collection
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


oebps_files = ["Fonts", "Audios", "Images", "Videos", "Text", "Styles", "Misc"]
oebps_path = None
tool_mapping = {}

with open("/static/ndf/epub/tool_mapping.json", "r") as tool_paths:
    global tool_mapping
    tool_mapping = json.loads(tool_paths.read())

# tool_mapping = {'policequad': 'modules/Tools/Police Quad/index.html',
#                 'turtleblocksjs': 'modules/Tools/Turtle Blocks/index.html',
#                 'biomechanic': 'modules/Tools/Bio- Mechanic/index.html'}

def create_subfolders(root,subfolder_names_list):
    for subfolder in subfolder_names_list:
        os.makedirs(os.path.join(root, subfolder))

def create_container_file(meta_path):
    with open("/static/ndf/epub/container.xml", "r") as base_container_obj:
        html_doc = base_container_obj.read()
        soup = BeautifulSoup(html_doc, 'xml')

    with open(os.path.join(meta_path,"container.xml"), "w+") as container_file:
        container_file.write(soup.prettify("utf-8"))

def create_mimetype(epub_name):
    with open(os.path.join(epub_name,"mimetype"), "w+") as mimetype_file:
        mimetype_file.write("application/epub+zip")

def create_update_ncx(file_display_name, file_slugified_name):
    """
    This will update toc.ncx by inserting "navPoint"
      <navMap>
        <navPoint id="navPoint-1" playOrder="1">
          <navLabel>
            <text>Introduction</text>
          </navLabel>
          <content src="Text/Gstudio_Introduction1_EBL10.xhtml"/>
        </navPoint>
    """
    soup = None
    file_path = "Text/"+ file_slugified_name + ".xhtml"
    with open("/static/ndf/epub/toc.ncx", "r") as base_ncx_obj:
        html_doc = base_ncx_obj.read()
        soup = BeautifulSoup(html_doc, 'xml')

    ncx_file_path = os.path.join(oebps_path,"toc.ncx")

    if os.path.exists(ncx_file_path):
        with open(ncx_file_path, "r") as existing_ncx_file:
            ncx_doc = existing_ncx_file.read()
            soup = BeautifulSoup(ncx_doc, 'xml')

    with open(ncx_file_path, "w+") as ncx_file:
        navMap_ele = soup.find("navMap")
        navpoint_ctr_val = len(soup.find_all("navPoint")) + 1
        navPoint_ele = soup.new_tag("navPoint", 
            id="navPoint"+(navpoint_ctr_val).__str__(),
            # playorder=(navpoint_ctr_val).__str__()
            )
        navLabel_ele = soup.new_tag("navLabel")
        navLabel_text_ele = soup.new_tag("text")
        navLabel_text_ele.string = file_display_name
        navLabel_ele.append(navLabel_text_ele)
        navPoint_ele.append(navLabel_ele)
        content_ele = soup.new_tag("content", src=file_path)
        navPoint_ele.append(content_ele)
        navMap_ele.append(navPoint_ele)
        ncx_file.write(soup.prettify("utf-8"))

def create_update_nav(file_display_name, filename, path):
    """
    This will update nav.xhtml
    """
    soup = None
    with open("/static/ndf/epub/nav.xhtml", "r") as base_nav_obj:
        html_doc = base_nav_obj.read()
        soup = BeautifulSoup(html_doc, 'xml')
    nav_file_path = os.path.join(path,"nav.xhtml")
    if os.path.exists(nav_file_path):
        with open(nav_file_path, "r") as existing_nav_file:
            nav_doc = existing_nav_file.read()
            soup = BeautifulSoup(nav_doc, 'xml')

    with open(nav_file_path, "w+") as nav_file:
        # find <ol> with id "toc-list"
        nav_list = soup.find("ol", {"id": "toc-list"})
        new_nav = soup.new_tag("li")
        new_nav_link = soup.new_tag("a", href="../Text/"+filename + ".xhtml")
        new_nav_link.string = file_display_name
        new_nav.append(new_nav_link)
        soup.body.nav.ol.append(new_nav)
        nav_file.write(soup.prettify("utf-8"))

def create_update_content_file(file_name_wo_ext, file_loc, media_type,  epub_name, is_non_html=False):
    """
    This will update content.opf
    Make use of : oebps_path
    file_loc : Text|Styles|Misc
    media-type: text/css|text/javascript
    """
    
    file_name_w_ext = file_name_wo_ext
    file_path = os.path.join(file_loc,file_name_wo_ext)
    if not is_non_html:
        file_path = os.path.join(file_loc,file_name_wo_ext+".xhtml")
        file_name_w_ext = file_name_wo_ext + ".xhtml"
    soup = None
    with open("/static/ndf/epub/content.opf", "r") as base_content_pkg_file:
        html_doc = base_content_pkg_file.read()
        soup = BeautifulSoup(html_doc, 'lxml')

    content_pkg_file_path = os.path.join(oebps_path,"content.opf")
    if os.path.exists(content_pkg_file_path):
        with open(content_pkg_file_path, "r") as existing_content_file:
            content_doc = existing_content_file.read()
            soup = BeautifulSoup(content_doc, 'lxml')

    with open(content_pkg_file_path, "w+") as content_pkg_file_obj:
        manifest_container = soup.find("manifest")


        new_item = soup.new_tag("item", id=file_name_w_ext, href=file_path)
        new_item.attrs.update({'media-type': media_type})
        manifest_container.append(new_item)
        if file_loc == "Text":
            # update <spine> only for .xhtml files
            spine_container = soup.find("spine")
            new_itemref = soup.new_tag("itemref", idref=file_name_wo_ext+".xhtml")
            spine_container.append(new_itemref)

        # print soup
        content_pkg_file_obj.write(soup.prettify("utf-8"))

def update_content_metadata(node_id, date_value, epub_name):

    soup = None
    content_pkg_file_path = os.path.join(oebps_path,"content.opf")
    if os.path.exists(content_pkg_file_path):
        with open(content_pkg_file_path, "r") as existing_content_file:
            content_doc = existing_content_file.read()
            soup = BeautifulSoup(content_doc, 'lxml')
    if soup:
        # print "\n\n: soup: ", soup
        with open(content_pkg_file_path, "w+") as content_meta_file_obj:
            meta_datetimestamp = soup.find('meta',{"property":"dcterms:modified"})
            meta_datetimestamp.string = date_value
            metadata_tag = soup.find('metadata')
            dc_ident = soup.find('dc:identifier',{"id": "BookId"})
            dc_ident.string = node_id
            dc_title = soup.find('dc:title',{"id": "bookTitle"})
            dc_title.string =  epub_name
            content_meta_file_obj.write(soup.prettify("utf-8"))

def copy_file_and_update_content_file(file_node, source_ele, src_val, epub_name):
    mimetype_val = file_node.if_file.mime_type.lower()
    # mimetype can be audio|video|image
    # file_name = slugify(file_node.name) + "." + file_extension
    file_name = file_node.name
    file_loc = None
    if "image" in mimetype_val:
        file_loc = "Images"
    elif "video" in mimetype_val:
        file_loc = "Videos"
    elif "audio" in mimetype_val:
        file_loc = "Audios"
    elif "text" in mimetype_val or "application" in mimetype_val:
        file_loc = "Misc"
    source_ele[src_val] = (os.path.join('..',file_loc, file_name))
    shutil.copyfile("/data/media/" + file_node['if_file']['original']['relurl'], os.path.join(oebps_path, file_loc, file_name))
    create_update_content_file(file_name, file_loc, mimetype_val, epub_name, is_non_html=True)

def find_file_from_media_url(source_attr):
    source_attr = source_attr.split("media/")[-1]
    file_extension = source_attr.rsplit(".",1)[-1]
    file_node = node_collection.find_one({"$or": [{'if_file.original.relurl': source_attr},
        {'if_file.mid.relurl': source_attr},{'if_file.thumbnail.relurl': source_attr}]})
    return file_node

def parse_content(path, content_soup, epub_name):
    """
    This will fill:
        OEBPS/Images
        OEBPS/Audios
        OEBPS/Videos
    Steps:
        1. Update links
        2. Copy media file object
    """
    # all_a = content_soup.find_all('a', href=True)
    # remove bower links

    tool_mapping_keys = tool_mapping.keys()
    scoped_style = content_soup.find_all('style', {'scoped': ''})
    static_imports = content_soup.find_all('script', src=re.compile('static'))
    for each_style in scoped_style:
        each_style.extract()
    for each_script in static_imports:
        each_script.extract()


    # ==== updating media elements ==== 
    #Transcipt file
    all_transcript_data = content_soup.find_all(attrs={'class':'transcript'})
    for each_transcript in all_transcript_data:
        trans_file_node = None
        data_ele = each_transcript.findNext('object',data=True)
        if data_ele:
            if 'media' in data_ele['data']:
                trans_file_node = find_file_from_media_url(data_ele['data'])
                copy_file_and_update_content_file(trans_file_node, data_ele, 'data', epub_name)


    # all_src = content_soup.find_all(src=True)
    all_src = content_soup.find_all(src=re.compile('media|readDoc'))
    # Fetching the files
    for each_src in all_src:
        src_attr = each_src["src"]
        file_node = None
        if src_attr.startswith("/media"): # file
            file_node = find_file_from_media_url(src_attr)

        if "readDoc" in src_attr:
            split_src = src_attr.split('/')
            node_id = split_src[split_src.index('readDoc') + 1]
            file_node = node_collection.one({'_id': ObjectId(node_id)})

        if file_node:
            copy_file_and_update_content_file(file_node, each_src, 'src', epub_name)

    all_iframes = content_soup.find_all('iframe',src=True)
    for each_iframe in all_iframes:
        iframe_src_attr = each_iframe["src"]
        new_iframe_src = iframe_src_attr
        if iframe_src_attr:
            if "assessment.AssessmentOffered" in iframe_src_attr:
                # ==== updating assessment iframes ==== 
                new_iframe_src = iframe_src_attr
                parsed = urlparse.urlparse(iframe_src_attr)
                new_iframe_src = parsed._replace(netloc="localhost:8888", path="/oea/")
                each_iframe["src"] = new_iframe_src.geturl()
            else:
                # ==== updating App iframes ==== 
                for each_tool_key,each_tool_val in tool_mapping.items():
                    if each_tool_key in iframe_src_attr:
                        new_iframe_src = each_tool_val
                each_iframe["src"] = new_iframe_src


    all_tool_links = content_soup.find_all('a',href=True)
    for each_tool_link in all_tool_links:
        tool_href = each_tool_link["href"]
        new_tool_link = tool_href
        if tool_href:
            for each_tool_key,each_tool_val in tool_mapping.items():
                if each_tool_key in tool_href:
                    new_tool_link = each_tool_val
            each_tool_link["href"] = new_tool_link


    all_img = content_soup.find_all('img',src=True)
    for each_img in all_img:
        img_src_attr = each_img["src"]
        file_name = img_src_attr.split("/")[-1]
        if "/static/ndf/images" in img_src_attr:
            each_img["src"] = "../Images/"+ file_name
            shutil.copyfile(img_src_attr, os.path.join(oebps_path, "Images", file_name))
            # idnetify the mimetype and add accordingly in following line
            create_update_content_file(file_name, "Images", "image/png", epub_name, is_non_html=True)

    return content_soup

def build_html(path,obj, epub_name):
    """
    obj = collection_dict
    {1: node}
    This will fill:
        OEBPS/Text
    Steps:
        1. Clone base-skeleton html file
        2. Build <body> by adding content object
        3. parse_content
    
    """

    soup = None
    for each_obj in obj.values():
        name = each_obj['name'].strip()
        name_slugified = slugify(name)
        # content_val = (each_obj["content"]).encode('ascii', 'ignore')
        content_val = each_obj["content"]
        new_content = parse_content(path, BeautifulSoup(content_val, 'html.parser'), epub_name)
        # new_content = parse_content(content_val)
        with open("/static/ndf/epub/epub_activity_skeleton.xhtml", "r") as base_file_obj:
            html_doc = base_file_obj.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            soup.body.append(new_content)
        with open(os.path.join(path, name_slugified +".xhtml"), "w") as content_file_obj:
            content_file_obj.write(soup.prettify("utf-8"))

        # update_ncx(each_obj["name"])
        create_update_nav(name, name_slugified, path)
        create_update_content_file(name_slugified, "Text",  epub_name, "application/xhtml+xml")
        create_update_ncx(name,name_slugified)
    pass

def fill_from_static():
    """
    This will fill:
        OEBPS/Styles
        OEBPS/Fonts
        OEBPS/Misc
        from /static/ndf/epub/epub_static_dependencies.json
    """
    # clean bower links from stylesheets
    clean_css_files = ['/static/ndf/css/clix-activity-styles.css', '/static/ndf/css/rubik-fonts.css']

    css_rf = open('/static/ndf/css/clix-activity-styles.css', 'r')
    tmp_file = css_rf.readlines()
    css_rf.close()

    with open('/tmp/clix-activity-styles.css', 'w+') as tmp_css_file:
        for each_css_line in tmp_file:
            if '@import' not in each_css_line:
                tmp_css_file.write(each_css_line)

    fonts_css_rf = open('/static/ndf/css/rubik-fonts.css', 'r')
    tmp_fonts_file = fonts_css_rf.readlines()
    fonts_css_rf.close()

    rubik_font_line = '/static/ndf/bower_components/rubik-googlefont'
    with open('/tmp/rubik-fonts.css', 'w+') as tmp_fonts_css_file:
        for each_fontscss_line in tmp_fonts_file:
            if rubik_font_line in each_fontscss_line:
                each_fontscss_line = each_fontscss_line.replace(rubik_font_line, '../Fonts')
            tmp_fonts_css_file.write(each_fontscss_line)

    with open('/static/ndf/epub/epub_static_dependencies.json') as dependencies_file:
        dependencies_data = json.load(dependencies_file)
        for dep_type, dep_list in dependencies_data.items():
            for each_dep in dep_list:
                tmp_filename = each_dep.split('/')[-1]
                new_filepath = os.path.join(oebps_path, dep_type, tmp_filename)
                if each_dep in clean_css_files:
                    shutil.copyfile('/tmp/'+tmp_filename, new_filepath)
                else:
                    shutil.copyfile(each_dep, new_filepath)
            # [shutil.copyfile(each_dep, os.path.join(oebps_path, dep_type, each_dep.split('/')[-1])) for each_dep in dep_list]

def epub_dump(path, ziph):
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            absname = os.path.abspath(os.path.join(root, file))
            arcname = absname[len(abs_src) + 1:]
            ziph.write(absname, arcname)

def create_epub(node_obj):
    epub_disp_name = None
    epub_name = node_obj.name
    if node_obj.altnames:
        epub_disp_name = node_obj.altnames
    else:
        epub_disp_name = node_obj.name
    content_list = node_obj.collection_dict
    if not os.path.exists(GSTUDIO_EPUBS_LOC_PATH):
        os.makedirs(GSTUDIO_EPUBS_LOC_PATH)
    datetimestamp = datetime.now().isoformat()
    epub_name = slugify(epub_name + "_"+ str(datetimestamp))
    epub_root = os.path.join(GSTUDIO_EPUBS_LOC_PATH, epub_name)
    os.makedirs(epub_root)
    os.makedirs(os.path.join(epub_root, "META-INF"))
    global oebps_path
    oebps_path = os.path.join(epub_root, "OEBPS")
    os.makedirs(oebps_path)
    create_mimetype(epub_root)
    create_container_file(os.path.join(epub_root, "META-INF"))
    create_subfolders(os.path.join(epub_root,"OEBPS"),oebps_files)
    build_html(os.path.join(epub_root,"OEBPS", "Text"),content_list, epub_name)
    update_content_metadata(str(node_obj._id), datetimestamp, epub_disp_name)
    # create_content_file(os.path.join(epub_name,"OEBPS"),content_list)
    # create_ncx_file(os.path.join(epub_name,"OEBPS"),content_list)
    fill_from_static()
    print "Successfully created epub extraction: ", epub_name
    zipf = zipfile.ZipFile(epub_root + '.epub', 'w', zipfile.ZIP_DEFLATED)
    epub_dump(epub_root, zipf)
    zipf.close()
    print "Successfully created epub: ", epub_name
    return str(epub_root + '.epub')

def check_ip_validity():
    import re
    if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):  
        print "Valid IP"  
    else:
        print "Invalid IP"

