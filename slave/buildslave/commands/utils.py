# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import os

from twisted.python import log
from twisted.python.procutils import which
from twisted.python import runtime

def getCommand(name):
    possibles = which(name)
    if not possibles:
        raise RuntimeError("Couldn't find executable for '%s'" % name)
    #
    # Under windows, if there is more than one executable "thing"
    # that matches (e.g. *.bat, *.cmd and *.exe), we not just use
    # the first in alphabet (*.bat/*.cmd) if there is a *.exe.
    # e.g. under MSysGit/Windows, there is both a git.cmd and a
    # git.exe on path, but we want the git.exe, since the git.cmd
    # does not seem to work properly with regard to errors raised
    # and catched in buildbot slave command (vcs.py)
    #
    if runtime.platformType  == 'win32' and len(possibles) > 1:
        possibles_exe = which(name + ".exe")
        if possibles_exe:
            return possibles_exe[0]
    return possibles[0]

# this just keeps pyflakes happy on non-Windows systems
if runtime.platformType != 'win32':
    WindowsError = RuntimeError

if runtime.platformType  == 'win32':
    def rmdirRecursive(dir):
        """This is a replacement for shutil.rmtree that works better under
        windows. Thanks to Bear at the OSAF for the code."""
        if not os.path.exists(dir):
            return

        if os.path.islink(dir):
            os.remove(dir)
            return

        # Verify the directory is read/write/execute for the current user
        os.chmod(dir, 0700)

        # os.listdir below only returns a list of unicode filenames if the parameter is unicode
        # Thus, if a non-unicode-named dir contains a unicode filename, that filename will get garbled.
        # So force dir to be unicode.
        try:
            dir = unicode(dir, "utf-8")
        except:
            log.msg("rmdirRecursive: decoding from UTF-8 failed")

        try:
            list = os.listdir(dir)
        except WindowsError, e:
            log.msg("rmdirRecursive: unable to listdir %s (%s). Trying to remove like a dir" % (dir, e.strerror))
            os.rmdir(dir)
            return

        for name in list:
            full_name = os.path.join(dir, name)
            # on Windows, if we don't have write permission we can't remove
            # the file/directory either, so turn that on
            if os.name == 'nt':
                if not os.access(full_name, os.W_OK):
                    # I think this is now redundant, but I don't have an NT
                    # machine to test on, so I'm going to leave it in place
                    # -warner
                    os.chmod(full_name, 0600)

            if os.path.islink(full_name):
                os.remove(full_name) # as suggested in bug #792
            elif os.path.isdir(full_name):
                rmdirRecursive(full_name)
            else:
                if os.path.isfile(full_name):
                    os.chmod(full_name, 0700)
                os.remove(full_name)
        os.rmdir(dir)
else:
    # use rmtree on POSIX
    import shutil
    rmdirRecursive = shutil.rmtree
