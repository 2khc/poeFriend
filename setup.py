import sys
import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = 'C:/Users/KHKel/AppData/Local/Programs/Python/Python36/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'C:/Users/KHKel/AppData/Local/Programs/Python/Python36/tcl/tk8.6'
# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os", "idna"], "excludes": ["tkinter"]}
build_exe_options = {"packages": ["os", "idna"],
                     "include_files":[
                         "C:/Users/KHKel/AppData/Local/Programs/Python/Python36/DLLs/tcl86t.dll",
                         "C:/Users/KHKel/AppData/Local/Programs/Python/Python36/DLLs/tk86t.dll"
                     ]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="poeFriend",
      version="0.2.5",
      description="POE_FRIEND",
      options={"build_exe": build_exe_options},
      executables=[Executable("__main__.py", base=base)])
