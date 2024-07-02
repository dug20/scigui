"""
Allows installation via pip, e.g. by navigating to this directory with the command prompt, and using 'pip install .'
"""

import sys
from setuptools import setup, find_packages

# Make sure to include the readme
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='scigui',
    author = '',                 
    author_email = '',        
    version = '0.1',
    license = '	AGPL-3.0',
    packages = find_packages(),
    install_requires = ['tk', 'matplotlib'],
    description = 'GUI toolbox that helps you turn standard Python libraries into system-model style GUIs',
    keywords = ['gui', 'system', 'model', 'fast', 'easy'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',     
        'Intended Audience :: Science/Research',    
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU Affero General Public License v3',   
        'Programming Language :: Python :: 3'],
    package_data = {'scigui': ['img/*.gif', 'img/*.cur']},
    long_description = long_description,
    long_description_content_type='text/markdown'
)
