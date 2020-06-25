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
        'python-dotenv',
    ],
    extras_require={
        'api': [
            'fastapi',
            'uvicorn',
        ],
        'test': [
            'pytest',
            'pytest-cov',
        ],
    },
    dependency_links=[
        'git+https://github.com/SAEONData/Hydra-Admin-Client.git#egg=Hydra_Admin_Client',
    ],
)
