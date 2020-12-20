import os
import sys
import typer
import subprocess
import typer
from pathlib import Path
import ascii_colors
import time
import platform

pc_name = platform.node()

windows_pc_name = 'DESKTOP-EIUG5MQ'
linux_pc_name = 'fridge'


if os.name == 'nt':
	additional_path_entries = [
		r'D:\\llvm\\build\\Debug\\bin', # For llvm-mca
		r'D:\\Programs',
		r'D:\\vcpkg',
		r'C:\\VulkanSDK\\1.2.135.0\\Bin',
		r'C:\\Program Files\\Far Manager',
		r'C:\\Users\\peppingdore\\AppData\\Local\\Android\\Sdk\\platform-tools'
	]

	for ent in additional_path_entries:
		os.environ["PATH"] += ent + os.pathsep

if os.name == 'posix':
	os.environ['PATH'] += os.pathsep + '/snap/bin'


import hot_reloader


import builder
hot_reloader.watch_module(builder)


#import command_time_printer
if True:
	import b_prompt
	hot_reloader.watch_module(b_prompt)
else:
	import run_only_wsl

# -- Moved b_syntax_proc to typer.py. 
# import b_syntax_proc
# hot_reloader.watch_module(b_syntax_proc)




typer_ship_folder = "E:/Typer_Ship"

typer_dev_folder = "D:/Typer"
typer_dev_runnable_folder = os.path.join(typer_dev_folder, "Runnable")




def copy_typer_to_ship():
	try:
		typer.commands.rmdir(typer_ship_folder, with_content = True)
	except:
		pass
		
	typer.commands.mkdir(typer_ship_folder)

	try:
		typer.commands.rmdir(os.path.join(typer_dev_runnable_folder, "python/__pycache__"), with_content = True)
		typer.commands.rmdir(os.path.join(typer_dev_runnable_folder, "user_scripts/__pycache__"), with_content = True)
	except:
		pass

	typer.commands.copy_directory(os.path.join(typer_dev_runnable_folder, "fonts"),        os.path.join(typer_ship_folder, "fonts"))
	typer.commands.copy_directory(os.path.join(typer_dev_runnable_folder, "python"),       os.path.join(typer_ship_folder, "python"))
	typer.commands.copy_directory(os.path.join(typer_dev_runnable_folder, "user_scripts"), os.path.join(typer_ship_folder, "user_scripts"))

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
		typer.commands.copy_file(os.path.join(typer_dev_runnable_folder, file), os.path.join(typer_ship_folder, file))




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
	typer.typer_commands.run_batch_file_and_import_its_environment_variables_to_current_process(os.path.join(find_vcvars_location(), "vcvarsall.bat"), args)
	# typer.commands.run_batch_file_and_import_its_environment_variables_to_current_process(os.path.join(find_vcvars_location(), "vcvarsall.bat"), args)



def print_directory_tree(path = '.', max_depth = 5):

	path = os.path.abspath(os.path.normpath(path))

	def traverse(path, depth):

		indent = ''
		for i in range(depth + 1):
			indent += '\t'

		if depth >= max_depth: return


		try:
			with os.scandir(path) as it:

				entry_index = 0

				for entry in it:
					sys.stdout.write(indent)

					if entry_index == 0:
						sys.stdout.write(f'|- |-{entry.name}\n')
					else:
						sys.stdout.write(f'\t|-{entry.name}\n')
					
					if entry.is_dir():
						traverse(entry.path, depth + 1)

					entry_index += 1
		except:
			pass


	traverse(path, 0)


def typer_dev():
	run_vcvarsall('x64')

	typer.commands.cd('E:/Typer')


def vis_dev():
	run_vcvarsall('x64')

	typer.commands.cd('E:/Vis')

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

	if pc_name == windows_pc_name:
		os.chdir("E:/Typer")
	elif pc_name == linux_pc_name:
		os.chdir("/home/peppingdore/Typerminal")

	try:
		subprocess.run(r"cloc --exclude-dir=detours,V-Tune,freetype,gl,stb,include,optick,cmake-build-debug,shaderc,vulkan,Tracy,python_headers,unicode,ft,icu,clip,python_lib_windows,python_lib_osx,python_lib_linux --include-ext=h,cpp,py,mm --exclude-list-file=cloc_exclude_list.txt --by-file src/b_lib/. src Runnable/python", shell = True, stdin = sys.stdin, stdout = sys.stdout, stderr = subprocess.STDOUT)
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


def reboot():
	if os.name == 'nt':
		os.system("shutdown /r")
	else:
		os.system("reboot now")



def run_conhost_bypass(cmd):
	subprocess.run(cmd, shell = True, stdout = sys.stdout, stderr = subprocess.STDOUT, stdin = sys.stdin)


def copy_typer_exe_to_ship():
	if pc_name == windows_pc_name:
		typer.commands.copy_file("E:/Typer/Runnable/Typerminal.exe", "E:/Typer_Ship/Typerminal.exe")
	elif pc_name == linux_pc_name:
		typer.commands.copy_file("/home/peppingdore/Typerminal/Runnable/Typerminal.elf", "/home/peppingdore/Typer_Ship/Typerminal.elf")



def penis():
	import typer.terminal_x


	for i in range(0, 1000):
		typer.terminal_x.begin_frame()
		typer.terminal_x.renderer_draw_rect(typer.terminal_x.Rect(0, 0, 400, 400), typer.terminal_x.rgba(255, 100, 100, 255))
		typer.terminal_x.end_frame()

