import os
import zipfile
import json
from xml.dom import minidom
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
from html import HTML
from django.template.defaultfilters import slugify
from gnowsys_ndf.settings import GSTUDIO_EPUBS_LOC_PATH
from gnowsys_ndf.ndf.models import node_collection
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


oebps_files = ["Fonts", "Audios", "Images", "Videos", "Text", "Styles", "Misc"]
oebps_path = None
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

# =====


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
    pass

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

def create_update_content_file(file_name_wo_ext, file_loc, media_type, is_non_html=False):
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
        soup = BeautifulSoup(html_doc, 'xml')

    content_pkg_file_path = os.path.join(oebps_path,"content.opf")
    if os.path.exists(content_pkg_file_path):
        with open(content_pkg_file_path, "r") as existing_content_file:
            content_doc = existing_content_file.read()
            soup = BeautifulSoup(content_doc, 'xml')

    with open(content_pkg_file_path, "w+") as content_pkg_file_obj:
        manifest_container = soup.find("manifest")
        # print soup
        new_item = soup.new_tag("item", id=file_name_w_ext, href=file_path)
        new_item.attrs.update({'media-type': media_type})
        manifest_container.append(new_item)
        if file_loc == "Text":
            # update <spine> only for .xhtml files
            spine_container = soup.find("spine")
            new_itemref = soup.new_tag("itemref", idref=file_name_wo_ext+".xhtml")
            spine_container.append(new_itemref)
        content_pkg_file_obj.write(soup.prettify("utf-8"))


def update_content_metadata(node_id, date_value):

    soup = None
    content_pkg_file_path = os.path.join(oebps_path,"content.opf")
    if os.path.exists(content_pkg_file_path):
        with open(content_pkg_file_path, "r") as existing_content_file:
            content_doc = existing_content_file.read()
            soup = BeautifulSoup(content_doc, 'xml')
    if soup:
        with open(content_pkg_file_path, "w+") as content_meta_file_obj:
            meta_datetimestamp = soup.find('meta',{"property":"dcterms:modified"})
            meta_datetimestamp.string = date_value
            dc_ident = soup.find('identifier',{"id": "BookId"})
            dc_ident.string = node_id
            content_meta_file_obj.write(soup.prettify("utf-8"))

# =====
def parse_content(path, content_soup):
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
    # ==== updating media elements ==== 
    all_src = content_soup.find_all(src=True)
    # Fetching the files
    for each_src in all_src:
        src_attr = each_src["src"]
        file_node = None
        if src_attr.startswith("/media"): # file
            src_attr = src_attr.split("media/")[-1]
            file_extension = src_attr.rsplit(".",1)[-1]
            file_node = node_collection.find_one({"$or": [{'if_file.original.relurl': src_attr},
                {'if_file.mid.relurl': src_attr},{'if_file.thumbnail.relurl': src_attr}]})

        if "readDoc" in src_attr:
            split_src = src_attr.split('/')
            node_id = split_src[split_src.index('readDoc') + 1]
            file_node = node_collection.one({'_id': ObjectId(node_id)})


        if file_node:
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
            elif "text" in mimetype_val:
                file_loc = "Misc"
            each_src["src"] = (os.path.join('..',file_loc, file_name))
            shutil.copyfile("/data/media/" + file_node['if_file']['original']['relurl'], os.path.join(oebps_path, file_loc, file_name))
            create_update_content_file(file_name, file_loc, mimetype_val, is_non_html=True)

    # ==== updating assessment iframes ==== 

    # ==== updating App iframes ==== 

    return content_soup

def build_html(path,obj):
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
        content_val = (each_obj["content"]).encode('ascii', 'ignore')
        new_content = parse_content(path, BeautifulSoup(content_val, 'html.parser'))
        # new_content = parse_content(content_val)
        with open("/static/ndf/epub/epub_activity_skeleton.xhtml", "r") as base_file_obj:
            html_doc = base_file_obj.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            soup.body.append(new_content)
        with open(os.path.join(path, name_slugified +".xhtml"), "w") as content_file_obj:
            content_file_obj.write(soup.prettify("utf-8"))

        # update_ncx(each_obj["name"])
        create_update_nav(name, name_slugified, path)
        create_update_content_file(name_slugified, "Text", "application/xhtml+xml")
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
    with open('/static/ndf/epub/epub_static_dependencies.json') as dependencies_file:
        dependencies_data = json.load(dependencies_file)
        for dep_type, dep_list in dependencies_data.items():
            [shutil.copyfile(each_dep, os.path.join(oebps_path, dep_type, each_dep.split('/')[-1])) for each_dep in dep_list]


def epub_dump(path, ziph):
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            absname = os.path.abspath(os.path.join(root, file))
            arcname = absname[len(abs_src) + 1:]
            ziph.write(absname, arcname)

def create_epub(node_obj):
    epub_name = node_obj.name
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
    build_html(os.path.join(epub_root,"OEBPS", "Text"),content_list)
    update_content_metadata(str(node_obj._id), datetimestamp)
    # create_content_file(os.path.join(epub_name,"OEBPS"),content_list)
    # create_ncx_file(os.path.join(epub_name,"OEBPS"),content_list)
    fill_from_static()
    print "Successfully created epub: ", epub_name
    zipf = zipfile.ZipFile(epub_root + '.epub', 'w', zipfile.ZIP_DEFLATED)
    epub_dump(epub_root, zipf)
    zipf.close()

# create_epub(node.name, node.collection_dict)

def check_ip_validity():
    import re
    if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):  
        print "Valid IP"  
    else:
        print "Invalid IP"

