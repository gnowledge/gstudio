import os
from html import HTML
from xml.dom import minidom
from bs4 import BeautifulSoup
import shutil
from django.template.defaultfilters import slugify
from gnowsys_ndf.settings import EPUB_store
from gnowsys_ndf.ndf.models import node_collection


oebps_files = ["Fonts", "Audio", "Images", "Videos", "Text", "Styles", "Misc"]

def create_subfolders(root,subfolder_names_list):
    for subfolder in subfolder_names_list:
        os.makedirs(os.path.join(root, subfolder))

def create_container_file(meta_path):
    doc = minidom.Document()
    container = doc.createElement("container")
    container.setAttribute("version", "1.0")
    container.setAttribute("xmlns", "urn:oasis:names:tc:opendocument:xmlns:container")
    rootfiles = doc.createElement("rootfiles")
    rootfile = doc.createElement("rootfile")
    rootfile.setAttribute("file-path","OEBPS/content.opf")
    rootfile.setAttribute("media-type","application/oebps-package+xml")
    rootfiles.appendChild(rootfile)
    container.appendChild(rootfiles)
    doc.appendChild(container)
    xml_str = doc.toprettyxml(indent="  ", encoding='UTF-8')
    with open(os.path.join(meta_path,"container.xml"), "w+") as container_file:
        container_file.write(xml_str)

def create_mimetype(epub_name):
    with open(os.path.join(epub_name,"mimetype"), "w+") as mimetype_file:
        mimetype_file.write("application/epub+zip")

def update_ncx(p):
    """
    This will update toc.ncx
    """
    pass

def update_nav(n):
    """
    This will update nav.html
    """
    pass
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
    all_src = content_soup.find_all(src=True)
    # Fetching the files
    for each_src in all_src:
        src_attr = each_src["src"]
        if src_attr.startswith("/media"): # file
            src_attr = src_attr.split("media/")[-1]
            file_extension = src_attr.rsplit(".",1)[-1]
            file_node = node_collection.find_one({"$or": [{'if_file.original.relurl': src_attr},
                {'if_file.mid.relurl': src_attr},{'if_file.thumbnail.relurl': src_attr}]})
            if file_node:
                mimetype_val = file_node.if_file.mime_type.lower()
                # mimetype can be audio|video|image
                # file_name = slugify(file_node.name) + "." + file_extension
                file_name = file_node.name
                if "image" in mimetype_val:
                    each_src["src"] = (os.path.join("..", "Images", file_name))
                    shutil.copyfile("/data/media/" + src_attr, (os.path.join(path, "..", "Images", file_name)))
                elif "video" in mimetype_val:
                    each_src["src"] = (os.path.join("..", "Videos", file_name))
                    shutil.copyfile("/data/media/" + src_attr, (os.path.join(path, "..", "Videos", file_name)))
                elif "audio" in mimetype_val:
                    each_src["src"] = (os.path.join("..", "Images", file_name))
                    shutil.copyfile("/data/media/" + src_attr, (os.path.join(path, "..", "Images", file_name)))
    # print content_soup
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
    import ipdb; ipdb.set_trace()
    for each_obj in obj.values():
        name = each_obj['name'].strip()
        name_slugified = slugify(each_obj['name'].strip())
        content_val = (each_obj["content"]).encode('ascii', 'ignore')
        new_content = parse_content(path, BeautifulSoup(content_val, 'html.parser'))
        # new_content = parse_content(content_val)
        print new_content
        with open("/static/ndf/epub_activity_skeleton.html", "r") as base_file_obj:
            html_doc = base_file_obj.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            soup.body.append(new_content)
        with open(os.path.join(path, name_slugified +".html"), "w") as content_file_obj:
            content_file_obj.write(soup.prettify("utf-8"))

        # update_ncx(each_obj["name"])
        # update_nav(each_obj["name"])
    pass


def fill_from_static():
    """
    This will fill:
        OEBPS/Styles
        OEBPS/Fonts
        OEBPS/Misc
    """
    pass

def update_content_file():
    """
    This will update content.opf
    """
    pass

def create_epub(epub_name, content_list):
    epub_root = os.path.join(EPUB_store, slugify(epub_name))
    os.makedirs(epub_root)
    os.makedirs(os.path.join(epub_root, "META-INF"))
    os.makedirs(os.path.join(epub_root, "OEBPS"))
    create_mimetype(epub_root)
    create_container_file(os.path.join(epub_root, "META-INF"))
    create_subfolders(os.path.join(epub_root,"OEBPS"),oebps_files)
    build_html(os.path.join(epub_root,"OEBPS", "Text"),content_list)
    # create_content_file(os.path.join(epub_name,"OEBPS"),content_list)
    # create_ncx_file(os.path.join(epub_name,"OEBPS"),content_list)
    fill_from_static()

# create_epub("Lesson", [{"name": "f1","content":"<p>Rachana</p>"}, 
# {"name": "f2","content": "<a>Hello</a>"}])
