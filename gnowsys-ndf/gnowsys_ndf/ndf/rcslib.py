"""RCS interface module.

Defines the class RCS, which represents a directory with rcs version
files and (possibly) corresponding work files.

"""

import fnmatch
import os
#import regsub
import re
import string
from tempfile import NamedTemporaryFile

class RCS:

    """RCS interface class (local filesystem version).

    An instance of this class represents a directory with rcs version
    files and (possible) corresponding work files.

    Methods provide access to most rcs operations such as
    checkin/checkout, access to the rcs metadata (revisions, logs,
    branches etc.) as well as some filesystem operations such as
    listing all rcs version files.

    XXX BUGS / PROBLEMS

    - The instance always represents the current directory so it's not
    very useful to have more than one instance around simultaneously

    """

    # Characters allowed in work file names
    okchars = string.ascii_letters + string.digits + '-_=+'
    filename = ''

    def __init__(self):
        """Constructor."""
        pass

    def __del__(self):
        """Destructor."""
        pass

    # ==== Methods that change files ====

    def checkin(self, name_rev, message=None, otherflags=""):
        """Check in NAME_REV from its work file.

        ---- ARGUMENTS ----

        The optional MESSAGE argument becomes the checkin message
        (default "<none>" if None); or the file description if this is
        a new file.

        The optional OTHERFLAGS argument is passed to ci without
        interpretation.

        ---- DESCRIPTION ----

        Any output from ci goes to directly to stdout.

        """
        name, rev = self._unmangle(name_rev)
        new = not self.isvalid(name)

        if not message: 
            message = "<none>"
        if message and message[-1] != '\n':
            message = message + '\n'

        lockflag = "-u"

        if new:
            temp_message_file = NamedTemporaryFile('w+t')
            temp_message_file.write(message)
            
            temp_message_file.seek(0)
            cmd = 'ci %s%s -t%s %s %s' % \
                (lockflag, rev, temp_message_file.name, otherflags, name)

            temp_message_file.close()
        else:
            message = re.sub('\([\\"$`]\)', '\\\\\\1', message)

            cmd = 'ci %s%s -m"%s" %s %s' % \
                (lockflag, rev, message, otherflags, name)

        result = self._system(cmd)

        if new:
            os.remove(tempfilename)	

        return result

    def isvalid(self, name):
        """Test whether NAME has a version file associated."""
        namev = self.rcsname(name)
        return (os.path.isfile(namev))

    def rcsname(self, name):
        """Return the path of the version file for NAME.

        ---- ARGUMENTS ----

        The argument can be a work file name or a version file name.
        If the version file does not exist, the name of the version
        file that would be created by "ci" is returned.

        Return: A string representing file-path 

        """
        if self._isrcs(name): 
            namev = name
        else: 
            namev = name + ',v'

        return namev

    # ==== Internal methods =====

    def _unmangle(self, name_rev):
        """INTERNAL: Normalize NAME_REV argument to (NAME, REV) tuple.

        ---- ARGUMENTS ----
        Raises an exception if NAME contains invalid characters.

        A NAME_REV argument is either NAME string (implying REV='') or
        a tuple of the form (NAME, REV).

        ---- EXAMPLE ----
        (a) string: _unmangle('5252648f5a40920c160bc774.json')
        (b) tuple : _unmangle('5252648f5a40920c160bc774.json', '1.3')
        """
        if type(name_rev) == type(''):
            name_rev = name, rev = name_rev, ''
        else:
            name, rev = name_rev

        for c in rev:
            if c not in self.okchars:
                raise ValueError, "Error: Bad character in revision number!!!"
        return name_rev

    def _isrcs(self, name):
        """INTERNAL: Test whether NAME ends in ',v'."""
        return name[-2:] == ',v'
