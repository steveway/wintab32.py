import ctypes
from ctypes import wintypes, c_char, c_int, POINTER
from ctypes.wintypes import HWND, UINT, DWORD, LONG, HANDLE, BOOL, LPVOID

HCTX = HANDLE
WTPKT = DWORD
FIX32 = DWORD
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
class PACKET(ctypes.Structure):
	_fields_ = [
		('pkButtons', DWORD),
		('pkX', LONG),
		('pkY', LONG),
		('pkNormalPressure', UINT)
	]

WTI_DEFCONTEXT = 3

dll = ctypes.WinDLL("wintab32.dll")

#dll.WTInfoA.argtypes = [UINT, UINT, LPVOID]
dll.WTInfoA.argtypes = [UINT, UINT, POINTER(LOGCONTEXTA)]
dll.WTInfoA.restype = UINT

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
	hctx = dll.WTOpenA(HWND(31234), lc, 1)
	buf = (100*PACKET)()
	n = dll.WTPacketsGet(hctx, 20, buf)
	print(n)
