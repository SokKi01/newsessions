import subprocess
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

confirmation_code = None

class CodeFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path == self.file_path:
            global confirmation_code
            with open(self.file_path, 'r') as file:
                confirmation_code = file.read().strip()
            print(f"Код обновлен: {confirmation_code}")

def run_script_and_wait():
    global confirmation_code
    
    process = subprocess.Popen(
        ['python3', 'основной скрипт тест.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    file_path = 'code.txt'
    event_handler = CodeFileHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                if "The confirmation code has been sent via Telegram app" in output:
                    while confirmation_code is None:
                        time.sleep(1)
                    process.stdin.write(confirmation_code + '\n')
                    process.stdin.flush()
                    confirmation_code = None

    finally:
        observer.stop()
        observer.join()
    process.wait()
if __name__ == "__main__":
    run_script_and_wait()
