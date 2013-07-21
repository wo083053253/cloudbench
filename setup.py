from setuptools import setup

setup(
    name='stackbench',
    version='0.1',
    packages=[
        'stackbench', 'stackbench.fio', 'stackbench.api', 'stackbench.utils',
        'stackbench.test', 'stackbench.test.api'
    ],
    url='',
    license='',
    author='Thomas Orozco',
    author_email='thomas@scalr.com',
    description='FIO Wrapper',
    install_requires=['requests',],
    setup_requires=["nose"],
    tests_require=["tox", "nose"],
)