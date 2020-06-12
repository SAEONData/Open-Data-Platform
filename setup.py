from setuptools import setup, find_namespace_packages

version = '1.0.0'

setup(
    name='ODP-API-ElasticAdapter',
    version=version,
    description='Elasticsearch adapter for the ODP API',
    url='https://github.com/SAEONData/ODP-API-ElasticAdapter',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_namespace_packages(),
    python_requires='~=3.8',
    install_requires=[
        'elasticsearch>=6.0.0,<7.0.0',
    ],
    extras_require={
        'test': ['pytest', 'coverage']
    },
)
