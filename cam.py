import time
import subprocess

p = subprocess.Popen("exec /usr/local/ecam_tk1/bin/ecam_tk1_guvcview --profile=default.gpfl", stdout=subprocess.PIPE, shell=True)
time.sleep(1.5)
p.kill()

