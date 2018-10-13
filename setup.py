from setuptools import setup, find_packages
from setuptools.command.install import install
import os

def read(relpath: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
        return f.read()

class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        install.run(self)
        os.mkdir("/etc/datalogger")

setup(
    name = "DataLogger",
    version_format = '{tag}+{gitsha}',
    description = 'Data Logger is an asynchronous data collector and recorder.',
    long_description = read('README.md'),
    author = 'YuSheng T.',
    author_email = 'hello@cwyark.me',
    license = 'Apache 2.0',
    packages = find_packages(),
    scripts = ['loggerd'],
    data_files = [
        ('/etc/systemd/system', ['configs/datalogger.service']), 
        ('', ['config.ini'])
    ],
    install_requires = ['uvloop',
        'configobj',
        'pyserial',
        'netifaces',
        'click'],
    classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
	],
    cmdclass = {
        'install': CustomInstallCommand
    },
    setup_requires = ['pytest-runner', 'setuptools-git-version'],
    tests_require = ['pytest']
)
