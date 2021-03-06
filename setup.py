from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['girder>=3.0.0a1']

setup(
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='A Girder plugin for data import tracking in HistomicsUI',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='girder-plugin, import_tracker',
    name='import_tracker',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/girder/import-tracker',
    version='0.1.0',
    zip_safe=False,
    entry_points={'girder.plugin': ['import_tracker = import_tracker:GirderPlugin']},
)
