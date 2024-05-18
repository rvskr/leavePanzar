import os
import sys
import subprocess
import psutil
import shutil
import tkinter as tk
from tkinter import filedialog

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.panzar_folder = None
        self.script1_path = None
        self.script2_path = None
        self.image_folder = None
        self.config_folder = None

    def set_panzar_folder(self, panzar_folder):
        self.panzar_folder = os.path.abspath(panzar_folder)
        self.script1_path = os.path.join(self.panzar_folder, "start.exe")
        self.script2_path = os.path.join(os.path.dirname(sys.executable), "pnz.exe")
        self.image_folder = os.path.join(os.path.dirname(sys.executable), "img")
        self.config_folder = os.path.join(self.panzar_folder, "USER")
        self.generate_config_file()
        if not self.is_set_exe_running():
            self.run_set_exe()
        self.copy_config_folder(self.config_folder)

    def generate_config_file(self):
        with open(self.config_file, 'w') as f:
            f.write("[Paths]\n")
            f.write(f"script1_path = \"{self.script1_path}\"\n")
            f.write(f"script2_path = \"{self.script2_path}\"\n")
            f.write(f"image_folder = \"{self.image_folder}\"\n")
            f.write(f"config_folder = \"{self.config_folder}\"\n")
            f.write(f"panzar_folder = \"{self.panzar_folder}\"")

    def run_set_exe(self):
        subprocess.Popen(["set.exe"])

    def is_set_exe_running(self):
        for process in psutil.process_iter(['pid', 'name']):
            if process.name() == "set.exe":
                return True
        return False

    def copy_config_folder(self, destination_folder):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        source_folder = os.path.join(current_dir, "Config by Danze")
        destination_folder = os.path.join(destination_folder, "Config by Danze")

        try:
            if not os.path.exists(destination_folder):
                shutil.copytree(source_folder, destination_folder)
                print("Папка успешно скопирована!")
            else:
                print("Папка уже существует, копирование не выполнено.")
        except shutil.Error as e:
            print(f"Ошибка при копировании папки: {e}")

class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Генератор конфигурационного файла")
        self.config_manager = ConfigManager("config.ini")

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=10, pady=10)

        lbl_panzar_folder = tk.Label(frame, text="Укажите папку Panzar:")
        lbl_panzar_folder.grid(row=0, column=0, sticky="w")

        self.entry_panzar_folder = tk.Entry(frame, width=50)
        self.entry_panzar_folder.grid(row=0, column=1, padx=5, pady=5)

        btn_browse_panzar_folder = tk.Button(frame, text="Обзор", command=self.select_panzar_folder)
        btn_browse_panzar_folder.grid(row=0, column=2, padx=5, pady=5)

        btn_generate = tk.Button(frame, text="Создать файл конфигурации", command=self.generate_config_and_run)
        btn_generate.grid(row=1, column=0, columnspan=3, pady=10)

        self.lbl_status = tk.Label(frame, text="")
        self.lbl_status.grid(row=2, column=0, columnspan=3)

    def select_panzar_folder(self):
        panzar_folder = filedialog.askdirectory()
        if panzar_folder:
            self.entry_panzar_folder.delete(0, tk.END)
            self.entry_panzar_folder.insert(0, panzar_folder)

    def generate_config_and_run(self):
        panzar_folder = self.entry_panzar_folder.get()
        if panzar_folder:
            self.config_manager.set_panzar_folder(panzar_folder)
            self.lbl_status.config(text="Конфигурационный файл обновлен успешно!")
            self.master.destroy()  # Закрываем главное окно после выполнения
        else:
            self.lbl_status.config(text="Не указана папка Panzar!")

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
