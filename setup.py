from setuptools import setup, find_packages

setup(
    name="creogen-common",
    version="0.3.1",
    packages=find_packages(),  # найдёт папку common/common
    install_requires=[         # List of dependencies
        'firebase-admin',
        'pydantic',
        'openai'
    ],
)
