import subprocess
import time

def run_script_and_wait():
    # Запуск скрипта
    process = subprocess.Popen(
        ['python', 'основной скрипт.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Чтение вывода в реальном времени
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Выводим полученную строку в консоль
            print(output.strip())
            
            # Проверяем, не является ли эта строка запросом на ввод кода
            if "The confirmation code has been sent via Telegram app" in output:
                # Ждем 10 секунд
                time.sleep(10)
                
                # Читаем код из файла
                with open('code.txt', 'r') as file:
                    confirmation_code = file.read().strip()
                
                # Отправляем код в консоль
                process.stdin.write(confirmation_code + '\n')
                process.stdin.flush()

    # Ожидание завершения процесса
    process.wait()

if __name__ == "__main__":
    run_script_and_wait()
