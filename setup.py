import sys

from setuptools import setup

DEP_LINKS = []
if sys.version_info.major > 3 or (sys.version_info.major == 3 and
                                  sys.version_info.minor >= 5):
    DEP_LINKS.append('https://github.com/python-cmd2/cmd2/tarball/78b6dd61d4b863eaf4b2bf331119dfec9b6bfe76')

setup(
    name = "aws-identity-manager",
    version = "0.0.2",
    author = "Matthew Reid",
    author_email = "matt@nomadic-recording.com",
    description = ("Manage credentials for multiple AWS accounts"),
    url='https://github.com/nocarryr/AWS-Identity-Manager',
    license='MIT',
    keywords = "aws",
    packages=['awsident'],
    include_package_data=True,
    scripts=['main.py'],
    entry_points={
        'console_scripts':[
            'awsidentity = main:main',
        ],
    },
    install_requires=['cmd2'],
    dependency_links=DEP_LINKS,
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
