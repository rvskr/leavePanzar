import ctypes
import ctypes.wintypes
import time
import pyautogui
import os
import shutil
import cv2
import numpy as np
import psutil
import win32gui
import subprocess
import sys

# Функция для проверки, является ли окно Panzar активным
def is_panzar_active():
    hwnd = win32gui.FindWindow(None, "Panzar")
    if hwnd:
        return win32gui.GetForegroundWindow() == hwnd
    else:
        return False

# Функция для клика по кнопке без перемещения курсора
def click_button(button_location):
    # Получаем хэндл окна под курсором
    button_x, button_y = int(button_location[0]), int(button_location[1])
    hwnd = ctypes.windll.user32.WindowFromPoint(ctypes.wintypes.POINT(button_x, button_y))
    # Проверяем, активно ли окно Panzar
    if not is_panzar_active():
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    # Получаем координаты окна
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    # Переводим координаты клика в координаты окна
    button_x, button_y = button_x - rect.left, button_y - rect.top
    # Отправляем сообщение о нажатии и отпускании кнопки
    ctypes.windll.user32.SendMessageW(hwnd, 0x201, 1, button_x + button_y * 0x10000)
    ctypes.windll.user32.SendMessageW(hwnd, 0x202, 0, button_x + button_y * 0x10000)
    print(f"Клик по кнопке: {button_location}")

# Функция для проверки, запущено ли окно Panzar
def is_panzar_running():
    return "start.exe" in (p.name().lower() for p in psutil.process_iter())

# Функция для запуска Panzar
def start_panzar(script1_path):
    subprocess.Popen(script1_path, shell=True)
    print("Запущено приложение Panzar")

# Функция для копирования папки
def copy_folder(source, destination):
    destination = os.path.join(destination, os.path.basename(source))
    
    try:
        shutil.copytree(source, destination)
        print(f"Папка {source} успешно скопирована в {destination}")
    except FileExistsError:
        print(f"Папка {destination} уже существует. Заменяем дублирующие файлы.")

        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)

            if os.path.isdir(s):
                copy_folder(s, d)
            else:
                if os.path.exists(d):
                    os.remove(d)
                shutil.copy2(s, d)
                print(f"Файл {s} успешно скопирован в {d}")

# Функция для поиска изображения на экране с учетом порогового значения сходства
def find_image_on_screen(image_path, threshold=0.9):
    # Загружаем изображение
    template = cv2.imread(image_path, 0)
    w, h = template.shape[::-1]

    # Получаем скриншот экрана
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Находим изображение на скриншоте
    res = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        return (loc[1][0] + w // 2, loc[0][0] + h // 2)  # Возвращаем центр первого найденного изображения
    else:
        return None

# Функция для поиска изображения на экране с учетом цветового диапазона
def find_image_on_screen_with_color(image_path, threshold=0.9):
    # Загружаем изображение
    template = cv2.imread(image_path)
    h, w = template.shape[:-1]

    # Получаем скриншот экрана
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Преобразуем изображение и шаблон в цветовое пространство HSV
    screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)

    # Определяем оранжевый цвет в HSV
    lower_orange = np.array([0, 100, 100])
    upper_orange = np.array([20, 255, 255])

    # Находим    # оранжевую кнопку на скриншоте
    mask = cv2.inRange(screenshot_hsv, lower_orange, upper_orange)
    res = cv2.matchTemplate(mask, cv2.cvtColor(template_hsv, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        return (loc[1][0] + w // 2, loc[0][0] + h // 2)  # Возвращаем центр первого найденного изображения
    else:
        return None

def find_and_click_all(config_file):
    button3_found = False
    
    # Загружаем данные из конфигурационного файла
    with open(config_file, "r") as f:
        lines = f.readlines()
        script1_path = None
        for line in lines:
            if line.strip().startswith("script1_path"):
                script1_path = line.strip().split("=")[1].strip().replace("\\", "/").strip('"')
                break
        
        script2_path = None
        for line in lines:
            if line.strip().startswith("script2_path"):
                script2_path = line.strip().split("=")[1].strip().replace("\\", "/").strip('"')
                break

        image_folder = None
        for line in lines:
            if line.strip().startswith("image_folder"):
                image_folder = line.strip().split("=")[1].strip().replace("\\", "/").strip('"')
                break

        config_folder = None
        for line in lines:
            if line.strip().startswith("config_folder"):
                config_folder = line.strip().split("=")[1].strip().replace("\\", "/").strip('"')
                break

        panzar_folder = None
        for line in lines:
            if line.strip().startswith("panzar_folder"):
                panzar_folder = line.strip().split("=")[1].strip().replace("\\", "/").strip('"')
                break
    
    if script1_path is None or script2_path is None or image_folder is None or config_folder is None or panzar_folder is None:
        print("Ошибка в конфигурационном файле. Проверьте, что все пути указаны.")
        return

    # Проверяем, запущено ли окно Panzar, и запускаем, если необходимо
    if not is_panzar_running():
        start_panzar(script1_path)
    
    while True:
        if is_panzar_running():
            if is_panzar_active():
                button1_location = find_image_on_screen_with_color(os.path.join(image_folder, 'button1.png'))
                if button1_location:
                    click_button(button1_location)
                    print("Кнопка 1 найдена и нажата.")
                    

                button2_location = find_image_on_screen(os.path.join(image_folder, 'button2.png'))
                if button2_location:
                    click_button(button2_location)
                    print("Кнопка 2 найдена и нажата.")
                    time.sleep(1)

                if not button3_found:
                    button3_location = find_image_on_screen_with_color(os.path.join(image_folder, 'button3.png'))
                    if button3_location:
                        print("Кнопка 3 найдена.")
                        button3_found = True
                        
                        # Перемещаем файлы, если они существуют
                        source_files = [os.path.join(panzar_folder, "PnzCl_d3d9.log"), os.path.join(panzar_folder, "PnzCl.dxvk-cache")]
                        destination_folder = os.path.join(config_folder, "Config by Danze")
                        for file_path in source_files:
                            if os.path.exists(file_path):
                                shutil.move(file_path, destination_folder)
                                print(f"Файл {os.path.basename(file_path)} перемещен в {destination_folder}")
                            else:
                                print(f"Файл {os.path.basename(file_path)} не найден.")
                        
                        # Переходим в папку с батником
                        os.chdir(os.path.join(config_folder, "Config by Danze"))
                        
                        # Запускаем указанный файл Wanz.bat
                        wanz_bat_path = os.path.join(config_folder, "Config by Danze", "Wanz.bat")
                        if os.path.exists(wanz_bat_path):
                            subprocess.Popen(wanz_bat_path, shell=True)
                            print("Файл Wanz.bat успешно запущен.")
                        else:
                            print("Не удалось найти файл Wanz.bat.")

                        # Пауза 2 секунды перед нажатием кнопки 3
                        time.sleep(2)

                        # Проверяем, запущен ли PnzCl.exe
                        pnzcl_running = any(p.name() == 'PnzCl.exe' for p in psutil.process_iter())

                        if not pnzcl_running:
                            # Нажимаем кнопку 3
                            click_button(button3_location)
                            print("Кнопка 3 нажата.")

                            # Проверяем, запущен ли set.exe, и запускаем, если необходимо
                            set_exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set.exe")
                            if not any(p.name() == 'set.exe' for p in psutil.process_iter()):
                                if os.path.exists(set_exe_path):
                                    subprocess.Popen(set_exe_path, shell=True)
                                    print("Файл set.exe успешно запущен.")
                                else:
                                    print("Не удалось найти файл set.exe.")
                            else:
                                print("Файл set.exe уже запущен.")
                    
                else:
                    # Ищем кнопку 3 снова
                    button3_location = find_image_on_screen_with_color(os.path.join(image_folder, 'button3.png'))
                    if button3_location:
                        print("Кнопка 3 найдена во второй раз.")
                        
                        # Нажимаем кнопку 3
                        click_button(button3_location)
                        print("Кнопка 3 нажата.")
                        time.sleep(1)
                    
                        # Проверяем, запущен ли set.exe, и запускаем, если необходимо
                        set_exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set.exe")
                        if not any(p.name() == 'set.exe' for p in psutil.process_iter()):
                            if os.path.exists(set_exe_path):
                                subprocess.Popen(set_exe_path, shell=True)
                                print("Файл set.exe успешно запущен.")
                                sys.exit()
                            else:
                                print("Не удалось найти файл set.exe.")
                        else:
                            print("Файл set.exe уже запущен.")
                    
                        # Закрываем скрипт
                        break
                    sys.exit()

                    
# Задаем путь к конфигурационному файлу
config_file = "config.ini"

# Вызываем функцию для поиска и
find_and_click_all(config_file)

