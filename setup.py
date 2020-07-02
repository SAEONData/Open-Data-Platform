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
    packages=find_packages() + ['odp_api_adapters'],
    include_package_data=True,
    python_requires='~=3.8',
    install_requires=[
        'sqlalchemy',
        'sqlalchemy-utils',
        'psycopg2',
        'pydantic[email]',
        'python-dotenv',
        'itsdangerous',
        'argon2-cffi',
        'requests',
    ],
    extras_require={
        'api': [
            'fastapi',
            'uvicorn',
        ],
        'ui': [
            'flask',
            'flask-login',
            'flask-admin',
            'flask-wtf',
            'flask-mail',
            'click',
            'wtforms',
            'gunicorn',
        ],
        'test': [
            'pytest',
            'pytest-cov',
        ],
    },
    dependency_links=[
        'git+https://github.com/SAEONData/Hydra-Admin-Client.git#egg=Hydra_Admin_Client',
        'git+https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git#egg=Hydra_OAuth2_Blueprint',
    ],
)