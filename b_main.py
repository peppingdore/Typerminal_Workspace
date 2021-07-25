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

windows_laptop_name = 'LAPTOP-APR7OV7Q'
windows_pc_name = 'DESKTOP-PT41GUN'
linux_pc_name = 'fridge'


if os.name == 'nt':
	additional_path_entries = [
		r'C:\\Programs',
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




if pc_name == windows_pc_name:
	typer_ship_folder = "E:/Typer_Ship"
	typer_dev_folder = "D:/Typer"
elif pc_name == windows_laptop_name:
	typer_ship_folder = "C:/Typer_Ship"
	typer_dev_folder = "C:/Typer"


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
	#typer.typer_commands.run_batch_file_and_import_its_environment_variables_to_current_process(os.path.join(find_vcvars_location(), "vcvarsall.bat"), args)
	typer.commands.run_batch_file_and_import_its_environment_variables_to_current_process(os.path.join(find_vcvars_location(), "vcvarsall.bat"), args)

def typer_dev():
	assert(os.name == 'nt')
	run_vcvarsall('x64')
	typer.commands.cd(typer_dev_folder)



def compile_typer_and_run():
	compile_typer()
	typer.launch_process("Runnable/Typerminal.exe")

did_run_typer_typer_dev = False
def compile_typer(*args):
	global did_run_typer_typer_dev

	if not did_run_typer_typer_dev:
		typer_dev()
		did_run_typer_typer_dev = True

	typer.commands.cls()

	'''
	typer.input_procedure("build/build.py debug unity do_not_compile_shaders")
	typer.input_procedure("Runnable/Typerminal.exe")
	'''

	'''
	if not compile_shaders:
		args.append('do_not_compile_shaders')

	if tracy:
		args.append('tracy')
	'''
	typer.commands.execute_script("build/build.py", *args)


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

	os.chdir(typer_dev_folder)

	try:
		subprocess.run(r"cloc --exclude-dir=detours,V-Tune,freetype,gl,stb,include,optick,cmake-build-debug,shaderc,vulkan,tracy,python_headers,unicode,ft,icu,clip,python_lib_windows,python_lib_osx,python_lib_linux,harfbuzz,gl_headers,examples,meow_hash --include-ext=h,cpp,py,mm --exclude-list-file=cloc_exclude_list.txt --by-file src/b_lib/. src Runnable/python", shell = True, stdin = sys.stdin, stdout = sys.stdout, stderr = subprocess.STDOUT)
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
	import time
	import math
	from typer import terminal_x

	t = time.time()

	for i in range(0, 100):
		terminal_x.begin_frame()
		
		scale = math.sin(t)
		scale = (scale + 1.0) / 2.0

		offset = int(400 * scale);
		# offset = 0

		# terminal_x.set_reserved_height(400)
		terminal_x.set_reserved_height(offset)
		offset = 0


		terminal_x.renderer_draw_rect(terminal_x.Rect(0, 0 + offset, 400, 400 + offset), terminal_x.rgba(255, 100, 100, 255))
		terminal_x.end_frame()
		t += (time.time() - t)


def penis2():
	import time
	import math
	from typer import terminal_x

	t = time.time()

	for i in range(0, 1000):
		terminal_x.begin_frame()
		
		scale = math.sin(t)
		scale = (scale + 1.0) / 2.0

		offset = int(400 * scale);
		# offset = 0

		# terminal_x.set_reserved_height(400)
		terminal_x.set_reserved_height(offset)

		offset = 0


		terminal_x.renderer_draw_rect(terminal_x.Rect(0, 0 + offset, 400, 400 + offset), terminal_x.rgba(255, 100, 100, 255))

		is_button_pressed = terminal_x.ui_button(terminal_x.Rect(0, 0 + offset, 400, 400 + offset), "suck dick", terminal_x.rgba(100, 100, 100, 255), terminal_x.UI_ID("chlen", 0, terminal_x.UI_ID_Type.Id))
		if is_button_pressed:
			terminal_x.end_frame()
			break

		terminal_x.end_frame()
		t += (time.time() - t)


def penis3():
	import time
	import math
	from typer import terminal_x

	t = time.time()

	working_dir = os.getcwd()
	entries = []

	def list_dir(dir):
		nonlocal new_current_dir

		new_current_dir = dir

		entries = []
		with os.scandir(dir) as it:
			for entry in it:
				entries.append(entry)

		return entries


	current_dir = working_dir
	entries = list_dir(working_dir)

	button_height = 32
	top_panel_height = 48

	new_entries = None
	new_current_dir = None

	while True:

		if new_entries:
			entries = new_entries
			current_dir = new_current_dir

			new_current_dir = None
			new_entries = None



		with terminal_x.frame():
			overall_height = 0
			overall_height += len(entries) * button_height

			overall_height += button_height
			overall_height += top_panel_height


			terminal_x.set_reserved_height(overall_height)

			offset = overall_height

			if terminal_x.ui_button(terminal_x.Rect(0, -button_height + offset, 100, 0 + offset), "cd", terminal_x.rgba(100, 120, 150, 255), terminal_x.UI_ID("chlen", offset / button_height, terminal_x.UI_ID_Type.Id)):
				os.chdir(current_dir)
				break

			if terminal_x.ui_button(terminal_x.Rect(100, -button_height + offset, 100 + 100, 0 + offset), "X", terminal_x.rgba(100, 120, 150, 255), terminal_x.UI_ID("chlen", offset / button_height, terminal_x.UI_ID_Type.Id)):
				break

			offset -= top_panel_height

			if terminal_x.ui_button(terminal_x.Rect(0, -button_height + offset, 400, 0 + offset), "..", terminal_x.rgba(100, 120, 150, 255), terminal_x.UI_ID("chlen", offset / button_height, terminal_x.UI_ID_Type.Id)):
				new_entries = list_dir(os.path.join(current_dir, ".."))

			offset -= button_height


			for entry in entries:
				is_button_pressed = terminal_x.ui_button(terminal_x.Rect(0, -button_height + offset, 400, 0 + offset), entry.name, terminal_x.rgba(100, 120, 150, 255), terminal_x.UI_ID("chlen", offset / button_height, terminal_x.UI_ID_Type.Id))

				if is_button_pressed:
					if entry.is_dir():
						new_entries = list_dir(entry.path)


				offset -= button_height


			t += (time.time() - t)



# @TODO: Why can't we call this with ' emojis 10 ' syntax????? 
def emojis(count = 1):
	for i in range(count):
		sys.stdout.write("😎🔫🍆  ✊🏿  ")

	sys.stdout.write('\n')


def allah():
	print(ascii_colors.rgb(30, 240, 100))
	print('''
suck my dick رواهُ عمرُ بْن الخطَّاب
رواهُ عمرُ بْن الخطَّاب
سَمِعْتُ عُمَرَ بْنَ الْخَطَّابِ – رضى الله عنه – يَقُولُ سَمِعْتُ هِشَامَ بْنَ حَكِيمِ بْنِ حِزَامٍ يَقْرَأُ سُورَةَ الْفُرْقَانِ عَلَى غَيْرِ مَا أَقْرَؤُهَا، وَكَانَ رَسُولُ اللَّهِ – صلى الله عليه وسلم – أَقْرَأَنِيهَا (بطريقةٍ مختلفة)، وَكِدْتُ أَنْ أَعْجَلَ عَلَيْهِ، ثُمَّ أَمْهَلْتُهُ حَتَّى انْصَرَفَ، ثُمَّ لَبَّبْتُهُ بِرِدَائِهِ فَجِئْتُ بِهِ رَسُولَ اللَّهِ – صلى الله عليه وسلم – فَقُلْتُ إِنِّى سَمِعْتُ هَذَا يَقْرَأُ عَلَى غَيْرِ مَا أَقْرَأْتَنِيهَا، فَقَالَ لِى أَرْسِلْهُ. ثُمَّ قَالَ لَهُ اقْرَأْ». فَقَرَأَ. قَالَ «هَكَذَا أُنْزِلَتْ». ثُمَّ قَالَ لِى «اقْرَأْ». فَقَرَأْتُ فَقَالَ «هَكَذَا أُنْزِلَتْ. إِنَّ الْقُرْآنَ أُنْزِلَ عَلَى سَبْعَةِ أَحْرُفٍ فَاقْرَءُوا مِنْهُ مَا تَيَسَّرَ«.

 صحيح البُخاري 2419: الكتاب 44، الحديث 9
رواهُ ن ابنِ مسعود
«سَمِعْتُ رَجُلاً قَرَأَ آيَةً (قُرآنيَّة) وَسَمِعْتُ النَّبِيَّ -صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ- يَقْرَأُ خِلاَفَهَا، فَجِئْتُ بِهِ النَّبِيَّ -صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ- فَأَخْبَرْتُهُ، فَعَرَفْتُ فِي وَجْهِهِ الْكَرَاهِيَةَ وَقَالَ: كِلاَكُمَا مُحْسِنٌ، وَلاَ تَخْتَلِفُوا، فَإِنَّ مَنْ كَانَ قَبْلَكُمُ اخْتَلَفُوا فَهَلَكُوا«. صحيح البُخاري

 3476: الكتاب 60، الحديث 143
يخبرنا هذان الحديثان بوضوح أنه كانت هناك، خلال حياة النبيّ محمَّد، عدّة نُسَخٍ مختلفة لتلاوة القرآن قد استُخدِمَت وتمَّ الموافقة عليها من قبل النبيّ محمدصلى الله عليه وسلم، فما الذي حدث بعد وفاته؟

أبو بكر والقرآن
 رواه زَيد بن ثابت

أَرْسَلَ إِلَيَّ أَبُو بَكْرٍ مَقْتَلَ أَهْلِ اليَمَامَةِ، فَإِذَا عُمَرُ بْنُ الخَطَّابِ عِنْدَهُ”، قَال أَبُو بَكْرٍ رَضِ
		''')
	print(ascii_colors.reset_foreground_color)
		


def hristos():
	print(ascii_colors.rgb(240, 255, 100))
	print('''
В.Путин: Уважаемые граждане России! Дорогие друзья!

Обращаюсь к вам по вопросу, который сейчас волнует всех нас.

Мы видим, как остро развивается ситуация с эпидемией коронавируса в мире. Во многих странах продолжает нарастать число заболевших. Под ударом оказалась вся мировая экономика, уже сейчас прогнозируется её спад.

Благодаря заранее принятым мерам нам в целом удаётся пока сдерживать и широкое, и стремительное распространение болезни. Но мы с вами должны понимать, что Россия – просто даже в силу своего географического положения – не может отгородиться от угрозы. Рядом с нашими границами находятся государства, уже серьёзно поражённые эпидемией, и полностью заблокировать её проникновение в нашу страну объективно невозможно.

Но то, что мы можем и уже делаем, – так это работать профессионально, организованно и на опережение. И главный приоритет здесь – жизнь и здоровье наших граждан.

К развёртыванию системы своевременной медицинской помощи и профилактики подключены все возможности и ресурсы. Хочу особо обратиться к врачам, фельдшерам, медицинским сёстрам, сотрудникам больниц, поликлиник, ФАПов, служб скорой помощи, к нашим учёным. Вы сейчас на переднем крае защиты страны. Сердечно благодарю всех вас за самоотверженный труд.

Прошу граждан с предельным вниманием отнестись к рекомендациям врачей и органов власти. От этого сейчас очень многое зависит. Особенно это касается наиболее уязвимых групп населения: людей старшего поколения и тех, кто страдает хроническими заболеваниями. И для них, и для всех граждан сейчас стоит задача максимально снизить риски.

Естественно, возникает вопрос и об организации общероссийского голосования по поправкам в Конституцию, с предварительно определённой датой – 22 апреля. Вы знаете, как серьёзно, насколько серьёзно я к этому отношусь. И конечно, буду просить вас прийти и высказать своё мнение по этому вопросу – принципиальному, ключевому для нашей страны, для нашего общества.

Однако, как уже говорил ранее, абсолютным приоритетом для нас является здоровье, жизнь и безопасность людей. Поэтому считаю, что голосование необходимо перенести на более позднюю дату.

Оценим, как будет развиваться ситуация и в регионах, и в целом по стране, и, только опираясь на профессиональное мнение, рекомендации врачей, специалистов, примем решение о новом дне голосования.

Далее. Сейчас крайне важно предотвратить угрозу быстрого распространения болезни.

Поэтому объявляю следующую неделю нерабочей, с сохранением заработной платы. То есть выходные дни продлятся с субботы 28 марта по воскресенье 5 апреля.

Естественно, все структуры жизнеобеспечения, в том числе медицинские учреждения, аптеки, магазины, учреждения, обеспечивающие банковские, финансовые расчёты, транспорт, а также органы власти всех уровней продолжат свою работу.

Повторю, длинные выходные предусмотрены именно для того, чтобы снизить скорость распространения болезни.

Обращаюсь ко всем гражданам страны. Давайте не будем поступать, полагаясь на наше русское «авось». Не думайте, пожалуйста, как у нас бывает: «А, меня это не коснется!» Это может коснуться каждого. И тогда то, что происходит сегодня во многих западных странах, и в Европе, и за океаном, может стать нашим ближайшим будущим. Все рекомендации необходимо обязательно соблюдать. Надо поберечь и себя, и своих близких, проявить дисциплину и ответственность. И поверьте, самое безопасное сейчас – побыть дома.

Отдельно остановлюсь на текущей социально-экономической ситуации. Здесь нам также нужны дополнительные шаги, прежде всего чтобы обеспечить социальную защиту граждан, сохранение их доходов и рабочих мест, а также поддержку малого и среднего бизнеса, в котором заняты миллионы людей.

В этой связи будут реализованы следующие первоочередные меры.

Первое. Все социальные пособия и льготы, которые полагаются гражданам, в течение ближайших шести месяцев должны продлеваться автоматически, без предоставления каких-либо дополнительных справок и хождений по инстанциям. Например, если семья имеет право на льготы по ЖКХ, ей не надо будет регулярно подтверждать уровень своих доходов, чтобы получать такую поддержку.

Также обращаю внимание: выплаты к 75-летию Великой Победы ветеранам и труженикам тыла в 75 и 50 тысяч рублей соответственно должны быть осуществлены до майских праздников, раньше обычного, уже в апреле.''')
	print(ascii_colors.reset_foreground_color)


def print_big_text():
	for i in range(0, 100):
		if i % 2 == 0:
			hristos()
		else:
			allah()

