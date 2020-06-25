from setuptools import setup, find_packages

version = '1.1.0'

setup(
    name='Open-Data-Platform',
    version=version,
    description='The SAEON Open Data Platform - Core Framework Components',
    url='https://github.com/SAEONData/Open-Data-Platform',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='~=3.8',
    install_requires=[
        'sqlalchemy',
        'sqlalchemy-utils',
        'psycopg2',
        'pydantic[email]',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
        ],
    },
)
