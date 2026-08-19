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

print(f"Building executable (this might take a while)... ", end='', flush=True)
call([os.path.join(DIR_BUILD, SUBDIR_VENV, "bin", "pyinstaller"), "--onefile", "--noconsole", "--optimize=2", "--name=gatti", os.path.join(DIR_BUILD, "main.py")], stderr=DEVNULL, stdout=DEVNULL)
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

with open(os.path.join(DIR_BUILD, "path"), "w") as file:
    file.write("config")

call(["cp", "-r", "themes", DIR_BUILD])
call(["cp", "about.json", DIR_BUILD])
print("Done!")

call(["mv", os.path.join(DIR_BIN, "gatti"), DIR_BUILD])
call(["rmdir", DIR_BIN])
