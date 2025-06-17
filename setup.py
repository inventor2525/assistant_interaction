from setuptools import setup, find_packages

setup(
    name="assistant_interaction",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "gitpython>=3.1.0",
    ],
    description="A package for processing AI interaction commands",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)