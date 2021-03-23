import os
import sys
import typer
import subprocess
from pathlib import Path
import ascii_colors
import time
from datetime import datetime

def get_active_branch_name():

	directory_stack = []
	directory_stack.append(Path.cwd())
	directory_stack.extend(Path.cwd().parents)
	
	for directory in directory_stack:
		head_dir = directory / ".git" / "HEAD"
		try:
			with head_dir.open("r") as f: content = f.read().splitlines()

			for line in content:
				if line[0:4] == "ref:":
					return line.partition("refs/heads/")[2]
		except:
			pass

	return ''

# Error is ~4 hours i think
birth_date = datetime.fromisoformat('2001-04-19T16:00:00.000000')

def days_since_birth():
	delta_date = datetime.today() - birth_date 
	return delta_date.days

'''
def to_year_fraction(date):
    def since_epoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = since_epoch(date) - since_epoch(startOfThisYear)
    yearDuration = since_epoch(startOfNextYear) - since_epoch(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction
'''

def b_prompt():

	return

	# sys.stdout.write('واهُ عمرُ بْن الخطَّاب ')

	sys.stdout.write(f'Day №{days_since_birth()} ')

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

	sys.stdout.write(f' {ascii_colors.yellow.background}       {ascii_colors.reset_background_color}')

	sys.stdout.write(' $ ')

typer.prompt = b_prompt

