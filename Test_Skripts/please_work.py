import subprocess

def get_saved_ssids():
    command = "security find-generic-password -D 'AirPort network password' -a all -g 2>&1 | grep 'acct' | cut -d '\"' -f 4"
    ssids = subprocess.check_output(command, shell=True).decode('utf-8').split('\n')
    return [ssid for ssid in ssids if ssid]

ssids = get_saved_ssids()
print(ssids)
