#!/usr/bin/env ruby

js_dir = File.join('..', 'public','javascripts')

command = ['fixjsstyle']
command += ['-r', js_dir]
command << '--debug_indentation'
command += ['-e', %w(closure-library externs).join(',')]
command += ['-x', %w(jquery-1.4.2.min.js deps.js compiled.js).join(',')]

command = command.join(' ')
puts command
puts `#{command}`
