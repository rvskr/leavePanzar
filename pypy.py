import subprocess

dependencies = [
    "keyboard",
    "psutil",
    "pyautogui",
    "opencv-python",
    "numpy",
    "pywin32",
    "pyscreeze",
    "Pillow"
]

# Создаем список команд для установки каждого пакета
install_commands = [["pip", "install", dep] for dep in dependencies]

# Запускаем все процессы установки одновременно
processes = [subprocess.Popen(cmd) for cmd in install_commands]

# Дожидаемся завершения каждого процесса
for process in processes:
    process.wait()

print("Все зависимости успешно установлены.")
