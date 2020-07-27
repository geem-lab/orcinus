#!/usr/bin/env python3

"""Setup script for orcinus."""

from setuptools import find_packages
from setuptools import setup

setup(
    name="orcinus",
    version=open("VERSION").read().strip(),
    description=(
        "a simple graphical user interface (GUI) for the ORCA "
        "quantum chemistry package"
    ),
    author="Felipe Silveira de Souza Schneider",
    author_email="schneider.felipe@posgrad.ufsc.br",
    url="https://github.com/schneiderfelipe/orcinus",
    packages=find_packages(),
    entry_points={"console_scripts": ["orcinus = orcinus.gui:main"]},
)
