from setuptools import setup

version = '0.1.0'

setup(
    name='ODP-API',
    version=version,
    description='The Open Data Platform API',
    url='https://github.com/SAEONData/ODP-API',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=['odp', 'odpapi_adapters'],
    include_package_data=True,
    install_requires=[
        # use requirements.txt
    ],
    python_requires='~=3.6',
)
