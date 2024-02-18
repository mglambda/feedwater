from setuptools import setup, find_packages
import os


FEEDWATER_VERSION='0.10.3'


with open("README.md", "r", encoding="utf-8") as readme_file:
    README = readme_file.read()

setup(
    name='feedwater',
    version=FEEDWATER_VERSION,
    url="https://github.com/mglambda/feedwater",
    author="Marius Gerdes",
    author_email="integr@gmail.com",
    description="Spawn a process and feed data into its stdin continuously and concurrently, reading output whenever you want it.",
    long_description=README,
    long_description_content_type="text/markdown",
    license_files=["LICENSE"],
    scripts=[],
    packages=find_packages(include=['feedwater']),
    install_requires=[]
)

