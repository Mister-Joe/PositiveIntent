# PositiveIntent
> [!WARNING]  
> Beta release. Please create an issue with as much detail as possible if you run into any bugs.
## Features

- Sandbox Evasion
  -  Hostname keying
  -  Delayed execution (busy wait loop - less susceptible to time acceleration)
- Shannon Entropy Normalization
  - Copyright free English books are embedded as resource files in the loader to keep entropy between 4.50-5.50
- ETW and AMSI Bypasses
  - ETW disabled via process fork with environment variable `COMPlus_ETWEnabled` set to zero
  - AmsiScanBuffer patched in-memory (via D/Invoke)
- Static Signature & Memory Scanning Evasion
  - Python pre-build script obfuscates all (most) methods, variables, strings, delegates, classes, and namespaces before building the loader
  - Your .NET assembly of choice (Rubeus, Seeker, etc.) is embedded in the loader as a resource file and RC4 encrypted
  - Certain variables, such as the byte array containing the opcodes used for patching AmsiScanBuffer, are also RC4 encrypted
  - No suspicious usage of crypto libraries - RC4 encryption/decryption is performed using a "raw" implementation of the RC4 algorithm (thanks ChatGPT)
- Miscellaneous AV/EDR Evasion Features
  - Python post-build script signs the loader with a self-signed certificate using values cloned from a domain of your choice
  - No P/Invoke - full implementation of D/Invoke with API hashing
- Compatibility
  - Built with older .NET Framework 4.8 and C# 7.3 for compatibility with various Windows versions

## Installation

```
cd PositiveIntent
docker build -t positiveintent .
```

## Usage

```
python build.py --file /tmp/Rubeus.exe --hostname TEST --domain www.zoom.com --delay 60

[+] Obfuscated loader source files
[+] Keyed on hostname TEST
[+] Encrypted and embedded /tmp/Rubeus.exe as a resource file
[+] Randomized loader filename
[+] Embedded 1 books as resource files
[+] Entropy of loader: 5.35
[+] Digitally signed loader with certificate cloned from www.zoom.com
[+] Loader compiled to /tmp/PositiveIntent/temp/pwCXupfi.exe
```

## Detection Status
> [!NOTE]  
> If your tooling isn't covered please create an issue with the vendor, tool, and detection status.

| Vendor | Tool | Status |
| ------------- | ------------- | ------------- |
| SentinelOne | Rubeus | Undetected (10/11/2024) |
| SentinelOne | Seeker | Undetected (10/11/2024) |
| SentinelOne | Internal Monologue | Undetected (10/11/2024) |
| CrowdStrike | Rubeus | Undetected (10/11/2024) |
| CrowdStrike | Seeker | Undetected (10/11/2024) |
| CrowdStrike | Internal Monologue | Detected |
| Windows Defender | Rubeus | Undetected (10/10/2024) |
| Windows Defender | Seatbelt | Undetected (10/10/2024) |
| ESET | Rubeus | Undetected (10/18/2024) |

## Roadmap

- Add option to key on username
- Add option to key on AD domain
- Programatically generate and randomize `assemblyinfo.cs`
- Manually parse PE headers of .NET assembly and stomp metadata before loading
- Manually map `kernel32.dll` and `ntdll.dll` to evade user-mode hooks
- Port all Python pre/post-build scripts to .NET & cross-compile for Linux
- Improve error handling
- ???

## References
[Anatomy of a .NET Assembly – The DOS Stub](https://www.red-gate.com/simple-talk/blogs/anatomy-of-a-net-assembly-the-dos-stub/)
