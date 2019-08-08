from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='Hydra-Admin-Client',
    version=version,
    description='Python client for the Hydra Admin API',
    url='https://github.com/SAEONData/Hydra-Admin-Client',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # use requirements.txt
    ],
    python_requires='~=3.6',
)
