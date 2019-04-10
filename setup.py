'''setup'''

from setuptools import setup, find_packages

setup(
    name="GenoMEL-PDC bionimbus pipeline",
    version="1.0",
    install_requires=[
        "GitPython==2.1.11",
        "PyYAML==3.12"
    ],
    packages=find_packages(),
)