#!/usr/bin/env python3
"""
Build script for creating a standalone Pooltool executable.

This script uses PyInstaller to package the game.

Usage:
    python build_app.py

Requirements:
    pip install pyinstaller
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the project root
    project_root = Path(__file__).parent
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Pooltool",
        "--windowed",  # No console window on Windows/macOS
        "--onedir",    # Create a directory with all files (faster startup than onefile)
        # Add data files
        f"--add-data={project_root / 'pooltool' / 'models'}{os.pathsep}pooltool/models",
        f"--add-data={project_root / 'pooltool' / 'logo'}{os.pathsep}pooltool/logo",
        # Hidden imports for Panda3D and dependencies
        "--hidden-import=panda3d.core",
        "--hidden-import=panda3d.direct",
        "--hidden-import=panda3d.physics",
        "--hidden-import=panda3d_gltf",
        "--hidden-import=simplepbr",
        "--hidden-import=direct.showbase.ShowBase",
        "--hidden-import=direct.gui.DirectGui",
        "--hidden-import=direct.task",
        "--hidden-import=direct.fsm",
        "--hidden-import=direct.interval",
        "--hidden-import=numpy",
        "--hidden-import=numba",
        "--hidden-import=scipy",
        "--hidden-import=scipy.spatial",
        "--hidden-import=scipy.optimize",
        "--hidden-import=attrs",
        "--hidden-import=cattrs",
        "--hidden-import=msgpack",
        "--hidden-import=msgpack_numpy",
        "--hidden-import=yaml",
        "--hidden-import=click",
        "--hidden-import=PIL",
        "--hidden-import=h5py",
        "--hidden-import=rich",
        "--hidden-import=quaternion",
        # Collect all submodules
        "--collect-all=panda3d",
        "--collect-all=panda3d_gltf", 
        "--collect-all=simplepbr",
        "--collect-all=pooltool",
        # Exclude unnecessary modules
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=IPython",
        "--exclude-module=jupyter",
        "--exclude-module=pytest",
        "--exclude-module=pyngrok",
        # Entry point
        str(project_root / "pooltool" / "main.py"),
    ]
    
    print("Building Pooltool executable...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✓ Build successful!")
        print(f"  Executable is in: {project_root / 'dist' / 'Pooltool'}")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
