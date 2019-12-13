import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as msgbox
import os
import sys
import subprocess
import requests
import threading

URL = 'https://raw.githubusercontent.com/sw2719/R6S-server-changer/master/server_list_ko.txt'  # NOQA
USER_DIR = os.path.expanduser('~')
R6_DIR = USER_DIR + '\\Documents\\My Games\\Rainbow Six - Siege'

for root, dirs, files in os.walk(R6_DIR):
    if 'GameSettings.ini' in files:
        R6_INI = root + '\\GameSettings.ini'

try:
    with open('server_list_ko.txt', 'r', encoding='utf-8') as f:
        raw = f.read()
except (OSError, FileNotFoundError):
    open('server_list_ko.txt', 'w', encoding='utf-8').close()
    raw = ''


def checkupdate():
    def get_sv_list():
        global raw
        try:
            response = requests.get(URL)
            response.encoding = 'utf-8'
            sv_raw = response.text
            if raw != sv_raw:
                if msgbox.askyesno('정보',
                                   '새 서버목록이 있습니다.\n'
                                   '지금 다운로드 하시겠습니까?'):
                    with open('server_list_ko.txt', 'w', encoding='utf-8') as f:  # NOQA
                        f.write(sv_raw)
                    if getattr(sys, 'frozen', False):
                        os.execv('R6 Server Changer KOR.exe', sys.argv)
                    else:
                        msgbox.showinfo('완료',
                                        '변경 사항을 적용하려면 재시작하세요.')
        except requests.RequestException:
            msgbox.showerror('오류',
                             '다운로드 중 오류가 발생했습니다.')
    t = threading.Thread(target=get_sv_list)
    t.start()


sv_dict = {}

for line in raw.splitlines():
    buf = line.split('=')
    sv_dict[buf[0]] = buf[1]

try:
    del buf
except Exception:
    pass


def get_current():
    with open(R6_INI, 'r') as f:
        ini = f.readlines()

    for line in ini:
        if 'DataCenterHint=' in line:
            value = line.strip().split('=')[1]
            return value


def change():
    index = server_cbox.current()
    target = tuple(sv_dict.keys())[index]
    print('Target server is', target)

    with open(R6_INI, 'r') as f:
        ini = f.readlines()

    for index, line in enumerate(ini):
        if 'DataCenterHint=' in line:
            ini[index] = f'DataCenterHint={target}\n'

    with open(R6_INI, 'w') as f:
        for line in ini:
            f.write(line)

    if get_current() != target:
        msgbox.showerror('오류', '서버를 변경하는데 실패했습니다')

    current.set('현재 서버: ' + sv_dict[get_current()].split(' - ')[0])
    main.update()


def open_r6_steam():
    try:
        print('Launching Steam...')
        subprocess.run("start steam://rungameid/359550",
                       shell=True, check=True)
        main.destroy()
    except subprocess.CalledProcessError:
        msgbox.showwarning('오류', '게임을 실행할 수 없습니다')
        pass


main = tk.Tk()
main.title("")
main.geometry("210x160+600+250")
main.resizable(False, False)

current = tk.StringVar()
try:
    current.set('현재 서버: ' + sv_dict[get_current()].split(' - ')[0])
except KeyError:
    current.set('현재 서버: 알 수 없음')

current_label = tk.Label(main, textvariable=current)
current_label.pack(side='top', anchor='w', padx=11, pady=(9, 0))

server_cbox = ttk.Combobox(main,
                           state="readonly",
                           values=list(sv_dict.values()),
                           width=30,
                           height=12)
try:
    server_cbox.set(sv_dict[get_current()])
except KeyError:
    pass
server_cbox.pack(side='top', anchor='center', padx=11, pady=(11, 1))

button_frame = tk.Frame(main)
button_frame.pack(side='bottom', padx=25, pady=(3, 6))

exit_button = ttk.Button(button_frame, text='나가기', width=8)
exit_button['command'] = main.destroy
exit_button.pack(side='left', padx=(0, 3))

change_button = ttk.Button(button_frame, text='변경', width=12)
change_button['command'] = change
change_button.pack(side='right', padx=(3, 0))

open_r6_steam_button = ttk.Button(main, text='게임 실행 (Steam)', width=22)  # NOQA
open_r6_steam_button['command'] = open_r6_steam
open_r6_steam_button.pack(side='bottom', padx=25, pady=3)

main.after(100, checkupdate)
main.mainloop()
