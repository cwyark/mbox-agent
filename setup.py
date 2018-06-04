from setuptools import setup, find_packages
import os

def read(relpath: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
        return f.read()

setup(
    name = "BoxAgent",
    version = read('version.txt').strip(),
    description = 'BoxAgent is asynchronous pacekt parser and executor',
    long_description = read('README.md'),
    author = 'ChesterTseng',
    author_email = 'hello@wylinks.io',
    license = 'Apache 2.0',
    packages = [
        'boxagent'
    ],
    scripts = ['boxd'],
    install_requires = ['uvloop',
        'pyserial',
        'netifaces',
        'click'],
    classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
	]
)
