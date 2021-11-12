import arrapi, os

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
    name=arrapi.__package_name__,
    version=__version__,
    description=arrapi.__description__,
    long_description=long_descr,
    url=arrapi.__url__,
    author=arrapi.__author__,
    author_email=arrapi.__email__,
    license=arrapi.__license__,
    packages=find_packages(),
    python_requires=">=3.6",
    keywords=["arrapi", "sonarr", "radarr", "arr", "wrapper", "api"],
    install_requires=[
        "requests"
    ],
    project_urls={
        "Documentation": "https://arrapi.readthedocs.io/en/latest/",
        "Funding": "https://github.com/sponsors/meisnate12",
        "Source": "https://github.com/meisnate12/ArrAPI",
        "Issues": "https://github.com/meisnate12/ArrAPI/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)
