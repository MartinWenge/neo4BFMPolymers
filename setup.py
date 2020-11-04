from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='neo4polymer',
    version='1.1.2a1',
    description='Neo4j python-interface to manage computer simulation data, in particular for polymers',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Martin Wengenmayr',
    author_email='martinwengenmayr@gmail.com',
    url='https://github.com/MartinWenge/neo4BFMPolymers',
    license=license,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research'
    ],
    python_requires='>=3.0',
    install_requires=[
        'py2neo',
        'pandas',
        'numpy'
    ],
    packages=find_packages(where='neo4Polymer')
)
