from setuptools import setup

setup(
    name='dfs',
    version='0.1',
    py_modules=['client.interface.cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        dfs=client.interface.cli:dfs
    ''',
)