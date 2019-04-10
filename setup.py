'''setup'''

from setuptools import setup, find_packages

setup(
    name="GenoMEL-PDC bionimbus pipeline",
    version="1.0",
    install_requires=[
        "GitPython==2.1.11",
        "PyYAML==4.2b1"
    ],
    packages=find_packages(),
)
