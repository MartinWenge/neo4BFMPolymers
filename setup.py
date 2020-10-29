from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='neo4Polymer',
    version='1.1',
    description='Neo4j python-interface to manage computer simulation data, in particular for polymers',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Martin Wengenmayr',
    author_email='martinwengenmayr@gmail.com',
    url='https://github.com/MartinWenge/neo4BFMPolymers',
    license=license,
    python_requires='>=3.0',
    install_requires=[
        'datetime',
        'os',
        'socket',
        're',
        'py2neo',
        'pandas',
        'numpy'
    ],
    packages=find_packages(exclude=('tests', 'bfm_files', 'figures'))
)
