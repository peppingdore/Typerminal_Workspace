import os
import sys
import typer_commands
import subprocess

# For llvm-mca
os.environ["PATH"] += r'E:\llvm\build\Debug\bin' + os.pathsep
os.environ["PATH"] += r'E:\Programs' + os.pathsep



import builder
import hot_reloader

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

	def traverse(path, depth):
		
		indent = ''
		for i in range(depth):
			indent += '\t'

		if depth >= max_depth: return

		with os.scandir(path) as it:
			for entry in it:
				print(f'{indent}{entry.name}')
				if entry.is_dir():
					traverse(entry.path, depth + 1)

	
	traverse(path, 0)


def prepare_typer_dev_environment():
	run_vcvarsall('x64')

	typer_commands.cd('E:/Typer')


def prepare_vis_dev_environment():
	run_vcvarsall('x64')

	typer_commands.cd('E:/Vis')