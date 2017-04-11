"""RCS interface module.

Defines the class RCS, which represents a directory with rcs version
files and (possibly) corresponding work files.

"""

import os
import re
import string
from tempfile import NamedTemporaryFile
from subprocess import call 
from sys import stderr

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
    okchars = string.ascii_letters + string.digits + '.'

    def __init__(self):
        """Constructor."""
        pass

    def __del__(self):
        """Destructor."""
        pass

    # ==== Informational methods about a single file/revision ====

    def head(self, name_rev):
        """Return the head revision for NAME_REV"""
        dict = self.info(name_rev)
        return dict['head']

    def info(self, name_rev):
        """Return a dictionary of info (from rlog -h) for NAME_REV

        The dictionary's keys are the keywords that rlog prints
        (e.g. 'head' and its values are the corresponding data
        (e.g. '1.3').

        XXX symbolic names and locks are not returned

        """
        f = self._open(name_rev, 'rlog -h')

        dict = {}
        while 1:
            line = f.readline()

            if not line: 
                break

            if line[0] == '\n' or line[0] == '\t':
                # XXX could be a lock or symbolic name
                # Anything else?
                continue

            keyval = string.split(line, ': ')
            if len(keyval) == 2:
                dict[keyval[0]] = keyval[1][:-1]

        status = self._closepipe(f)
        if status:
            raise IOError, status

        return dict

    def calculateVersionNumber(self, name_rev, back):
        """
        The version number of 'name_rev' wound back by 'back' times.
        So if 'name_rev' is currently version 1.14 'back' of 1
        is 1.13. Back of 2 is 1.12. Back of 0 is 1.14.
        """

        currentRev = self.head(name_rev)

        splitVersion = currentRev.split('.')
        previousSubNumber = int(splitVersion[1]) - back 

        if previousSubNumber <= 0:
            previousSubNumber = 1

        return splitVersion[0] +"."+ str(previousSubNumber)

    def diff(self, name, revleft=None, revright=None):
        """The output of rcsdiff

        These arguments REVLEFT & REVRIGHT accepts string as an I/P;
        i.e. '1.2'.
        """
        
        self.checkrev(revleft)
        self.checkrev(revright)

        if revleft is None or revleft == '':
            if revright == self.head(name):
                revleft = self.calculateVersionNumber(name, 1)
            else:
                revleft = self.head(name)

        if revright is None or revright == '':
            if revleft == self.head(name):
                revright = self.calculateVersionNumber(name, 1)
            else:
                revright = self.head(name)
        
        if (revleft == revright) and (revleft is not None or revleft != ''):
            if revleft == self.head(name):
                revright = self.calculateVersionNumber(name, 1)
            else:
                revleft = self.head(name)

        # Diff
        f = self._open(name, "rcsdiff -r"+ revleft +" -r"+ revright) 

        data = ''.join(f.readlines())

        self._closepipe(f)

        # Refer following code for proper O/P
        '''
        line = ""
        for ch in data:
            if ch == "\n":
                print(" " + line)
                line = ""
            else:
                line += ch
        '''
        return data
        

    # ==== Methods that change files ====

    def checkout(self, name_rev, withlock=1, otherflags=""):
        """Check-out NAME_REV to its work file.

        If optional WITHLOCK is set, check out locked, else unlocked.

        The optional OTHERFLAGS is passed to co without
        interpretation.

        Any output from co goes to directly to stdout.

        """
        name, rev = self.checkfile(name_rev)

        lockflag = "-q"
        if withlock: 
            lockflag += " -l"
        else: 
            lockflag += " -u"

        cmd = 'co %s%s %s %s' % \
            (lockflag, rev, otherflags, name)

        return self._system(cmd)

    def checkin(self, name_rev, delworkfile=1, message=None, otherflags=""):
        """Check-in NAME_REV from its work file.

        The optional MESSAGE argument becomes the checkin message
        (default "<none>" if None); or the file description if this is
        a new file.

        The optional OTHERFLAGS argument is passed to ci without
        interpretation.

        Any output from ci goes to directly to stdout.

        """
        name, rev = self._unmangle(name_rev)
        new = not self.isvalid(name)

        lockflag = "-q"
        if not delworkfile:
            lockflag += "-u"

        if not message: 
            message = "<none>"
        if message and message[-1] != '\n':
            message = message + '\n'

        temp_message_file = None
        if new:
            temp_message_file = NamedTemporaryFile('w+t')
            temp_message_file.write(message)
            
            temp_message_file.seek(0)
            cmd = 'ci %s%s -t%s %s %s' % \
                (lockflag, rev, temp_message_file.name, otherflags, name)

        else:
            message = re.sub('\([\\"$`]\)', '\\\\\\1', message)

            cmd = 'ci %s%s -m"%s" %s %s' % \
                (lockflag, rev, message, otherflags, name)

        result = self._system(cmd)

        if new:
            temp_message_file.close()

        return result

    def isvalid(self, name):
        """Test whether NAME has a version file associated."""
        namev = self.rcsname(name)
        return (os.path.isfile(namev))

    def rcsname(self, name):
        """Return the path of the version file for NAME.

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

    def checkfile(self, name_rev):
        """Normalize NAME_REV into a (NAME, REV) tuple.

        Raise an exception if there is no corresponding version file.

        """
        name, rev = self._unmangle(name_rev)

        if not self.isvalid(name):
            raise os.error, '\n Error: Not an rcs file %s!!!\n' % `name`

        return name, rev

    def checkrev(self, rev):
        for c in rev:
            if c not in self.okchars:
                raise ValueError, "Error: Bad character in revision number!!!"

    # ==== Internal methods =====

    def _unmangle(self, name_rev):
        """INTERNAL: Normalize NAME_REV argument to (NAME, REV) tuple.

        Raises an exception if NAME contains invalid characters.

        A NAME_REV argument is either NAME string (implying REV='') or
        a tuple of the form (NAME, REV).

        ---- EXAMPLE ----
        (a) string: _unmangle('5252648f5a40920c160bc774.json')
        (b) tuple : _unmangle(('5252648f5a40920c160bc774.json', '1.3'))
        """
        if type(name_rev) == type(''):
            name_rev = name, rev = name_rev, ''
        else:
            name, rev = name_rev

        self.checkrev(rev)
        
        return name_rev

    def _open(self, name_rev, cmd = 'co -p', rflag = '-r'):
        """INTERNAL: open a read pipe to NAME_REV using optional COMMAND.

        Optional FLAG is used to indicate the revision (default -r).

        Default COMMAND is "co -p".

        Return a file object connected by a pipe to the command's
        output.

        """
        name, rev = self.checkfile(name_rev)
        namev = self.rcsname(name)
        if rev:
            cmd = cmd + ' ' + rflag + rev
        return os.popen("%s %s" % (cmd, namev))

    def _closepipe(self, f):
        """INTERNAL: Close PIPE and print its exit status if nonzero."""
        sts = f.close()
        if not sts: 
            return None
        detail, reason = divmod(sts, 256)
        if reason == 0: 
            return 'exit', detail   # Exit status
        signal = reason&0x7F
        if signal == 0x7F:
            code = 'stopped'
            signal = detail
        else:
            code = 'killed'
        if reason&0x80:
            code = code + '(coredump)'
        return code, signal

    def _system(self, cmd):
        """INTERNAL: Run COMMAND in a subshell.

        Standard input for the command is taken from /dev/null.

        Return whatever the calling method should return; normally
        None.

        A derived class may override this method and redefine it to
        capture stdout/stderr of the command and return it.

        """
        cmd = cmd + " </dev/null"
        try:
            retcode = call(cmd, shell=True)
            if retcode < 0:
                raise IOError, "command exit status %d" % retcode
                #print >>stderr, "\n Child was terminated by signal", -retcode
        except IOError as ise:
            print >>stderr, "\n Execution failed(ise):", ise
        except OSError as ose:
            print >>stderr, "\n Execution failed(ose):", ose
        except Exception as e:
            print >>stderr, "\n Execution failed(e):", e
            
    def _isrcs(self, name):
        """INTERNAL: Test whether NAME ends in ',v'."""
        return name[-2:] == ',v'
