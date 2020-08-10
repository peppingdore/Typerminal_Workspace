import os
import sys
import typer_commands
import subprocess
import typer
from pathlib import Path
import ascii_colors
import time
import platform


if os.name == 'nt':
	additional_path_entries = [
		r'E:\llvm\build\Debug\bin', # For llvm-mca
		r'E:\Programs',
		r'E:\vcpkg',
		r'C:\VulkanSDK\\1.2.135.0\\Bin'
	]

	for ent in additional_path_entries:
		os.environ["PATH"] += ent + os.pathsep

if os.name == 'posix':
	os.environ['PATH'] += os.pathsep + '/snap/bin'



import builder
import hot_reloader

#import command_time_printer
import b_prompt
import b_syntax_proc


hot_reloader.watch_module(builder)


typer_ship_folder = "E:/Typer_Ship"

typer_dev_folder = "E:/Typer"
typer_dev_runnable_folder = os.path.join(typer_dev_folder, "Runnable")




def copy_typer_to_ship():
	try:
		typer_commands.rmdir(typer_ship_folder, with_content = True)
	except:
		pass
		
	typer_commands.mkdir(typer_ship_folder)

	try:
		typer_commands.rmdir(os.path.join(typer_dev_runnable_folder, "python/__pycache__"), with_content = True)
		typer_commands.rmdir(os.path.join(typer_dev_runnable_folder, "user_scripts/__pycache__"), with_content = True)
	except:
		pass

	typer_commands.copy_directory(os.path.join(typer_dev_runnable_folder, "fonts"),        os.path.join(typer_ship_folder, "fonts"))
	typer_commands.copy_directory(os.path.join(typer_dev_runnable_folder, "python"),       os.path.join(typer_ship_folder, "python"))
	typer_commands.copy_directory(os.path.join(typer_dev_runnable_folder, "user_scripts"), os.path.join(typer_ship_folder, "user_scripts"))

	root_files_to_copy = [
		'freetype.dll',
		'icudt67.dll',
		'icuuc67.dll',
		'python38.dll',
		'python38.zip',
		'dbghelp.dll',
		'Typerminal.exe',
		'Typerminal.pdb'
	]


	for file in root_files_to_copy:
		typer_commands.copy_file(os.path.join(typer_dev_runnable_folder, file), os.path.join(typer_ship_folder, file))




def run_vswhere(args):
	vswhere_path = r"%ProgramFiles(x86)%/Microsoft Visual Studio/Installer/vswhere.exe"
	vswhere_path = os.path.expandvars(vswhere_path)
	if not os.path.exists(vswhere_path):
		raise EnvironmentError("vswhere.exe not found at: %s", vswhere_path)

	result = subprocess.run(f'{vswhere_path} {args}', capture_output = True)

	if result.returncode != 0:
		raise EnvironmentError("vswhere failed with exit code: {}".format(result.returncode))

	return result.stdout.decode("utf-8").rstrip()

def find_vcvars_location():
	vs_path = run_vswhere('-latest -prerelease -property installationPath')

	if not vs_path:
		raise EnvironmentError("vswhere.exe didn't find Visual Studio")

	print(f"Found VS at: {vs_path}\n")

	vcvars_path = os.path.join(vs_path, 'VC\\Auxiliary\\Build\\')
	if not os.path.exists(vcvars_path):
		raise EnvironmentError("vcvars directory doesn't exist: %s", vcvars_path)

	return vcvars_path

#Example usage: #run_vcvarsall("x64")
def run_vcvarsall(args):
	typer_commands.run_batch_file_and_import_its_environment_variables_to_current_process(os.path.join(find_vcvars_location(), "vcvarsall.bat"), args)



def print_directory_tree(path = '.', max_depth = 5):

	path = os.path.abspath(os.path.normpath(path))

	did_trigger_breakpoint = False

	def traverse(path, depth):
		nonlocal did_trigger_breakpoint

		indent = ''
		for i in range(depth):
			indent += '\t'

		if depth > 3 and not did_trigger_breakpoint:
			import traceback
			did_trigger_breakpoint = True;
			breakpoint()


		if depth >= max_depth: return

		with os.scandir(path) as it:
			for entry in it:
				print(f'{indent}{entry.name}')
				if entry.is_dir():
					traverse(entry.path, depth + 1)

	traverse(path, 0)


def typer_dev():
	run_vcvarsall('x64')

	typer_commands.cd('E:/Typer')


def vis_dev():
	run_vcvarsall('x64')

	typer_commands.cd('E:/Vis')

def open_sublime_text_packages_folder():
	assert(os.name == 'nt')
	
	st_path = os.path.join(os.environ["APPDATA"], 'Sublime Text 3')
	os.startfile(st_path)

def tlauncher():
	assert(os.name == 'nt')
	
	st_path = os.path.join(os.environ["APPDATA"], '.minecraft/tlauncher.exe')
	os.startfile(st_path)

def count_typer_lines():
	saved_cwd = os.getcwd();

	pc_name = platform.node()

	if pc_name == 'DESKTOP-EIUG5MQ':
		os.chdir("E:/Typer")
	elif pc_name == 'fridge':
		os.chdir("/home/peppingdore/Typerminal")

	try:
		subprocess.run(r"cloc --exclude-dir=detours,V-Tune,freetype,gl,stb,include,optick,cmake-build-debug,shaderc,vulkan,Tracy,python_headers,unicode,ft,icu,clip --include-ext=h,cpp  --by-file src/b_lib/. src", shell = True, stdin = sys.stdin, stdout = sys.stdout, stderr = subprocess.STDOUT)
	finally:
		os.chdir(saved_cwd)




def debugger_test():
	def b(arg_a, arg_b, sys_module, *varargs, **kwargs):
		print(varargs)
		breakpoint()
		
		for it in kwargs:
			print(it)


	def a(a_arg, b_arg):
		print(a_arg)
		print(b_arg)

		b(a_arg, b_arg, sys, "1 str", "2 str", 3, 4, a, sys, dick = "suck", gachi = "bass", b_sys = sys)


	a('argument a', 'argument b')
	
	import threading
	t = threading.Thread(target = a, args = ('thread 2 b', 'thread 2 a'))
	t.start()
	t.join()



def test():
	for x in range(100):
		print(f'{x=}\n')

	i = 4 * 3
	breakpoint()
	print(f"hut {i}")

def print_some_text():
	for i in range(600):
		sys.stdout.write(f"text {i}")


