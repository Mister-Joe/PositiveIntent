import os
import colorama

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

def encrypt_file(file, output_file_path, key):

    # Read the input file into a byte array
    file_bytes = file.read()
    
    # Create an instance of the RC4 class
    rc4 = RC4(key)

    # Encrypt the file bytes
    encrypted_bytes = rc4.encrypt_decrypt(file_bytes)
    
    # Write the encrypted bytes to a new file
    with open(output_file_path, 'wb') as file:
        file.write(encrypted_bytes)

def run(file):

    # Set the key (it must be in bytes)
    key = b'DepthSecurity'
    
    # Encrypt the executable file
    encrypt_file(file, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\\temp\\PositiveIntent\\Resources\\File1.exe"), key)
