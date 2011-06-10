import os
import string
import glob
from Shared import *
import HtmlPost

jar_path = os.path.join(os.path.dirname(__file__), 'compiler-svn1171.jar')

tmp_dir = 'tmp'

def make_deps_core(closure_path, deps_js_path, js_dirs):
  
  command = ['python']
  command += [os.path.join(closure_path, 'bin','calcdeps.py')]
  
  command += ["--d", closure_path]
  command += ["-o", "deps"]
  
  for js_dir in js_dirs:
    command += ["-p", js_dir]
  
  tmp_file_path = get_tmp_file_name(deps_js_path)
  command += ["--output_file", tmp_file_path]
  return command, tmp_file_path, deps_js_path

class Closure:
  def __init__(self, closure_path, application_js_path, root_symbol, closure_dependencies, deps_js_path, compiled_js_path, extern_files):
    self.closure_path = closure_path
    self.deps_js_path = deps_js_path
    self.closure_dependencies = closure_dependencies
    self.application_js_path = application_js_path
    self.root_symbol = root_symbol
    self.extern_files = extern_files
    self.compiled_js_path = compiled_js_path
    self.debug = False
  
  def googPath(self):
    return os.path.join(self.closure_path, 'goog')
  
  def do_makeDeps(self):
    run_process_file_command(self.make_deps)
  
  def do_compile(self, debug = False):
    self.debug = debug
    run_process_file_command(self.compile)
  
  def deps_and_compile(self, debug = False):
    self.do_makeDeps()
    self.do_compile(debug)
  
  def build_and_process(self, source_html, target_html, debug = False, skip_build = False):
    if(not skip_build):
      self.deps_and_compile(debug)
    
    source_js_files = [os.path.join(self.googPath(), 'base.js')]
    source_js_files += [self.deps_js_path]

    if(self.application_js_path):
      source_js_files += [self.application_js_path]
    HtmlPost.replaceJsFiles(source_html, target_html, self.compiled_js_path, source_js_files)
  
  def make_deps(self):
    return make_deps_core(self.closure_path, self.deps_js_path, self.closure_dependencies)
  
  def get_compile_files(self):
    js_files = get_js_files_for_compile(self.closure_path, self.application_js_path, self.root_symbol, self.deps_js_path)
    
    return js_files
  
  def compile(self):
    js_files = self.get_compile_files()
    return compile_core(self.googPath(), js_files, self.extern_files, self.compiled_js_path, self.root_symbol, self.debug)
  
  # def print_tree(self):
  #   js_files, extern_files = self.get_compile_files()
  #   return print_tree_core(js_files, extern_files)

def get_closure_base():
  return ["java", "-jar", jar_path]

def get_closure_inputs(goog_path, js_files, extern_files):
  command_inputs = []
  
  command_inputs += ["--js", os.path.join(goog_path, 'base.js')]
  
  for file in js_files:
    command_inputs += ["--js", file]
  
  for file in extern_files:
    command_inputs += ["--externs", file]
  
  command_inputs += ["--manage_closure_dependencies", "true"]
  return command_inputs

def get_js_files_for_compile(closure_path, app_file, root_symbol, app_dep_file):
  goog_path = os.path.join(closure_path,'goog')
  dep_files = [app_dep_file]
  dep_files.append(os.path.join(goog_path,'deps.js'))
  
  provide_to_file_hash = {}
  file_to_require_hash = {}
  
  for dep_file in dep_files:
    process_deps(goog_path, dep_file, provide_to_file_hash, file_to_require_hash)

  files = []

  if(app_file):
    populate_required_files_for_file(app_file, files, provide_to_file_hash, file_to_require_hash)
  else:
    populate_required_files_for_symbol(root_symbol, files, provide_to_file_hash, file_to_require_hash)
  
  # ugly exception ->
  exception_files = [os.path.join(goog_path, 'events', 'eventhandler.js'), os.path.join(goog_path, 'events', 'eventtarget.js'), os.path.join(goog_path, 'debug', 'errorhandler.js')]
  for exception in exception_files:
    if(not exception in files):
      files.append(exception)
  
  return files

def get_goog_js_files():
  files = []
  # add js files in goog dir, without files in demos
  for file in find_files(closure_path, '*.js'):
    if(file.find('demos') == -1):
      files.append(file)
  return files

def get_command_with_inputs(goog_path, js_files, extern_files):
  return get_closure_base() + get_closure_inputs(goog_path, js_files, extern_files)

def compile_core(goog_path, js_files, extern_files, compiled_js_path, closure_entry_point = None, debug=False):
  command = get_command_with_inputs(goog_path, js_files, extern_files)

  if(closure_entry_point):
    command += ['--closure_entry_point', closure_entry_point]
  
  command += ["--compilation_level", "ADVANCED_OPTIMIZATIONS"] # SIMPLE_OPTIMIZATIONS
  command += ["--summary_detail_level", "3"]
  command += ["--warning_level", "VERBOSE"]
  command += ['--create_name_map_files']
  command += ['--jscomp_warning=checkTypes']
  # make sure everything is in a good order
  # ...but make compiling take 2x more time :-/
  # command += ["--jscomp_dev_mode", "EVERY_PASS"]

  if(debug):
    # debug makes var names readable, but was causing weirdness..
    command += ["--debug", "true"]
    command += ["--formatting", "PRETTY_PRINT"]
    command += ["--formatting", "PRINT_INPUT_DELIMITER"]
  else:
    # property map
    propMapFiles = glob.glob(os.path.join(tmp_dir, '*_props_map.out'))
    if(len(propMapFiles) > 0):
      command += ['--property_map_input_file', propMapFiles[-1]]

    # vars map
    varMapFiles = glob.glob(os.path.join(tmp_dir, '*_vars_map.out'))
    if(len(varMapFiles) > 0):
      command += ['--variable_map_input_file', varMapFiles[-1]]
  
  tmp_file_path = get_tmp_file_name(compiled_js_path, tmp_dir)
  command += ["--js_output_file", tmp_file_path]
  return command, tmp_file_path, compiled_js_path

def run_addDependency(goog_path, file_path, provided, required, provide_to_file_hash, file_to_require_hash):
  file_path = os.path.join(goog_path, file_path)
  file_path = os.path.normpath(file_path)
  if(file_path in file_to_require_hash):
    raise Exception("I've already seen '%s'" % file_path)
  file_to_require_hash[file_path] = required
  for symbol in provided:
    if(symbol in provide_to_file_hash):
      raise Exception("I've already seen '%s'" % symbol)
    provide_to_file_hash[symbol] = file_path

def process_line(goog_path, line, provide_to_file_hash, file_to_require_hash):
  locals = {'addDependency': lambda x, y, z: run_addDependency(goog_path, x, y, z, provide_to_file_hash, file_to_require_hash) }
  line = line.strip()
  if(line.startswith('goog.addDependency')):
    line = string.replace(line, 'goog.addDependency', 'addDependency')
    line = string.replace(line, ';', '')
    eval(line, {}, locals)

def process_deps(goog_path, dep_file, provide_to_file_hash, file_to_require_hash):
  for line in open(dep_file,"r").readlines():
    process_line(goog_path, line, provide_to_file_hash, file_to_require_hash)

def populate_required_files_for_file(js_file, files_array, provide_to_file_hash, file_to_require_hash):
  if(not js_file in files_array):
    # append the provided file, since we don't have it
    files_array.append(js_file)
    # figure out which 'symbols' are required by this file
    if(not js_file in file_to_require_hash):
      raise Exception("Don't know where the file '%s' is!" % js_file)
    required_symbols = file_to_require_hash[js_file]
    # figure out which files provide these symbols
    for symbol in required_symbols:
      populate_required_files_for_symbol(symbol, files_array, provide_to_file_hash, file_to_require_hash)

def populate_required_files_for_symbol(symbol, files_array, provide_to_file_hash, file_to_require_hash):
  if(not symbol in provide_to_file_hash):
    raise Exception("Don't know where the symbol '%s' is!" % symbol)
  next_file = provide_to_file_hash[symbol]
  populate_required_files_for_file(next_file, files_array, provide_to_file_hash, file_to_require_hash)

# def print_help():
#   command = get_closure_base()
#   command.append("--help")
#   return command, None, None
#
# def print_tree_core(js_files, extern_files):
#   command = get_command_with_inputs(js_files, extern_files)
#   command.append("--print_tree")
#   command.append("true")
#   return command, None, None
