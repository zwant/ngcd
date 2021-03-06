from setuptools import setup, find_packages

setup(
    name='ngcd_common',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "protobuf",
        'psycopg2',
        'SQLAlchemy',
        'pytz',
        'python-dateutil',
        'kombu'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-mock',
        'pytest-cov'
    ],
)
