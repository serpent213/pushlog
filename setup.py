#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="pushlog",
    version="0.2.0",
    description="Pushover notifications for systemd journal entries",
    author="serpent213",
    url="https://github.com/serpent213/pushlog",
    py_modules=["pushlog_lib"],
    packages=find_packages(),
    scripts=["pushlog"],
    install_requires=[
        "click",
        "PyYAML",
        "fuzzywuzzy",
        "python-systemd",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
        ],
    },
    python_requires=">=3.6",
)
