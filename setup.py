from setuptools import setup, find_packages

setup(
    name="creogen-common",
    version="0.2.7",
    packages=find_packages(),  # найдёт папку common/common
    install_requires=[         # List of dependencies
        'firebase-admin',
        'pydantic'
    ],
)
