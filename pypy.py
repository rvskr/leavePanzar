import subprocess
import concurrent.futures
import shutil
import os

dependencies = [
    "pyinstaller", 
    "keyboard",
    "psutil",
    "pyautogui",
    "opencv-python",
    "numpy",
    "pywin32",
    "pyscreeze",
    "Pillow",
]

# Создаем список команд для установки каждого пакета
install_commands = [["pip", "install", dep] for dep in dependencies]

# Запускаем все процессы установки одновременно
processes = [subprocess.Popen(cmd) for cmd in install_commands]

# Дожидаемся завершения каждого процесса
for process in processes:
    process.wait()

print("Все зависимости успешно установлены.")

# Выполняем дополнительные команды параллельно
additional_commands = [
    "pyinstaller --onefile set.py",
    "pyinstaller --onefile pnz.py",
    "pyinstaller --onefile cfg.py"
]

def execute_command(command):
    subprocess.run(command, shell=True, check=True)

# Используем ThreadPoolExecutor для выполнения команд параллельно
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(execute_command, additional_commands)

print("Дополнительные команды выполнены.")

# Определяем пути к папкам, которые нужно скопировать
source_folders = [
    "img",
    "Config by Danze"
]

# Определяем пути к исходной и целевой папкам
source_directory = os.path.dirname(os.path.abspath(__file__))  # Путь к текущей папке скрипта
target_directory = os.path.join(source_directory, "dist")

# Создаем целевую папку, если она не существует
os.makedirs(target_directory, exist_ok=True)

# Копируем папки
for folder in source_folders:
    source_path = os.path.join(source_directory, folder)
    target_path = os.path.join(target_directory, folder)
    try:
        shutil.copytree(source_path, target_path)
    except FileExistsError:
        print(f"Папка {target_path} уже существует.")

print("Папки успешно скопированы.")
