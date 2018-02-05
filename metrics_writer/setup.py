from setuptools import setup, find_packages

setup(
    name='metrics_writer',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pika',
        'influxdb'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
