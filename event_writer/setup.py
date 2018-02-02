from setuptools import setup, find_packages

setup(
    name='event_writer',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
          'console_scripts': [
              'event_writer = event_writer.event_writer.__main__:main',
          ]
      },
    install_requires=[
        'pika',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
