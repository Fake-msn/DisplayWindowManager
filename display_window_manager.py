#!/usr/bin/env python3
"""
鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒 - Display Window Manager v2.0
==============================================
绾?Python + Win32 API 瀹炵幇锛岄€氳繃娴忚鍣ㄦ彁渚涚ǔ瀹?GUI銆?
鍔熻兘锛?  1. 涓€閿皢绐楀彛浠庡壇灞忕Щ鍥炰富灞忥紙鎴栧弽鍚戯級
  2. 璁剧疆涓垏鎹㈢Щ鍔ㄦ柟鍚戯紙涓诲睆鈫掑壇灞?/ 鍓睆鈫掍富灞忥級
  3. 鏄剧ず鍣ㄥ睆钄斤細閫夋嫨灞忚斀鏌愭樉绀哄櫒锛岄樆姝㈡柊绐楀彛杩涘叆
  4. 鍏ㄥ眬鐑敭 Ctrl+Shift+M / Ctrl+Shift+S
  5. 绯荤粺鎵樼洏鍥炬爣 + 鍙抽敭鑿滃崟

杩愯鏂瑰紡: python display_window_manager.py
娴忚鍣ㄤ細鑷姩鎵撳紑 http://127.0.0.1:18888
"""

import ctypes
from ctypes import wintypes, byref, sizeof, POINTER, cast
import json
import os
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ============================================================
# DPI 鎰熺煡
# ============================================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ============================================================
# Win32 甯搁噺
# ============================================================
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
MONITOR_DEFAULTTONULL = 0
GWL_EXSTYLE = -20
GWL_STYLE = -16
GWL_ID = -12
SW_RESTORE = 9
SW_HIDE = 0
SW_SHOW = 5
SW_SHOWNORMAL = 1
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
VK_M = 0x4D
VK_S = 0x53
NIM_ADD = 0
NIM_DELETE = 2
NIF_MESSAGE = 1
NIF_ICON = 2
NIF_TIP = 4
WM_TRAYICON = 0x0400 + 2000
WM_HOTKEY = 0x0312
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONUP = 0x0205
MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800
TPM_LEFTALIGN = 0x0000
TPM_RIGHTBUTTON = 0x0002
IDI_APPLICATION = 32512
LR_DEFAULTSIZE = 0x00000040
LR_SHARED = 0x00008000
IMAGE_ICON = 1
IDC_ARROW = 32512
MB_OK = 0
MB_YESNO = 4
MB_ICONINFORMATION = 0x40
MB_ICONWARNING = 0x30
MB_ICONQUESTION = 0x20
IDYES = 6
ERROR_ALREADY_EXISTS = 183
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_EX_NOACTIVATE = 0x08000000
MDT_EFFECTIVE_DPI = 0

# 琛ュ厖 wintypes 缂哄け绫诲瀷锛堜粎琛?Python 3.10 涓湡姝ｇ己澶辩殑锛?wintypes.LRESULT = wintypes.LONG
wintypes.HRESULT = wintypes.LONG
wintypes.UINT_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
wintypes.LONG_PTR = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
wintypes.WPARAM = wintypes.UINT_PTR
wintypes.LPARAM = wintypes.LONG_PTR
wintypes.HCURSOR = wintypes.HANDLE

# ============================================================
# 缁撴瀯浣?# ============================================================
class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
    @property
    def width(self): return self.right - self.left
    @property
    def height(self): return self.bottom - self.top

class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

class MSG(ctypes.Structure):
    _fields_ = [
        ('hwnd', wintypes.HWND), ('message', wintypes.UINT), ('wParam', wintypes.WPARAM),
        ('lParam', wintypes.LPARAM), ('time', wintypes.DWORD), ('pt', POINT),
    ]

class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD), ('rcMonitor', RECT), ('rcWork', RECT),
        ('dwFlags', wintypes.DWORD), ('szDevice', wintypes.WCHAR * 32),
    ]

class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD), ('hWnd', wintypes.HWND), ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT), ('uCallbackMessage', wintypes.UINT), ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 128), ('dwState', wintypes.DWORD), ('dwStateMask', wintypes.DWORD),
        ('szInfo', wintypes.WCHAR * 256), ('uTimeout', wintypes.UINT),
        ('szInfoTitle', wintypes.WCHAR * 64), ('dwInfoFlags', wintypes.DWORD),
    ]

# ============================================================
class ICONINFO(ctypes.Structure):
    _fields_ = [
        ('fIcon', wintypes.BOOL), ('xHotspot', wintypes.DWORD), ('yHotspot', wintypes.DWORD),
        ('hbmMask', wintypes.HBITMAP), ('hbmColor', wintypes.HBITMAP),
    ]

# ============================================================
# Win32 DLL 鍔犺浇
# ============================================================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32
shcore = ctypes.windll.shcore
gdi32 = ctypes.windll.gdi32

# 鍑芥暟鍘熷瀷
user32.EnumWindows.argtypes = [ctypes.c_void_p, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetClassNameW.argtypes = [wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.SetWindowPos.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.EnumDisplayMonitors.argtypes = [wintypes.HDC, ctypes.c_void_p, ctypes.c_void_p, wintypes.LPARAM]
user32.EnumDisplayMonitors.restype = wintypes.BOOL
user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFOEX)]
user32.GetMonitorInfoW.restype = wintypes.BOOL
user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.MonitorFromWindow.restype = wintypes.HMONITOR
user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = wintypes.LRESULT
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None
user32.CreatePopupMenu.argtypes = []
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, wintypes.UINT_PTR, ctypes.c_wchar_p]
user32.AppendMenuW.restype = wintypes.BOOL
user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, ctypes.POINTER(RECT)]
user32.TrackPopupMenu.restype = wintypes.BOOL
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.MessageBoxW.argtypes = [wintypes.HWND, ctypes.c_wchar_p, ctypes.c_wchar_p, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int
user32.GetDpiForWindow.argtypes = [wintypes.HWND]
user32.GetDpiForWindow.restype = wintypes.UINT
shcore.GetDpiForMonitor.argtypes = [wintypes.HMONITOR, ctypes.c_int, ctypes.POINTER(wintypes.UINT), ctypes.POINTER(wintypes.UINT)]
shcore.GetDpiForMonitor.restype = ctypes.c_long

# CreateWindowExW / RegisterClassExW锛堝繀椤昏 argtypes锛屽惁鍒?64 浣?HINSTANCE 浼氭孩鍑猴級
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, ctypes.c_wchar_p, ctypes.c_wchar_p, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.RegisterClassExW.argtypes = [ctypes.c_void_p]
user32.RegisterClassExW.restype = wintypes.ATOM

kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, ctypes.c_wchar_p]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.GetLastError.argtypes = []
kernel32.GetLastError.restype = wintypes.DWORD
kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

# GDI 鍑芥暟锛堢敤浜庣粯鍒舵墭鐩樺浘鏍囷級
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteDC.restype = wintypes.BOOL
gdi32.CreateSolidBrush.argtypes = [wintypes.COLORREF]
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), wintypes.HBRUSH]
user32.FillRect.restype = ctypes.c_int
gdi32.CreateBitmap.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.UINT, wintypes.UINT, ctypes.c_void_p]
gdi32.CreateBitmap.restype = wintypes.HBITMAP
user32.CreateIconIndirect.argtypes = [ctypes.POINTER(ICONINFO)]
user32.CreateIconIndirect.restype = wintypes.HICON
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.DestroyIcon.argtypes = [wintypes.HICON]
user32.DestroyIcon.restype = wintypes.BOOL
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = wintypes.LRESULT

# ============================================================
# 绐楀彛绠＄悊鍣?# ============================================================
class WindowManager:
    SKIP_CLASSES = {
        'Progman', 'Shell_TrayWnd', 'NotifyIconOverflowWindow',
        'Shell_SecondaryTrayWnd', 'Windows.UI.Core.CoreWindow',
        'Button', 'Static', 'ToolbarWindow32', 'SysShadow',
        'CiceroUIWndFrame', 'IME', 'MSCTFIME UI', 'ApplicationFrameWindow',
    }
    _MonitorEnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)
    _WindowEnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @classmethod
    def get_monitors(cls):
        data = []
        def cb(h, dc, r, lp):
            mi = MONITORINFOEX()
            mi.cbSize = sizeof(MONITORINFOEX)
            user32.GetMonitorInfoW(h, byref(mi))
            data.append({
                'index': len(data) + 1,
                'handle': h,
                'rect': (mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom),
                'work': (mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom),
                'primary': bool(mi.dwFlags & 1),
                'device': mi.szDevice,
            })
            return True
        user32.EnumDisplayMonitors(None, None, cls._MonitorEnumProc(cb), 0)
        return data

    @classmethod
    def get_visible_windows(cls):
        windows = []
        def cb(hwnd, lp):
            if not user32.IsWindowVisible(hwnd):
                return True
            tl = user32.GetWindowTextLengthW(hwnd)
            if tl == 0:
                return True
            buf = ctypes.create_unicode_buffer(tl + 1)
            user32.GetWindowTextW(hwnd, buf, tl + 1)
            title = buf.value
            if not title:
                return True
            rect = RECT()
            user32.GetWindowRect(hwnd, byref(rect))
            if rect.width <= 0 or rect.height <= 0:
                return True
            if rect.width < 100 and rect.height < 100:
                return True
            cb2 = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cb2, 256)
            cn = cb2.value
            if cn in cls.SKIP_CLASSES:
                return True
            ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if (ex & WS_EX_TOOLWINDOW) and not (ex & WS_EX_APPWINDOW):
                return True
            if ex & WS_EX_NOACTIVATE:
                return True
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, byref(pid))
            windows.append({
                'hwnd': hwnd,
                'title': title,
                'x': rect.left, 'y': rect.top, 'w': rect.width, 'h': rect.height,
                'class_name': cn, 'pid': pid.value,
            })
            return True
        user32.EnumWindows(cls._WindowEnumProc(cb), 0)
        return windows

    @classmethod
    def get_monitor_for_window(cls, hwnd):
        hm = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONULL)
        if not hm:
            return None
        for m in cls.get_monitors():
            if m['handle'] == hm:
                return m
        return None

    @classmethod
    def move_window_to_monitor(cls, hwnd, target_monitor):
        rect = RECT()
        user32.GetWindowRect(hwnd, byref(rect))
        orig_x, orig_y = rect.left, rect.top
        w, h = rect.width, rect.height

        try:
            sdpi = user32.GetDpiForWindow(hwnd)
            dx = wintypes.UINT(); dy = wintypes.UINT()
            shcore.GetDpiForMonitor(target_monitor['handle'], MDT_EFFECTIVE_DPI, byref(dx), byref(dy))
            tdpi = dx.value
            if sdpi > 0 and tdpi > 0 and sdpi != tdpi:
                scale = tdpi / sdpi
                w = int(w * scale); h = int(h * scale)
        except Exception:
            pass

        tw, th = target_monitor['work'][2] - target_monitor['work'][0], target_monitor['work'][3] - target_monitor['work'][1]
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
            time.sleep(0.05)
        nw = min(w, tw); nh = min(h, th)
        nx = target_monitor['work'][0] + max(0, (tw - nw) // 2)
        ny = target_monitor['work'][1] + max(0, (th - nh) // 2)
        user32.SetWindowPos(hwnd, 0, nx, ny, nw, nh, SWP_NOZORDER | SWP_NOACTIVATE)
        time.sleep(0.03)
        nr = RECT()
        user32.GetWindowRect(hwnd, byref(nr))
        return nr.left != orig_x or nr.top != orig_y

    @classmethod
    def move_all_from_monitor(cls, source_index, target_index):
        monitors = cls.get_monitors()
        if source_index < 1 or source_index > len(monitors): return []
        if target_index < 1 or target_index > len(monitors): return []
        if source_index == target_index: return []
        moved = []
        for win in cls.get_visible_windows():
            m = cls.get_monitor_for_window(win['hwnd'])
            if m and m['index'] == source_index:
                if cls.move_window_to_monitor(win['hwnd'], monitors[target_index - 1]):
                    moved.append(win['title'])
        return moved


# ============================================================
# 灞忚斀鍣?# ============================================================
class DisplayShield:
    def __init__(self):
        self._shielded = None
        self._target = None
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    @property
    def is_active(self): return self._running
    @property
    def shielded_monitor(self): return self._shielded
    @property
    def target_monitor(self): return self._target

    def start(self, shielded_idx, target_idx):
        with self._lock:
            if self._running:
                self._stop()
            self._shielded = shielded_idx
            self._target = target_idx
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop()

    def _stop(self):
        self._running = False
        self._thread = None

    def _loop(self):
        while self._running:
            try:
                WindowManager.move_all_from_monitor(self._shielded, self._target)
            except Exception:
                pass
            time.sleep(0.5)


# ============================================================
# 閰嶇疆
# ============================================================
class ConfigManager:
    DEFAULT = {
        'move_direction': 'secondary_to_primary',
        'shield_enabled': False,
        'shield_monitor': 2,
        'shield_target': 1,
    }

    def __init__(self):
        try:
            base = os.path.dirname(os.path.abspath(sys.argv[0]))
        except Exception:
            base = os.path.dirname(os.path.abspath(__file__))
        self.path = Path(base) / 'display_manager_config.json'
        self._cfg = self.DEFAULT.copy()
        self.load()

    def load(self):
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    for k in self.DEFAULT:
                        if k in saved:
                            self._cfg[k] = saved[k]
        except Exception:
            pass

    def save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        self.save()

    def __getitem__(self, key):
        return self._cfg[key]

    def __setitem__(self, key, value):
        self._cfg[key] = value
        self.save()


# ============================================================
# HTTP 鏈嶅姟鍣?# ============================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei UI','Segoe UI',sans-serif;background:#f0f2f5;color:#333;min-height:100vh;display:flex;justify-content:center;padding:20px}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08);width:100%;max-width:420px;padding:24px}
h1{font-size:20px;text-align:center;margin-bottom:20px;color:#1a1a2e}
.section{margin-bottom:16px}
.section-title{font-size:13px;font-weight:700;color:#666;text-transform:uppercase;margin-bottom:8px;letter-spacing:.5px}
.monitor-list{display:flex;flex-direction:column;gap:6px}
.monitor-item{display:flex;align-items:center;padding:10px 14px;background:#f8f9fa;border-radius:8px;border:1px solid #e9ecef;font-size:14px}
.monitor-item .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-left:8px}
.badge-primary{background:#e3f2fd;color:#1565c0}
.badge-secondary{background:#f3e5f5;color:#7b1fa2}
.status-row{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;background:#f8f9fa;border-radius:8px;margin-bottom:6px;font-size:14px}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.status-dot.active{background:#4caf50}
.status-dot.inactive{background:#bdbdbd}
.btn-row{display:flex;gap:10px;margin-top:16px}
.btn{flex:1;padding:12px 16px;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;transition:all .15s}
.btn:hover{transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,.15)}
.btn:active{transform:translateY(0)}
.btn-primary{background:#1976d2;color:#fff}
.btn-primary:hover{background:#1565c0}
.btn-danger{background:#e53935;color:#fff}
.btn-danger:hover{background:#c62828}
.btn-danger.active{background:#4caf50}
.btn-danger.active:hover{background:#388e3c}
.btn-outline{background:#fff;color:#1976d2;border:2px solid #1976d2;flex:0.5}
.btn-outline:hover{background:#e3f2fd}
.settings-panel{display:none;margin-top:20px;padding:20px;background:#f8f9fa;border-radius:8px;border:1px solid #e9ecef}
.settings-panel.show{display:block}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:13px;font-weight:600;color:#555;margin-bottom:4px}
.form-group select{width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;background:#fff;cursor:pointer}
.radio-group{display:flex;flex-direction:column;gap:6px}
.radio-option{display:flex;align-items:center;padding:8px 12px;background:#fff;border:1px solid #ddd;border-radius:6px;cursor:pointer;font-size:13px}
.radio-option input{margin-right:8px;accent-color:#1976d2}
.radio-option.selected{border-color:#1976d2;background:#e3f2fd}
.checkbox-group{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.checkbox-group input{accent-color:#1976d2;width:16px;height:16px;cursor:pointer}
.checkbox-group label{font-size:13px;cursor:pointer}
.shield-options{display:none;margin-top:8px}
.shield-options.show{display:block}
.shield-row{display:flex;gap:8px;align-items:center}
.shield-row select{flex:1;padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px;background:#fff}
.shield-arrow{font-size:16px;color:#1976d2;font-weight:700}
.settings-btns{display:flex;gap:8px;margin-top:16px}
.settings-btns .btn{flex:1;padding:10px;font-size:13px}
.toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;z-index:999;opacity:0;transition:opacity .3s}
.toast.show{opacity:1}
.hk-info{font-size:12px;color:#888;text-align:center;margin-top:16px}
@media (max-width:440px){.card{margin:0;border-radius:0}}
</style>
</head>
<body>
<div class="card">
  <h1>鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒</h1>

  <div class="section">
    <div class="section-title">鏄剧ず鍣ㄧ姸鎬?/div>
    <div class="monitor-list" id="monitorList">鍔犺浇涓?..</div>
  </div>

  <div class="section">
    <div class="status-row">
      <span>绉诲姩鏂瑰悜</span>
      <span id="directionLabel" style="font-weight:600;color:#1976d2">鍓睆 鈫?涓诲睆</span>
    </div>
    <div class="status-row">
      <span>鏄剧ず鍣ㄥ睆钄?/span>
      <span id="shieldLabel" style="font-weight:600;color:#888">鏈惎鐢?/span>
    </div>
  </div>

  <div class="btn-row">
    <button class="btn btn-primary" onclick="moveWindows()">绉诲姩绐楀彛</button>
    <button class="btn btn-danger" id="shieldBtn" onclick="toggleShield()">灞忚斀: 鍏?/button>
  </div>
  <div class="btn-row">
    <button class="btn btn-outline" onclick="toggleSettings()">璁剧疆</button>
    <button class="btn btn-outline" onclick="refresh()">鍒锋柊</button>
  </div>

  <div class="settings-panel" id="settingsPanel">
    <div class="section">
      <div class="section-title">绉诲姩鏂瑰悜</div>
      <div class="radio-group">
        <label class="radio-option" id="dirOpt1">
          <input type="radio" name="direction" value="secondary_to_primary" checked>
          鍓睆 鈫?涓诲睆锛堝皢绗簩灞忓箷绐楀彛绉诲洖涓诲睆骞曪級
        </label>
        <label class="radio-option" id="dirOpt2">
          <input type="radio" name="direction" value="primary_to_secondary">
          涓诲睆 鈫?鍓睆锛堝皢涓诲睆骞曠獥鍙ｇЩ鑷崇浜屽睆骞曪級
        </label>
      </div>
    </div>

    <div class="section" style="margin-top:16px">
      <div class="section-title">鏄剧ず鍣ㄥ睆钄?/div>
      <div class="checkbox-group">
        <input type="checkbox" id="shieldEnabled">
        <label for="shieldEnabled">鍚敤灞忚斀锛堥樆姝㈡柊绐楀彛杩涘叆鎸囧畾鏄剧ず鍣級</label>
      </div>
      <div class="shield-options" id="shieldOptions">
        <div class="shield-row">
          <select id="shieldMonitor"></select>
          <span class="shield-arrow">鈫?/span>
          <select id="shieldTarget"></select>
        </div>
        <p style="font-size:12px;color:#888;margin-top:8px">鍚敤鍚庯紝灞忚斀鏄剧ず鍣ㄤ笂鐨勭獥鍙ｅ皢琚嚜鍔ㄧЩ璧帮紝鏂扮獥鍙ｄ篃涓嶄細鍋滅暀鍦ㄨ鏄剧ず鍣ㄤ笂銆?/p>
      </div>
    </div>

    <div class="settings-btns">
      <button class="btn btn-primary" onclick="saveSettings()">淇濆瓨</button>
      <button class="btn btn-outline" onclick="toggleSettings()">鍙栨秷</button>
    </div>
  </div>

  <div class="hk-info">Ctrl+Shift+M 绉诲姩 路 Ctrl+Shift+S 鍒囨崲灞忚斀</div>
</div>
<div class="toast" id="toast"></div>

<script>
const API = '/api';

async function refresh() {
  try {
    const r = await fetch(API+'/state');
    const s = await r.json();
    renderMonitors(s.monitors);
    renderDirection(s.direction);
    renderShield(s.shield);
    renderSettings(s);
  } catch(e) {
    console.error(e);
  }
}

function renderMonitors(monitors) {
  const el = document.getElementById('monitorList');
  if (!monitors || monitors.length === 0) {
    el.innerHTML = '<div class="monitor-item" style="color:#888">鏈娴嬪埌鏄剧ず鍣?/div>';
    return;
  }
  el.innerHTML = monitors.map(m =>
    `<div class="monitor-item">
      <span>鏄剧ず鍣?${m.index}: ${m.width}x${m.height}</span>
      ${m.primary ? '<span class="badge badge-primary">涓绘樉绀哄櫒</span>' : '<span class="badge badge-secondary">鍓睆</span>'}
    </div>`
  ).join('');
}

function renderDirection(dir) {
  const el = document.getElementById('directionLabel');
  el.textContent = dir === 'secondary_to_primary' ? '鍓睆 鈫?涓诲睆' : '涓诲睆 鈫?鍓睆';
}

function renderShield(sh) {
  const el = document.getElementById('shieldLabel');
  const btn = document.getElementById('shieldBtn');
  if (sh.active) {
    el.innerHTML = '<span class="status-dot active"></span>宸插惎鐢?(鏄剧ず鍣?+sh.shielded+' 鈫?鏄剧ず鍣?+sh.target+')';
    el.style.color = '#e53935';
    btn.textContent = '灞忚斀: 寮€';
    btn.classList.add('active');
  } else {
    el.innerHTML = '<span class="status-dot inactive"></span>鏈惎鐢?;
    el.style.color = '#888';
    btn.textContent = '灞忚斀: 鍏?;
    btn.classList.remove('active');
  }
}

function renderSettings(s) {
  document.querySelector('input[name="direction"][value="'+s.direction+'"]').checked = true;
  document.querySelectorAll('.radio-option').forEach(o => {
    o.classList.toggle('selected', o.querySelector('input').checked);
  });
  document.getElementById('shieldEnabled').checked = s.shield_enabled;
  document.getElementById('shieldOptions').classList.toggle('show', s.shield_enabled);

  const sm = document.getElementById('shieldMonitor');
  const st = document.getElementById('shieldTarget');
  sm.innerHTML = st.innerHTML = '';
  if (s.monitors) {
    s.monitors.forEach(m => {
      const opt = `<option value="${m.index}">${m.index === 1 ? '鏄剧ず鍣?1'+(m.primary?' (涓?':'') : '鏄剧ず鍣?'+m.index}</option>`;
      sm.innerHTML += opt;
      st.innerHTML += opt;
    });
  }
  sm.value = s.shield_monitor;
  st.value = s.shield_target;
}

function toggleSettings() {
  const p = document.getElementById('settingsPanel');
  if (p.classList.contains('show')) {
    p.classList.remove('show');
    refresh();
  } else {
    p.classList.add('show');
    refresh();
  }
}

async function saveSettings() {
  const dir = document.querySelector('input[name="direction"]:checked').value;
  const enabled = document.getElementById('shieldEnabled').checked;
  const sm = parseInt(document.getElementById('shieldMonitor').value);
  const st = parseInt(document.getElementById('shieldTarget').value);

  try {
    const r = await fetch(API+'/save-settings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({move_direction: dir, shield_enabled: enabled, shield_monitor: sm, shield_target: st})
    });
    const j = await r.json();
    if (j.ok) {
      showToast('璁剧疆宸蹭繚瀛?);
      document.getElementById('settingsPanel').classList.remove('show');
      refresh();
    } else {
      showToast('淇濆瓨澶辫触: ' + (j.error || '鏈煡閿欒'));
    }
  } catch(e) {
    showToast('缃戠粶閿欒');
  }
}

async function moveWindows() {
  try {
    const r = await fetch(API+'/move');
    const j = await r.json();
    showToast(j.message);
    refresh();
  } catch(e) {
    showToast('鎿嶄綔澶辫触');
  }
}

async function toggleShield() {
  try {
    const r = await fetch(API+'/toggle-shield');
    const j = await r.json();
    showToast(j.message);
    refresh();
  } catch(e) {
    showToast('鎿嶄綔澶辫触');
  }
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

document.querySelectorAll('input[name="direction"]').forEach(r => {
  r.addEventListener('change', () => {
    document.querySelectorAll('.radio-option').forEach(o => {
      o.classList.toggle('selected', o.querySelector('input').checked);
    });
  });
});
document.getElementById('shieldEnabled').addEventListener('change', function() {
  document.getElementById('shieldOptions').classList.toggle('show', this.checked);
});
document.querySelectorAll('.radio-option').forEach(o => {
  o.addEventListener('click', function(e) {
    if (e.target.tagName !== 'INPUT') {
      this.querySelector('input').click();
    }
  });
});

// 蹇冭烦锛氭瘡 5 绉?ping 涓€娆★紝淇濇寔鏈嶅姟绔瓨娲?setInterval(() => { fetch(API+'/ping').catch(()=>{}); }, 5000);

// 鍏抽棴缃戦〉鏃堕€氱煡鏈嶅姟绔€€鍑?window.addEventListener('beforeunload', () => {
  navigator.sendBeacon(API+'/quit');
});

refresh();
</script>
</body>
</html>"""


class RequestHandler(BaseHTTPRequestHandler):
    app = None

    def log_message(self, format, *args):
        pass

    def _send(self, status, body, content_type='application/json'):
        body = body.encode('utf-8') if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self._send(200, HTML_PAGE, 'text/html')
        elif self.path == '/api/state':
            app = self.app
            monitors = WindowManager.get_monitors()
            self._send(200, {
                'monitors': [{'index': m['index'], 'width': m['rect'][2]-m['rect'][0],
                              'height': m['rect'][3]-m['rect'][1], 'primary': m['primary']} for m in monitors],
                'direction': app.config['move_direction'],
                'shield': {
                    'active': app.shield.is_active,
                    'shielded': app.shield.shielded_monitor,
                    'target': app.shield.target_monitor,
                },
                'shield_enabled': app.config['shield_enabled'],
                'shield_monitor': app.config['shield_monitor'],
                'shield_target': app.config['shield_target'],
            })
        elif self.path == '/api/move':
            app = self.app
            cfg = app.config
            monitors = WindowManager.get_monitors()
            if len(monitors) < 2:
                self._send(200, {'ok': False, 'message': '浠呮娴嬪埌涓€涓樉绀哄櫒'})
                return
            if cfg['move_direction'] == 'secondary_to_primary':
                primary = next((m for m in monitors if m['primary']), None)
                if not primary:
                    self._send(200, {'ok': False, 'message': '鏃犳硶纭畾涓绘樉绀哄櫒'})
                    return
                total = 0
                for m in monitors:
                    if not m['primary']:
                        total += len(WindowManager.move_all_from_monitor(m['index'], primary['index']))
                self._send(200, {'ok': True, 'message': f'宸插皢 {total} 涓獥鍙ｄ粠鍓睆绉诲姩鍒颁富灞?})
            else:
                primary = next((m for m in monitors if m['primary']), None)
                if not primary:
                    self._send(200, {'ok': False, 'message': '鏃犳硶纭畾涓绘樉绀哄櫒'})
                    return
                target = next((m for m in monitors if not m['primary']), None)
                if not target:
                    self._send(200, {'ok': False, 'message': '娌℃湁妫€娴嬪埌鍓睆'})
                    return
                moved = WindowManager.move_all_from_monitor(primary['index'], target['index'])
                self._send(200, {'ok': True, 'message': f'宸插皢 {len(moved)} 涓獥鍙ｄ粠涓诲睆绉诲姩鍒版樉绀哄櫒 {target["index"]}'})
        elif self.path == '/api/toggle-shield':
            app = self.app
            if app.shield.is_active:
                app.shield.stop()
                app.config['shield_enabled'] = False
                app.config.save()
                self._send(200, {'ok': True, 'message': '灞忚斀宸插叧闂?})
            else:
                monitors = WindowManager.get_monitors()
                if len(monitors) < 2:
                    self._send(200, {'ok': False, 'message': '闇€瑕佽嚦灏?2 涓樉绀哄櫒'})
                    return
                si = app.config['shield_monitor']
                ti = app.config['shield_target']
                if si == ti:
                    self._send(200, {'ok': False, 'message': '灞忚斀鏄剧ず鍣ㄥ拰鐩爣鏄剧ず鍣ㄤ笉鑳界浉鍚?})
                    return
                app.shield.start(si, ti)
                app.config['shield_enabled'] = True
                app.config.save()
                self._send(200, {'ok': True, 'message': f'灞忚斀宸插惎鐢?(鏄剧ず鍣?{si} 鈫?鏄剧ず鍣?{ti})'})
        elif self.path == '/api/ping':
            self.app.last_heartbeat = time.time()
            self._send(200, {'ok': True, 'ping': 'pong'})
        elif self.path == '/api/quit':
            self._send(200, {'ok': True, 'message': '姝ｅ湪閫€鍑?..'})
            threading.Thread(target=self.app.quit, daemon=True).start()
        else:
            self._send(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path == '/api/save-settings':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            app = self.app
            app.config['move_direction'] = body.get('move_direction', 'secondary_to_primary')
            app.config['shield_enabled'] = body.get('shield_enabled', False)
            app.config['shield_monitor'] = body.get('shield_monitor', 2)
            app.config['shield_target'] = body.get('shield_target', 1)
            app.config.save()
            app.apply_shield_settings()
            self._send(200, {'ok': True})
        elif self.path == '/api/quit':
            self._send(200, {'ok': True, 'message': '姝ｅ湪閫€鍑?..'})
            threading.Thread(target=self.app.quit, daemon=True).start()
        else:
            self._send(404, {'error': 'Not found'})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# ============================================================
# 鎵樼洏 + 鐑敭 娑堟伅绐楀彛
# ============================================================
class TrayWindow:
    def __init__(self, app):
        self.app = app
        self.hwnd = None
        self._icon = None
        self._wndproc = None
        self._running = False
        self._create()

    def _create(self):
        hinst = kernel32.GetModuleHandleW(None)
        self._wndproc = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)(self._wnd_proc)
        wc = ctypes.create_unicode_buffer("DWM_TrayWindow")
        wcx = ctypes.cast(wc, ctypes.c_void_p).value

        cls = type('WNDCLASSEXW', (ctypes.Structure,), {
            '_fields_': [
                ('cbSize', wintypes.UINT), ('style', wintypes.UINT), ('lpfnWndProc', ctypes.c_void_p),
                ('cbClsExtra', ctypes.c_int), ('cbWndExtra', ctypes.c_int), ('hInstance', wintypes.HINSTANCE),
                ('hIcon', wintypes.HICON), ('hCursor', wintypes.HCURSOR), ('hbrBackground', wintypes.HBRUSH),
                ('lpszMenuName', ctypes.c_wchar_p), ('lpszClassName', ctypes.c_wchar_p), ('hIconSm', wintypes.HICON),
            ]
        })()
        cls.cbSize = ctypes.sizeof(cls)
        cls.lpfnWndProc = cast(self._wndproc, ctypes.c_void_p)
        cls.hInstance = hinst
        cls.lpszClassName = "DWM_TrayWindow"
        user32.RegisterClassExW(byref(cls))

        self.hwnd = user32.CreateWindowExW(0, "DWM_TrayWindow", "", 0, 0, 0, 0, 0, None, None, hinst, None)

        self._icon = self._create_tray_icon()
        nid = NOTIFYICONDATAW()
        nid.cbSize = sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        nid.uCallbackMessage = WM_TRAYICON
        nid.hIcon = self._icon
        nid.szTip = "鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒"
        shell32.Shell_NotifyIconW(NIM_ADD, byref(nid))

        user32.RegisterHotKey(self.hwnd, 1, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_M)
        user32.RegisterHotKey(self.hwnd, 2, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_S)

    def _create_tray_icon(self):
        """鐢?GDI 缁樺埗涓€涓畝鍗曠殑鏄剧ず鍣ㄥ浘鏍?""
        SM_CXSMICON = 49
        SM_CYSMICON = 50
        w = user32.GetSystemMetrics(SM_CXSMICON)
        h = user32.GetSystemMetrics(SM_CYSMICON)

        hdc = user32.GetDC(None)
        mem_dc = gdi32.CreateCompatibleDC(hdc)

        # 鍒涘缓棰滆壊浣嶅浘
        bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
        gdi32.SelectObject(mem_dc, bmp)

        # 钃濊壊鑳屾櫙
        full = RECT(0, 0, w, h)
        brush = gdi32.CreateSolidBrush(0x00D67619)  # BGR = #1976D2
        user32.FillRect(mem_dc, byref(full), brush)
        gdi32.DeleteObject(brush)

        # 鐧借壊灞忓箷鍖哄煙
        pad = max(2, w // 8)
        sr = RECT(pad, pad, w - pad, h - pad - h // 4)
        brush = gdi32.CreateSolidBrush(0x00FFFFFF)
        user32.FillRect(mem_dc, byref(sr), brush)
        gdi32.DeleteObject(brush)

        # 鐧借壊搴曞骇
        sw = max(3, w // 4)
        br = RECT(w // 2 - sw // 2, h - pad - h // 4, w // 2 + sw // 2, h - pad)
        brush = gdi32.CreateSolidBrush(0x00FFFFFF)
        user32.FillRect(mem_dc, byref(br), brush)
        gdi32.DeleteObject(brush)

        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(None, hdc)

        # 鍒涘缓鍗曡壊 AND 鎺╃爜锛堝叏鐧?鍏ㄤ笉閫忔槑锛?        mask_bytes = (ctypes.c_ubyte * (((w * h) + 7) // 8))()
        for i in range(len(mask_bytes)):
            mask_bytes[i] = 0xFF
        mask_bmp = gdi32.CreateBitmap(w, h, 1, 1, mask_bytes)

        # 鍒涘缓鍥炬爣
        ic = ICONINFO()
        ic.fIcon = True
        ic.hbmColor = bmp
        ic.hbmMask = mask_bmp
        hicon = user32.CreateIconIndirect(byref(ic))

        gdi32.DeleteObject(bmp)
        gdi32.DeleteObject(mask_bmp)
        return hicon

    def _show_menu(self):
        menu = user32.CreatePopupMenu()
        s = "灞忚斀: 寮€" if self.app.shield.is_active else "灞忚斀: 鍏?
        user32.AppendMenuW(menu, MF_STRING, 1, "绉诲姩绐楀彛")
        user32.AppendMenuW(menu, MF_STRING, 2, s)
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, 3, "鎵撳紑鐣岄潰")
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, 4, "閫€鍑?)
        pt = POINT()
        user32.GetCursorPos(byref(pt))
        user32.SetForegroundWindow(self.hwnd)
        user32.TrackPopupMenu(menu, TPM_LEFTALIGN | TPM_RIGHTBUTTON, pt.x, pt.y, 0, self.hwnd, None)
        user32.PostMessageW(self.hwnd, 0, 0, 0)
        user32.DestroyMenu(menu)

    def _wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg == WM_HOTKEY:
            if wParam == 1:
                threading.Thread(target=self._api_move, daemon=True).start()
            elif wParam == 2:
                threading.Thread(target=self._api_toggle_shield, daemon=True).start()
            return 0
        elif msg == WM_TRAYICON:
            if lParam == WM_LBUTTONDBLCLK:
                threading.Thread(target=self._api_move, daemon=True).start()
            elif lParam == WM_RBUTTONUP:
                self._show_menu()
            return 0
        elif msg == 0x0111:  # WM_COMMAND from menu
            cmd = wParam & 0xFFFF
            if cmd == 1:
                threading.Thread(target=self._api_move, daemon=True).start()
            elif cmd == 2:
                threading.Thread(target=self._api_toggle_shield, daemon=True).start()
            elif cmd == 3:
                webbrowser.open('http://127.0.0.1:18888')
            elif cmd == 4:
                self._quit()
            return 0
        elif msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wParam, lParam)

    def _api_move(self):
        app = self.app
        cfg = app.config
        monitors = WindowManager.get_monitors()
        if len(monitors) < 2:
            return
        if cfg['move_direction'] == 'secondary_to_primary':
            primary = next((m for m in monitors if m['primary']), None)
            if not primary: return
            for m in monitors:
                if not m['primary']:
                    WindowManager.move_all_from_monitor(m['index'], primary['index'])
        else:
            primary = next((m for m in monitors if m['primary']), None)
            if not primary: return
            target = next((m for m in monitors if not m['primary']), None)
            if not target: return
            WindowManager.move_all_from_monitor(primary['index'], target['index'])

    def _api_toggle_shield(self):
        app = self.app
        if app.shield.is_active:
            app.shield.stop()
            app.config['shield_enabled'] = False
        else:
            monitors = WindowManager.get_monitors()
            if len(monitors) < 2: return
            si = app.config['shield_monitor']
            ti = app.config['shield_target']
            if si == ti: return
            app.shield.start(si, ti)
            app.config['shield_enabled'] = True
        app.config.save()

    def _quit(self):
        self.app.shield.stop()
        nid = NOTIFYICONDATAW()
        nid.cbSize = sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        shell32.Shell_NotifyIconW(NIM_DELETE, byref(nid))
        user32.DestroyWindow(self.hwnd)
        os._exit(0)

    def run(self):
        self._running = True
        msg = MSG()
        while self._running and user32.GetMessageW(byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))


# ============================================================
# 搴旂敤绋嬪簭
# ============================================================
class App:
    def __init__(self):
        h = kernel32.CreateMutexW(None, False, "Global\\DWM_SingleInstance_v2")
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            user32.MessageBoxW(None, "鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒宸茬粡鍦ㄨ繍琛屼腑銆?, "宸插湪杩愯", MB_OK | MB_ICONWARNING)
            sys.exit(0)

        self.config = ConfigManager()
        self.shield = DisplayShield()
        self.tray = None
        self.server = None
        self.last_heartbeat = time.time()

    def _heartbeat_checker(self):
        """鍚庡彴绾跨▼锛氭娴嬪績璺宠秴鏃跺垯鑷姩閫€鍑?""
        while True:
            time.sleep(5)
            if time.time() - self.last_heartbeat > 15:
                self.quit()
                return

    def quit(self):
        """瀹夊叏閫€鍑哄簲鐢?""
        self.shield.stop()
        if self.tray:
            self.tray._running = False
            user32.PostMessageW(self.tray.hwnd, WM_CLOSE, 0, 0)
        os._exit(0)

    def apply_shield_settings(self):
        if self.config['shield_enabled']:
            monitors = WindowManager.get_monitors()
            if len(monitors) >= 2:
                si = self.config['shield_monitor']
                ti = self.config['shield_target']
                if si != ti and si <= len(monitors) and ti <= len(monitors):
                    if not self.shield.is_active:
                        self.shield.start(si, ti)
                    elif self.shield.shielded_monitor != si or self.shield.target_monitor != ti:
                        self.shield.stop()
                        self.shield.start(si, ti)
        else:
            if self.shield.is_active:
                self.shield.stop()

    def start_server(self):
        RequestHandler.app = self
        self.server = HTTPServer(('127.0.0.1', 18888), RequestHandler)
        self.server.timeout = 1
        t = threading.Thread(target=self.server.serve_forever, daemon=True)
        t.start()

    def run(self):
        self.apply_shield_settings()
        self.start_server()
        threading.Thread(target=self._heartbeat_checker, daemon=True).start()
        webbrowser.open('http://127.0.0.1:18888')
        self.tray = TrayWindow(self)
        self.tray.run()


def main():
    app = App()
    app.run()

if __name__ == '__main__':
    main()