import sys
import os
import json
from subprocess import call, DEVNULL


# Create building environment
DIR_BIN = "dist"
DIR_SRC_PY = "src_py"
DIR_SRC_NUMBA = "src_numba"
DIR_BUILD = "build"
SUBDIR_SRC = "src"
SUBDIR_VENV = "venv_build"
VENDOR = ["numpy", "numba", "icc-rt", "pygame-ce", "setuptools", "pyinstaller"]
DIR_LINUX = "/usr/local/bin"

def clean():
    call(["rm", "-rf", "build"])


def main():
    try:
        os.mkdir(DIR_BUILD)
    except FileExistsError:
        pass
    
    # installing modules
    print(f"Creating build environment... ", end='', flush=True)
    call(["python", "-m", "venv", os.path.join(DIR_BUILD, SUBDIR_VENV)])
    print("Done!")
    
    for module in VENDOR:
        print(f"Installing build packages: {module}... ", end='', flush=True)
        call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-m", "pip", "install", module, "--quiet", "--quiet"])
        print("Done!")
    
    # compiling python-numba modules
    for fname in os.listdir(os.path.join(DIR_SRC_NUMBA)):
        print(f"Copying {os.path.join(DIR_SRC_NUMBA, fname)}... ", end='', flush=True)
        call(["cp", os.path.join(DIR_SRC_NUMBA, fname), DIR_BUILD])
        print("Done!")
    
        print(f"Compiling {os.path.join(DIR_SRC_NUMBA, fname)} (this might take a while)... ", end='', flush=True)
        call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-BO", os.path.join(DIR_BUILD, fname)])
        print("Done!")
    
        print(f"Removing {os.path.join(DIR_BUILD, fname)}... ", end='', flush=True)
        os.remove(os.path.join(DIR_BUILD, fname))
        print("Done!")
    
    # copying python-vanilla modules
    for fname in os.listdir(os.path.join(DIR_SRC_PY)):
        print(f"Copying {os.path.join(DIR_SRC_PY, fname)}... ", end='', flush=True)
        call(["cp", os.path.join(DIR_SRC_PY, fname), DIR_BUILD])
        print("Done!")
    
    with open(os.path.join(DIR_BUILD, "path"), "w") as file:
        file.write("config")

    print(f"Building executable (this might take a while)... ", end='', flush=True)
    call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "pyinstaller"), "--add-data", os.path.join(DIR_BUILD, "path") + ":.", "--onefile", "--noconsole", "--optimize=2", "--name=gatti", os.path.join(DIR_BUILD, "main.py")], stderr=DEVNULL, stdout=DEVNULL)
    print("Done!")
    
    # cleaning up
    print(f"Cleaning up gatti.spec... ", end='', flush=True)
    call(["rm", "gatti.spec"])
    print("Done!")
    
    for fname in os.listdir(DIR_BUILD):
        print(f"Cleaning up {os.path.join(DIR_BUILD, fname)}... ", end='', flush=True)
        call(["rm", "-rf", os.path.join(DIR_BUILD, fname)])
        print("Done!")
    
    # copying assets
    print("Copying/creating assets... ", end='', flush=True)
    
    os.mkdir(os.path.join(DIR_BUILD, "config"))
    
    with open(os.path.join(DIR_BUILD, "config", "settings.json"), "w") as file:
        json.dump({
            "width": 1280,
            "height": 720,
            "theme": os.path.join("themes", "default.json"),
            "grid_spacing": 50
        }, file, indent=4)

    call(["cp", "-r", "themes", DIR_BUILD])
    call(["cp", "about.json", DIR_BUILD])
    print("Done!")
    
    call(["mv", os.path.join(DIR_BIN, "gatti"), ])
    call(["rmdir", DIR_BIN])


def install_linux():
    dir_config_linux = os.path.join(os.path.expanduser("~"), ".config", "gatti")
    
    try:
        os.mkdir(DIR_BUILD)
    except FileExistsError:
        pass
    
    # installing modules
    print(f"Creating build environment... ", end='', flush=True)
    call(["python", "-m", "venv", os.path.join(DIR_BUILD, SUBDIR_VENV)])
    print("Done!")
    
    for module in VENDOR:
        print(f"Installing build packages: {module}... ", end='', flush=True)
        call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-m", "pip", "install", module, "--quiet", "--quiet"])
        print("Done!")
    
    # compiling python-numba modules
    for fname in os.listdir(os.path.join(DIR_SRC_NUMBA)):
        print(f"Copying {os.path.join(DIR_SRC_NUMBA, fname)}... ", end='', flush=True)
        call(["cp", os.path.join(DIR_SRC_NUMBA, fname), DIR_BUILD])
        print("Done!")
    
        print(f"Compiling {os.path.join(DIR_SRC_NUMBA, fname)} (this might take a while)... ", end='', flush=True)
        call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-BO", os.path.join(DIR_BUILD, fname)])
        print("Done!")
    
        print(f"Removing {os.path.join(DIR_BUILD, fname)}... ", end='', flush=True)
        os.remove(os.path.join(DIR_BUILD, fname))
        print("Done!")
    
    # copying python-vanilla modules
    for fname in os.listdir(os.path.join(DIR_SRC_PY)):
        print(f"Copying {os.path.join(DIR_SRC_PY, fname)}... ", end='', flush=True)
        call(["cp", os.path.join(DIR_SRC_PY, fname), DIR_BUILD])
        print("Done!")
    
    with open(os.path.join(DIR_BUILD, "path"), "w") as file:
        file.write(dir_config_linux)

    print(f"Building executable (this might take a while)... ", end='', flush=True)
    call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "pyinstaller"), "--add-data", os.path.join(DIR_BUILD, "path") + ":.", "--onefile", "--noconsole", "--optimize=2", "--name=gatti", os.path.join(DIR_BUILD, "main.py")], stderr=DEVNULL, stdout=DEVNULL)
    print("Done!")
    
    # cleaning up
    print(f"Cleaning up gatti.spec... ", end='', flush=True)
    call(["rm", "gatti.spec"])
    print("Done!")
    
    for fname in os.listdir(DIR_BUILD):
        print(f"Cleaning up {os.path.join(DIR_BUILD, fname)}... ", end='', flush=True)
        call(["rm", "-rf", os.path.join(DIR_BUILD, fname)])
        print("Done!")
    
    # copying assets
    print("Copying/creating assets... ", end='', flush=True)
    
    os.mkdir(os.path.join(dir_config_linux))
    
    with open(os.path.join(dir_config_linux, "settings.json"), "w") as file:
        json.dump({
            "width": 1280,
            "height": 720,
            "theme": os.path.join(dir_config_linux, "themes", "default.json"),
            "grid_spacing": 50
        }, file, indent=4)

    call(["cp", "-r", "themes", dir_config_linux])
    call(["cp", "about.json", dir_config_linux])
    print("Done!")
    
    call(["sudo", "mv", os.path.join(DIR_BIN, "gatti"), DIR_LINUX])
    call(["rmdir", DIR_BIN])


def uninstall_linux():
    dir_config_linux = os.path.join(os.path.expanduser("~"), ".config", "gatti")
    call(["sudo", "rm", "-f", os.path.join(DIR_LINUX, "gatti")])
    call(["rm", "-rf", dir_config_linux])


def install_devenv():
    try:
        os.mkdir(DIR_BUILD)
    except FileExistsError:
        pass
    
    # installing modules
    print(f"Creating build environment... ", end='', flush=True)
    call(["python", "-m", "venv", os.path.join(DIR_BUILD, SUBDIR_VENV)])
    print("Done!")
    
    for module in VENDOR:
        print(f"Installing build packages: {module}... ", end='', flush=True)
        call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-m", "pip", "install", module, "--quiet", "--quiet"])
        print("Done!")

    # copying python-vanilla modules
    for fname in os.listdir(os.path.join(DIR_SRC_PY)):
        _sync_files(os.path.join(DIR_SRC_PY, fname), os.path.join(DIR_BUILD, fname))

    # compiling python-numba modules
    for fname in os.listdir(os.path.join(DIR_SRC_NUMBA)):
        if _sync_files(os.path.join(DIR_SRC_NUMBA, fname), os.path.join(DIR_BUILD, fname)):
            print(f"Compiling {os.path.join(DIR_SRC_NUMBA, fname)} (this might take a while)... ", end='', flush=True)
            call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-BO", os.path.join(DIR_BUILD, fname)])
            print("Done!")

    # copying assets
    print("Copying/creating assets... ", end='', flush=True)
    os.mkdir(os.path.join(DIR_BUILD, "config"))
    with open(os.path.join(DIR_BUILD, "config", "settings.json"), "w") as file:
        json.dump({
            "width": 1280,
            "height": 720,
            "theme": os.path.join("themes", "default.json"),
            "grid_spacing": 50
        }, file, indent=4)
    
    with open(os.path.join(DIR_BUILD, "path"), "w") as file:
        file.write(os.path.join(DIR_BUILD, "config"))
    
    call(["cp", "-r", "themes", DIR_BUILD])
    call(["cp", "about.json", DIR_BUILD])
    print("Done!")


def run_devenv():
    # copying python-vanilla modules
    for fname in os.listdir(os.path.join(DIR_SRC_PY)):
        _sync_files(os.path.join(DIR_SRC_PY, fname), os.path.join(DIR_BUILD, fname))

    # compiling python-numba modules
    for fname in os.listdir(os.path.join(DIR_SRC_NUMBA)):
        if _sync_files(os.path.join(DIR_SRC_NUMBA, fname), os.path.join(DIR_BUILD, fname)):
            print(f"Compiling {os.path.join(DIR_SRC_NUMBA, fname)} (this might take a while)... ", end='', flush=True)
            call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-BO", os.path.join(DIR_BUILD, fname)])
            print("Done!")

    call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "python"), "-B", os.path.join(DIR_BUILD, "main.py")])


def _sync_files(master: str, slave: str):
    try:
        with open(master, "r") as file_master:
            with open(slave, "r") as file_slave:
                if file_slave.read() == file_master.read():
                    return False
    except FileNotFoundError:
        pass

    print(f"Copying {master}... ", end='', flush=True)
    with open(master, "r") as file_master:
        with open(slave, "w") as file_slave:
            file_slave.write(file_master.read())
            print("Done!")
            return True


BINDINGS = {
    "clean": clean,
    "developer": install_devenv,
    "run": run_devenv,
    "uninstall": uninstall_linux if os.name == "posix" else None,
    "portable": main
}

if len(sys.argv) > 1:
    BINDINGS[sys.argv[1]]()
else:
    if os.name == "posix":
        install_linux()
    else:
        raise Exception(f"Platform '{os.name}' currently not supported")
