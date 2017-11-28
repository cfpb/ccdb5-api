import os
import pip
from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def parse_requirements():
    """Return abstract requirements (without version numbers)
    from requirements.txt.
    As an exception, requirements that are URLs are used as-is.
    This is tested to be compatible with pip 9.0.1.
    Background: https://stackoverflow.com/a/42033122/
    """

    path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = pip.req.parse_requirements(
        path, session=pip.download.PipSession()
    )
    requirements = [
        req.name or req.link.url
        for req in requirements
        if 'git+' not in (req.name or req.link.url)
    ]
    return requirements


install_requires = parse_requirements()

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
        'Framework :: Django :: 1.8',
    ],
    keywords='complaint search api',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    setup_requires=['setuptools-git-version==1.0.3'],
    install_requires=install_requires,
)
