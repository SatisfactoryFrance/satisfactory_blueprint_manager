import os
import sys
import time
import shutil
import subprocess

base_dir = os.path.dirname(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
log = os.path.join(base_dir, "updater.log")


def write(msg):
    try:
        with open(log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass


write("=== UPDATER START ===")
write(str(sys.argv))

if len(sys.argv) < 3:
    write("ERREUR: arguments manquants")
    time.sleep(5)
    sys.exit(1)

target = sys.argv[1]
source = sys.argv[2]

write(f"TARGET={target}")
write(f"SOURCE={source}")

exe_name = os.path.basename(target)

# attendre fermeture réelle
write("Waiting process death...")
while True:
    r = os.system(f'tasklist | find /i "{exe_name}" >nul')
    if r != 0:
        break
    time.sleep(1)

write("Process stopped")

time.sleep(2)

old = target + ".old"

try:
    os.rename(target, old)
    write("Rename OK")
except Exception as e:
    write(f"Rename fail: {e}")

try:
    shutil.copy2(source, target)
    write("Copy OK")
except Exception as e:
    write(f"Copy fail: {e}")

try:
    os.remove(old)
except:
    pass

write("Launching new exe")

subprocess.Popen([target], cwd=os.path.dirname(target))

write("DONE")
time.sleep(3)
