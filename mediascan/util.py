
import subprocess

def get_terminal_size():
	width = int(subprocess.check_output(['tput', 'cols']))
	height = int(subprocess.check_output(['tput', 'lines']))
	return (width, height)
