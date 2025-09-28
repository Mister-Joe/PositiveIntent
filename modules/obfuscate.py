import os
import re
import shutil
import random
import string
import colorama
import shlex
import xml.etree.ElementTree as ET

def update_encryption_key(content):
    key = ''.join(random.choices(string.ascii_letters, k=16))
    content = re.sub(re.escape('public static byte[] key = Encoding.UTF8.GetBytes("DepthSecurity");'), f'public static byte[] key = Encoding.UTF8.GetBytes("{key}");', content)
    return content, key

def update_writetofile(content):
    content = re.sub(re.escape('Fork(string.Join(" ", args));'), 'Fork(string.Join(" ", args), true);', content)
    return content

def update_arguments(args, obfuscation_map, content):

    # Split args into a list of strings
    arg_parts = shlex.split(args)
    
    # Format each argument as a reversed string in the C# string array
    formatted_args = ", ".join(f'StringHelper.Reverse(@"{arg[::-1]}")' for arg in arg_parts)

    # Update argument count
    content = re.sub(re.escape('else if (args.Length != 0)'), 'else if (args.Length == 0)', content)

    # Update the parameters declaration
    content = re.sub(
        re.escape('object[] parameters = new[] { args };'), 
        rf'string[] parameters = new string[] {{ {formatted_args} }};', 
        content
    )
    
    # Update the method invocation
    content = re.sub(
        re.escape('object execute = method.Invoke(null, parameters);'), 
        'object execute = method.Invoke(null, new object[] { parameters });', 
        content
    )
    
    return content

# Method to reverse a string
def obfuscate_string(original_string, string_map):
    string_map[original_string] = f'StringHelper.Reverse({original_string[::-1]})'
    return string_map[original_string]

# Method to obfuscate names
def obfuscate_name(original_method, obfuscation_map):
    if original_method not in obfuscation_map:
        obfuscated = ''.join(random.choices(string.ascii_letters, k=8))
        obfuscation_map[original_method] = obfuscated
    return obfuscation_map[original_method]

def update_references(content, obfuscation_map):
    for original_name, obfuscated_name in obfuscation_map.items():
        content = re.sub(rf'\b{original_name}\b', obfuscated_name, content)
    return content

# Update solution namespace to match randomized assembly name
def randomize_namespace(csproj_filepath, new_name):

    # Parse the .csproj XML file
    tree = ET.parse(csproj_filepath)
    root = tree.getroot()

    property_group = root.find('PropertyGroup')
    if property_group is not None:
        assembly_name_element = ET.SubElement(property_group, 'RootNamespace')

    # Update the AssemblyName to the new random name
    assembly_name_element.text = new_name
    
    # Write changes back to the .csproj file
    tree.write(csproj_filepath, encoding="utf-8", xml_declaration=True)

    with open(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp/PositiveIntent.sln")), 'r+', encoding='utf-8') as file:
                additional_content = file.read()
                additional_content = re.sub(r'=\s"PositiveIntent"', f'= "{new_name}"', additional_content)
                file.seek(0)
                file.write(additional_content)
                file.truncate()

    with open(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp/PositiveIntent/Properties/Resources.Designer.cs")), 'r+', encoding='utf-8') as file:
                additional_content = file.read()
                additional_content = re.sub(r'PositiveIntent', f'{new_name}', additional_content)
                file.seek(0)
                file.write(additional_content)
                file.truncate()

    return new_name

def update_strings(content, string_map):
    for original_name, obfuscated_name in string_map.items():
        try:
            content = re.sub(rf'{original_name}', obfuscated_name, content)
        except:
            content = re.sub(rf'{original_name}', re.escape(obfuscated_name), content)
    return content

def update_hostname(content, hostname):
    content = re.sub(r'TESTVM', hostname, content)
    return content

def update_resource_references(content, num_chunks, obfuscation_map):
    resources = ''
    for i in range(num_chunks):
        resources += (f"{obfuscation_map['chunks']}.Add(Resources.FileChunk{i});\n            ")
    content = re.sub(re.escape(f"{obfuscation_map['chunks']}.Add(Resources.FileChunk1);"), resources, content)
    return content

def randomize_assembly_name(csproj_filepath, new_name):
    
    # Parse the .csproj XML file
    tree = ET.parse(csproj_filepath)
    root = tree.getroot()

    property_group = root.find('PropertyGroup')
    if property_group is not None:
        assembly_name_element = ET.SubElement(property_group, 'AssemblyName')

    # Update the AssemblyName to the new random name
    assembly_name_element.text = new_name
    
    # Write changes back to the .csproj file
    tree.write(csproj_filepath, encoding="utf-8", xml_declaration=True)

    return new_name

# Method to obfuscate method names
def obfuscate_methods(content, obfuscation_map):
    method_pattern = re.compile(r'(public|private|protected|internal)\s(?:static\s+|delegate\s)?(.*NTSTATUS|void|byte\[\]|int|double|IntPtr|string|bool|uint|T)\s(\w+)\(')
    for match in method_pattern.finditer(content):
        original_method = match.group(3)
        if original_method != 'Main' and original_method != 'Reverse':
            obfuscate_name(original_method, obfuscation_map)

# Method to obfuscate class names
def obfuscate_classes(content, obfuscation_map):
    class_pattern = re.compile(r'(class)\s(\w*)')
    for match in class_pattern.finditer(content):
        original_class = match.group(2)
        if original_class != 'StringHelper' and original_class != 'Generic' and original_class != "for":
            obfuscate_name(original_class, obfuscation_map)

# Method to obfuscate namespaces
def obfuscate_namespaces(content, obfuscation_map):
    namespace_pattern = re.compile(r'(namespace)\s(\w*)\s|(namespace)\s(\w*)\.(\w*)\s')
    for match in namespace_pattern.finditer(content):
        original_namespace = match.group(2)
        if match.group(2) != None:
            original_namespace = match.group(2)
            obfuscate_name(original_namespace, obfuscation_map)
        elif match.group(5) != None:
            original_namespace = match.group(5)
            obfuscate_name(original_namespace, obfuscation_map)

# Method to obfuscate variables
def obfuscate_variables(content, obfuscation_map):
    variable_pattern = re.compile(r'(var|object\[\]|object|uint|bool|string|int|byte\[\]|IntPtr)\s(\w*)\s=')
    for match in variable_pattern.finditer(content):
        original_variable = match.group(2)
        if original_variable != 'System' and original_variable != "Size":
            obfuscate_name(original_variable, obfuscation_map)

# Method to obfuscate non-const strings
def obfuscate_strings(content, obfuscation_map, string_map):
    # First, find all const strings to ignore them
    const_string_pattern = re.compile(r'const\sstring\s\w+\s=\s(".*")')
    hostname_pattern = re.compile(r'("TESTVM")')
    const_strings = set(m.group(1) for m in const_string_pattern.finditer(content))
    hostname_strings = set(m.group(1) for m in hostname_pattern.finditer(content))
    
    # Then, obfuscate strings that aren't const
    string_pattern = re.compile(r'(".*?")')
    for match in string_pattern.finditer(content):
        original_string = match.group(1)
        if "ntdll.dll" in original_string or original_string in const_strings or original_string in hostname_strings or original_string in obfuscation_map.values():
            string_map[original_string] = original_string
        else:
            obfuscate_string(original_string, string_map)

# Method to process a C# file
def process_file(file_path, obfuscation_map, string_map):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    obfuscate_methods(content, obfuscation_map)
    obfuscate_variables(content, obfuscation_map)
    obfuscate_classes(content, obfuscation_map)
    obfuscate_strings(content, obfuscation_map, string_map)

def run(hostname, num_chunks, args, writetofile):
    # Input and output directories
    input_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
    output_dir =  os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp"))

    # Copy unobfuscated source to preserve it
    if(os.path.exists(output_dir)):
        shutil.rmtree(output_dir)
        shutil.copytree(input_dir, output_dir)
    else:
        shutil.copytree(input_dir, output_dir)

    # Maps to store obfuscated names for methods/variables/strings
    obfuscation_map = {}
    string_map = {}

    # Loop over source files, identify method and variable names, add obfscated/unobfuscated names to obfuscation_map dictionary
    for root, dirs, files in os.walk(output_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in ("bin", "obj", "Resources", "Properties")]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith('.cs'):
                process_file(file_path, obfuscation_map, string_map)

    csproj_filepath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp/PositiveIntent/PositiveIntent.csproj"))
    assembly_name = randomize_assembly_name(csproj_filepath, ''.join(random.choices(string.ascii_letters, k=8)))
    namespace = randomize_namespace(csproj_filepath, ''.join(random.choices(string.ascii_letters, k=8)))
    obfuscation_map['PositiveIntent'] = namespace
    
    # Loop over source files again and update all references to obfuscated methods, variables, and strings
    for root, dirs, files in os.walk(output_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in ("bin", "obj", "Resources", "Properties")]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith('.cs'):
                with open(file_path, 'r+', encoding='utf-8') as file:
                    content = file.read()
                    if(writetofile):
                        content = update_writetofile(content)
                    if(args):
                        content = update_arguments(args, obfuscation_map, content)
                    if("RC4" in file_name):
                        content, key = update_encryption_key(content)
                    content = update_references(content, obfuscation_map)
                    content = update_strings(content, string_map)
                    content = update_hostname(content, hostname)
                    content = update_resource_references(content, num_chunks, obfuscation_map)
                    file.seek(0)
                    file.write(content)
                    file.truncate()
    return assembly_name, key
