from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='ODP-Admin',
    version=version,
    description='The SAEON Open Data Platform Admin Service',
    url='https://github.com/SAEONData/ODP-Admin',
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
