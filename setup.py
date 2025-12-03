from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='simplefoc',
    packages=find_packages(include=['simplefoc']),
    version='0.0.4',
    description='SimpleFOC Python API',
    long_description=long_description,
    author='Richard Unger',
    author_email="runger@simplefoc.com",
    install_requires=['serial', 'rx'],
    extras_require={
        'can': ['python-can>=4.0.0'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10'
)
