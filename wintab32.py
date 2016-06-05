"""
Another implementation / good reference:
https://bitbucket.org/pyglet/pyglet/src/f388bbe83f4e59079be1329eb61761adcc7f646c/pyglet/input/wintab.py?at=default&fileviewer=file-view-default
"""

import ctypes
from ctypes import windll, wintypes, c_char, c_int, POINTER 
from ctypes.wintypes import HWND, UINT, DWORD, LONG, HANDLE, BOOL, LPVOID
import atexit
import libwintab as wintab

HCTX = HANDLE
WTPKT = DWORD
FIX32 = DWORD

LONG = ctypes.c_long
BOOL = ctypes.c_int
UINT = ctypes.c_uint
WORD = ctypes.c_uint16
DWORD = ctypes.c_uint32
WCHAR = ctypes.c_wchar

WTI_DEVICES = 100
DVC_NAME = 1
DVC_HARDWARE = 2
DVC_NCSRTYPES = 3
DVC_FIRSTCSR = 4
DVC_PKTRATE = 5
DVC_PKTDATA = 6
DVC_PKTMODE = 7
DVC_CSRDATA = 8
DVC_XMARGIN = 9
DVC_YMARGIN = 10
DVC_ZMARGIN = 11
DVC_X = 12
DVC_Y = 13
DVC_Z = 14
DVC_NPRESSURE = 15
DVC_TPRESSURE = 16
DVC_ORIENTATION = 17
DVC_ROTATION = 18  # 1.1
DVC_PNPID = 19  # 1.1
DVC_MAX = 19


class AXIS(ctypes.Structure):
    _fields_ = (
        ('axMin', LONG),
        ('axMax', LONG),
        ('axUnits', UINT),
        ('axResolution', FIX32)
    )

    def get_scale(self):
        # if self.axMin < 0:
        #    self.axMax += abs(self.axMin)
        #    self.axMin += abs(self.axMin)
        return 1 / float(self.axMax - self.axMin)

    def get_bias(self):
        return -self.axMin


class LOGCONTEXTA(ctypes.Structure):
    _fields_ = [
        ('lcName', 40 * c_char),
        ('lcOptions', UINT),
        ('lcStatus', UINT),
        ('lcLocks', UINT),
        ('lcMsgBase', UINT),
        ('lcDevice', UINT),
        ('lcPktRate', UINT),
        ('lcPktData', WTPKT),
        ('lcPktMode', WTPKT),
        ('lcMoveMask', WTPKT),
        ('lcBtnDnMask', DWORD),
        ('lcBtnUpMask', DWORD),
        ('lcInOrgX', LONG),
        ('lcInOrgY', LONG),
        ('lcInOrgZ', LONG),
        ('lcInExtX', LONG),
        ('lcInExtY', LONG),
        ('lcInExtZ', LONG),
        ('lcOutOrgX', LONG),
        ('lcOutOrgY', LONG),
        ('lcOutOrgZ', LONG),
        ('lcOutExtX', LONG),
        ('lcOutExtY', LONG),
        ('lcOutExtZ', LONG),
        ('lcSensX', FIX32),
        ('lcSensY', FIX32),
        ('lcSensZ', FIX32),
        ('lcSysMode', BOOL),
        ('lcSysOrgX', c_int),
        ('lcSysOrgY', c_int),
        ('lcSysExtX', c_int),
        ('lcSysExtY', c_int),
        ('lcSysSensX', FIX32),
        ('lcSysSensY', FIX32)
    ]


PK_CONTEXT = 0x0001  # reporting context */
PK_STATUS = 0x0002  # status bits */
PK_TIME = 0x0004  # time stamp */
PK_CHANGED = 0x0008  # change bit vector */
PK_SERIAL_NUMBER = 0x0010  # packet serial number */
PK_CURSOR = 0x0020  # reporting cursor */
PK_BUTTONS = 0x0040  # button information */
PK_X = 0x0080  # x axis */
PK_Y = 0x0100  # y axis */
PK_Z = 0x0200  # z axis */
PK_NORMAL_PRESSURE = 0x0400  # normal or tip pressure */
PK_TANGENT_PRESSURE = 0x0800  # tangential or barrel pressure */
PK_ORIENTATION = 0x1000  # orientation info: tilts */
PK_ROTATION = 0x2000  # rotation info; 1.1 */

#lcPktData = (PK_CHANGED | PK_CURSOR | PK_BUTTONS | PK_X | PK_Y | PK_NORMAL_PRESSURE)
lcPktData = (
            wintab.PK_CHANGED | wintab.PK_CURSOR | wintab.PK_BUTTONS |
            wintab.PK_X | wintab.PK_Y | wintab.PK_Z |
            wintab.PK_NORMAL_PRESSURE | wintab.PK_TANGENT_PRESSURE |
            wintab.PK_ORIENTATION)
lcPktMode = 0  # all absolute


class PACKET(ctypes.Structure):
    _fields_ = [
        ('pkChanged', WTPKT),
        ('pkCursor', UINT),
        ('pkButtons', DWORD),
        ('pkX', LONG),
        ('pkY', LONG),
        ('pkNormalPressure', UINT)
    ]


WTI_DEFCONTEXT = 3

CXO_SYSTEM = 0x0001
CXO_PEN = 0x0002
CXO_MESSAGES = 0x0004
CXO_MARGIN = 0x8000

CSR_NAME = 1
WTI_CURSORS = 200

dll = ctypes.WinDLL("wintab32.dll")

#dll.WTInfoA.argtypes = [UINT, UINT, POINTER(LOGCONTEXTA)]
#dll.WTInfoA.restype = UINT

#dll.WTInfoW.argtypes = [UINT, UINT, POINTER(AXIS)]
#dll.WTInfoW.restype = UINT

#dll.WTOpenA.argtypes = [HWND, POINTER(LOGCONTEXTA), BOOL]
#dll.WTOpenA.restype = HCTX

#dll.WTClose.argtypes = [HCTX]
#dll.WTClose.restype = BOOL

#dll.WTPacketsGet.argtypes = [HCTX, c_int, POINTER(PACKET)]
#dll.WTPacketsGet.restype = c_int

#dll.WTPacket.argtypes = [HCTX, UINT, POINTER(PACKET)]
#dll.WTPacket.restype = BOOL

lib = dll

def wtinfo(category, index, buffer):
    size = lib.WTInfoW(category, index, None)
    assert size <= ctypes.sizeof(buffer)
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return buffer

def wtinfo_string(category, index):
    size = lib.WTInfoW(category, index, None)
    buffer = ctypes.create_unicode_buffer(size)
    lib.WTInfoW(category, index, buffer)
    return buffer.value

def wtinfo_uint(category, index):
    buffer = wintab.UINT()
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return buffer.value

def wtinfo_word(category, index):
    buffer = wintab.WORD()
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return buffer.value

def wtinfo_dword(category, index):
    buffer = wintab.DWORD()
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return buffer.value

def wtinfo_wtpkt(category, index):
    buffer = wintab.WTPKT()
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return buffer.value

def wtinfo_bool(category, index):
    buffer = wintab.BOOL()
    lib.WTInfoW(category, index, ctypes.byref(buffer))
    return bool(buffer.value)


class WintabInput:
    hctx = None
    buf = None
    lc = None
    origtopleft = None
    rslt = None
    pressure = None
    xpos = None
    ypos = None
    zpos = None
    name = None
    _cursor = None
    lcPktData = None
    lcPktMode = None
    hwnd = None

    def __init__(self, temphwnd=31234):
        if temphwnd != 0:
            self.hwnd = HWND(temphwnd)
        else:
            self.hwnd = HWND(31234)
        # get window handle
        #self.hwnd = windll.user32.GetActiveWindow()
        # we might want to use this as hour userhwnd
        #print("self.hwnd: " + str(self.hwnd) + "\nuserhwnd: " + str(userhwnd))
        self.lc = wintab.LOGCONTEXT()
        self.rslt = wtinfo(wintab.WTI_DEFSYSCTX, 0, self.lc)
        #self.rslt = dll.WTInfoA(WTI_DEFCONTEXT, 0, self.lc)
        #print(self.lc.lcOptions)
        self.lcPktData = (
            wintab.PK_CHANGED | wintab.PK_CURSOR | wintab.PK_BUTTONS |
            wintab.PK_X | wintab.PK_Y | wintab.PK_Z |
            wintab.PK_NORMAL_PRESSURE | wintab.PK_TANGENT_PRESSURE |
            wintab.PK_ORIENTATION)

        self.lcPktMode = 0  # all absolute
        self.lc.lcPktData = self.lcPktData
        self.lc.lcPktMode = self.lcPktMode

        # lc.lcOptions = (CXO_SYSTEM | CXO_PEN | CXO_MESSAGES)
        #print(self.lc.lcOptions)
        #self.hctx = dll.WTOpenA(userhwnd, self.lc, 1)
        self.hctx = lib.WTOpenW(self.hwnd, ctypes.byref(self.lc), True)
        self.axisinfo = wintab.AXIS()
        #self.rslt2 = dll.WTInfoW(WTI_DEFCONTEXT, DVC_NPRESSURE, self.axisinfo)
        self.rslt2 = wtinfo(WTI_DEFCONTEXT, wintab.DVC_NPRESSURE, self.axisinfo)
        self.origtopleft = True
        #self.buf = (10 * PACKET)()
        self.buf = wintab.PACKET()

    def get_packet(self):
        #packet = wintab.PACKET()
        n = lib.WTPacketsGet(self.hctx, 1, self.buf)
        #n = dll.WTPacketsGet(self.hctx, 1, self.buf)
        if self.buf.pkChanged:
        #if n > 0:
        # TODO: Create separate class for cursor then do get_packet for each one
        # Or maybe not since we can differentiate them with pkCursor
            self._cursor = wintab.WTI_CURSORS + self.buf.pkCursor
            self.name = wtinfo_string(self._cursor, wintab.CSR_NAME).strip()
            self.xpos = (self.buf.pkX / float(self.lc.lcOutExtX)) * self.lc.lcSysExtX
            self.zpos = (self.buf.pkZ / float(self.lc.lcInOrgZ)) + 1
            if self.origtopleft:
                self.ypos = self.lc.lcSysExtY - ((self.buf.pkY / float(self.lc.lcOutExtY)) * self.lc.lcSysExtY)
            else:
                self.ypos = (self.buf.pkY / float(self.lc.lcOutExtY)) * self.lc.lcSysExtY
            try:
                self.pressure = float(self.buf.pkNormalPressure) / float(self.axisinfo.get_bias())
            except ZeroDivisionError:
                self.pressure = 0
            return self.name, self.xpos, self.ypos, self.pressure, self.zpos
        else:
            return None

    def close(self):
        lib.WTClose(self.rslt2)
        print("Cleaned Up")


if __name__ == "__main__":
    test = WintabInput(0)
    atexit.register(test.close)
    status = None
    try:
        while True:
            output = test.get_packet()
            if output:
                if not status:
                    status = "on_enter"  # begin
                    print(status)
                elif status == "on_enter":
                    status = "on_move"  # update
                    print(status)
                elif status == "on_leave":
                    status = "on_enter"  # begin
                    print(status)
                elif status == "on_move":
                    status = "on_move"  # update
                    print("on_move2")
                print("< %s > X:%f Y:%f Pressure:%f Z:%f" % output)
            else:
                if status:
                    if status != "on_leave":
                        status = "on_leave"  # end
                        print(status)
                    else:
                        status = None
    finally:
        test.close()
