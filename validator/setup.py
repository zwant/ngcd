from setuptools import setup, find_packages

setup(
    name='validator',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kombu',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-mock'
    ],
)
