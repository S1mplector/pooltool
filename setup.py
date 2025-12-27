"""
Build script for creating standalone executables using Panda3D's build_apps.

Usage:
    python setup.py build_apps

This will create a standalone executable in the 'build' directory.
"""

from setuptools import setup

setup(
    name="Pooltool",
    options={
        "build_apps": {
            # Entry point - the main script to run
            "gui_apps": {
                "Pooltool": "pooltool/main.py",
            },
            # Platforms to build for (current platform by default)
            # "platforms": ["manylinux2014_x86_64", "macosx_10_9_x86_64", "win_amd64"],
            # Include these patterns
            "include_patterns": [
                "pooltool/**/*.py",
                "pooltool/**/*.glb",
                "pooltool/**/*.png",
                "pooltool/**/*.jpeg",
                "pooltool/**/*.jpg",
                "pooltool/**/*.ttf",
                "pooltool/**/*.otf",
                "pooltool/**/*.yaml",
                "pooltool/**/*.yml",
                "pooltool/logo/*",
                "pooltool/models/**/*",
            ],
            # Exclude patterns
            "exclude_patterns": [
                "pooltool/**/*.blend*",
                "pooltool/**/*.svg",
                "pooltool/**/*.exr",
                "pooltool/**/*.pptx",
                "pooltool/**/test_*",
            ],
            # Required plugins
            "plugins": [
                "pandagl",
                "p3openal_audio",
            ],
            # Log output
            "log_filename": "$USER_APPDATA/Pooltool/output.log",
            "log_append": False,
            # Include these packages
            "include_modules": [
                "pooltool.*",
                "panda3d.*",
                "panda3d_gltf",
                "simplepbr",
                "numpy",
                "numba",
                "scipy",
                "attrs",
                "cattrs",
                "msgpack",
                "msgpack_numpy",
                "yaml",
                "click",
                "PIL",
                "h5py",
                "rich",
                "quaternion",
            ],
            # Exclude unnecessary modules to reduce size
            "exclude_modules": [
                "tkinter",
                "test",
                "distutils",
                "pyngrok",  # Multiplayer disabled for now
            ],
        }
    }
)
