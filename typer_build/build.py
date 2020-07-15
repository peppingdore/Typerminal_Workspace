import sys
import os
import time
import ascii_colors
from enum import Enum

import builder
import subprocess




class Build_Type(Enum):
	Debug         = 0
	Optimized     = 1
	Tracy         = 2
	Shipment      = 3


build_type = Build_Type.Debug




def main():
	global build_type

	if len(sys.argv) > 1:
		build_type_name_lower = sys.argv[1].lower()

		found_enum_value = False

		for it in Build_Type:
			if build_type_name_lower == it.name.lower():
				build_type = it
				found_enum_value = True

		if not found_enum_value:
			raise Exception(f'{ascii_colors.red}Build type "{sys.argv[1]}" is not found{ascii_colors.reset_foreground_color}')




	print(f'Build {build_type.name} started')
	build_start_time = time.perf_counter()

	build_options = builder.Build_Options()

	build_options.generate_debug_symbols = True

	build_options.disable_warnings = True

	build_options.src_directory = 'src'

	# Ignored if clang-cl
	build_options.architecture = 'x86_64'
	build_options.vendor = 'pc'
	build_options.system = 'win32'
	build_options.abi = 'msvc'

	build_options.executable_path = 'Runnable/Typerminal.exe'

	build_options.sources = [
		'Main.cpp',
		'UI.cpp',
		'Renderer.cpp',
		'Settings.cpp',
		'Python_Debugger.cpp',
		'Python_Interp.cpp',
	]

	build_options.include_directories = [
		'b_lib/ft'
	]

	build_options.lib_directories = [
		'lib'
	]

	build_options.defines = [
		'_UNICODE',
		'UNICODE',
	]



	build_options.print_source_compilation_time = True


	build_options.use_clang_cl = True

	build_options.use_windows_dynamic_crt = True
	build_options.use_windows_crt_debug_version = build_type == Build_Type.Debug

	build_options.use_windows_subsystem = True

	build_options.avx = True


	build_options.root_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
	build_options.intermidiate_dir = "build_temp"


	if build_type == Build_Type.Shipment:
		build_options.defines.append('NDEBUG')
	else:
		build_options.defines.append('_DEBUG')
		build_options.defines.append(('DEBUG', 1))


	if build_type == Build_Type.Debug:
		build_options.optimization_level = 0
	elif build_type == Build_Type.Optimized or build_type == Build_Type.Tracy:
		build_options.optimization_level = 2
	elif build_type == Build_Type.Shipment:
		build_options.optimization_level = 3


	if build_type == Build_Type.Tracy:
		build_options.sources.append("tracy/TracyClient.cpp")
		build_options.defines.append('TRACY_ENABLE')



	result = builder.build(build_options)
	if result.success:
		icon_success = subprocess.run(f'rcedit "{result.executable_path}" --set-icon "{os.path.join(os.path.dirname(__file__), "../exe_icon.ico")}"').returncode == 0
		print(f'{(ascii_colors.green if icon_success else ascii_colors.red).foreground}Setting icon for executable {"SUCCEEDED" if icon_success else "FAILED"}{ascii_colors.reset_foreground_color}')



	print(f'Build took: {time.perf_counter() - build_start_time} seconds')


if __name__ == '__main__':
	main()