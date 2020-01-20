from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='ODP-AccountsLib',
    version=version,
    description='Data access layer for the SAEON Open Data Platform accounts database',
    url='https://github.com/SAEONData/ODP-AccountsLib',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='~=3.6',
    install_requires=[
        'sqlalchemy',
        'psycopg2',
    ],
    extras_require={
        'test': ['pytest', 'coverage']
    },
)
