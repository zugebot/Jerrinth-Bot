import os
import time
from datetime import datetime, timedelta
import subprocess
import sys
import platform


def run_bot(_venv_python):
    process = subprocess.Popen([_venv_python, 'bot.py'])
    return process


def kill_bot(process):
    process.terminate()
    process.wait()


def install_dependencies(_venv_python):
    subprocess.run([_venv_python, '-m', 'pip', 'install', '-U', 'g4f[all]'], check=True)


def seconds_until_midnight():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
    return (midnight - now).total_seconds()


def get_venv_python():
    if platform.system() == "Windows":
        return os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe')
    else:
        return os.path.join(os.getenv('VIRTUAL_ENV'), 'bin', 'python')


if __name__ == "__main__":
    venv_python = get_venv_python()

    if not os.path.exists(venv_python):
        raise EnvironmentError("Python executable not found in the virtual environment.")

    bot_process = run_bot(venv_python)
    while True:
        time_until_midnight = seconds_until_midnight()
        time.sleep(time_until_midnight)
        kill_bot(bot_process)
        install_dependencies(venv_python)
        bot_process = run_bot(venv_python)
