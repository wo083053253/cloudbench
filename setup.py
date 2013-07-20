from setuptools import setup

setup(
    name='stackbench',
    version='0.1',
    packages=['stackbench', 'stackbench.engine', 'stackbench.api', 'stackbench.utils', 'stackbench.test'],
    url='',
    license='',
    author='Thomas Orozco',
    author_email='thomas@scalr.com',
    description='FIO Wrapper',
    install_requires=['requests',],
)