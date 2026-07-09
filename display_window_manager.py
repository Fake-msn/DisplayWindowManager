#!/usr/bin/env python3
"""
窗归 - WinBack v2.0
==============================================
纯 Python + Win32 API 实现，通过浏览器提供稳定 GUI。

功能：
  1. 一键将窗口从副屏移回主屏（或反向）
  2. 设置中切换移动方向（主屏→副屏 / 副屏→主屏）
  3. 显示器屏蔽：选择屏蔽某显示器，阻止新窗口进入
  4. 全局热键 Ctrl+Shift+M / Ctrl+Shift+S
  5. 系统托盘图标 + 右键菜单

运行方式: python display_window_manager.py
浏览器会自动打开 http://127.0.0.1:18888
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
# 多语言 (i18n)
# ============================================================
I18N = {
    'zh': {
        'title': '窗归',
        'heading': '窗归',
        'section_monitor': '显示器状态',
        'loading': '加载中...',
        'direction_label': '移动方向',
        'dir_secondary_to_primary': '副屏 → 主屏',
        'dir_primary_to_secondary': '主屏 → 副屏',
        'shield_label': '显示器屏蔽',
        'shield_off': '未启用',
        'shield_on': '已启用',
        'btn_move': '移动窗口',
        'btn_shield_off': '屏蔽: 关',
        'btn_shield_on': '屏蔽: 开',
        'btn_settings': '设置',
        'btn_refresh': '刷新',
        'settings_direction': '移动方向',
        'dir_opt1': '副屏 → 主屏（将第二屏幕窗口移回主屏幕）',
        'dir_opt2': '主屏 → 副屏（将主屏幕窗口移至第二屏幕）',
        'settings_shield': '显示器屏蔽',
        'shield_checkbox': '启用屏蔽（阻止新窗口进入指定显示器）',
        'shield_hint': '启用后，屏蔽显示器上的窗口将被自动移走，新窗口也不会停留在该显示器上。',
        'btn_save': '保存',
        'btn_cancel': '取消',
        'hk_info': 'Ctrl+Shift+M 移动 · Ctrl+Shift+S 切换屏蔽',
        'monitor': '显示器',
        'primary': '主显示器',
        'secondary': '副屏',
        'no_monitor': '未检测到显示器',
        'toast_saved': '设置已保存',
        'toast_save_fail': '保存失败',
        'toast_unknown_error': '未知错误',
        'toast_network_error': '网络错误',
        'toast_operation_fail': '操作失败',
        'tray_tip': '窗归',
        'menu_move': '移动窗口',
        'menu_shield_on': '屏蔽: 开',
        'menu_shield_off': '屏蔽: 关',
        'menu_open': '打开界面',
        'menu_exit': '退出',
        'msg_single_monitor': '仅检测到一个显示器',
        'msg_no_primary': '无法确定主显示器',
        'msg_no_secondary': '没有检测到副屏',
        'msg_moved_to_primary': '已将 {total} 个窗口从副屏移动到主屏',
        'msg_moved_to_secondary': '已将 {count} 个窗口从主屏移动到显示器 {index}',
        'msg_shield_off': '屏蔽已关闭',
        'msg_shield_need_two': '需要至少 2 个显示器',
        'msg_shield_same': '屏蔽显示器和目标显示器不能相同',
        'msg_shield_on': '屏蔽已启用 (显示器 {si} → 显示器 {ti})',
        'msg_quitting': '正在退出...',
        'msg_already_running': '窗归已经在运行中。',
        'msg_already_running_title': '已在运行',
        'lang_toggle': 'English',
        'lang_switch': '语言',
    },
    'en': {
        'title': 'WinBack',
        'heading': 'WinBack',
        'section_monitor': 'Monitor Status',
        'loading': 'Loading...',
        'direction_label': 'Move Direction',
        'dir_secondary_to_primary': 'Secondary → Primary',
        'dir_primary_to_secondary': 'Primary → Secondary',
        'shield_label': 'Display Shield',
        'shield_off': 'Disabled',
        'shield_on': 'Enabled',
        'btn_move': 'Move Windows',
        'btn_shield_off': 'Shield: Off',
        'btn_shield_on': 'Shield: On',
        'btn_settings': 'Settings',
        'btn_refresh': 'Refresh',
        'settings_direction': 'Move Direction',
        'dir_opt1': 'Secondary → Primary (move windows from secondary to primary monitor)',
        'dir_opt2': 'Primary → Secondary (move windows from primary to secondary monitor)',
        'settings_shield': 'Display Shield',
        'shield_checkbox': 'Enable Shield (prevent new windows from entering the selected monitor)',
        'shield_hint': 'When enabled, windows on the shielded monitor will be automatically moved away, and new windows will not stay on that monitor.',
        'btn_save': 'Save',
        'btn_cancel': 'Cancel',
        'hk_info': 'Ctrl+Shift+M Move · Ctrl+Shift+S Toggle Shield',
        'monitor': 'Monitor',
        'primary': 'Primary',
        'secondary': 'Secondary',
        'no_monitor': 'No monitors detected',
        'toast_saved': 'Settings saved',
        'toast_save_fail': 'Save failed',
        'toast_unknown_error': 'Unknown error',
        'toast_network_error': 'Network error',
        'toast_operation_fail': 'Operation failed',
        'tray_tip': 'WinBack',
        'menu_move': 'Move Windows',
        'menu_shield_on': 'Shield: On',
        'menu_shield_off': 'Shield: Off',
        'menu_open': 'Open UI',
        'menu_exit': 'Exit',
        'msg_single_monitor': 'Only one monitor detected',
        'msg_no_primary': 'Cannot determine primary monitor',
        'msg_no_secondary': 'No secondary monitor detected',
        'msg_moved_to_primary': 'Moved {total} windows from secondary to primary monitor',
        'msg_moved_to_secondary': 'Moved {count} windows from primary to monitor {index}',
        'msg_shield_off': 'Shield disabled',
        'msg_shield_need_two': 'At least 2 monitors required',
        'msg_shield_same': 'Shield monitor and target monitor must be different',
        'msg_shield_on': 'Shield enabled (Monitor {si} → Monitor {ti})',
        'msg_quitting': 'Exiting...',
        'msg_already_running': 'WinBack is already running.',
        'msg_already_running_title': 'Already Running',
        'lang_toggle': '中文',
        'lang_switch': 'Language',
    },
}

def get_lang_str(lang, key):
    """获取翻译字符串，缺失时回退到中文"""
    return I18N.get(lang, I18N['zh']).get(key, I18N['zh'].get(key, key))

# ============================================================
# DPI 感知
# ============================================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ============================================================
# Win32 常量
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

# 补充 wintypes 缺失类型（仅补 Python 3.10 中真正缺失的）
wintypes.LRESULT = wintypes.LONG
wintypes.HRESULT = wintypes.LONG
wintypes.UINT_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
wintypes.LONG_PTR = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
wintypes.WPARAM = wintypes.UINT_PTR
wintypes.LPARAM = wintypes.LONG_PTR
wintypes.HCURSOR = wintypes.HANDLE

# ============================================================
# 结构体
# ============================================================
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
# Win32 DLL 加载
# ============================================================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32
shcore = ctypes.windll.shcore
gdi32 = ctypes.windll.gdi32

# 函数原型
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

# CreateWindowExW / RegisterClassExW（必须设 argtypes，否则 64 位 HINSTANCE 会溢出）
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

# GDI 函数（用于绘制托盘图标）
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
# 窗口管理器
# ============================================================
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
# 屏蔽器
# ============================================================
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
# 配置
# ============================================================
class ConfigManager:
    DEFAULT = {
        'move_direction': 'secondary_to_primary',
        'shield_enabled': False,
        'shield_monitor': 2,
        'shield_target': 1,
        'language': 'zh',
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
# HTTP 服务器
# ============================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei UI','Segoe UI',sans-serif;background:#f0f2f5;color:#333;min-height:100vh;display:flex;justify-content:center;padding:20px}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08);width:100%;max-width:420px;padding:24px}
.header-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.lang-toggle{background:none;border:1px solid #1976d2;color:#1976d2;padding:4px 12px;border-radius:4px;font-size:12px;cursor:pointer;transition:all .15s}
.lang-toggle:hover{background:#e3f2fd}
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
  <div class="header-row">
    <h1 style="margin-bottom:0">{heading}</h1>
    <button class="lang-toggle" onclick="switchLang()">{lang_toggle}</button>
  </div>

  <div class="section">
    <div class="section-title">{section_monitor}</div>
    <div class="monitor-list" id="monitorList">{loading}</div>
  </div>

  <div class="section">
    <div class="status-row">
      <span>{direction_label}</span>
      <span id="directionLabel" style="font-weight:600;color:#1976d2">{dir_secondary_to_primary}</span>
    </div>
    <div class="status-row">
      <span>{shield_label}</span>
      <span id="shieldLabel" style="font-weight:600;color:#888">{shield_off}</span>
    </div>
  </div>

  <div class="btn-row">
    <button class="btn btn-primary" onclick="moveWindows()">{btn_move}</button>
    <button class="btn btn-danger" id="shieldBtn" onclick="toggleShield()">{btn_shield_off}</button>
  </div>
  <div class="btn-row">
    <button class="btn btn-outline" onclick="toggleSettings()">{btn_settings}</button>
    <button class="btn btn-outline" onclick="refresh()">{btn_refresh}</button>
  </div>

  <div class="settings-panel" id="settingsPanel">
    <div class="section">
      <div class="section-title">{settings_direction}</div>
      <div class="radio-group">
        <label class="radio-option" id="dirOpt1">
          <input type="radio" name="direction" value="secondary_to_primary" checked>
          <span id="dirOpt1Text">{dir_opt1}</span>
        </label>
        <label class="radio-option" id="dirOpt2">
          <input type="radio" name="direction" value="primary_to_secondary">
          <span id="dirOpt2Text">{dir_opt2}</span>
        </label>
      </div>
    </div>

    <div class="section" style="margin-top:16px">
      <div class="section-title">{settings_shield}</div>
      <div class="checkbox-group">
        <input type="checkbox" id="shieldEnabled">
        <label for="shieldEnabled" id="shieldCheckLabel">{shield_checkbox}</label>
      </div>
      <div class="shield-options" id="shieldOptions">
        <div class="shield-row">
          <select id="shieldMonitor"></select>
          <span class="shield-arrow">→</span>
          <select id="shieldTarget"></select>
        </div>
        <p style="font-size:12px;color:#888;margin-top:8px" id="shieldHintText">{shield_hint}</p>
      </div>
    </div>

    <div class="settings-btns">
      <button class="btn btn-primary" onclick="saveSettings()">{btn_save}</button>
      <button class="btn btn-outline" onclick="toggleSettings()">{btn_cancel}</button>
    </div>
  </div>

  <div class="hk-info">{hk_info}</div>
</div>
<div class="toast" id="toast"></div>

<script>
var I18N = {i18n_json};

function switchLang() {
  var cur = I18N.lang_toggle === 'English' ? 'en' : 'zh';
  window._switchingLang = true;
  fetch('/api/set-language?lang=' + cur).then(function() { location.reload(); });
}

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
    el.innerHTML = '<div class="monitor-item" style="color:#888">' + I18N.no_monitor + '</div>';
    return;
  }
  el.innerHTML = monitors.map(function(m) {
    return '<div class="monitor-item"><span>' + I18N.monitor + ' ' + m.index + ': ' + m.width + 'x' + m.height + '</span>' +
      (m.primary ? '<span class="badge badge-primary">' + I18N.primary + '</span>' : '<span class="badge badge-secondary">' + I18N.secondary + '</span>') +
      '</div>';
  }).join('');
}

function renderDirection(dir) {
  const el = document.getElementById('directionLabel');
  el.textContent = dir === 'secondary_to_primary' ? I18N.dir_secondary_to_primary : I18N.dir_primary_to_secondary;
}

function renderShield(sh) {
  const el = document.getElementById('shieldLabel');
  const btn = document.getElementById('shieldBtn');
  if (sh.active) {
    el.innerHTML = '<span class="status-dot active"></span>' + I18N.shield_on + ' (' + I18N.monitor + sh.shielded + ' \u2192 ' + I18N.monitor + sh.target + ')';
    el.style.color = '#e53935';
    btn.textContent = I18N.btn_shield_on;
    btn.classList.add('active');
  } else {
    el.innerHTML = '<span class="status-dot inactive"></span>' + I18N.shield_off;
    el.style.color = '#888';
    btn.textContent = I18N.btn_shield_off;
    btn.classList.remove('active');
  }
}

function renderSettings(s) {
  document.querySelector('input[name="direction"][value="'+s.direction+'"]').checked = true;
  document.querySelectorAll('.radio-option').forEach(function(o) {
    o.classList.toggle('selected', o.querySelector('input').checked);
  });
  document.getElementById('shieldEnabled').checked = s.shield_enabled;
  document.getElementById('shieldOptions').classList.toggle('show', s.shield_enabled);

  const sm = document.getElementById('shieldMonitor');
  const st = document.getElementById('shieldTarget');
  sm.innerHTML = st.innerHTML = '';
  if (s.monitors) {
    s.monitors.forEach(function(m) {
      var label = I18N.monitor + ' ' + m.index + (m.primary ? ' (' + I18N.primary + ')' : '');
      sm.innerHTML += '<option value="' + m.index + '">' + label + '</option>';
      st.innerHTML += '<option value="' + m.index + '">' + label + '</option>';
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
      showToast(I18N.toast_saved);
      document.getElementById('settingsPanel').classList.remove('show');
      refresh();
    } else {
      showToast(I18N.toast_save_fail + ': ' + (j.error || I18N.toast_unknown_error));
    }
  } catch(e) {
    showToast(I18N.toast_network_error);
  }
}

async function moveWindows() {
  try {
    const r = await fetch(API+'/move');
    const j = await r.json();
    showToast(j.message);
    refresh();
  } catch(e) {
    showToast(I18N.toast_operation_fail);
  }
}

async function toggleShield() {
  try {
    const r = await fetch(API+'/toggle-shield');
    const j = await r.json();
    showToast(j.message);
    refresh();
  } catch(e) {
    showToast(I18N.toast_operation_fail);
  }
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() { t.classList.remove('show'); }, 2000);
}

document.querySelectorAll('input[name="direction"]').forEach(function(r) {
  r.addEventListener('change', function() {
    document.querySelectorAll('.radio-option').forEach(function(o) {
      o.classList.toggle('selected', o.querySelector('input').checked);
    });
  });
});
document.getElementById('shieldEnabled').addEventListener('change', function() {
  document.getElementById('shieldOptions').classList.toggle('show', this.checked);
});
document.querySelectorAll('.radio-option').forEach(function(o) {
  o.addEventListener('click', function(e) {
    if (e.target.tagName !== 'INPUT') {
      this.querySelector('input').click();
    }
  });
});

// heartbeat
setInterval(function() { fetch(API+'/ping').catch(function(){}); }, 5000);

// notify on close
window.addEventListener('beforeunload', function() {
  if (window._switchingLang) return;
  navigator.sendBeacon(API+'/quit');
});

refresh();
</script>
</body>
</html>"""


def get_html(lang='zh'):
    """根据语言生成 HTML 页面"""
    i18n = I18N.get(lang, I18N['zh'])
    page = HTML_PAGE
    for key, val in i18n.items():
        page = page.replace('{' + key + '}', val)
    page = page.replace('{i18n_json}', json.dumps(i18n, ensure_ascii=False))
    page = page.replace('{lang_code}', 'zh-CN' if lang == 'zh' else 'en')
    return page


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
            self._send(200, get_html(self.app.lang), 'text/html')
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
                self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_single_monitor')})
                return
            if cfg['move_direction'] == 'secondary_to_primary':
                primary = next((m for m in monitors if m['primary']), None)
                if not primary:
                    self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_no_primary')})
                    return
                total = 0
                for m in monitors:
                    if not m['primary']:
                        total += len(WindowManager.move_all_from_monitor(m['index'], primary['index']))
                self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_moved_to_primary').format(total=total)})
            else:
                primary = next((m for m in monitors if m['primary']), None)
                if not primary:
                    self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_no_primary')})
                    return
                target = next((m for m in monitors if not m['primary']), None)
                if not target:
                    self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_no_secondary')})
                    return
                moved = WindowManager.move_all_from_monitor(primary['index'], target['index'])
                self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_moved_to_secondary').format(count=len(moved), index=target["index"])})
        elif self.path == '/api/toggle-shield':
            app = self.app
            if app.shield.is_active:
                app.shield.stop()
                app.config['shield_enabled'] = False
                app.config.save()
                self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_shield_off')})
            else:
                monitors = WindowManager.get_monitors()
                if len(monitors) < 2:
                    self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_shield_need_two')})
                    return
                si = app.config['shield_monitor']
                ti = app.config['shield_target']
                if si == ti:
                    self._send(200, {'ok': False, 'message': get_lang_str(self.app.lang, 'msg_shield_same')})
                    return
                app.shield.start(si, ti)
                app.config['shield_enabled'] = True
                app.config.save()
                self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_shield_on').format(si=si, ti=ti)})
        elif self.path.startswith('/api/set-language'):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            lang = qs.get('lang', ['zh'])[0]
            if lang in I18N:
                self.app.lang = lang
                self.app.config['language'] = lang
                self.app.config.save()
            self._send(200, {'ok': True, 'language': self.app.lang})
        elif self.path == '/api/ping':
            self.app.last_heartbeat = time.time()
            self._send(200, {'ok': True, 'ping': 'pong'})
        elif self.path == '/api/quit':
            self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_quitting')})
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
            self._send(200, {'ok': True, 'message': get_lang_str(self.app.lang, 'msg_quitting')})
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
# 托盘 + 热键 消息窗口
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
        nid.szTip = get_lang_str(self.app.lang, 'tray_tip')
        shell32.Shell_NotifyIconW(NIM_ADD, byref(nid))

        user32.RegisterHotKey(self.hwnd, 1, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_M)
        user32.RegisterHotKey(self.hwnd, 2, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_S)

    def _create_tray_icon(self):
        """用 GDI 绘制一个简单的显示器图标"""
        SM_CXSMICON = 49
        SM_CYSMICON = 50
        w = user32.GetSystemMetrics(SM_CXSMICON)
        h = user32.GetSystemMetrics(SM_CYSMICON)

        hdc = user32.GetDC(None)
        mem_dc = gdi32.CreateCompatibleDC(hdc)

        # 创建颜色位图
        bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
        gdi32.SelectObject(mem_dc, bmp)

        # 蓝色背景
        full = RECT(0, 0, w, h)
        brush = gdi32.CreateSolidBrush(0x00D67619)  # BGR = #1976D2
        user32.FillRect(mem_dc, byref(full), brush)
        gdi32.DeleteObject(brush)

        # 白色屏幕区域
        pad = max(2, w // 8)
        sr = RECT(pad, pad, w - pad, h - pad - h // 4)
        brush = gdi32.CreateSolidBrush(0x00FFFFFF)
        user32.FillRect(mem_dc, byref(sr), brush)
        gdi32.DeleteObject(brush)

        # 白色底座
        sw = max(3, w // 4)
        br = RECT(w // 2 - sw // 2, h - pad - h // 4, w // 2 + sw // 2, h - pad)
        brush = gdi32.CreateSolidBrush(0x00FFFFFF)
        user32.FillRect(mem_dc, byref(br), brush)
        gdi32.DeleteObject(brush)

        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(None, hdc)

        # 创建单色 AND 掩码（全白=全不透明）
        mask_bytes = (ctypes.c_ubyte * (((w * h) + 7) // 8))()
        for i in range(len(mask_bytes)):
            mask_bytes[i] = 0xFF
        mask_bmp = gdi32.CreateBitmap(w, h, 1, 1, mask_bytes)

        # 创建图标
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
        lang = self.app.lang
        s = get_lang_str(lang, 'menu_shield_on') if self.app.shield.is_active else get_lang_str(lang, 'menu_shield_off')
        user32.AppendMenuW(menu, MF_STRING, 1, get_lang_str(lang, 'menu_move'))
        user32.AppendMenuW(menu, MF_STRING, 2, s)
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, 3, get_lang_str(lang, 'menu_open'))
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, 4, get_lang_str(lang, 'menu_exit'))
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
# 应用程序
# ============================================================
class App:
    def __init__(self):
        h = kernel32.CreateMutexW(None, False, "Global\\DWM_SingleInstance_v2")
        self.config = ConfigManager()
        self.lang = self.config.get('language', 'zh')
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            user32.MessageBoxW(None, get_lang_str(self.lang, 'msg_already_running'), get_lang_str(self.lang, 'msg_already_running_title'), MB_OK | MB_ICONWARNING)
            sys.exit(0)

        self.shield = DisplayShield()
        self.tray = None
        self.server = None
        self.last_heartbeat = time.time()

    def _heartbeat_checker(self):
        """后台线程：检测心跳超时则自动退出"""
        while True:
            time.sleep(5)
            if time.time() - self.last_heartbeat > 15:
                self.quit()
                return

    def quit(self):
        """安全退出应用"""
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