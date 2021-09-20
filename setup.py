# -*- coding: utf-8 -*-

import os, sys
from shutil import rmtree

from setuptools import setup, Command

with open("VERSION") as handle:
    for line in handle.readlines():
        line = line.strip()
        if len(line) > 0:
            version = line
            break

with open("README.rst", "r") as f:
    long_descr = f.read()

here = os.path.abspath(os.path.dirname(__file__))

class PublishCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(name="arrapi",
      version=version,
      description="A lightweight Python library for Radarr and Sonarr API.",
      long_description=long_descr,
      url="https://github.com/meisnate12/arrapi",
      author="Nathan Taggart",
      author_email="meisnate12@gmail.com",
      license="MIT",
      packages=["arrapi"],
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
      ],
      cmdclass={
          "publish": PublishCommand,
      },
      zip_safe=False)
