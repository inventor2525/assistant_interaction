from setuptools import setup, find_packages

setup(
    name="assistant_interaction",
    version="0.1.0",
    author="Charlie Mehlenbeck",
    author_email="charlie_inventor2003@yahoo.com",
    description="A (currently, likely forever, very shitty) scripting language for facilitating an AI to run bash commands, save and read files, and perform merge request like functions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/inventor2525/assistant_interaction",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10.12",
    install_requires=[
        "assistant_merger @ git+https://github.com/inventor2525/assistant_merger.git@master",
    ],
    extras_require={
        "dev": ["unittest"],
    },
)