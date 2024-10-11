# PositiveIntent
> [!WARNING]  
> Beta release. Please create an issue with as much detail as possible if you run into any bugs.
## Features

- Sandbox Evasion
  -  Hostname keying
  -  Delayed execution (not susceptible to time acceleration)
- Shannon Entropy Normalization
  - Copyright free English books are embedded as resource files in the loader to keep entropy between 4.50-5.50
- ETW and AMSI Bypasses
  - ETW disabled via process fork with environment variable `COMPlus_ETWEnabled` set to zero
  - AmsiScanBuffer patched in-memory (via D/Invoke)
- Static Signature & Memory Scanning Evasion
  - Python pre-build script obfuscates all methods, variables, and strings before building the loader
  - Your .NET assembly of choice (Rubeus, Seatbelt, etc.) is embedded in the loader as a resource file and RC4 encrypted
  - Certain variables, such as the byte array containing the opcodes used for patching AmsiScanBuffer, are also RC4 encrypted
  - No suspicious usage of crypto libraries - RC4 encryption/decryption is performed using a "raw" implementation of the RC4 algorithm (thanks ChatGPT)
- Miscellaneous AV/EDR Evasion Features
  - Python post-build script signs the loader with a self-certificate certificate using values cloned from a domain of your choice
  - No P/Invoke. Full implementation of D/Invoke with API hashing.
- Compatibility
  - Built with .NET Framework 4.8 and C# 7.3 to ensure maximum compatibility with various Windows versions.

## Installation

```
pip install -r requirements.txt
sudo bash install.sh
```

## Usage

```
python build.py --file "..\Rubeus.exe" --hostname JOE-WIN10-VM --domain www.zoom.com

[+] Obfuscated loader source files
[+] Keyed on hostname JOE-WIN10-VM
[+] Encrypted and embedded ..\Rubeus.exe as a resource file
[+] Randomized loader filename
[+] Embedded 5 books as resource files
[+] Entropy of loader: 5.35
[+] Digitally signed loader with certificate cloned from www.zoom.com
[+] Loader compiled to C:\Users\Joe\source\repos\temp\iVZuUrrL.exe
```

## Detection Status

| Vendor | Tool | Status |
| ------------- | ------------- | ------------- |
| SentinelOne | Rubeus | Undetected |
| CrowdStrike | Rubeus | Undetected |
| Windows Defender | Rubeus | Undetected (10/10/2024) |
| Windows Defender | Seatbelt | Undetected (10/10/2024) |

## Roadmap

- Add obfuscation of class names to `obfuscate.py`
- Add obfuscation of namespace names `obfuscate.py`
- Programatically generate and randomize `assemblyinfo.cs`
- Port all Python pre/post-build scripts to .NET & cross-compile for Linux
- ???
