"""
Another implementation / good reference:
https://bitbucket.org/pyglet/pyglet/src/f388bbe83f4e59079be1329eb61761adcc7f646c/pyglet/input/wintab.py?at=default&fileviewer=file-view-default
"""

import ctypes
from ctypes import wintypes, c_char, c_int, POINTER
from ctypes.wintypes import HWND, UINT, DWORD, LONG, HANDLE, BOOL, LPVOID

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
DVC_ROTATION = 18 # 1.1 
DVC_PNPID = 19 # 1.1 
DVC_MAX = 19


class AXIS(ctypes.Structure):
    _fields_ = (
        ('axMin', LONG),
        ('axMax', LONG),
        ('axUnits', UINT),
        ('axResolution', FIX32)
    )

    def get_scale(self):
        #if self.axMin < 0:
        #    self.axMax += abs(self.axMin)
        #    self.axMin += abs(self.axMin)
        return 1 / float(self.axMax - self.axMin)

    def get_bias(self):
        return -self.axMin



class LOGCONTEXTA(ctypes.Structure):
    _fields_ = [
        ('lcName', 40*c_char),
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

PK_CONTEXT =        0x0001  # reporting context */
PK_STATUS =             0x0002  # status bits */
PK_TIME =           0x0004  # time stamp */
PK_CHANGED =        0x0008  # change bit vector */
PK_SERIAL_NUMBER = 0x0010   # packet serial number */
PK_CURSOR =             0x0020  # reporting cursor */
PK_BUTTONS =        0x0040  # button information */
PK_X =              0x0080  # x axis */
PK_Y =              0x0100  # y axis */
PK_Z =              0x0200  # z axis */
PK_NORMAL_PRESSURE = 0x0400 # normal or tip pressure */
PK_TANGENT_PRESSURE = 0x0800    # tangential or barrel pressure */
PK_ORIENTATION =    0x1000  # orientation info: tilts */
PK_ROTATION =       0x2000  # rotation info; 1.1 */

lcPktData = (PK_CHANGED | PK_CURSOR | PK_BUTTONS | PK_X | PK_Y | PK_NORMAL_PRESSURE)
lcPktMode = 0

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

dll = ctypes.WinDLL("wintab32.dll")

dll.WTInfoA.argtypes = [UINT, UINT, POINTER(LOGCONTEXTA)]
dll.WTInfoA.restype = UINT

dll.WTInfoW.argtypes = [UINT, UINT, POINTER(AXIS)]
dll.WTInfoW.restype = UINT

dll.WTOpenA.argtypes = [HWND, POINTER(LOGCONTEXTA), BOOL]
dll.WTOpenA.restype = HCTX

dll.WTClose.argtypes = [HCTX]
dll.WTClose.restype = BOOL

dll.WTPacketsGet.argtypes = [HCTX, c_int, POINTER(PACKET)]
dll.WTPacketsGet.restype = c_int

dll.WTPacket.argtypes = [HCTX, UINT, POINTER(PACKET)]
dll.WTPacket.restype = BOOL

if __name__ == "__main__":
    lc = LOGCONTEXTA()
    rslt = dll.WTInfoA(WTI_DEFCONTEXT, 0, lc);
    print(lc.lcOptions)
    lc.lcPktData = lcPktData
    lc.lcPktMode = lcPktMode
    
    #lc.lcOptions = (CXO_SYSTEM | CXO_PEN | CXO_MESSAGES)
    print(lc.lcOptions)
    hctx = dll.WTOpenA(HWND(31234), lc, 1)

    axisinfo = AXIS()
    rslt2 = dll.WTInfoW(WTI_DEFCONTEXT, DVC_NPRESSURE,axisinfo)
    origtopleft = True
    buf = (10*PACKET)()
    while True:
        n = dll.WTPacketsGet(hctx, 1, buf)
        if n > 0:
            xpos = (buf[0].pkX/float(lc.lcOutExtX))*lc.lcSysExtX
            if origtopleft:
                ypos = abs(((buf[0].pkY/float(lc.lcOutExtY))*lc.lcSysExtY)-lc.lcSysExtY)
            else:
                ypos = (buf[0].pkY/float(lc.lcOutExtY))*lc.lcSysExtY
            pressure = buf[0].pkNormalPressure / float(axisinfo.get_bias())
            print("%f %f %f" % (xpos, ypos, pressure))
