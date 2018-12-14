from setuptools import setup, find_packages, Extension
from setuptools.command.install_scripts import install_scripts
import os
import shutil

spi_module = Extension('spi', sources = ['spi.c'])

def read(relpath: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
        return f.read()

class CustomInstallCommand(install_scripts):
    """Customized setuptools install command"""

    def run(self):
        RSYSLOG_PATH = "/etc/rsyslog.d"
        CONFIG_PATH = "/etc/mbox-agent"
        SYSTEMD_PATH = "/etc/systemd/system"
        install_scripts.run(self)
        if not os.path.exists(CONFIG_PATH):
            os.mkdir(CONFIG_PATH)
        shutil.copy2("config.ini", CONFIG_PATH)
        shutil.copy2("configs/mbox-agent.service", SYSTEMD_PATH)
        if os.path.exists(RSYSLOG_PATH):
            shutil.copy2("configs/mbox-agent.rsyslog.conf", RSYSLOG_PATH)

setup(
    name = "mbox-agent",
    version_format = '{tag}+{gitsha}',
    description = 'mbox-agent is an asynchronous data collector and recorder.',
    long_description = read('README.md'),
    author = 'YuSheng T.',
    author_email = 'hello@cwyark.me',
    license = 'Apache 2.0',
    packages = find_packages(),
    scripts = ['loggerd'],
    include_package_data = True,
    data_files = [
        ('/etc/systemd/system', ['configs/mbox-agent.service']), 
        ('/etc/mbox-agent', ['config.ini'])
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
        'install_scripts': CustomInstallCommand
    },
    setup_requires = ['pytest-runner', 'setuptools-git-version'],
    tests_require = ['pytest'],
    platforms=['Linux'],
    ext_modules = [spi_module]
)
