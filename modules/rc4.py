import os
import colorama
import base64
import re
import xml.etree.ElementTree as ET

class RC4:
    def __init__(self, key):
        self.S = list(range(256))  # Initialize the state array S
        self.x = 0
        self.y = 0
        self.key_setup(key)

    def key_setup(self, key):
        key_length = len(key)
        j = 0
        for i in range(256):
            j = (j + self.S[i] + key[i % key_length]) % 256
            self.swap(i, j)

    def swap(self, i, j):
        self.S[i], self.S[j] = self.S[j], self.S[i]

    def encrypt_decrypt(self, data):
        output = bytearray(len(data))
        for k in range(len(data)):
            self.x = (self.x + 1) % 256
            self.y = (self.y + self.S[self.x]) % 256
            self.swap(self.x, self.y)
            key_stream = self.S[(self.S[self.x] + self.S[self.y]) % 256]
            output[k] = data[k] ^ key_stream
        return output

def encrypt_file(file, key):

    # Read the input file into a byte array
    file_bytes = file.read()
    
    # Create an instance of the RC4 class
    rc4 = RC4(key)

    # Encrypt the file bytes
    encrypted_bytes = rc4.encrypt_decrypt(file_bytes)

    return encrypted_bytes

def update_resx(encrypted_bytes, num_chunks):

    #Split encrypted bytes array into specified number of chunks.
    chunk_size = len(encrypted_bytes) // num_chunks
    remainder = len(encrypted_bytes) % num_chunks
    
    chunks = []
    start = 0
    
    for i in range(num_chunks):
        # Add one extra byte to the first 'remainder' chunks to handle uneven splits
        current_chunk_size = chunk_size + (1 if i < remainder else 0)
        end = start + current_chunk_size
        chunks.append(encrypted_bytes[start:end])
        start = end

    # Parse existing .resx file
    resx_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp/PositiveIntent/Properties/Resources.resx"))
    tree = ET.parse(resx_path)
    root = tree.getroot()

    # Add chunks as raw binary data
    for i, chunk in enumerate(chunks):
        data_elem = ET.Element("data")
        data_elem.set("name", f"FileChunk{i}")
        data_elem.set("type", "System.Byte[], mscorlib")
        
        value_elem = ET.SubElement(data_elem, "value")
        # .resx format requires base64 encoding for binary data
        encoded_chunk = base64.b64encode(chunk).decode('utf-8')
        value_elem.text = encoded_chunk
        
        root.append(data_elem)
        
    # Write updated .resx file
    tree.write(resx_path, encoding="utf-8", xml_declaration=True)

def update_designer(num_chunks):
    
    #Add FileChunk entries to the Resources.Designer.cs file.
    designer_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp/PositiveIntent/Properties/Resources.Designer.cs"))
    
    # Read the existing designer file
    with open(designer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the closing brace of the class
    last_brace_pos = content.rfind('    }')  # Find the last closing brace with 4 spaces indent
    
    # Generate the new properties
    new_properties = []
    for i in range(num_chunks):
        property_code = f'''        
        /// <summary>
        ///   Looks up a localized resource of type System.Byte[].
        /// </summary>
        internal static byte[] FileChunk{i} {{
            get {{
                object obj = ResourceManager.GetObject("FileChunk{i}", resourceCulture);
                return ((byte[])(obj));
            }}
        }}'''
        new_properties.append(property_code)
    
    # Insert the new properties before the last closing brace
    new_content = (content[:last_brace_pos] + 
                   '\n'.join(new_properties) + '\n' + 
                   content[last_brace_pos:])
    
    # Write the updated designer file
    with open(designer_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def run(file, num_chunks, key):
    
    encrypted_bytes = encrypt_file(file, key)
    update_resx(encrypted_bytes, num_chunks)
    update_designer(num_chunks)
