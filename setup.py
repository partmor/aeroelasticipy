from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

NAME = 'ezaero'
DESCRIPTION = 'Aerodynamics in Python.'
URL = 'https://github.com/partmor/ezaero'
EMAIL = 'part.morales@gmail.com'
AUTHOR = 'Pedro Arturo Morales Maries'
REQUIRES_PYTHON = '>=3.5'
VERSION = '0.1.dev0'

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # TODO
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    python_requires=REQUIRES_PYTHON,
    install_requires=[
        'matplotlib>=2.0',
        'numpy'
    ],
    extras_require={
        'jupyter': ['notebook'],
        'dev': [
            'flake8',
            'isort',
            'pytest',
            'sphinx',
            'sphinx_rtd_theme'
            'tox'
        ]
    }
)
