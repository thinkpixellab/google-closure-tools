UTF8_BOM_REGEX = /\A\xEF\xBB\xBF/.freeze

def process_file(file_name)
  file_contents = needs_clean = nil
  File.open(file_name) do |file|
    file_contents = file.read
    needs_clean = file_contents.gsub!(UTF8_BOM_REGEX,'')
  end
  
  if(needs_clean)
    puts file_name
    File.open(file_name, 'w') do |file|
      file.write(file_contents)
    end
  end
  

end

source_files_pattern = File.join('..', 'public','**', '*.js')
source_files = Dir.glob(source_files_pattern)

source_files.each do |file_name|
  process_file(file_name)
end
