import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox as msgbox
import os
import sys
import subprocess
import requests
import threading

main = tk.Tk()
main.title("")
main.geometry("210x160+600+250")
main.resizable(False, False)

URL = 'https://raw.githubusercontent.com/sw2719/R6S-server-changer/master/server_list_ko.txt'

doc_dir = os.path.expanduser('~')
r6_dir = doc_dir + '\\Documents\\My Games\\Rainbow Six - Siege'

if not os.path.isdir(r6_dir):
    if not os.path.isfile('doc_path.txt'):
        while True:
            msgbox.showwarning('경고',
                               '자동으로 GameSettings.ini를 감지할 수 없습니다.\n' +
                               "표시되는 대화 상자에서 '내 문서'를 선택하십시오.")
            path = filedialog.askopenfile().name
            if os.path.isdir(path + '\\My Games\\Rainbow Six - Siege'):
                with open('doc_path.txt', 'w') as f:
                    f.write(path)
                r6_dir = path + '\\My Games\\Rainbow Six - Siege'
                break
    else:
        with open('doc_path.txt', 'r') as f:
            doc_dir = f.read().strip()
            r6_dir = doc_dir + '\\My Games\\Rainbow Six - Siege'

r6_ini = []

for root, dirs, files in os.walk(r6_dir):
    if 'GameSettings.ini' in files:
        r6_ini.append(root + '\\GameSettings.ini')


try:
    with open('server_list_ko.txt', 'r', encoding='utf-8') as f:
        local_raw = f.read()
except OSError:
    open('server_list_ko.txt', 'w', encoding='utf-8').close()
    local_raw = ''


def checkupdate():
    def get_sv_list():
        global local_raw
        try:
            response = requests.get(URL)
            response.encoding = 'utf-8'
            sv_raw = response.text
            if local_raw != sv_raw:
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
            else:
                print('Server list update check completed.')
        except requests.RequestException:
            msgbox.showerror('오류',
                             '다운로드 중 오류가 발생했습니다.')
    t = threading.Thread(target=get_sv_list)
    t.start()


sv_dict = {}

for line in local_raw.splitlines():
    buf = line.split('=')
    sv_dict[buf[0]] = buf[1]

try:
    del buf
except Exception:
    pass


def get_current():
    region_list = []

    for ini in r6_ini:
        with open(ini, 'r') as f:
            ini = f.readlines()

        for line in ini:
            if 'DataCenterHint=' in line:
                value = line.strip().split('=')[1]
                region_list.append(value)
    if(len(set(region_list)) == 1):
        return region_list[0]
    else:
        return 0


def change():
    index = server_cbox.current()
    target = tuple(sv_dict.keys())[index]
    print('Target server is', target)

    for ini_file in r6_ini:
        with open(ini_file, 'r') as f:
            ini = f.readlines()

        for index, line in enumerate(ini):
            if 'DataCenterHint=' in line:
                ini[index] = f'DataCenterHint={target}\n'

        with open(ini_file, 'w') as f:
            for line in ini:
                f.write(line)

    if get_current() != target:
        msgbox.showerror('오류', '서버를 변경하는데 실패했습니다.')

    current.set('현재 서버: ' + sv_dict[get_current()].split(' - ')[0])
    main.update()


def open_r6_steam():
    try:
        subprocess.run("start steam://rungameid/359550",
                       shell=True, check=True)
        main.destroy()
    except subprocess.CalledProcessError:
        msgbox.showwarning('오류', '게임을 시작할 수 없습니다.')
        pass


def sv_different_error():
    msgbox.showwarning('경고', '다수의 계정을 감지했으며,' + '\n' +
                       '각각 설정된 서버가 다릅니다.' + '\n\n' +
                       "서버를 변경하면 자동으로 모든 계정의 설정이 변경됩니다.")


current = tk.StringVar()
try:
    if not get_current() == 0:
        current.set('현재 서버: ' + sv_dict[get_current()].split(' - ')[0])
    else:
        main.after(50, sv_different_error)
        current.set('현재 서버: 표시할 수 없음')
except KeyError:
    current.set('현재 서버: 가져올 수 없음')

current_label = tk.Label(main, textvariable=current)
current_label.pack(side='top', anchor='w', padx=11, pady=(9, 0))

server_cbox = ttk.Combobox(main,
                           state="readonly",
                           values=list(sv_dict.values()),
                           width=30,
                           height=len(sv_dict))
try:
    server_cbox.set(sv_dict[get_current()])
except KeyError:
    pass
server_cbox.pack(side='top', anchor='center', padx=11, pady=(11, 1))

acc_label = tk.Label(main, text='%s개의 계정이 감지됨' % len(r6_ini))
acc_label.pack(pady=(5, 0))

button_frame = tk.Frame(main)
button_frame.pack(side='bottom', padx=25, pady=(3, 6))

exit_button = ttk.Button(button_frame, text='나가기', width=8)
exit_button['command'] = main.destroy
exit_button.pack(side='left', padx=(0, 3))

change_button = ttk.Button(button_frame, text='변경', width=12)
change_button['command'] = change
change_button.pack(side='right', padx=(3, 0))

open_r6_steam_button = ttk.Button(main, text='게임 실행 (Steam 전용)', width=22)  # NOQA
open_r6_steam_button['command'] = open_r6_steam
open_r6_steam_button.pack(side='bottom', padx=25, pady=3)

main.after(100, checkupdate)
main.mainloop()
