"""

This module provides the bits and pieces to implement an AIPSTask
proxy object.

"""

# The results from parsing POPSDAT.HLP.
from Proxy.Popsdat import Popsdat

# Bits from the generic Task implementation.
from Proxy.Task import Task

# Generic Python stuff.
import glob, os, pickle, struct

# FIXME: Get rid of this.
class Range:
    min = 0
    max = 0

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return "Range(%s, %s)" % (str(self.min), str(self.max))


class _AIPSTaskParams:
    def __parse(self, name):
        """Determine the proper attributes for the AIPS task NAME by
        parsing its HELP file."""

        # Pretend we know nothing yet.
        task = None
        desc = None

        popsdat = Popsdat(self.version)

        path = os.environ['AIPS_ROOT'] + '/' + self.version + '/HELP/' \
               + name.upper() + '.HLP'
        input = open(path)
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
                            raise AttributeError, msg
                        else:
                            match_key = key
            if not match_key:
                match_key = key
            self.adverb_dict[adverb] = popsdat.default_dict[match_key]

            if code in ' *&$':
                self.input_list.append(adverb)
            if code in '&%$@':
                self.output_list.append(adverb)
            if adverb in popsdat.strlen_dict:
                self.strlen_dict[adverb] = popsdat.strlen_dict[adverb]
            if min != None and max != None:
                self.range_dict[adverb] = Range(min, max)

    def __init__(self, name, version):
        self.adverb_dict = {}
        self.input_list = []
        self.output_list = []
        self.range_dict = {}
        self.strlen_dict = {}

        self.name = name
        if version in ['OLD', 'NEW', 'TST']:
            self.version = os.path.basename(os.environ[version])
        else:
            self.version = version

        path = os.environ['HOME'] + '/.ParselTongue/' \
               + self.version + '/' + name.lower() + '.pickle'

        try:
            unpickler = pickle.Unpickler(open(path))
            self.adverb_dict = unpickler.load()
            self.input_list = unpickler.load()
            self.output_list = unpickler.load()
            self.range_dict = unpickler.load()
            self.strlen_dict = unpickler.load()
        except (IOError, EOFError):
            self.__parse(name)

            # Make sure the directory exists.
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            pickler = pickle.Pickler(open(path, mode='w'))
            pickler.dump(self.adverb_dict)
            pickler.dump(self.input_list)
            pickler.dump(self.output_list)
            pickler.dump(self.range_dict)
            pickler.dump(self.strlen_dict)

    # Provide a dictionary-like interface to deal with the
    # idiosyncrasies of XML-RPC.
    def __getitem__(self, key):
        return self.__dict__[key]


class AIPSTask(Task):
    def __init__(self):
        Task.__init__(self)
        self._params = {}
        self._popsno = {}

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
            file.write(struct.pack(fmt, value.ljust(strlen)))
        elif type(value) == list:
            for subvalue in value:
                self.__write_adverb(params, file, adverb, subvalue)
        else:
            raise AssertionError, type(value)

    def __read_adverb(self, params, file, adverb):
        """Read (scalar) adverb from TD file FILE."""

        assert(adverb in params.output_list)

        value = params.adverb_dict[adverb]
        if type(value) == float:
            (value,) = struct.unpack('f', file.read(4))
        elif type(value) == str:
            strlen = ((params.strlen_dict[adverb] + 3) // 4) * 4
            fmt = "%ds" % strlen
            (value,) = struct.unpack(fmt, file.read(strlen))
            value.strip()
        else:
            raise AssertionError, type(value)
        return value

    def spawn(self, name, version, userno, msgkill, isbatch, input_dict):
        """Start the task."""

        params = _AIPSTaskParams(name, version)
        popsno = _allocate_popsno()
        index = popsno - 1

        # Construct the environment for the task.  For the 'infile'
        # and 'outfile' adverbs, we split off the directory component
        # of the pathname and use that as the FITS and PLOTFILE area.
        env = os.environ.copy()
        area = 'a'
        for adverb in ['infile', 'outfile']:
            if adverb in input_dict:
                assert(ord(area) <= ord('z'))
                dirname = os.path.dirname(input_dict[adverb])
                if dirname:
                    env[area] = dirname
                    input_dict[adverb] = area + ':' + \
                                         os.path.basename(input_dict[adverb])
                    area = chr(ord(area) + 1)

        td_name = os.environ['DA00'] + '/TDD000004;'
        td_file = open(td_name, mode='r+b')

        td_file.seek(index * 20)
        td_file.write(struct.pack('8s', name.upper().ljust(8)))
        td_file.write(struct.pack('l', -999))
        td_file.write(struct.pack('2l', 0, 0))

        td_file.seek(1024 + index * 4096)
        td_file.write(struct.pack('i', userno))
        td_file.write(struct.pack('i', 0))
        td_file.write(struct.pack('i', 0))
        td_file.write(struct.pack('i', msgkill))
        td_file.write(struct.pack('i', isbatch))
        td_file.write(struct.pack('i', 0))
        td_file.write(struct.pack('2i', 0, 0))
        td_file.write(struct.pack('f', 1.0))
        td_file.write(struct.pack('4s', '    '))
        for adverb in params.input_list:
            self.__write_adverb(params, td_file, adverb, input_dict[adverb])

        td_file.close()

        path = os.environ['AIPS_ROOT'] + '/' + params.version + '/' \
               + os.environ['ARCH'] + '/LOAD/' + name.upper() + ".EXE"
        tid = Task.spawn(self, path, [name.upper() + str(popsno)], env)
        self._params[tid] = params
        self._popsno[tid] = popsno
        return tid

    def wait(self, tid):
        """Wait for the task to finish."""

        assert(self.finished(tid))

        params = self._params[tid]
        popsno = self._popsno[tid]
        index = popsno - 1

        td_name = os.environ['DA00'] + '/TDD000004;'
        td_file = open(td_name, mode='rb')

        td_file.seek(index * 20 + 8)
        (result,) = struct.unpack('i', td_file.read(4))
        if result != 0:
            msg = "Task '%s' returns '%d'" % (params.name, result)
            raise RuntimeError, msg

        td_file.seek(1024 + index * 4096 + 40)
        output_dict = {}
        for adverb in params.output_list:
            output_dict[adverb] = self.__read_adverb(params, td_file, adverb)

        td_file.close()

        _free_popsno(popsno)

        del self._params[tid]
        del self._popsno[tid]
        Task.wait(self, tid)

        return output_dict


# In order to prevent multiple AIPS instances from using the same POPS
# number, every AIPS instance creates a lock file in /tmp.  These lock
# files are named AIPSx.yyy, where x is the POPS number (in extended
# hex) and yyy is the process ID of the AIPS instance.

def _allocate_popsno():
    ehex = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for popsno in range(1,16):
        # In order to prevent a race, first create a lock file for
        # POPSNO.
        try:
            path = '/tmp/AIPS' + ehex[popsno] + '.' + str(os.getpid())
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0666)
            os.close(fd)
        except:
            continue

        # Get a list of likely lock files and iterate over them.
        # Leave out our own lock file though.
        files = glob.glob('/tmp/AIPS' + ehex[popsno] + '.[0-9]*')
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

    raise RuntimeError, "No free AIPS POPS number available on this system"

def _free_popsno(popsno):
    ehex = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    path = '/tmp/AIPS' + ehex[popsno] + '.' + str(os.getpid())
    os.unlink(path)
