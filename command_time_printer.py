import time
import ascii_colors
import typer

def print_command_time():
	print(f'{ascii_colors.yellow}Command execution started at: {time.strftime("%H:%M:%S", time.localtime())}{ascii_colors.reset_foreground_color}\n')


typer.execute_function_before_command(print_command_time)
