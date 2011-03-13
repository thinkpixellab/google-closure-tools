import subprocess
import sys
import os
import glob
import re

def coffee(js_dir, coffee_dir):
  args = ['coffee', '--bare']
  args += ['-o', js_dir]
  args += ['-c', coffee_dir]

  subprocess.call(args)

def getCommonArgs(closure_library_path):
  args = ['python', os.path.join(closure_library_path, 'closure/bin/calcdeps.py')]
  args += ['--dep', os.path.join(closure_library_path, 'closure/goog/base.js')]
  args += ["-o", "deps"]
  return args

def generate_deps(closure_library_path, js_dirs, deps_path):
  args = getCommonArgs(closure_library_path)

  for dir in js_dirs:
    args += ['-p', dir]
  args += ["--output_file", deps_path]

  subprocess.call(args)

def removeOrphanedJs(diff):
  # remove corresponding js files
  if(diff.has_key('removed')):
    removed = diff['removed']
    print removed
    for file in removed:
      file = re.sub('coffee/', 'js/', file)
      file = re.sub('\.coffee$', '\.js', file)
      if os.path.exists(file):
        print 'removing ' + file
        os.remove(file)

      print file
