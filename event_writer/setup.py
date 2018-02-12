from setuptools import setup, find_packages

setup(
    name='event_writer',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kombu',
        'sqlalchemy-utils'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
