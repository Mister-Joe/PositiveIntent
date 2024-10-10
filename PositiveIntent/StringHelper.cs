using System;

namespace PositiveIntent;

public class StringHelper
{
    // This function will reverse the string at runtime
    public static string Reverse(string input)
    {
        char[] charArray = input.ToCharArray();
        Array.Reverse(charArray);
        return new string(charArray);
    }
}