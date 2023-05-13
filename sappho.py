import zipfile
import requests
import yaml
import sys
import os

def sync_dbs():
    config = yaml.safe_load(open("sappho.yaml"))
    print(":: Synchronizing Package Databases...")
    for key, value in config["servers"].items():
        for line in open(value["include"]).read().splitlines():
            if line.startswith("#") or not line: continue
            print(f'Synchronizing {key}...', end='\t')
            try:
                r = requests.get(line.replace("$os", sys.platform).replace("$repo", key)+"/sync")
                r.raise_for_status()
                print(f"ok ({r.elapsed.total_seconds()*1000}ms)")
                with open(f'clusters/{key}.yaml', 'w+') as f:
                    text = (r.text[1:-3].replace("\\n","\n"))
                    f.write(text)
                break
            except:
                print(f":: ERROR Synchronizing {key}")
                print(f":: This Error will be ignored for now. You can supply the -Rc Parameter to remove broken Repositories.")
                continue

def search(repo_name):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    config = yaml.safe_load(open("sappho.yaml"))
    found = None
    for key, value in config["servers"].items():
        db = yaml.safe_load(open(f'clusters/{key}.yaml'))['objects']
        if repo_name in db:
            if found:
                if isinstance(found, list):
                    found.append(db[repo_name])
                else:
                    found = [found, db[repo_name]]
            else:
                found = db[repo_name]
            break
    if not found:
            return print(f":: E: Target not found: {repo_name}")
    elif isinstance(found, list):
            print(f":: Found conflicting Packages: Expected 1 Package, found {len(found)}")
            for num, i in enumerate(found):
                print(f'{num}.{i["name"]}')
            ok = False
            while not ok:
                number = input("You can specify which packages to install (1,2,3,...)")
                try:
                    number = int(number)
                    if 0 < number <= len(found):
                        found = found[number-1]
                        ok = True
                except:
                    continue       
    print(f"Downloading Archive {repo_name}.zip...")
    response = requests.get(found['download'], stream=True)
    file_size = int(response.headers.get("Content-Length", 0))
    block_size = 1024 # 1 Kibibyte
    dl = 0
    filename = f"cache/{repo_name}.zip"
    with open(filename, "wb") as f:
        for i,data in enumerate(response.iter_content(block_size)):
            dl += len(data)
            f.write(data)
            done = int(100 * dl / file_size)
            sys.stdout.write("\r[%s%s] [%s%s]" % ('=' * done, ' ' * (100-done), done, "%"))
            sys.stdout.flush()
    print()
    print("Expanding Installation...")
    with zipfile.ZipFile(filename) as ziph:
        print(f"Selecting previously unselected package {repo_name}...")
        dirname = filename.split("/")[1][:-4]
        ziph.extractall()
        os.chdir(dirname)
        data = yaml.safe_load(open(".sappho-build.yml"))
        print(data)
        p = data["meta"]["platforms"]
        if p and p.get("exclude") and sys.platform in p.get("exclude") :

            raise OSError(f"Platform {sys.platform} is excluded from the installation")
        print("Collecting build dependencies...")
        for dependency in data["meta"]["requirements"]:
            search(dependency)
        print(":: Build Process Started")
        print("  ~> Entering Fake Environment...")
        for key, value in data["meta"]["environ"]:
            os.environ[key] = value
        print(f"sappho@{dirname}~# sappho-env -p activate ./.sappho-build.yml -a")
        print(f"(sappho master) sappho@{dirname}~# sappho-env -p get sappho-ci")
        print(os.getcwd())
        if os.path.basename(os.getcwd()) != dirname:
            os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname))
        for command in data["commands"][sys.platform]:
            if not command: continue
            print(f"(sappho master) sappho@{dirname}~# sappho-ci -g -L --as-secondary {command}")
            os.system(command)
    print(":: Setup Complete!")
if __name__ == "__main__":
    for i, arg in enumerate(sys.argv):
        if arg.startswith("-"):
            if "S" in arg:
                search(sys.argv[i+1])
            if "y" in arg:
                sync_dbs()
            if "u" in arg:...
