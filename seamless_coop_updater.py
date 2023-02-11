import json
import urllib.request
from winreg import *
from steamfiles import acf
import sys
import os
import zipfile

app_id = '1245620'
games_path = []

print("[!] Searching Steam installation path...")
reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)

try:
    print("[!] Opening registry key...")
    key = OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam")
except FileNotFoundError as e:
    print("[x] Can't find your Steam installation")
    raise e

print("[!] Retrieving key value...")
steam_path = QueryValueEx(key, "InstallPath")[0]
#print('[+] Found Steam installation path: {}'.format(steam_path))

print("[!] Searching Elden Ring installation path...")
try:
    with open(steam_path + "\steamapps\libraryfolders.vdf") as foldersfile:
        data = acf.load(foldersfile)
except OSError as e:
    print("[x] Can't find your libraryfolders.vdf file"
            "Full error :\n {e}")
    sys.exit(-1)  
except TypeError or ValueError as e:
    print(f"[x] An error occurred while trying to parse {steam_path}\steamapps\libraryfolders.vdf")
    sys.exit(-1)

finally:
    if foldersfile is not None:
        foldersfile.close()

if not data["libraryfolders"]:
    print("[x] An error occurred while trying to use data from your libraryfolders.vdf file")
    sys.exit(-1) 
else:
    for key in data["libraryfolders"]:
        if key.isdigit(): 
            games_path.append(data["libraryfolders"][key]['path'] + "\steamapps")

for path in games_path:
    for file in os.listdir(path):
        if os.path.isfile((os.path.join(path, file))): 
            if app_id in file:  
                if os.path.splitext(file)[1] == ".acf":
                    try: 
                        with open(os.path.join(path, file)) as acf_file:
                            data = acf.load(acf_file)
                    except OSError as e:
                        print(f"[x] A problem occurred while trying to open {os.path.join(path, file)}. Make sure you gave the permission to read this path")
                        sys.exit(-1)
                    except TypeError or ValueError as e:
                        print(f"[x] An error occurred while trying to parse {os.path.join(path, file)}")
                        sys.exit(-1)  

                    if acf_file is not None:
                        acf_file.close()
                    if data is not None and data["AppState"]["installdir"] is not None:
                        directory = data["AppState"]["installdir"]
                        elden_ring_path = path + "\\common\\" + directory + "\Game"
                    else:
                        print("[x] Can't find Elden Ring")

#print(f"[+] Found Elden Ring installation path: {elden_ring_path}")
print("[!] Downloading latest release...")
try:
    _json = json.loads(urllib.request.urlopen(urllib.request.Request(
        'https://api.github.com/repos/LukeYui/EldenRingSeamlessCoopRelease/releases/latest',
        headers={'Accept': 'application/vnd.github.v3+json'},
    )).read())
    asset = _json['assets'][0]
    urllib.request.urlretrieve(asset['browser_download_url'], asset['name'])
except RuntimeError as e:
    print(f"Unexpected {e}=, {type(e)}")
    raise

print(f"[!] Extracting {asset['name']}...")
try:
    archive = zipfile.ZipFile(asset['name'], 'r') 
    archive.extract('launch_elden_ring_seamlesscoop.exe',elden_ring_path)
    archive.extract('SeamlessCoop/elden_ring_seamless_coop.dll', elden_ring_path)
    archive.close()
except RuntimeError as e:
    print(f"Unexpected {e}=, {type(e)}")
    raise

print("[-] Cleaning temporary files...")
os.remove(asset['name'])

print("[+] Done!")
os.system("pause")