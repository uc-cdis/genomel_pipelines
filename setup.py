'''setup'''

from setuptools import setup, find_packages

setup(
    name="GenoMEL-PDC bionimbus pipeline",
    version="1.0",
    install_requires=[
        "GitPython==3.1.32",
        "PyYAML==5.4"
    ],
    packages=find_packages(),
)
