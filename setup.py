from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='sunderseaice',
    url='',
    author='Andy Barrett',
    author_email='andypbarrett@gmail.com',
    # Needed to actually package something
    packages=setuptools.find_packages(),
    # Needed for dependencies
    install_requires=['numpy','matplotlib','cartopy','pandas','xarray'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='Tools for Sunlight Under Sea Ice project',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
