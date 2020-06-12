from setuptools import setup, find_packages

version = '1.0.0'

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
    python_requires='~=3.6',
    install_requires=[
        'flask',
        'flask-login',
        'flask-admin',
        'python-dotenv',
        'click',
        'wtforms',
    ],
    extras_require={
        'test': ['pytest', 'coverage']
    },
    dependency_links=[
        'git+https://github.com/SAEONData/ODP-AccountsLib.git#egg=ODP_AccountsLib',
        'git+https://github.com/SAEONData/Hydra-Admin-Client.git#egg=Hydra_Admin_Client',
        'git+https://github.com/SAEONData/Hydra-OAuth2-Blueprint.git#egg=Hydra_OAuth2_Blueprint',
    ],
)
