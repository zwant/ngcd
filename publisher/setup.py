from setuptools import setup, find_packages

setup(
    name='publisher',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'kombu',
        'Flask-Env'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
