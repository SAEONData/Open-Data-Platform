from setuptools import setup, find_namespace_packages

version = '0.1.0'

setup(
    name='ODP-API-CKANAdapter',
    version=version,
    description='CKAN Adapter for the ODP API',
    url='https://github.com/SAEONData/ODP-API-CKANAdapter',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[
        # use requirements.txt
    ],
    python_requires='~=3.6',
)
