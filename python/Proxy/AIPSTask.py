# Copyright (C) 2005 Joint Institute for VLBI in Europe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

This module provides the bits and pieces to implement an AIPSTask
proxy object.

"""

# Global AIPS defaults.
from AIPSUtil import ehex
from Proxy.AIPS import AIPS

# The results from parsing POPSDAT.HLP.
from Proxy.Popsdat import Popsdat

# Bits from the generic Task implementation.
from Proxy.Task import Task

# AIPS Lite
import AIPSLite

# Generic Python stuff.
import glob, os, signal, struct

class _AIPSTaskParams:
    def __parse(self, name):
        """Determine the proper attributes for the AIPS task NAME by
        parsing its HELP file."""

        # Pretend we know nothing yet.
        task = None
        desc = None

        popsdat = Popsdat(self.version)

        path = self.version + '/HELP/' + name.upper() + '.HLP'
        input = open(path)

        # Parse INPUTS section.
        for line in input:
            # A line of dashes terminates the parameter definitions.
            if line.startswith('--------'):
                break;

            # Comment lines start with ';'.
            if line.startswith(';'):
                continue

            # Empty lines start with '\n'.
            if line.startswith('\n'):
                continue

            # Continuation lines start with ' '.
            if line.startswith(' '):
                continue

            if not task:
                min_start = line.find('LLLLLLLLLLLL')
                min_end = line.rfind('L')
                max_start = line.find('UUUUUUUUUUUU')
                max_end = line.rfind('U')
                dir_start = min_start - 2
                dir_end = min_start - 1
                if not min_start == -1 and not max_start == -1:
                    task = line.split()[0]
                continue

            if not desc:
                if line.startswith(task):
                    desc = line
                continue

            adverb = line.split()[0].lower()
            code = line[min_start - 1:min_start]
            if not code:
                code = ' '
            try:
                min = float(line[min_start:min_end])
                max = float(line[max_start:max_end])
            except:
                min = None
                max = None

            match_key = None
            if adverb in popsdat.default_dict:
                 match_key = adverb
            else:
                # Some HELP files contain typos.
                for key in popsdat.default_dict:
                    if key.startswith(adverb):
                        if match_key:
                            msg = "adverb '%s' is ambiguous" % adverb
                            raise AttributeError(msg)
                        else:
                            match_key = key
            if not match_key:
                match_key = key
            self.default_dict[adverb] = popsdat.default_dict[match_key]

            if code in ' *&$':
                self.input_list.append(adverb)
            if code in '&%$@':
                self.output_list.append(adverb)
            if adverb in popsdat.strlen_dict:
                self.strlen_dict[adverb] = popsdat.strlen_dict[adverb]
            if min != None:
                self.min_dict[adverb] = min
            if max != None:
                self.max_dict[adverb] = max

        # Parse HELP section.
        for line in input:
            # A line of dashes terminates the help message.
            if line.startswith('--------'):
                break;

            self.help_string = self.help_string + line
            continue

        # Parse EXPLAIN section.
        for line in input:
            self.explain_string = self.explain_string + line
            continue

        pass

    def __init__(self, name, version):
        self.default_dict = {}
        self.input_list = []
        self.output_list = []
        self.min_dict = {}
        self.max_dict = {}
        self.strlen_dict = {}
        self.help_string = ''
        self.explain_string = ''

        self.name = name
        if version in os.environ:
            self.version = os.environ[version]
        else:
            self.version = os.environ['AIPS_ROOT'] + '/' + version
            pass

        if AIPSLite.initialized:
            AIPSLite.get_task(name, version=version)
            pass

        self.__parse(name)

    # Provide a dictionary-like interface to deal with the
    # idiosyncrasies of XML-RPC.
    def __getitem__(self, key):
        return self.__dict__[key]


class AIPSTask(Task):

    # List of adverbs referring to file names.
    # some new for 31DEC08
    # O.W.  07 Nov 2008
    _file_adverbs = ['infile', 'infile2', 'outfile', 'outprint',
                     'ofmfile', 'boxfile', 'oboxfile',
                     'intext', 'outtext', 'datain', 'dataout', 'calin',
                     'inlist', 'data2in'
                     ]

    def __init__(self):
        Task.__init__(self)
        self._params = {}
        self._popsno = {}
        self._userno = {}
        self._msgno = {}
        self._msgkill = {}

    def params(self, name, version):
        """Return parameter set for version VERSION of task NAME."""
        return _AIPSTaskParams(name, version)

    def __write_adverb(self, params, file, adverb, value):
        """Write (sub)value VALUE of adverb ADVERB into TD file FILE."""

        assert(adverb in params.input_list)

        if type(value) == float:
            file.write(struct.pack('f', value))
        elif type(value) == str:
            strlen = ((params.strlen_dict[adverb] + 3) // 4) * 4
            fmt = "%ds" % strlen
            file.write(struct.pack(fmt, value.ljust(strlen).encode('utf-8')))
        elif type(value) == list:
            for subvalue in value[1:]:
                self.__write_adverb(params, file, adverb, subvalue)
        else:
            raise AssertionError(type(value))

    def __read_adverb(self, params, file, adverb, value=None):
        """Read (sub)value for adverb ADVERB from TD file FILE."""

        assert(adverb in params.output_list)

        # We use the default value for type checks.
        if value == None:
            value = params.default_dict[adverb]

        if type(value) == float:
            (value,) = struct.unpack('f', file.read(4))
        elif type(value) == str:
            strlen = ((params.strlen_dict[adverb] + 3) // 4) * 4
            fmt = "%ds" % strlen
            (value,) = struct.unpack(fmt, file.read(strlen))
            value.strip()
        elif type(value) == list:
            newvalue = [None]
            for subvalue in value[1:]:
                subvalue = self.__read_adverb(params, file, adverb, subvalue)
                newvalue.append(subvalue)
                continue
            value = newvalue
        else:
            raise AssertionError(type(value))
        return value

    def spawn(self, name, version, userno, msgkill, isbatch, tv, input_dict):
        """Start the task."""

        params = _AIPSTaskParams(name, version)
        popsno = _allocate_popsno()
        index = popsno - 1

        try:
            # A single hardcoded TV will do until support for multiple
            # TVs is implemented.
            ntvdev = 1

            # Construct the environment for the task.  For the adverbs
            # like 'infile', 'outfile' and 'outprint', we split off
            # the directory component of the pathname and use that as
            # the area.
            env = os.environ.copy()
            area = 'a'
            for adverb in self._file_adverbs:
                if adverb in input_dict:
                    assert(ord(area) <= ord('z'))
                    dirname = os.path.dirname(input_dict[adverb])
                    if dirname:
                        if not os.path.isdir(dirname):
                            msg = "Direcory '%s' does not exist" % dirname
                            raise RuntimeError(msg)
                        env[area] = dirname
                        basename = os.path.basename(input_dict[adverb])
                        input_dict[adverb] = area + ':' + basename
                        area = chr(ord(area) + 1)
                        pass
                    pass
                continue
            # Send output to the TV running on this machine.
            env['TVDEV'] = 'TVDEV01'
            env['TVDEV' + ehex(ntvdev, 2, 0)] = tv
            if tv.find(':') == -1:
                env['TVLOK'] = 'TVLOK01'
                env['TVLOK' + ehex(ntvdev, 2, 0)] = tv.replace('DEV', 'LOK')
                pass

            td_name = os.environ['DA00'] + '/TD' + AIPS.revision + '000004;'
            td_file = open(td_name, mode='r+b')

            td_file.seek(index * 20)
            td_file.write(struct.pack('8s', name.upper().ljust(8).encode('utf-8')))
            td_file.write(struct.pack('l', -999))
            td_file.write(struct.pack('2l', 0, 0))

            td_file.seek(1024 + index * 4096)
            td_file.write(struct.pack('i', userno))
            td_file.write(struct.pack('i', ntvdev))
            td_file.write(struct.pack('i', 0))
            td_file.write(struct.pack('i', msgkill + 32000 - 1))
            td_file.write(struct.pack('i', isbatch))
            td_file.write(struct.pack('i', 0))
            td_file.write(struct.pack('i', 1))
            td_file.write(struct.pack('i', 0))
            td_file.write(struct.pack('f', 1.0))
            td_file.write(struct.pack('4s', b'    '))
            for adverb in params.input_list:
                self.__write_adverb(params, td_file, adverb,
                                    input_dict[adverb])
                continue

            td_file.close()

            # Create the message file if necessary and record the
            # number of messages currently in it.
            user = ehex(userno, 3, 0)
            ms_name = os.environ['DA01'] + '/MS' + AIPS.revision \
                      + user + '000.' + user + ';'
            if not os.path.exists(ms_name):
                ms_file = open(ms_name, mode='wb')
                ms_file.truncate(1024)
                ms_file.close()
                os.chmod(ms_name, 0o664)
                pass
            ms_file = open(ms_name, mode='rb')
            (msgno,) = struct.unpack('i', ms_file.read(4))
            ms_file.close()

            path = params.version + '/' + os.environ['ARCH'] + '/LOAD/' \
                   + name.upper() + ".EXE"
            tid = Task.spawn(self, path, [name.upper() + ehex(popsno)], env)

        except Exception as exception:
            _free_popsno(popsno)
            raise exception
            
        self._params[tid] = params
        self._popsno[tid] = popsno
        self._userno[tid] = userno
        self._msgkill[tid] = msgkill
        self._msgno[tid] = msgno
        return tid

    def __read_message(self, file, msgno):
        file.seek((msgno // 10) * 1024 + 8 + (msgno % 10) * 100)
        (tmp, task, message) = struct.unpack('i8x5s3x80s', file.read(100))
        (popsno, priority) = (tmp // 16, tmp % 16)
        task = task.decode('utf-8').rstrip()
        message = message.decode('utf-8').rstrip()
        return (task, popsno, priority, message)

    def messages(self, tid):
        """Return task's messages."""

        # Make sure we read the messages, even if we throw them away
        # later to prevent the task from blocking.
        messages = Task.messages(self, tid)

        # Strip out all formal messages.
        name = self._params[tid].name.upper()
        start = '%-5s%c' % (name, ehex(self._popsno[tid]))
        messages = [msg for msg in messages if not msg.startswith(start)]

        messages = [(1, msg) for msg in messages]

        user = ehex(self._userno[tid], 3, 0)
        ms_name = os.environ['DA01'] + '/MS' + AIPS.revision \
                  + user + '000.' + user + ';'
        ms_file = open(ms_name, mode='rb')

        (msgno,) = struct.unpack('i', ms_file.read(4))
        while self._msgno[tid] < msgno:
            (task, popsno, priority, msg) = \
                   self.__read_message(ms_file, self._msgno[tid])
            # Filter
            if popsno == self._popsno[tid]:
                msg = '%-5s%c: %s' % (task, ehex(popsno), msg)
                messages.append((priority, msg))
                pass
            self._msgno[tid] += 1
            continue

        ms_file.close()
        return messages

    def wait(self, tid):
        """Wait for the task to finish."""

        assert(self.finished(tid))

        params = self._params[tid]
        popsno = self._popsno[tid]
        index = popsno - 1

        td_name = os.environ['DA00'] + '/TDD000004;'

        try:
            td_file = open(td_name, mode='rb')

            td_file.seek(index * 20 + 8)
            (result,) = struct.unpack('i', td_file.read(4))
            if result != 0:
                msg = "Task '%s' returns '%d'" % (params.name, result)
                raise RuntimeError(msg)

            td_file.seek(1024 + index * 4096 + 40)
            output_dict = {}
            for adverb in params.output_list:
                output = self.__read_adverb(params, td_file, adverb)
                output_dict[adverb] = output
                continue

            td_file.close()

        finally:
            _free_popsno(popsno)
            pass

        del self._params[tid]
        del self._popsno[tid]
        del self._userno[tid]
        del self._msgno[tid]
        Task.wait(self, tid)

        return output_dict

    # AIPS seems to ignore SIGINT, so use SIGTERM instead.
    def abort(self, tid, sig=signal.SIGTERM):
        """Abort a task."""

        _free_popsno(self._popsno[tid])

        del self._params[tid]
        del self._popsno[tid]
        del self._userno[tid]
        del self._msgno[tid]

        return Task.abort(self, tid, sig)

    pass                                # class AIPSTask

class AIPSMessageLog:
    def __init__(self):
        return

    def _open(self, userno):
        user = ehex(userno, 3, 0)
        ms_name = os.environ['DA01'] + '/MS' + AIPS.revision \
                  + user + '000.' + user + ';'
        return open(ms_name, mode='r+b')

    def zap(self, userno):
        """Zap message log."""

        ms_file = self._open(userno)
        ms_file.write(struct.pack('i', 0))
        return True                # Return something other than None.

    pass                                # class AIPSMessageLog


# In order to prevent multiple AIPS instances from using the same POPS
# number, every AIPS instance creates a lock file in /tmp.  These lock
# files are named AIPSx.yyy, where x is the POPS number (in extended
# hex) and yyy is the process ID of the AIPS instance.

def _allocate_popsno():
    for popsno in range(1,36):
        # In order to prevent a race, first create a lock file for
        # POPSNO.
        try:
            path = '/tmp/AIPS' + ehex(popsno, 1, 0) + '.' + str(os.getpid())
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
            os.close(fd)
        except:
            continue

        # Get a list of likely lock files and iterate over them.
        # Leave out our own lock file though.
        files = glob.glob('/tmp/AIPS' + ehex(popsno, 1, 0) + '.[0-9]*')
        files.remove(path)
        for file in files:
            # If the part after the dot isn't an integer, it's not a
            # proper lock file.
            try:
                pid = int(file.split('.')[1])
            except:
                continue

            # Check whether the AIPS instance is still alive.
            try:
                os.kill(pid, 0)
            except:
                # The POPS number is no longer in use.  Try to clean
                # up the lock file.  This might fail though if we
                # don't own it.
                try:
                    os.unlink(file)
                except:
                    pass
            else:
                # The POPS number is in use.
                break
        else:
            # The POPS number is still free.
            return popsno

        # Clean up our own mess.
        os.unlink(path)

    raise RuntimeError("No free AIPS POPS number available on this system")

def _free_popsno(popsno):
    path = '/tmp/AIPS' + ehex(popsno, 1, 0) + '.' + str(os.getpid())
    os.unlink(path)
