import os
from codecs import open

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


install_requires = [
    'Django>=1.11,<1.12',
    'djangorestframework>=3.6,<3.9',
    'requests>=2.18,<3',
    'elasticsearch>=2.4.1,<3',
    'django-localflavor>=1.1,<2',
    'django-flags>=4.0.1,<5',
    'unicodecsv>=0.14.1,<1',
]

testing_extras = [
    'coverage>=4.5.1,<5',
    'mock==2.0.0',
    'deep==0.10',
    'deepdiff>=3.3,<5.0',
    'django-nose==1.4.1',
    'parameterized==0.6.1',
]

docs_extras = [
    'mkdocs==0.17.5',
    'mkDOCter==1.0.5',
]


setup(
    name='ccdb5-api',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    description='Complaint Search API',
    long_description=long_description,
    url='https://github.com/cfpb/ccdb5-api',
    author='CFPB',
    author_email='tech@cfpb.gov',
    license='CC0',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 1.11',
    ],
    keywords='complaint search api',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    setup_requires=['setuptools-git-version==1.0.3'],
    install_requires=install_requires,
    extras_require={
        'docs': docs_extras,
        'testing': testing_extras,
    }
)
