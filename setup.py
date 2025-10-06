from setuptools import setup, find_packages
from importlib import import_module

def my_dependency(dep_name:str) -> str:
	'''
	Creates a install_requires link to one of my other
	dependencies that respects any existing install of a
	dependency with pip install -e
	'''
	try:
		import_module(dep_name)
		return dep_name
	except:
		return f"{dep_name} @ git+https://github.com/Inventor2525/{dep_name}@master"


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
		my_dependency("assistant_merger"),
	],
	extras_require={
		"dev": ["unittest"],
	},
)