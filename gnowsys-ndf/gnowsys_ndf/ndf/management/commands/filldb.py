''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from bson import ObjectId

from django_mongokit import get_database

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.models import GSystemType
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS

####################################################################################################################

class Command(BaseCommand):
    help = "Inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, GSystemType"

    def handle(self, *args, **options):
        db = get_database()
        hm = HistoryManager()
        rcsobj = RCS()

        db.drop_collection(GSystem.collection_name)
        db.drop_collection(GSystemType.collection_name)
        
        # Creating a GSystemType document as 'Wikipage'
        c_gt = db[GSystemType.collection_name]
        o_gt = c_gt.GSystemType()
        o_gt.name = u"Wikipage"
        o_gt.member_of = u"GSystemType"
        o_gt.save()

        if not hm.create_or_replace_json_file(o_gt):
            c_gt.remove({'_id': o_gt._id})
        else:
            fp = hm.get_file_path(o_gt)
            rcsobj.checkin(fp, 0, "This document("+str(o_gt.name)+") is of GSystemType.", "-i")
        

        # Extracting document-id
        objid = c_gt.GSystemType.one({'name': u"Wikipage"})._id

        # Creating five GSystem documents with dummy values
        c_gs = db[GSystem.collection_name]
        
        o_gs = c_gs.GSystem()
        o_gs.name = unicode("math_functions")
        o_gs.tags.append(unicode("math_functions"))
        o_gs.member_of = unicode("Wikipage")
        o_gs.gsystem_type.append(objid)
        o_gs.content_org = unicode("MATH FUNCTIONS\r\n\r\n* Fractions and Log\r\n** code\r\n#+BEGIN_EXAMPLE\r\n$\\frac{1}{k}\\log_2 c(f)$\r\n$\\frac{1}{k}\\log_2 c(f)$\r\n#+END_EXAMPLE\r\n** Result\r\n$\\frac{1}{k}\\log_2 c(f)$\r\n$\\frac{1}{k}\\log_2 c(f)$\r\n\r\n\r\n* Binomial coefficient\r\n** Code\r\n#+BEGIN_EXAMPLE\r\n$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\r\n#+END_EXAMPLE\r\n** Result\r\n$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\r\n\r\n\r\n* Continued fractions\r\n** Code\r\n#+BEGIN_EXAMPLE\r\n$\\cfrac{1}{\\sqrt{2}+\r\n\\cfrac{1}{\\sqrt{2}+\r\n\\cfrac{1}{\\sqrt{2}+\\dotsb}}}$\r\n$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\r\n#+END_EXAMPLE\r\n** Result\r\n$\\cfrac{1}{\\sqrt{2}+\r\n\\cfrac{1}{\\sqrt{2}+\r\n\\cfrac{1}{\\sqrt{2}+\\dotsb}}}$\r\n$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\r\n\r\n\r\n* Big brackets\r\n** Code \r\n#+BEGIN_EXAMPLE\r\n$\\biggl[\\sum_i a_i\\Bigl\\lvert\\sum_j x_{ij}\\Bigr\\rvert^p\\biggr]^{1/p}$\r\n#+END_EXAMPLE\r\n** Result\r\n$\\biggl[\\sum_i a_i\\Bigl\\lvert\\sum_j x_{ij}\\Bigr\\rvert^p\\biggr]^{1/p}$\r\n\r\n\r\n* Complex Fraction\r\n** Code\r\n#+BEGIN_EXAMPLE\r\n$\\frac{\\sum_{n > 0} z^n}\r\n{\\prod_{1\\leq k\\leq n} (1-q^k)}$\r\n#+END_EXAMPLE\r\n** Result\r\n$\\frac{\\sum_{n > 0} z^n}\r\n{\\prod_{1\\leq k\\leq n} (1-q^k)}$\n\n")
        o_gs.content = unicode("<div id=\"preamble\">\n</div>\n<div id=\"content\">\n<h1 class=\"title\">MATH FUNCTIONS</h1>\n<div id=\"outline-container-1\" class=\"outline-2\">\n<h2 id=\"sec-1\">Fractions and Log</h2>\n<div class=\"outline-text-2\" id=\"text-1\">\n</div>\n<div id=\"outline-container-1-1\" class=\"outline-3\">\n<h3 id=\"sec-1-1\">code</h3>\n<div class=\"outline-text-3\" id=\"text-1-1\">\n<pre class=\"example\">$\\frac{1}{k}\\log_2 c(f)$\n$\\frac{1}{k}\\log_2 c(f)$\n</pre>\n</div>\n</div>\n<div id=\"outline-container-1-2\" class=\"outline-3\">\n<h3 id=\"sec-1-2\">Result</h3>\n<div class=\"outline-text-3\" id=\"text-1-2\">\n\\(\\frac{1}{k}\\log_2 c(f)\\)\n\\(\\frac{1}{k}\\log_2 c(f)\\)\n</div>\n</div>\n</div>\n<div id=\"outline-container-2\" class=\"outline-2\">\n<h2 id=\"sec-2\">Binomial coefficient</h2>\n<div class=\"outline-text-2\" id=\"text-2\">\n</div>\n<div id=\"outline-container-2-1\" class=\"outline-3\">\n<h3 id=\"sec-2-1\">Code</h3>\n<div class=\"outline-text-3\" id=\"text-2-1\">\n<pre class=\"example\">$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\n</pre>\n</div>\n</div>\n<div id=\"outline-container-2-2\" class=\"outline-3\">\n<h3 id=\"sec-2-2\">Result</h3>\n<div class=\"outline-text-3\" id=\"text-2-2\">\n\\(2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}\\)\n</div>\n</div>\n</div>\n<div id=\"outline-container-3\" class=\"outline-2\">\n<h2 id=\"sec-3\">Continued fractions</h2>\n<div class=\"outline-text-2\" id=\"text-3\">\n</div>\n<div id=\"outline-container-3-1\" class=\"outline-3\">\n<h3 id=\"sec-3-1\">Code</h3>\n<div class=\"outline-text-3\" id=\"text-3-1\">\n<pre class=\"example\">$\\cfrac{1}{\\sqrt{2}+\n\\cfrac{1}{\\sqrt{2}+\n\\cfrac{1}{\\sqrt{2}+\\dotsb}}}$\n$2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}$\n</pre>\n</div>\n</div>\n<div id=\"outline-container-3-2\" class=\"outline-3\">\n<h3 id=\"sec-3-2\">Result</h3>\n<div class=\"outline-text-3\" id=\"text-3-2\">\n\\(\\cfrac{1}{\\sqrt{2}+\n\\cfrac{1}{\\sqrt{2}+\n\\cfrac{1}{\\sqrt{2}+\\dotsb}}}\\)\n\\(2^k-\\binom{k}{1}2^{k-1}+\\binom{k}{2}2^{k-2}\\)\n</div>\n</div>\n</div>\n<div id=\"outline-container-4\" class=\"outline-2\">\n<h2 id=\"sec-4\">Big brackets</h2>\n<div class=\"outline-text-2\" id=\"text-4\">\n</div>\n<div id=\"outline-container-4-1\" class=\"outline-3\">\n<h3 id=\"sec-4-1\">Code</h3>\n<div class=\"outline-text-3\" id=\"text-4-1\">\n<pre class=\"example\">$\\biggl[\\sum_i a_i\\Bigl\\lvert\\sum_j x_{ij}\\Bigr\\rvert^p\\biggr]^{1/p}$\n</pre>\n</div>\n</div>\n<div id=\"outline-container-4-2\" class=\"outline-3\">\n<h3 id=\"sec-4-2\">Result</h3>\n<div class=\"outline-text-3\" id=\"text-4-2\">\n\\(\\biggl[\\sum_i a_i\\Bigl\\lvert\\sum_j x_{ij}\\Bigr\\rvert^p\\biggr]^{1/p}\\)\n</div>\n</div>\n</div>\n<div id=\"outline-container-5\" class=\"outline-2\">\n<h2 id=\"sec-5\">Complex Fraction</h2>\n<div class=\"outline-text-2\" id=\"text-5\">\n</div>\n<div id=\"outline-container-5-1\" class=\"outline-3\">\n<h3 id=\"sec-5-1\">Code</h3>\n<div class=\"outline-text-3\" id=\"text-5-1\">\n<pre class=\"example\">$\\frac{\\sum_{n &gt; 0} z^n}\n{\\prod_{1\\leq k\\leq n} (1-q^k)}$\n</pre>\n</div>\n</div>\n<div id=\"outline-container-5-2\" class=\"outline-3\">\n<h3 id=\"sec-5-2\">Result</h3>\n<div class=\"outline-text-3\" id=\"text-5-2\">\n\\(\\frac{\\sum_{n > 0} z^n}\n{\\prod_{1\\leq k\\leq n} (1-q^k)}\\)\n</div>\n</div>\n</div>\n</div>\n<div id=\"postamble\">\n<a href=\"http://validator.w3.org/check?uri=referer\">Validate XHTML 1.0</a>\n</div>\n")
        o_gs.save()

        if not hm.create_or_replace_json_file(o_gs):
            c_gs.remove({'_id': o_gs._id})
        else:
            fp = hm.get_file_path(o_gs)
            rcsobj.checkin(fp, 0, "This document("+str(o_gs.name)+") is of GSystem.", "-i")
        
        # --- End of handle() ---
