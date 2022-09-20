#!/usr/bin/env python

from setuptools import setup, find_packages

README = 'README.md'

with open('requirements.txt') as f:
    requirements = f.readlines()


def long_desc():
    try:
        import pypandoc
    except ImportError:
        with open(README) as f:
            return f.read()
    else:
        return pypandoc.convert(README, 'rst')

setup(
    name='cloudwatch_logs_cli',
    version='1',
    description='AWS CloudWatch log getter/follower tool',
    author='Justin Mayfield',
    url='https://github.com/mayfield/cloudwatch_logs_cli/',
    license='MIT',
    long_description=long_desc(),
    packages=find_packages(),
    test_suite='test',
    install_requires=requirements,
    entry_points={
        'console_scripts': ['cloudwatch-logs=cloudwatch_logs.cli:main'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
    ]
)
