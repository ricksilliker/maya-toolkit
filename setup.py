import os
import platform
import shutil
import errno

from setuptools import setup


setup(
    name='maya-toolkit',
    version='1.0.0',
    author='Rick Silliker',
    author_email='ricksilliker@gmail.com',
    url='https://github.com/ricksilliker/maya-toolkit.git',
    packages=['mltk'],
    package_dir={'': 'src'},
    install_requires=['pyyaml', 'Qt.py'],
    include_package_data=True,
    data_files=[
        ('maya/modules', ['src/mltk.mod'])
    ]
)
