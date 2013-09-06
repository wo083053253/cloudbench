#coding:utf-8
import setuptools

setuptools.setup(
    name="cloudbench",
    version="0.3.0",
    packages=setuptools.find_packages(),
    url="https://github.com/Scalr/cloudbench",
    license="Apache 2.0",
    author="Thomas Orozco",
    author_email="thomas@scalr.com",
    description="An utility to benchmark your Cloud",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        'console_scripts': [
            'cloudbench = cloudbench.cli:main',
            ],
        },
    install_requires=["requests", "six", "lockfile", "argparse"],
    extras_require={
        "EC2 Support": ["boto"],
        },
    setup_requires=["nose"],
    tests_require=["tox", "nose"],
)
