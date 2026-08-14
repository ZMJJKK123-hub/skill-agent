package com.mojang.text2speech;

import com.sun.jna.Pointer;
import com.sun.jna.WString;
import com.sun.jna.platform.win32.COM.COMUtils;
import com.sun.jna.platform.win32.COM.Unknown;
import com.sun.jna.platform.win32.Guid;
import com.sun.jna.platform.win32.Ole32;
import com.sun.jna.platform.win32.WTypes;
import com.sun.jna.platform.win32.WinNT;
import com.sun.jna.ptr.IntByReference;
import com.sun.jna.ptr.PointerByReference;

public class NarratorWindows extends Unknown implements Narrator {
    // GUIDs taken from Win32 sapi.h
    private static final String COM_CLASS_SP_VOICE = "96749377-3391-11D2-9EE3-00C04F797396";
    private static final String INTERFACE_SP_VOICE = "6C44DF74-72B9-4992-A1EC-EF996E0422D4";
    // struct ISpVoice vtable offsets calculated from Win32 sapi.h
    private static final int VTABLE_INDEX_SPEAK = 20;
    private static final int VTABLE_INDEX_SKIP = 23;
    private static final int VTABLE_INDEX_SET_VOLUME = 30;
    // enum SPEAKFLAGS from Win32 sapi.h
    private static final int SPF_ASYNC = 1;
    private static final int SPF_PURGEBEFORESPEAK = 1 << 1;
    private static final int SPF_IS_NOT_XML = 1 << 4;

    private static final WString SKIP_TYPE = new WString("Sentence");
    private static final int MAX_NUM_ITEMS = Integer.MAX_VALUE;

    private static Pointer initSAPI() throws InitializeException {
        Ole32.INSTANCE.CoInitialize(null);

        final PointerByReference spVoicePointer = new PointerByReference();

        final WinNT.HRESULT result = Ole32.INSTANCE.CoCreateInstance(new Guid.CLSID(COM_CLASS_SP_VOICE), null, WTypes.CLSCTX_ALL, new Guid.IID(INTERFACE_SP_VOICE), spVoicePointer);
        if (COMUtils.FAILED(result)) {
            throw new InitializeException("SP_VOICE returned code " + result);
        }

        return spVoicePointer.getValue();
    }

    public NarratorWindows() throws InitializeException {
        super(initSAPI());
    }

    @Override
    public void say(final String msg, final boolean interrupt, final float volume) {
        int flags = SPF_ASYNC | SPF_IS_NOT_XML;
        if (interrupt) {
            flags |= SPF_PURGEBEFORESPEAK;
        }
        setVolume(volume);
        /*
            https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee125024(v=vs.85)
            HRESULT Speak(
               LPCWSTR       *pwcs,
               DWORD          dwFlags,
               ULONG         *pulStreamNumber
            );
         */
        _invokeNativeInt(VTABLE_INDEX_SPEAK, new Object[] {getPointer(), new WString(msg), flags, null});
    }

    private void setVolume(final float volume) {
        final short volumeLevel = (short) (volume * 100);
        /*
            https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee125022(v=vs.85)
            HRESULT SetVolume(
               USHORT 	usVolume
            );
         */
        _invokeNativeInt(VTABLE_INDEX_SET_VOLUME, new Object[] {getPointer(), volumeLevel});
    }

    @Override
    public void clear() {
        /*
            https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee125023(v=vs.85)
            HRESULT Skip(
               LPCWSTR   *pItemType,
               long       lNumItems,
               ULONG     *pulNumSkipped
            );

            Note: `long` in WinAPI is just a fancy way of saying `int`
            See: https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types
         */
        final IntByReference pulNumSkipped = new IntByReference();
        _invokeNativeInt(VTABLE_INDEX_SKIP, new Object[] {getPointer(), SKIP_TYPE, MAX_NUM_ITEMS, pulNumSkipped});
    }

    @Override
    public void destroy() {
        Release();
        Ole32.INSTANCE.CoUninitialize();
    }
}
