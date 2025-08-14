# -*- coding: utf-8 -*-
"""
IR Auto Proxy (Duck, Tray) v3
- آیکون اردک بامزه در سینی سیستم و پنجره اصلی
- انتخاب حالت: فقط Chrome یا کل ویندوز
- تست همه پروکسی‌ها قبل از اعمال
- اعلان در صورت عدم اتصال به هیچ پروکسی
- پایش اتصال و تعویض خودکار
"""
import tkinter as tk
from tkinter import messagebox
import threading, time, os, subprocess, base64
from io import BytesIO

import requests
from PIL import Image, ImageTk
import pystray
from win10toast import ToastNotifier
import winreg
from ctypes import windll, c_void_p

# منابعی که گفتی در ایران بازند
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]

CHECK_URLS = ["http://www.gstatic.com/generate_204", "https://api.ipify.org?format=json"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"

TIMEOUT = 6
MONITOR_INTERVAL = 25
ROTATE_AFTER_FAILS = 2

# آیکون اردک به‌صورت base64 (PNG)
DUCK_B64 = "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"

toaster = ToastNotifier()

current_mode = None   # 'windows' یا 'chrome'
current_proxy = None
stop_flag = False
tray_icon = None

def notify(title, msg):
    try:
        toaster.show_toast(title, msg, duration=5, threaded=True)
    except Exception:
        pass

def duck_image_pil():
    data = base64.b64decode(DUCK_B64)
    return Image.open(BytesIO(data))

def duck_image_tk():
    data = base64.b64decode(DUCK_B64)
    return ImageTk.PhotoImage(Image.open(BytesIO(data)))

def fetch_proxies():
    seen = set()
    out = []
    headers = {"User-Agent": UA}
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=headers)
            if r.ok:
                for ln in r.text.splitlines():
                    ln = ln.strip()
                    if ":" in ln and 7 <= len(ln) <= 25 and ln.count(":") == 1:
                        if ln not in seen:
                            seen.add(ln); out.append(ln)
        except Exception:
            pass
    return out

def test_proxy(proxy):
    headers = {"User-Agent": UA}
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    for url in CHECK_URLS:
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=headers, proxies=proxies)
            # generate_204 returns 204; ipify returns 200
            if r.status_code in (200, 204):
                return True
        except Exception:
            continue
    return False

def set_system_proxy(proxy):
    key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, "ProxyServer", 0, winreg.REG_SZ, f"http={proxy};https={proxy}")
        winreg.SetValueEx(k, "ProxyOverride", 0, winreg.REG_SZ, "")
    windll.Wininet.InternetSetOptionW(0, 39, c_void_p(), 0)
    windll.Wininet.InternetSetOptionW(0, 37, c_void_p(), 0)

def disable_system_proxy():
    key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(k, "ProxyServer", 0, winreg.REG_SZ, "")
    windll.Wininet.InternetSetOptionW(0, 39, c_void_p(), 0)
    windll.Wininet.InternetSetOptionW(0, 37, c_void_p(), 0)

def start_chrome_with_proxy(proxy):
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    exe = None
    for c in candidates:
        if os.path.exists(c):
            exe = c; break
    if not exe:
        messagebox.showerror("Chrome not found", "فایل اجرایی Chrome پیدا نشد.")
        return False
    subprocess.Popen([exe, f"--proxy-server=http://{proxy}"])
    return True

def pick_and_apply(mode):
    # همه پروکسی‌ها قبل از اعمال تست می‌شن
    proxies = fetch_proxies()
    if not proxies:
        notify("Proxy", "هیچ لیست پروکسی در دسترس نیست.")
        return None

    for proxy in proxies[:800]:
        if test_proxy(proxy):
            if mode == "windows":
                try:
                    set_system_proxy(proxy)
                    notify("Proxy Connected", f"Windows proxy set: {proxy}")
                except Exception:
                    continue
            else:  # chrome
                if not start_chrome_with_proxy(proxy):
                    continue
                notify("Proxy Connected", f"Chrome launched with: {proxy}")
            return proxy

    # اگر هیچ‌کدام وصل نشد
    notify("Proxy Failed", "هیچ پروکسی فعالی پیدا نشد.")
    return None

def monitor_loop():
    global current_proxy
    fails = 0
    while not stop_flag:
        ok = False
        if current_proxy:
            headers = {"User-Agent": UA}
            proxies = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"}
            for url in CHECK_URLS:
                try:
                    r = requests.get(url, timeout=TIMEOUT, headers=headers, proxies=proxies)
                    if r.status_code in (200, 204):
                        ok = True; break
                except Exception:
                    continue
        if ok:
            fails = 0
        else:
            fails += 1

        if fails >= ROTATE_AFTER_FAILS:
            newp = pick_and_apply(current_mode)
            if newp:
                current_proxy = newp; fails = 0
        time.sleep(MONITOR_INTERVAL)

# ---------- Tray ----------
def tray_show(icon, item):
    try: root.after(0, root.deiconify)
    except: pass

def tray_disable(icon, item):
    try:
        disable_system_proxy()
        notify("Proxy", "System proxy disabled.")
    except: pass

def tray_exit(icon, item):
    global stop_flag
    stop_flag = True
    try: icon.stop()
    except: pass
    try: root.after(0, root.destroy)
    except: pass

def start_tray():
    image = duck_image_pil()
    menu = pystray.Menu(
        pystray.MenuItem("Show", tray_show),
        pystray.MenuItem("Disable System Proxy", tray_disable),
        pystray.MenuItem("Exit", tray_exit),
    )
    icon = pystray.Icon("IRProxyDuck", image, "IR Proxy (Duck)", menu)
    threading.Thread(target=icon.run, daemon=True).start()

# ---------- UI ----------
def start_mode(selected):
    global current_mode, current_proxy, stop_flag
    current_mode = selected
    root.withdraw()
    notify("Proxy Manager", "شروع فرآیند پیدا کردن پروکسی...")
    def runner():
        global current_proxy
        current_proxy = pick_and_apply(selected)
        if current_proxy:
            threading.Thread(target=monitor_loop, daemon=True).start()
    threading.Thread(target=runner, daemon=True).start()

root = tk.Tk()
root.title("IR Auto Proxy (Duck)")
root.geometry("380x220"); root.resizable(False, False)

# آیکون اردک برای پنجره
try:
    duck_tk = duck_image_tk()
    root.iconphoto(True, duck_tk)
except Exception:
    pass

title = tk.Label(root, text="انتخاب حالت اعمال پروکسی", font=("Segoe UI", 11, "bold"))
title.pack(pady=10)

img_label = tk.Label(root, image=duck_tk)
img_label.pack(pady=2)

btn1 = tk.Button(root, text="فقط Chrome", width=28, height=2, command=lambda: start_mode('chrome'))
btn1.pack(pady=6)

btn2 = tk.Button(root, text="کل ویندوز (System-wide)", width=28, height=2, command=lambda: start_mode('windows'))
btn2.pack(pady=6)

hint = tk.Label(root, text="پس از شروع، برنامه به سینی سیستم می‌رود. آیکون اردک کنار ساعت.", font=("Segoe UI", 9))
hint.pack(pady=6)

root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())
start_tray()
root.mainloop()
