import os
import socket
import ssl
import subprocess
from cryptography import x509
from cryptography.hazmat.primitives.serialization import PrivateFormat, pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

# Step 1: Fetch SSL/TLS Certificate
def fetch_certificate(domain):
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert(True)
            return x509.load_der_x509_certificate(cert, default_backend())

# Step 2: Generate a Self-Signed Certificate
def generate_self_signed_certificate(cert):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    subject = cert.subject
    issuer = cert.subject

    self_signed_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256(), default_backend())  # Correct import for SHA256

    return private_key, self_signed_cert

# Step 3: Convert PEM to PKCS#12
def save_pkcs12(cert, private_key, output_filename, password):
    p12 = pkcs12.serialize_key_and_certificates(
        name=b'certificate',
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    )
    with open(output_filename, 'wb') as f:
        f.write(p12)

# Step 4: Digitally Sign Executable File
def sign_executable(p12_path, assembly_name):
    cmd = [
        "C:\\Users\\Joe\\Downloads\\osslsigncode-2.9-windows-x64-mingw\\bin\\osslsigncode.exe", "sign",
        "-pkcs12", p12_path,
        "-pass", "DepthSecurity",
        "-in", os.path.join(os.path.dirname(os.path.abspath(__file__)), f"..\\temp\\PositiveIntent\\bin\\release\\net48\\{assembly_name}.exe"),
        "-n", assembly_name,
        "-t", "http://timestamp.digicert.com",
        "-out", os.path.join(os.path.dirname(os.path.abspath(__file__)), f"..\\temp\\{assembly_name}.exe")
    ]
    subprocess.run(cmd, check=True, stdout = subprocess.DEVNULL)

def run(domain, assembly_name):

    # Configuration
    output_dir =os.path.join(os.path.dirname(os.path.abspath(__file__)), f"..\\temp")
    password = b'DepthSecurity'
    
    # Fetch certificate
    cert = fetch_certificate(domain)

    # Generate self-signed certificate and private key
    private_key, self_signed_cert = generate_self_signed_certificate(cert)

    # Save private key and self-signed cert in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(password))
    
    # Convert to PKCS#12
    pkcs12_path = os.path.join(output_dir, 'cert.p12')
    save_pkcs12(self_signed_cert, private_key, pkcs12_path, password)

    # Sign the executable file
    sign_executable(pkcs12_path, assembly_name)
