from setuptools import setup, find_namespace_packages

version = '0.1.0'

setup(
    name='ODP-API',
    version=version,
    description='The Open Data Platform API',
    url='https://github.com/SAEONData/ODP-API',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_namespace_packages(),
    include_package_data=True,
    python_requires='~=3.6',
    install_requires=[
        'fastapi',
        'uvicorn',
        'python-dotenv',
    ],
    extras_require={
        'test': ['pytest', 'coverage']
    },
    dependency_links=[
        'git+https://github.com/SAEONData/Hydra-Admin-Client.git#egg=Hydra_Admin_Client',
    ],
)
