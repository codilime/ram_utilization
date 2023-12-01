"""
setup for the memory_consumer package
"""
from setuptools import setup, find_packages

setup(
    author="tomasz.janaszka@codilime.com",
    description="A package for running process consuming memory according to given time characteristics",
    name="memory_consumer",
    version="2.0.2",
    packages=find_packages(include=["memory_consumer", "memory_consumer*"])
)