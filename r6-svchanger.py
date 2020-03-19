import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox as msgbox
import os
import sys
import subprocess
import requests
import threading
import locale
import gettext
from ruamel.yaml import YAML
from packaging import version

VERSION = '1.1'
LOCALE = locale.getdefaultlocale()[0]

yaml = YAML()

t = gettext.translation('r6_switcher',
                        localedir='locale',
                        languages=[LOCALE],
                        fallback=True)
_ = t.gettext

main = tk.Tk()
main.title("")
main.geometry("210x190+600+250")
main.resizable(False, False)

LIST_URL = 'https://raw.githubusercontent.com/sw2719/R6S-server-changer/master/server_list.yml'
VERSION_URL = 'https://raw.githubusercontent.com/sw2719/R6S-server-changer/master/version.yml'

doc_dir = os.path.expanduser('~')
r6_dir = doc_dir + '\\Documents\\My Games\\Rainbow Six - Siege'

if not os.path.isdir(r6_dir):
    if not os.path.isfile('doc_path.txt'):
        while True:
            msgbox.showwarning(_('Warning'),
                               _('Could not locate GameSettings.ini automatically.') + '\n' +
                               _("Select 'Documents' folder in the following dialog to continue."))
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
    with open('server_list.yml', 'r', encoding='utf-8') as f:
        local_raw = f.read()
except OSError:
    open('server_list.yml', 'w').close()
    local_raw = ''


def checkupdate():
    def get_update():
        global local_raw
        try:
            v_response = requests.get(VERSION_URL)
            response = requests.get(LIST_URL)

            v_response.raise_for_status()
            response.raise_for_status()

            sv_version = yaml.load(v_response.text)['version']

            if version.parse(VERSION) < version.parse(sv_version):
                msgbox.showinfo(_('Update available'), _('Please download new version from GitHub') + '\n' +
                                _('to continue using this program.'))

                os.startfile('https://github.com/sw2719/R6S-server-changer/releases')
                os._exit(0)
            else:
                print('New version check completed.')

            response.encoding = 'utf-8'
            sv_raw = response.text
            if local_raw != sv_raw and sv_raw:
                if msgbox.askyesno(_('Info'),
                                   _('New server list is available.') + '\n' +
                                   _('Download it now?')):
                    try:
                        with open('server_list.yml', 'w', encoding='utf-8') as f:
                            f.write(sv_raw)
                        if getattr(sys, 'frozen', False):
                            os.execv('R6 Server Changer.exe', sys.argv)
                        else:
                            msgbox.showinfo(_('Done'),
                                            _('Restart to apply changes.'))
                    except requests.RequestException:
                        msgbox.showerror(_('Error'),
                                         _('An error occured while downloading.'))
                else:
                    msgbox.showwarning(_('Warning'), _('You chose not to download new server list.') + '\n' +
                                       _('Server changer might not work.'))
            else:
                print('Server list update check completed.')
        except requests.RequestException:
            msgbox.showerror(_('Error'),
                             _('An error occured while checking for new server list.'))
    t = threading.Thread(target=get_update)
    t.start()


local_yml = yaml.load(local_raw)

try:
    if LOCALE == 'ko_KR':
        sv_dict = local_yml['ko']
    else:
        sv_dict = local_yml['en']
except TypeError:
    sv_dict = {}


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
        return 'N/A'


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
        msgbox.showerror(_('Error'), _('Failed to change server.'))

    current.set(_('Current server: ') + sv_dict[get_current()].split(' - ')[0])
    main.update()


def open_r6_steam():
    subprocess.run("start steam://rungameid/359550",
                   shell=True, check=True)
    main.destroy()


def open_r6_uplay():
    subprocess.run("start uplay://launch/635/0",
                   shell=True, check=True)
    main.destroy()


def sv_different_warning():
    msgbox.showinfo(_('Info'), _('It looks like you have more than one account') + '\n' +
                    _('and they are set to different servers.') + '\n\n' +
                    _("Change server and all accounts' server will be set to the selected one."))


current = tk.StringVar()
try:
    if not get_current() == 'N/A':
        current.set(_('Current server: ') + sv_dict[get_current()].split(' - ')[0])
    else:
        main.after(50, sv_different_warning)
        current.set(_('Current server: N/A'))
except KeyError:
    current.set(_('Current server: Unknown or Invalid'))

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

acc_label = tk.Label(main, text=_('%s accounts detected') % len(r6_ini))
acc_label.pack(pady=(5, 0))

button_frame = tk.Frame(main)
button_frame.pack(side='bottom', padx=25, pady=(3, 6))

exit_button = ttk.Button(button_frame, text=_('Exit'), width=8)
exit_button['command'] = main.destroy
exit_button.pack(side='left', padx=(0, 3))

change_button = ttk.Button(button_frame, text=_('Change'), width=12)
change_button['command'] = change
change_button.pack(side='right', padx=(3, 0))

open_r6_steam_button = ttk.Button(main, text=_('Launch R6S (Steam)'), width=22)  # NOQA
open_r6_steam_button['command'] = open_r6_steam
open_r6_steam_button.pack(side='bottom', padx=25, pady=3)

open_r6_uplay_button = ttk.Button(main, text=_('Launch R6S (Uplay)'), width=22)  # NOQA
open_r6_uplay_button['command'] = open_r6_uplay
open_r6_uplay_button.pack(side='bottom', padx=25, pady=3)

main.after(100, checkupdate)
main.mainloop()
