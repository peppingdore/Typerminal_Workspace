import os
import sys
import typer
import subprocess

def run_wsl():
	process = typer.launch_process('wsl')

	typer.exit()

typer.prompt = run_wsl