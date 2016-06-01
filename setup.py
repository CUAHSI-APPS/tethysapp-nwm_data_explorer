import os
import sys
from setuptools import setup, find_packages
from tethys_apps.app_installation import custom_develop_command, custom_install_command

### Apps Definition ###
app_package = 'nwm_data_explorer'
release_package = 'tethysapp-' + app_package
app_class = 'nwm_data_explorer.app:NationalWaterModelDataExplorer'
app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tethysapp', app_package)

### Python Dependencies ###
dependencies = ['django', 'tethys_sdk', 'requests', 'hurry.filesize']

setup(
    name=release_package,
    version='1.0',
    description='This app explores the National Water Data provided for the NFIE Summer Institute and provides an API '
                'for accessing the data externally.',
    long_description='',
    keywords='',
    author='Shawn Crawley',
    author_email='scrawley@byu.edu',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['tethysapp', 'tethysapp.' + app_package],
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
    cmdclass={
        'install': custom_install_command(app_package, app_package_dir, dependencies),
        'develop': custom_develop_command(app_package, app_package_dir, dependencies)
    }
)
