from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()


setup(
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description='A Girder plugin for data import tracking in HistomicsUI',
    install_requires=[
        'girder-jobs>=3.0.3',
        'girder>=3.1.23',
    ],
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='girder-plugin, import_tracker',
    name='import_tracker',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/DigitalSlideArchive/import-tracker',
    version='0.1.0',
    zip_safe=False,
    entry_points={'girder.plugin': ['import_tracker = import_tracker:GirderPlugin']},
)
