# Module to assist in running AIPS/ParselTongue on machines without
# an AIPS installation.
#
# Stephen Bourke, JIVE
# Version: 20091216

"""
This module assists in running AIPS/ParselTongue on machines without
an AIPS installation.
"""

import os, shutil, string, sys, time

# Generic AIPS functionality.
from AIPSUtil import ehex

import AIPS
import Obit
import OErr

_aips_server = 'ftp.aoc.nrao.edu'

_default_year = time.gmtime().tm_year - 1
default_version = '31DEC' + str(_default_year)[-2:]
initialized = False

# Minimum files required:
_intel_libs = ['libimf.so', 'libsvml.so']
_mac_libs = ['libimf.dylib', 'libirc.dylib', 'libsvml.dylib']
_popsdat_files = ['POPSDAT.HLP']
_binary_files = ['FILAIP.EXE']
_ions_files = ['TEXT/IONS/*']

def _arch(version):
	"""Return the AIPS architecture for the current machine"""
	uname = os.uname()
	if uname[0] == 'Linux' and uname[4].startswith('i') and uname[4].endswith('86'):
		return 'LINUX'
	if uname[0] == 'Linux' and uname[4] == 'x86_64':
		# LNX64 only became an arch since 09
		year = int(version[-2:])
		# AIPS version stores 2 digit year, we'll say 00 - 60 are 2000's
		if year > 8 and year < 60:
			return 'LNX64'
		else:
			return 'LINUX'
	elif uname[0] == 'Darwin' and uname[4] == 'i386':
		return 'MACINT'
	else:
		raise NotImplementedError, 'Unknown Architecture'

def _init_environ(path=None, version=None):
	"""Set required environment variables"""
	if not path:
		path = os.getcwd()
	if not version:
		version = default_version
	os.environ['AIPS_ROOT'] = path
	os.environ['ARCH'] = _arch(version)
	os.environ['VERSION'] = 'NEW'
	os.environ['PLOTTER'] = '/tmp'
	_set_version(version)
	# Add the intel libs to [DY]LD_LIBRARY_PATH
	if os.environ['ARCH'] == 'LINUX' or os.environ['ARCH'] == 'LNX64':
		lib_env = 'LD_LIBRARY_PATH'
	elif os.environ['ARCH'] == 'MACINT':
		lib_env = 'DYLD_LIBRARY_PATH'
	lib_dir = '%s/%s/LIBR/INTELCMP' % (os.environ['AIPS_VERSION'], os.environ['ARCH'])
	if os.environ.has_key(lib_env):
		os.environ[lib_env] += ':' + lib_dir
	else:
		os.environ[lib_env] = lib_dir

def _set_version(version):
	os.environ['AIPS_VERSION'] = os.environ['AIPS_ROOT'] + '/' + version
	os.environ['LOAD'] = os.environ['AIPS_VERSION'] + '/' + os.environ['ARCH'] + '/LOAD'
	os.environ['NEW'] = os.environ['AIPS_VERSION']
	os.environ['AIPSIONS'] = os.environ['AIPS_VERSION'] + '/IONS'

def _create_path_list(path, file_list):
	url_list = []
	for filename in file_list:
		url = '%s/%s' % (path, filename)
		url_list.append(url)
	return url_list

def _lib_urls(version):
	base = version + '/' + os.environ['ARCH'] + '/LIBR/INTELCMP'
	if os.environ['ARCH'] == 'LINUX' or os.environ['ARCH'] == 'LNX64':
		lib_files = _intel_libs
	elif os.environ['ARCH'] == 'MACINT':
		lib_files = _mac_libs
	return _create_path_list(base, lib_files)

def _popsdat_urls(version):
	base = version + '/HELP'
	return _create_path_list(base, _popsdat_files)

def _binary_urls(version):
	exe_path = version + '/' + os.environ['ARCH'] + '/LOAD'
	return _create_path_list(exe_path, _binary_files)

def _ions_urls():
	return _ions_files

def _rsync(server, path_list, dest, force=False):
	args = ['rsync', '--compress', '--relative', '--progress']
	if not force:
		args.append('--ignore-existing')
	args.append(server + '::' + ' '.join(path_list))
	args.append(dest)	# Download destination
	if os.spawnvp(os.P_WAIT, 'rsync', args) != 0:
		# TODO: Better failure reporting
		print >> sys.stderr, 'rsync failure'
		sys.exit(-1)

def _make_da00(da00_path=None, force=False):
	"""Create DA00 directory."""
	if not da00_path:
		da00_path = os.environ['AIPS_ROOT'] + '/DA00'
	if not os.path.exists(da00_path) or force:
		template_path = os.environ['AIPS_VERSION'] + '/' + os.environ['ARCH'] + '/TEMPLATE'
		shutil.copytree(template_path, da00_path)
	os.environ['DA00'] = da00_path
	os.environ['NET0'] = da00_path
	global initialized
	initialized = True

def attach_disk(disk_path=None):
	"""Make the directory and put the 'SPACE' file in it."""
	if not disk_path:
		disk_path = os.environ['AIPS_ROOT'] + '/DATA'
	space_file = disk_path + '/SPACE'
	if not os.path.exists(space_file):
		if not os.path.isdir(disk_path):
			os.makedirs(disk_path)
		open(space_file, 'w').close()
	_disk_list_add(disk_path)
	return

def _disk_list_add(*args):
	"""Add DAxx entries for the directories supplied and update NVOL."""
	try:
		nvol = int(os.environ['NVOL'])
	except KeyError:
		nvol = 0
	for i in range(len(args)):
		os.environ['DA%s' % ehex(nvol+1+i, 2, 0)] = args[i]
		AIPS.disks.append(AIPS.AIPSDisk(None, nvol + 1 + i))
		err = OErr.OErr()
		Obit.AIPSSetDirname(nvol + 1 + i, args[i] + '/', err.me)
		if err.isErr:
			raise RuntimeError
	os.environ['NVOL'] = str(nvol + len(args))

def _download_aips(version, force=False):
	dest = os.environ['AIPS_ROOT'] + '/' + version
	urls = _lib_urls(version) + _popsdat_urls(version) + _binary_urls(version)
	_rsync(_aips_server, urls, dest, force=force)
	urls = _ions_urls()
	_rsync(_aips_server, urls, dest, force=force)
	_filaip(force=force)
	return

def _filaip(force=False):
	mem_dir = os.environ['AIPS_VERSION'] + '/' + os.environ['ARCH'] + '/MEMORY'
	template_dir = os.environ['AIPS_VERSION'] + '/' + os.environ['ARCH'] + '/TEMPLATE'
	data_dir = os.environ['AIPS_VERSION'] + '/DATA'
	if force:
		shutil.rmtree(mem_dir, ignore_errors=True)
		shutil.rmtree(template_dir, ignore_errors=True)
		msfile = data_dir + '/MSD001000.001;'
		if os.path.exists(msfile):
			os.remove(msfile)
	if os.path.exists(mem_dir) or os.path.exists(template_dir):
		run_filaip = False
	else:
		run_filaip = True
	for tdir in [mem_dir, template_dir, data_dir]:
		if not os.path.exists(tdir):
			os.makedirs(tdir)
	# Download DA00 to TEMPLATE. make_da00 will copy this to the actual DA00
	da00 = os.environ.get('DA00')
	da01 = os.environ.get('DA01')
	net0 = os.environ.get('NET0')
	nvol = os.environ.get('NVOL')
	os.environ['DA00'] = template_dir
	os.environ['NET0'] = template_dir
	os.environ['DA01'] = data_dir
	os.environ['NVOL'] = '1'
	os.environ['NEWMEM'] = mem_dir
	if run_filaip:
		os.system('echo 8 2 | %s/%s/LOAD/FILAIP.EXE' % (os.environ['AIPS_VERSION'], os.environ['ARCH']))
		pass
	if da00:
		os.environ['DA00'] = da00
	else:
		del os.environ['DA00']
		pass
	if da01:
		os.environ['DA01'] = da01
	else:
		del os.environ['DA01']
		pass
	if net0:
		os.environ['NET0'] = net0
	else:
		del os.environ['NET0']
		pass
	if nvol:
		os.environ['NVOL'] = nvol
	else:
		del os.environ['NVOL']
		pass
	return

def setup(basedir=None, *args, **kwargs):
	"""Get required files and make DA00 area"""
	if not basedir:
		basedir = os.getcwd()
		pass
	if 'version' in kwargs:
		version = kwargs['version']
	else:
		version = default_version
		pass
	if 'force' in kwargs:
		force = kwargs['force']
	else:
		force = False
		pass
	_init_environ(basedir, version=version)
	_download_aips(version=version, force=force)
	_make_da00(force=force)
	if len(args) == 0:
		attach_disk()
	else:
		for path in args:
			attach_disk(path)
			continue
		pass
	return

def _get_version():
	"""Return the AIPS version or None if its not defined."""
	try:
		return os.environ['AIPS_VERSION'].split('/')[-1]
	except KeyError:
		return None

def get_task(*args, **kwargs):
	"""Get the Task and Help file for the specified task"""
	if 'force' in kwargs:
		force = kwargs['force']
	else:
		force = False
	dest = os.environ['AIPS_VERSION']
	if 'version' in kwargs:
		task_version = kwargs['version']
		if task_version in os.environ:
			task_version=os.environ[task_version].split('/')[-1]
		if task_version != _get_version():
			_download_aips(version=task_version)
			dest = os.environ['AIPS_ROOT'] + '/' + task_version
	else:
		task_version = _get_version()
	#FIXME: Not finished

	exe_path = task_version + '/' + os.environ['ARCH'] + '/LOAD'
	help_path = task_version + '/HELP'
	urls = []
	for taskname in args:
		if not os.path.exists(exe_path + '/' + taskname.upper() + '.EXE') \
		   or not os.path.exists(help_path + '/' + taskname.upper() + '.HLP') \
		   or force:
			urls += _create_path_list(exe_path, [taskname.upper() + '.EXE'])
			urls += _create_path_list(help_path, [taskname.upper() + '.HLP'])
	if urls:
		_rsync(_aips_server, urls, dest, force=force)
