import os
import re

from setuptools import find_packages, setup

ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

requires = [
    'aws-encryption-sdk>=2.0.0',
    'boto3>=1.16.63',
    'dynamodb-encryption-sdk>=1.2.0',
]


def get_version():
    init = open(os.path.join(ROOT, 'cryptoshredding', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='cryptoshredding',
    version=get_version(),
    description='Crypto shredding for Python',
    long_description=open('README.rst').read(),
    author='hupe1980',
    url='https://github.com/hupe1980/cryptoshredding',
    scripts=[],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requires,
    license="MIT",
    python_requires=">= 3.6",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
