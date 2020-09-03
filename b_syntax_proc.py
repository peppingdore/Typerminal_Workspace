import typer
import typer_commands
import os
import sys

def syntax_proc(input, globals):
	if not input:
		return

	if input.startswith('#'):
		eval_string = input[1:]
		eval_result = eval(eval_string, globals, globals)
		if eval_result != None:
			print(eval_result)
	else:

		pieces = input.split()

		piece_one = pieces[0]
		arg_pieces = pieces[1:]

		def arg_mapper_func(arg):
			try:
				eval(arg, globals, globals)
			except:
				# Fallback to string
				return arg

		if piece_one in globals:
			evaled_args = map(arg_mapper_func, arg_pieces)

			globals[piece_one](*evaled_args)
		else:

			if piece_one.lower().endswith('.py') and os.path.isfile(piece_one):
				typer_commands.execute_script(piece_one, *arg_pieces)
			else:
				typer.launch_process(input)


typer.syntax_procedure = syntax_proc

