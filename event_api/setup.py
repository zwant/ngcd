from setuptools import setup, find_packages

setup(
    name='event_api',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pika',
        'SQLAlchemy',
        'Flask',
        'Flask-SQLAlchemy'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
