from setuptools import setup, find_packages

version = '1.1.0'

setup(
    name='ODP-API-CKANAdapter',
    version=version,
    description='CKAN Adapter for the ODP API',
    url='https://github.com/SAEONData/ODP-API-CKANAdapter',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_packages() + ['odp_api_adapters'],
    python_requires='~=3.8',
    install_requires=[
        'ckanapi',
    ],
    extras_require={
        'test': ['pytest', 'pytest-cov'],
    },
)
