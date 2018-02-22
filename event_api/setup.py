from setuptools import setup, find_packages

setup(
    name='event_api',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy',
        'Flask',
        'flask-swagger',
        'flask-swagger-ui',
        'Flask-Env'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
