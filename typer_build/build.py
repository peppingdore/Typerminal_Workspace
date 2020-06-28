import sys
import os
import time
from enum import Enum

import builder




class Build_Type(Enum):
	Debug         = 0
	Optimized     = 1
	Tracy         = 2
	Max_Optimized = 3


build_type = Build_Type.Optimized





def main():
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

	build_options.executable_path = 'Runnable/Typer.exe'

	build_options.sources = [
		'Main.cpp',
		'UI.cpp',
		'Renderer.cpp',
		'Settings.cpp'
	]

	build_options.include_directories = [
		'b_lib/ft'
	]

	build_options.lib_directories = [
		'lib'
	]

	build_options.defines = [
		'_DEBUG',
		('DEBUG', 1),
		'_UNICODE',
		'UNICODE',
	]


	build_options.use_clang_cl = True

	build_options.use_windows_dynamic_crt = True
	build_options.use_windows_crt_debug_version = build_type == Build_Type.Debug

	build_options.use_windows_subsystem = True

	build_options.avx = True


	build_options.root_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
	build_options.intermidiate_dir = "build_temp"



	if build_type == Build_Type.Debug:
		build_options.optimization_level = 0
	elif build_type == Build_Type.Optimized or build_type == Build_Type.Tracy:
		build_options.optimization_level = 2

	if build_type == Build_Type.Tracy:
		build_options.sources.append("tracy/TracyClient.cpp")
		build_options.defines.append('TRACY_ENABLE')



	builder.build(build_options)

	print(f'Build took: {time.perf_counter() - build_start_time} seconds')


if __name__ == '__main__':
	main()