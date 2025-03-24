# PositiveIntent
> [!WARNING]  
> Beta release. Please create an issue with as much detail as possible if you run into any bugs.
## Features

-  ETW disabled via process fork with environment variable `COMPlus_ETWEnabled` set to zero. No memory patching.
-  Unique AMSI patch that targets a writable pointer to `AmsiScanBuffer` in the .data section of `clr.dll`. This means that `amsi.dll` is never touched and no memory page permissions are changed anywhere.
-  PE headers of your assembly (after it's been decrypted and loaded) are stomped to hide it from memory page scanners looking for implanted PE signatures.
-  Hostname keying. 
-  Python pre-build script obfuscates all (most) methods, variables, strings, delegates, classes, and namespaces before building the loader (the code is disgusting don't read it please).
-  Your .NET assembly of choice (Rubeus, Seeker, etc.) is embedded in the loader as a resource file and RC4 encrypted.
-  No suspicious usage of crypto libraries - RC4 encryption/decryption is performed using a "raw" implementation of the RC4 algorithm (thanks ChatGPT).
-  No P/Invoke usage. D/Invoke only with API hashing.
- Copyright free English books are embedded as resource files in the loader to keep Shannon entropy between 4.50-5.50.
- Python post-build script signs the loader with a self-signed certificate using values cloned from a domain of your choice.
- Built with .NET Framework 4.8 and C# 7.3 for compatibility with various Windows versions.

## Installation (Kali/Debian-Based)

```
sudo apt update && apt install -y osslsigncode dirmngr ca-certificates gnupg
sudo echo "deb [trusted=yes] https://download.mono-project.com/repo/debian stable-buster main" | tee /etc/apt/sources.list.d/mono-official-stable.list
sudo apt update && apt install -y mono-complete
cd PositiveIntent
pip install -r requirements.txt
```

## Usage

```
python build.py --file /tmp/Rubeus.exe --hostname TEST --domain www.zoom.com

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
> Detection status is evaluated over RDP (i.e. no smbexec, wmiexec, etc).  

| Vendor | Tool | Status |
| ------------- | ------------- | ------------- |
| SentinelOne | Rubeus | Undetected (03/23/2025) |
| SentinelOne | Seeker | Undetected (03/18/2025) |
| SentinelOne | Internal Monologue | Undetected (10/11/2024) |
| CrowdStrike | Rubeus | Undetected (10/11/2024) |
| CrowdStrike | Seeker | Undetected (10/11/2024) |
| CrowdStrike | Internal Monologue | Detected (Behavioral) |
| Windows Defender | Rubeus | Undetected (03/23/2025) |
| Windows Defender | Seatbelt | Undetected (10/10/2024) |
| ESET | Rubeus | Undetected (10/18/2024) |

## Roadmap

- Add option to key on username
- Add option to key on AD domain
- Add support for 32 bit processes
- Programatically generate and randomize `assemblyinfo.cs`
- Port all Python pre/post-build scripts to .NET & cross-compile for Linux
- Improve error handling
- ???

## References
[Anatomy of a .NET Assembly – The DOS Stub](https://www.red-gate.com/simple-talk/blogs/anatomy-of-a-net-assembly-the-dos-stub/)  
[A Dive Into the PE File Format](https://0xrick.github.io/win-internals/pe3)  
[Red Team Tradecraft: Loading Encrypted C# Assemblies In Memory](https://www.mike-gualtieri.com/posts/red-team-tradecraft-loading-encrypted-c-sharp-assemblies-in-memory)  
[Building, Modifying, and Packing with Azure DevOps](https://blog.xpnsec.com/building-modifying-packing-devops/)  
[DeepSeek](https://deepseek.com/) (THE GOAT)  
[ChatGPT](https://chatgpt.com/)  
