import os
import sys
import typer
import subprocess
from pathlib import Path
import ascii_colors

def get_active_branch_name():

    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f: content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]

def b_prompt():
	current_path = Path.cwd().resolve()
	sys.stdout.write(f'{ascii_colors.yellow}{current_path}{ascii_colors.reset_foreground_color}')

	current_branch = ''
	try:
		current_branch = get_active_branch_name()
	except:
		pass

	#current_branch = subprocess.run('git branch --show-current', shell = True, stdout = subprocess.PIPE).stdout.decode('utf-8')
	#current_branch = current_branch.rstrip('\n')

	if len(current_branch):
		sys.stdout.write(f' {ascii_colors.green.background}{current_branch}{ascii_colors.reset_background_color}')

	sys.stdout.write(' $ ')

typer.prompt = b_prompt

