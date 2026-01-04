from setuptools import setup, find_packages

setup(
    name="fileremover",
    version="1.1.0",
    description="Application de suppression de fichiers avec choix corbeille/définitif pour KDE Dolphin",
    author="Your Name",
    py_modules=["fileremover"],
    install_requires=[
        "PyQt6>=6.0.0",
        "send2trash>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "fileremover=fileremover:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
)