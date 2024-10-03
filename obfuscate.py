import os
import re
import shutil
import random
import string

# Function to reverse a string
def obfuscate_string(original_string, string_map):
    string_map[original_string] = f'StringHelper.Reverse({original_string[::-1]})'
    return string_map[original_string]

# Function to generate a random 8-character obfuscated name
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Function to obfuscate names
def obfuscate_name(original_method, obfuscation_map):
    if original_method not in obfuscation_map:
        obfuscated = generate_random_string()
        obfuscation_map[original_method] = obfuscated
    return obfuscation_map[original_method]

def update_references(content, obfuscation_map):
    for original_name, obfuscated_name in obfuscation_map.items():
        content = re.sub(rf'\b{original_name}\b', obfuscated_name, content)
    return content

def update_strings(content, string_map):
    for original_name, obfuscated_name in string_map.items():
        try:
            content = re.sub(rf'{original_name}', obfuscated_name, content)
        except:
            content = re.sub(rf'{original_name}', re.escape(obfuscated_name), content)
    return content

# Function to obfuscate method names and their references
def obfuscate_methods(content, obfuscation_map):
    method_pattern = re.compile(r'(public|private|protected|internal)\s(static|delegate)\s(.*NTSTATUS|void|int|double|IntPtr|string|bool|uint|T)\s(\w*)')
    for match in method_pattern.finditer(content):
        original_method = match.group(4)
        if original_method != 'Main' and original_method != 'Reverse':
            obfuscate_name(original_method, obfuscation_map)

# Function to obfuscate method names and their references
def obfuscate_variables(content, obfuscation_map):
    variable_pattern = re.compile(r'(var|object\[\]|uint|bool|string|IntPtr)\s(\w*)\s=')
    for match in variable_pattern.finditer(content):
        original_variable = match.group(2)
        if original_variable != 'System':
            obfuscate_name(original_variable, obfuscation_map)

# Function to obfuscate non-const strings
def obfuscate_strings(content, obfuscation_map, string_map):
    # First, find all const strings to ignore them
    const_string_pattern = re.compile(r'const\sstring\s\w+\s=\s(".*")')
    const_strings = set(m.group(1) for m in const_string_pattern.finditer(content))
    
    # Then, obfuscate strings that aren't const
    string_pattern = re.compile(r'(".*?")')
    for match in string_pattern.finditer(content):
        original_string = match.group(1)
        if original_string in const_strings or original_string in obfuscation_map.values():
            string_map[original_string] = original_string
        else:
            obfuscate_string(original_string, string_map)

# Function to process a C# file
def process_file(file_path, obfuscation_map):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    obfuscate_methods(content, obfuscation_map)
    obfuscate_variables(content, obfuscation_map)
    obfuscate_strings(content, obfuscation_map, string_map)

# Input and output directories
input_dir = 'C:\\Users\\Joe\\source\\repos\\TestSvc - Copy - Copy - Copy'
output_dir = 'C:\\Users\\Joe\\Desktop\\obfuscated_source'

# Map to store obfuscated names for methods and variables
obfuscation_map = {}
string_map = {}

# Copy unobfuscated source to preserve it
shutil.copytree(input_dir, output_dir)

# Loop over source files, identify method and variable names, add obfscated/unobfuscated names to obfuscation_map dictionary
for root, dirs, files in os.walk(output_dir, topdown=True):
    dirs[:] = [d for d in dirs if d not in ("bin", "obj", "Resources", "Properties")]
    for file_name in files:
        file_path = os.path.join(root, file_name)
        if file_name.endswith('.cs'):
            process_file(file_path, obfuscation_map)

# Loop over source files again and update all references to obfuscated methods, variables, and strings
for root, dirs, files in os.walk(output_dir, topdown=True):
    dirs[:] = [d for d in dirs if d not in ("bin", "obj", "Resources", "Properties")]
    for file_name in files:
        file_path = os.path.join(root, file_name)
        if file_name.endswith('.cs'):
            with open(file_path, 'r+', encoding='utf-8') as file:
                content = file.read()
                content = update_references(content, obfuscation_map)
                content = update_strings(content, string_map)
                file.seek(0)
                file.write(content)
                file.truncate()

print('Obfuscation complete.')
