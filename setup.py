from setuptools import find_packages, setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

# Get admin.
admin = {}
with open("hvec_importers/admin.py") as fp:
    exec(fp.read(), admin)

setup(
    name = 'hvec_importers',
    version = admin['__version__'],
    author = admin['__author__'],
    author_email = admin['__author_email__'],
    description = 'Python package with importers '
                'for several open data sources.',
    long_description=long_description,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10'
        'Programming Language :: SQL',
        'Topic :: Scientific/Engineering'
    ],
    platforms='Windows',
    install_requires=['numpy',
                      'pandas>=2.0',
                      'scipy',
                      'requests',
                      'tqdm',
                      'lxml',
                      'openpyxl'],
    package_data = {'': ['endpoints.json']},
    include_package_data = True,
    packages=find_packages(exclude=[]),
    
)
