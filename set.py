import tkinter as tk
import keyboard
import subprocess
import psutil
import os
import ctypes
import configparser
import sys  

config_file = 'config.ini'

class TimerApp:
    def __init__(self):
        self.default_time = 15 * 60
        self.remaining_time = self.default_time
        self.running = True
        self.cfg_executed = False

        self.setup_gui()
        self.setup_hotkeys()
        self.start_timer()

        # Выводим описание кнопок
        self.print_key_descriptions()

    def read_config(self):
        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            if 'Paths' in config and 'script1_path' in config['Paths']:
                self.script1_path = config['Paths']['script1_path'].replace("\\", "\\\\")  # Заменяем одинарные обратные слеши на двойные
            else:
                print("Ошибка: Отсутствует секция 'Paths' или ключ 'script1_path' в файле конфигурации.")
                self.start_cfg_exe()  # Запуск cfg.exe в случае отсутствия нужных данных в конфигурации
        else:
            print(f"Ошибка: Файл конфигурации '{config_file}' не найден.")
            self.start_cfg_exe()  # Запуск cfg.exe в случае отсутствия файла конфигурации
            sys.exit()

    def start_cfg_exe(self):
        try:
            # Пытаемся запустить cfg.exe
            subprocess.Popen(["cfg.exe"])
            print("Запущен cfg.exe")
        except FileNotFoundError:
            # Если файл не найден, выводим сообщение об ошибке
            print("Ошибка: Файл cfg.exe не найден.")
            sys.exit()  # Завершаем выполнение скрипта в случае ошибки

    # Остальной код остается без изменений...


    def setup_gui(self):
        self.read_config()
        self.root = tk.Tk()
        self.root.attributes("-transparentcolor", "white")
        self.root.overrideredirect(True)  # Убираем рамки окна
        self.root.attributes("-topmost", True)
        self.root.bind("<Button-1>", self.on_click)
        self.label = tk.Label(self.root, text="", font=("Helvetica", 30), bg="white", fg="#aaaaaa", bd=2)  # Светло-серый цвет текста
        self.label.pack(expand=True)

        # Устанавливаем прозрачность окна
        self.set_window_transparency()

    def set_window_transparency(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00000020)  # WS_EX_LAYERED
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(255 * 0.8), 0x2)  # 80% прозрачность

    def setup_hotkeys(self):
        keyboard.on_press(self.on_key_press)

    def start_timer(self):
        self.remaining_time = self.default_time
        self.update_display()
        self.root.after(1000, self.timer_tick)

    def timer_tick(self):
        if self.running:
            self.remaining_time -= 1
            self.update_display()
            
            if self.remaining_time <= 1:
                self.remaining_time = self.default_time
                self.close_process_via_task_manager("pnzcl.exe")  # Закрыть процесс pnzcl.exe
                self.close_process_via_task_manager("pnz.exe")
                self.start_panzar()
                self.start_pnz_exe()
        
        if self.running:
            self.root.after(1000, self.timer_tick)

    def update_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.label.config(text="{:02d}:{:02d}".format(minutes, seconds))

    def on_key_press(self, event):
        key = event.name
        if key == '+':
            self.remaining_time += 10
            self.update_display()
            print("Добавлено 10 секунд")
        elif key == '-':
            self.remaining_time = max(0, self.remaining_time - 10)
            self.update_display()
            print("Убрано 10 секунд")
        elif key == '*':
            self.remaining_time = self.default_time
            self.update_display()
            print("Таймер сброшен")
        elif key == '/':
            self.remaining_time = 1
            self.update_display()
            print("Успех")
            self.close_process_via_task_manager("pnzcl.exe")
            self.close_process_via_task_manager("pnz.exe")  
            self.start_panzar()
            self.start_pnz_exe()
        elif key == 'home':
            self.close_processes_in_order()
            print("Все процессы закрыты")


    def close_process_via_task_manager(self, process_name):
        os.system(f"taskkill /F /IM {process_name}")

    def close_processes_in_order(self):
        processes = ["pnz.exe", "cfg.exe", "set.exe"]
        for process_name in processes:
            self.close_process_via_task_manager(process_name)

    def is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def start_pnz_exe(self):
        try:
            # Пытаемся запустить pnz.exe
            subprocess.Popen(["pnz.exe"])
            print("Запущен pnz.exe")
        except FileNotFoundError:
            # Если файл не найден, выводим сообщение об ошибке
            print("Ошибка: Файл pnz.exe не найден.")

    def start_panzar(self):
        try:
            # Пытаемся запустить start.exe
            config = configparser.ConfigParser()
            config.read('config.ini')
            script1_path = config.get('Paths', 'script1_path')
            subprocess.Popen(script1_path)
            print("Запущено приложение Panzar")
        except FileNotFoundError:
            # Если файл не найден, выводим сообщение об ошибке
            print("Ошибка: Файл start.exe не найден.")

    def on_click(self, event):
        pass

    def print_key_descriptions(self):
        print("Описание кнопок:")
        print("+: Добавить 10 секунд")
        print("-: Убрать 10 секунд")
        print("*: Сбросить таймер")
        print("/: Нажмите для старта/перезагрузки Panzar")
        print("Home:Закрыть все процессы")

if __name__ == "__main__":
    TimerApp().root.mainloop()
