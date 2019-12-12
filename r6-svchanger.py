import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as msgbox
import os
import subprocess

USER_DIR = os.path.expanduser('~')
R6_DIR = USER_DIR + '\\Documents\\My Games\\Rainbow Six - Siege'

for root, dirs, files in os.walk(R6_DIR):
    if 'GameSettings.ini' in files:
        R6_INI = root + '\\GameSettings.ini'
        R6_INI_ALT = root + '\\GameSettings_.ini'

sv_dict = {
    'default': 'Ping based (Auto) - default',
    'eus':     'US East - eus',
    'cus':     'US Central - cus',
    'scus':    'US South Central - scus',
    'wus':     'US West - wus',
    'sbr':     'Brazil South - sbr',
    'neu':     'Europe North - neu',
    'weu':     'Europe West - weu',
    'eas':     'Asia East - eas',
    'seas':    'Asia South East - seas',
    'eau':     'Australia East - eau',
    'wja':     'Japan West - wja'
}


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
    print('Target server is' , target)

    with open(R6_INI, 'r') as f:
        ini = f.readlines()

    for index, line in enumerate(ini):
        if 'DataCenterHint=' in line:
            ini[index] = f'DataCenterHint={target}\n'

    with open(R6_INI, 'w') as f:
        for line in ini:
            f.write(line)

    if get_current() != target:
        msgbox.showerror('Error', 'Failed to change server')

    current.set('Current server: ' + sv_dict[get_current()].split(' - ')[0])
    main.update()


def open_r6_steam():
    try:
        print('Launching Steam...')
        subprocess.run("start steam://rungameid/359550",
                       shell=True, check=True)
    except subprocess.CalledProcessError:
        pass


main = tk.Tk()
main.title("R6S Server")
main.geometry("250x140+600+250")
main.resizable(False, False)

current = tk.StringVar()
try:
    current.set('Current server: ' + sv_dict[get_current()].split(' - ')[0])
except KeyError:
    current.set('Current server: Unknown or Invalid')

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
button_frame.pack(side='bottom', pady=(3, 6))

exit_button = ttk.Button(button_frame, text='Exit', width=5)
exit_button['command'] = main.destroy
exit_button.pack(side='left', padx=3)

button_steam = ttk.Button(button_frame, text='Open R6 and Exit (Steam only)')
button_steam['command'] = open_r6_steam
button_steam.pack(side='right', padx=3)

change_button = ttk.Button(main, text='Change')
change_button['command'] = change
change_button.pack(side='bottom', padx=11, pady=3, fill='x')

main.mainloop()
