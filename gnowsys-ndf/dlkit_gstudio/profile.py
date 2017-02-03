"""gstudio osid profile elements common among all service packages"""
# -*- coding: utf-8 -*-

ID = {'authority': 'tiss.edu',
      'namespace': 'dlkit.implementation',
      'identifier': 'gstudio'}

# Need to deal with this in locale/proxy/config:
LANGUAGETYPE = {
    'identifier': 'ENG',
    'namespace': '639-2',
    'authority': 'ISO',
    'domain': 'DisplayText Languages',
    'display_name': 'English Text Language',
    'display_label': 'English',
    'description': 'The display text language type for the English language.'
    }

# Need to deal with this in locale/proxy/config:
SCRIPTTYPE = {
    'identifier': 'LATN',
    'namespace': '15924',
    'authority': 'ISO',
    'domain': 'ISO Script Types',
    'display_name': 'Latin Text Script',
    'display_label': 'Latin',
    'description': 'The display text script type for the Latin script.'
    }

# Need to deal with this in locale/proxy/config:
FORMATTYPE = {
    'identifier': 'PLAIN',
    'namespace': 'TextFormats',
    'authority': 'okapia.net',
    'domain': 'DisplayText Formats',
    'display_name': 'Plain Text Format',
    'display_label': 'Plain',
    'description': 'The display text format type for the Plain format.'
    }

DISPLAYNAME = 'GStudio osid'

DESCRIPTION = 'GStudio osid implementation'

VERSIONSCHEME = {'authority': 'odl.mit.edu',
                 'namespace': 'dlkit.mit.edu',
                 'identifier': 'version_scheme'}

# Need to deal with this in locale/proxy/config:
LOCALES = None

LICENSE = """
<p>This implementation ("Work") and the information contained herein is 
provided on an "AS IS" basis. The Massachusetts Institute of Technology. 
THE AUTHORS DISCALIM ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT 
NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OF IN 
CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS IN THE WORK.
</p><p>Permission to use, copy, modify, adapt and distribute this Work, 
for any purpose, without fee or royalty is hereby granted, provided that 
you include the above copyright notice and the 
terms of this license on ALL copies of the Work of portions thereof.
</p><p>The export of software employing encryption technology may require 
a specific license from the United States Government. It is the 
responsibility of any person or organization contemplating export to obtain 
such a license before exporting this Work.</p>"""

PROVIDERID = {'authority': 'tiss.edu',
              'namespace': 'dept name',
              'identifier': 'identifier'}

OSIDVERSION = [3, 0, 0]
