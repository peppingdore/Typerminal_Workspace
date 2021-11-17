# This is small 'build system' that i use to build Typerminal itself and my second personal project.


import sys
import os
import subprocess
import types
import threading
import time
from pathlib import Path

import ascii_colors


class Library:
	def __init__(self, name, link_statically = False):
		self.name = name
		self.link_statically = link_statically

class Build_Options:
	def __init__(self):
		self.disable_warnings = False
		self.generate_debug_symbols = True

		self.optimization_level = 0

		self.src_directory = None
		self.output_directory = None

		self.architecture = None
		self.vendor = None
		self.system = None
		self.abi = None

		self.executable_path = None

		self.sources = None

		self.include_directories = []

		self.lib_directories = []

		self.libraries = []

		self.defines = []

		self.root_dir = None
		self.intermidiate_dir = None

		self.use_clang_cl = False

		self.use_msvc = False

		self.use_windows_dynamic_crt = False
		self.use_windows_crt_debug_version = False
		self.use_windows_subsystem = False

		self.avx = False
		self.aes = False

		self.output_assembly = False

		self.print_source_compilation_time = False

		self.additional_clang_flags = []
		self.additional_linker_flags = []

		self.natvis_files = []


class Build_Result:
	def __init__(self):
		self.success = False
		self.executable_path = None



root_dir = ''
intermidiate_dir = ''
src_dir = ''


def build(build_options):

	if os.name != 'nt':
		assert(not build_options.use_clang_cl)
		assert(not build_options.use_windows_dynamic_crt)
		assert(not build_options.use_windows_crt_debug_version)
		assert(not build_options.use_windows_subsystem)

	result = Build_Result()

	global root_dir
	global intermidiate_dir
	global src_dir

	root_dir = build_options.root_dir
	intermidiate_dir = os.path.join(root_dir, build_options.intermidiate_dir)
	src_dir = os.path.join(root_dir,  build_options.src_directory)


	os.makedirs(intermidiate_dir, exist_ok = True)


	any_failed_source = False

	threads = []



	max_source_length = 30
	max_source_length_without_ellipsis = max_source_length - len('...')
	max_actual_source_length = min((max(map(lambda x: len(x), build_options.sources), default = 0), max_source_length))

	print_result_lock = threading.Lock()

	print("Compiling:")
	for source in build_options.sources:
		print(f"  {source}")

	for source in build_options.sources:

		cmd_line = build_clang_command_line_for_source(build_options, source)


		def build_thread_proc(source):

			source_compilation_start_time = time.perf_counter()
			run_result = subprocess.run(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, shell = True)
			source_compilation_time = time.perf_counter() - source_compilation_start_time


			print_result_lock.acquire()

			succeeded = run_result.returncode == 0

			nonlocal any_failed_source

			if not succeeded:
				any_failed_source = True
		

			file_name_background_rgb = (20, 150, 0) if succeeded else (200, 20, 0)



			file_name_to_print = ''
			
			if len(source) >= max_source_length_without_ellipsis:
				file_name_to_print += source[:max_source_length_without_ellipsis]
				file_name_to_print += '...'
			else:
				file_name_to_print += source
				for i in range(max_actual_source_length - len(source)):
					file_name_to_print += ' '


			if not succeeded:
				file_name_to_print += " (FAILED)    "
			else:
				file_name_to_print += " (SUCCEEDED) "
				
				if build_options.output_assembly:
					file_name_background_rgb = (0, 150, 150)
					file_name_to_print += f' -> {get_asm_output_path(source)}  '


			if build_options.print_source_compilation_time:
				file_name_to_print += "  {:.2f} s ".format(source_compilation_time)



			print(f'{ascii_colors.rgb(*file_name_background_rgb).background}{ascii_colors.rgb(0, 0, 0).foreground}--- {file_name_to_print}{ascii_colors.reset_background_color}{ascii_colors.reset_foreground_color}')

			if len(run_result.stdout):
				sys.stdout.write('\n')
				print(run_result.stdout.decode('utf-8'))
				print('\n\n')


			print_result_lock.release()


		build_thread = threading.Thread(target = build_thread_proc, args = [source])
		build_thread.start()

		threads.append(build_thread)



	for t in threads:
		t.join()


	if any_failed_source or build_options.output_assembly:
		return result



	run_result = subprocess.run(build_linker_command_line(build_options), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, shell = True)
	succeeded = run_result.returncode == 0

	linking_result_title_background = (20, 150, 0) if succeeded else (200, 20, 0)
	linking_result_title = "LINKING "
	if not succeeded:
		linking_result_title += " FAILED "
	else:
		linking_result_title += " SUCCEEDED "

	print(f'{ascii_colors.rgb(*linking_result_title_background).background}{ascii_colors.rgb(0, 0, 0).foreground}--- {linking_result_title}{ascii_colors.reset_background_color}{ascii_colors.reset_foreground_color}')


	if not succeeded or not build_options.ignore_linker_output_on_success:
		print(run_result.stdout.decode('utf-8', errors = 'ignore'))

	if succeeded:
		print(f'{ascii_colors.yellow}{get_linker_output_path(build_options)}{ascii_colors.reset_foreground_color}\n')

	result.success = True
	result.executable_path = get_linker_output_path(build_options)

	return result


def get_asm_output_path(source):
	return os.path.join(intermidiate_dir, f"{Path(source).stem}.asm")

def get_source_output_path(source):
	return os.path.join(intermidiate_dir, f"{Path(source).stem}.obj")

def get_linker_output_path(build_options):
	return os.path.normpath(os.path.join(root_dir, f"{build_options.executable_path}"))


def build_linker_command_line(build_options):
	linker_inputs = ' '
	for source in build_options.sources:
		linker_inputs += ' "'
		linker_inputs += get_source_output_path(source)
		linker_inputs += '" '

	for lib in build_options.libraries:
		if lib.link_statically:
			linker_inputs += f' {lib.name} '


	cmd = 'clang-cl' if build_options.use_clang_cl else 'clang++'

	cmd += f' {linker_inputs} '

	if os.name == 'nt':
		cmd += ' -fuse-ld=lld-link '


	if os.name == 'nt':
		for it in build_options.natvis_files:
			cmd += f' -clang:--for-linker=/natvis:"{os.path.join(src_dir, it)}" '


	if build_options.use_clang_cl:
		cmd += f' {get_windows_crt_variant(build_options)} '

	if build_options.use_clang_cl:
		cmd += ' /clang:-g '
	else:
		cmd += ' -g '

	
	linker_output_path = get_linker_output_path(build_options)

	if build_options.use_clang_cl:
		cmd += f' /clang:--output="{linker_output_path}"'
	else:
		cmd += f' --output="{linker_output_path}"'


	for clang_flag in build_options.additional_linker_flags:
		if build_options.use_clang_cl:
			cmd += f' /clang:{clang_flag} '
		else:
			cmd += f' {clang_flag} '



	#cmd += f' -v '


	for lib_dir in build_options.lib_directories:
		lib_path = os.path.join(root_dir, lib_dir)
		
		if build_options.use_clang_cl:
			cmd += f' -clang:--for-linker=/LIBPATH:"{lib_path}" '
		else:
			cmd += f' --library-directory="{lib_path}" '


	for lib in build_options.libraries:

		if os.name != 'posix':
			if lib.link_statically:
				raise Exception("link_statically is only supported on POSIX")

		if build_options.use_clang_cl:
			cmd += f' /clang:-l{lib.name} '
		else:
			if not lib.link_statically:
				cmd += f' -l{lib.name} '


	if build_options.use_clang_cl and build_options.use_windows_subsystem:
		cmd += ' -clang:--for-linker=/SUBSYSTEM:WINDOWS ' 
		cmd += ' -clang:--for-linker=/entry:mainCRTStartup '

	return cmd


def get_windows_crt_variant(build_options):
	assert(build_options.use_clang_cl)

	if build_options.use_windows_dynamic_crt:
		if build_options.use_windows_crt_debug_version:
			return '/MDd'
		else:
			return '/MD'
	else:
		if build_options.use_windows_crt_debug_version:
			return '/MTd'
		else:
			return '/MT'


def build_clang_command_line_for_source(build_options, source):


	cmd = 'clang-cl' if build_options.use_clang_cl else 'clang++'


	use_msvc = build_options.use_clang_cl and build_options.use_msvc
	
	if build_options.use_clang_cl and use_msvc:
		cmd = 'cl'

	if build_options.use_clang_cl and not use_msvc:
		cmd += ' /Zc:dllexportinlines- '

	if use_msvc:
		cmd += ' /FS ' # Fix PDB write issues.

	if build_options.disable_warnings and not use_msvc:
		cmd += ' -Wno-everything '


	# Clang doesn't report missing return by default. By I'd prefer it to.
	
	if not use_msvc:
		cmd += ' -Werror=return-type '
		cmd += ' -fno-strict-aliasing '


	def add_flag(flag):
		nonlocal cmd
		cmd += ' '
		cmd += flag
		cmd += ' '


	# We always want our output to be colored
	if not use_msvc:
		add_flag('-fansi-escape-codes')
		add_flag('-fcolor-diagnostics')


	if build_options.use_clang_cl:
		cmd += '  /TP ' # Compile as C++
		cmd += f' {get_windows_crt_variant(build_options)} '


	# cmd += ' -ferror-limit=0 '

	if build_options.use_clang_cl:
		add_flag('/std:c++latest')
	else:
		add_flag('-std=c++2a')


	if build_options.output_assembly:
		if build_options.use_clang_cl:
			add_flag('/c')  
			add_flag(f'/Fa"{get_asm_output_path(source)}"')  
		else:
			raise Exception("I couldn't make clang++ output assembly, please set build_options.use_clang_cl = True for now it will do that ")
			add_flag(f'-S --output="{get_asm_output_path(source)}"')  
	else:	
		# Prevent linker execution
		if build_options.use_clang_cl:
			add_flag('/c')  
		else:
			add_flag('-c')


	for clang_flag in build_options.additional_clang_flags:
		if build_options.use_clang_cl:
			add_flag(f'-clang:{clang_flag}')
		else:
			add_flag(clang_flag)


	if not build_options.use_clang_cl:
		target_name = f'{build_options.architecture}-{build_options.vendor}-{build_options.system}-{build_options.abi}'
		add_flag(f'--target={target_name}')


	if build_options.generate_debug_symbols:
		if build_options.use_clang_cl:
			add_flag('/Zi')
		else:
			# add_flag('-gcodeview')
			add_flag('-g')

	for inc in build_options.include_directories:
		inc_path = os.path.join(src_dir, inc)
		
		if build_options.use_clang_cl:
			add_flag(f'/I"{inc_path}"')
		else:
			add_flag(f'--include-directory="{inc_path}"')



	if build_options.avx:
		if build_options.use_clang_cl:
			add_flag(f'/arch:AVX')
		else:
			add_flag(f'-mavx')


	if build_options.aes:
		if build_options.use_clang_cl:
			if not use_msvc:
				add_flag(f'-clang:-maes')
			else:
				pass # Does msvc enable aes by default? 
		else:
			add_flag(f'-maes')




	for define in build_options.defines:
		if isinstance(define, tuple):
			if build_options.use_clang_cl:
				add_flag(f'/D{define[0]}={define[1]}')
			else:
				add_flag(f'-D{define[0]}={define[1]}')
		else:
			if build_options.use_clang_cl:
				add_flag(f'/D{define}')
			else:
				add_flag(f'-D{define}')



	if not (build_options.optimization_level >= 0 and build_options.optimization_level <= 3):
		raise Exception('optimization_level should be integer in range[0; 3]')


	if build_options.use_clang_cl:
		if build_options.optimization_level == 0:
			add_flag('/Od')
		elif build_options.optimization_level == 1:
			add_flag('/O2')
		elif build_options.optimization_level == 2:
			add_flag('/O2')
		elif build_options.optimization_level == 3:
			add_flag('/O2ix')

	else:
		if build_options.optimization_level == 0:
			add_flag('-O0')
		elif build_options.optimization_level == 1:
			add_flag('-O1')
		elif build_options.optimization_level == 2:
			add_flag('-O2')
		elif build_options.optimization_level == 3:
			add_flag('-O3')



	if not build_options.output_assembly:
		if build_options.use_clang_cl:
			cmd += f' /Fo"{get_source_output_path(source)}"'
		else:
			cmd += f' --output="{get_source_output_path(source)}"'

	cmd += ' "'
	cmd += os.path.join(src_dir, source)
	cmd += '" '


	# print(cmd)

	return cmd


