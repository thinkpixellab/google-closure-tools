UTF8_BOM_REGEX = /\A\xEF\xBB\xBF/.freeze

def process_file(file_name)
  File.open(file_name) do |file|
    value = file.read
    cool = value.gsub!(UTF8_BOM_REGEX,'')
    if(cool)
      puts file_name
    end
  end

end

source_files_pattern = File.join('..', 'public','**', '*.js')
source_files = Dir.glob(source_files_pattern)

source_files.each do |file_name|
  process_file(file_name)
end
