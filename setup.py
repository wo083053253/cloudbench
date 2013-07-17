from setuptools import setup

setup(
    name='fio',
    version='0.1',
    packages=['fio', 'fio.api', 'fio.test'],
    url='',
    license='',
    author='Thomas Orozco',
    author_email='thomas@scalr.com',
    description='FIO Wrapper',
    install_requires=['requests',],
)