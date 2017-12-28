from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='release-ccharp',
    version='1.0.0',
    description='Release management for c# applications at SNP&SEQ technology platform, Uppsala University',
    url='https://github.com/Molmed/release_ccharp',
    author='GitEdvard',
    license='MIT',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,

    keywords='development deployment release',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['click', 'pyfakefs', 'pypiwin32'],

    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    },

    entry_points={
        'console_scripts': [
            'release-ccharp=release_ccharp.cli:cli_main',
        ],
    },
)
