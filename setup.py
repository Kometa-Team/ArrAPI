import os

from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_descr = f.read()

__version__ = None
if os.path.exists("VERSION"):
    with open("VERSION") as handle:
        for line in handle.readlines():
            line = line.strip()
            if len(line) > 0:
                __version__ = line
                break

setup(
    name="arrapi",
    version=__version__,
    description="Python wrapper for Radarr and Sonarr APIs:",
    long_description=long_descr,
    url="https://github.com/Kometa-Team/ArrAPI",
    author="Kometa Team",
    author_email="kometateam@proton.me",
    license="MIT License",
    packages=find_packages(),
    python_requires=">=3.10",
    keywords=["arrapi", "sonarr", "radarr", "arr", "wrapper", "api"],
    install_requires=[
        "requests"
    ],
    project_urls={
        "Documentation": "https://arrapi.kometa.wiki",
        "Funding": "https://github.com/sponsors/meisnate12",
        "Source": "https://github.com/Kometa-Team/ArrAPI",
        "Issues": "https://github.com/Kometa-Team/ArrAPI/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ]
)
