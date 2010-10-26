import os
import sys
import logging
import subprocess
import datetime
import fnmatch

_default_tmp_dir = 'tmp'

def writeXmlSansInstructions(dom, file):
  with open(file, "w") as fp:
    for node in dom.childNodes:
      node.writexml(fp)
  
def remove_if_exists(path):
  if os.path.exists(path):
    os.remove(path)

def get_tmp_file_name(source_file_name, tmp_dir = _default_tmp_dir):
  name = os.path.basename(source_file_name)
  safe_now = datetime.datetime.utcnow().isoformat().replace(':','_')
  name = "{0}_{1}".format(safe_now, name)
  if os.path.exists(tmp_dir) != True:
    os.mkdir(tmp_dir)
  return os.path.join(tmp_dir, name)

def run_process_file_command(command_func):
  args, tmp_file, out_file = command_func()
  stdoutdata = run_process(args)
  logging.info("Moving temp file to '%s'", out_file)
  remove_if_exists(out_file)
  os.rename(tmp_file, out_file)

def run_process(args):
  logging.basicConfig(format=' * %(message)s', level=logging.INFO)
  logging.info('* * * * *')
  logging.info('Requested command: %s', ' '.join(args))
  proc = subprocess.Popen(args, stdout=sys.stdout)
  logging.info('Running...')
  proc.communicate()
  if(proc.returncode != 0):
    logging.error('Command failed')
    sys.exit(1)

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename
