from Shared import *

def fix_js_style(js_dir, excluded_files = [], excluded_dirs = []):
  command = ['fixjsstyle']
  command += ['-r', js_dir]
  command += ['--debug_indentation']
  if(len(excluded_files)):
    command += ['-x', ','.join(excluded_files)]
  if(len(excluded_dirs)):
    command += ['-e', ','.join(excluded_dirs)]

  run_process(command)
