from setuptools import setup

setup(
    name='iobench',
    version='0.1',
    packages=['iobench', 'iobench.engine', 'iobench.api', 'iobench.utils', 'iobench.test'],
    url='',
    license='',
    author='Thomas Orozco',
    author_email='thomas@scalr.com',
    description='FIO Wrapper',
    install_requires=['requests',],
)