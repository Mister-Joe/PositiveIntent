using System.Text;

namespace PositiveIntent
{
    public class RC4
    {
        private byte[] S = new byte[256];
        private int x = 0;
        private int y = 0;
        public static byte[] key = Encoding.UTF8.GetBytes("DepthSecurity"); // placeholder

        public RC4(byte[] key)
        {
            KeySetup(key);
        }
        
        private void KeySetup(byte[] key)
        {
            int keyLength = key.Length;
            for (int i = 0; i < 256; i++)
            {
                S[i] = (byte)i;
            }

            int j = 0;
            for (int i = 0; i < 256; i++)
            {
                j = (j + S[i] + key[i % keyLength]) % 256;
                Swap(i, j);
            }
        }
        
        private void Swap(int i, int j)
        {
            byte temp = S[i];
            S[i] = S[j];
            S[j] = temp;
        }
        
        public byte[] EncryptDecrypt(byte[] data)
        {
            byte[] output = new byte[data.Length];
            for (int k = 0; k < data.Length; k++)
            {
                x = (x + 1) % 256;
                y = (y + S[x]) % 256;
                Swap(x, y);
                byte keyStream = S[(S[x] + S[y]) % 256];
                output[k] = (byte)(data[k] ^ keyStream);
            }

            return output;
        }
    }
}
