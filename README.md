![example of polymer and simulations in te database](figures/sketch_polymers_simulations.png)
# neo4BFMPolymers
> Access a [neo4j](https://neo4j.com/) database to efficiently organize simulations of polymers, using the [bond fluctuation model (BFM)](https://en.wikipedia.org/wiki/Bond_fluctuation_model) and the [LeMonADE library](https://github.com/LeMonADE-project).

[![GitHub issues open](https://img.shields.io/github/issues/MartinWenge/neo4BFMPolymers)](https://github.com/MartinWenge/neo4BFMPolymers/issues)
[![CircleCI](https://circleci.com/gh/MartinWenge/neo4BFMPolymers.svg?style=svg&circle-token=384ea1a8f93ec4063c766071ee8bb1544a0b1a26)](https://app.circleci.com/pipelines/gh/MartinWenge/neo4BFMPolymers)

## Python interface for a graph based database
The neo4BFMPolymers tool collection contains several python functions to add polymers, simulation setups, simulation parameters and relations between the various nodes in a neo4j database.
The available node types and connection types are defined in the function definitions, to avoid doubling of nodes with similar meaning.

The available functions can be used as a python module by exporting the jupyter-notebooks to a plain python file or directly in the notebook.

## Getting Started
For a local usage, it is recommended to install the [desktop version of neo4j](https://neo4j.com/download/) and access a plain database.
The python library [py2neo](https://py2neo.org/v4/) is used to access the database (default with username `neo4j` and host `bolt://localhost:7687`) via the [Graph class](https://py2neo.org/v4/database.html#the-graph) of py2neo with the jupyter-notebooks provided in this repository.
Once the connection to the database is working, the available functions allow you to add nodes, connections and data to the database.
You can insert the data manually, or parse bfm files or output files from [LeMonADE](https://github.com/LeMonADE-project) for large amounts of data.

## Basic Usage
### Get the library from (test) pypi
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple neo4polymer
```

### Setup database connection
To apply actions on the database, setup an instance of the Graph class of the py2neo library and pass it to the neo4Polymer class.

```python
from py2neo import Graph
import neo4Polymer
# connect the graph with (default local) database -> it should be running already
graph = Graph(scheme="bolt", host="localhost", port=7687, auth=('<username>', '<password>'))
# setup instance of the neo4Polymer - BFM file interface
myNeo4Polymer = neo4Polymer.neo4BFMPolymer(graph)
```

### Manually add nodes
To add nodes, find the interfaces you need from the docs and run them on the neo4Polymer class instance.

```python
# add Linear Chain as Polymer node:
myNeo4Polymer.addNewPolymer("Linear Chain")
# add SimulationProject node
myNeo4Polymer.addNewSimulationProject("Linear polymer solutions")
# connect Polymer node and simulation project
myNeo4Polymer.connectSimulationToPolymer("Linear Chain", "Linear polymer solutions")
# add SimulationRun node
simRunName = "Linear polymer solutions"
myNeo4Polymer.addSimulationRunToSimulationProject("short_chain_dilute",simRunName)
# add some meta information to SimulationRun node
myNeo4Polymer.addLinearChainLengthToSimulationRun(simRunName,32)
myNeo4Polymer.addVolumeFractionToSimulationRun(simRunName,0.05)
```

### Parse files to add content
To add information from a file, use the file reader functions for supported file formats.

```python
# read in bfm / radius of gyration / bond length file
myNeo4Polymer.addBFMFileToDatabase(simRunName,"<path/to/file>")
myNeo4Polymer.addAnyRadiusOfGyrationFileToDatabase(simRunName,"<path/to/file>")
myNeo4Polymer.addAnyBondLengthFileToDatabase(simRunName, "<path/to/file>")
```

### Run search queries to get
Once there are some information, neo4polymer provides some search query templates, returning pandas data frames as result.
```python
# setup instance of search request class connected to the graph
myRequest = neo4Polymer.neo4PolymerRequests(graph)
# get "Linear polymer solutions" and some additional information from the above example graph
print(myRequest.getSimulationProjectsByPolymer("Linear Chain"))
# get "short_chain_dilute" and some additional information from the above example graph
print(myRequest.getSimulationRunsBySimulationProject(simRunName, "<path/to/file>"))
```

## Documentation
The documentation is done with [DocStrings](https://www.python.org/dev/peps/pep-0257/).
To call a documentation, run `help( class or function )`.

## Dependencies
Naturally, the python tools need a running [neo4j](https://neo4j.com/) database that can be accessed by the [Graph class](https://py2neo.org/v4/database.html#the-graph).

The following python libraries are used:
* [py2neo](https://py2neo.org/v4/)
* [pandas](https://pandas.pydata.org/)
* [datetime](https://docs.python.org/3/library/datetime.html)
* [os](https://docs.python.org/3/library/os.html)
* [sys](https://docs.python.org/3/library/sys.html)
* [socket](https://docs.python.org/3/library/socket.html)
* [inspect](https://docs.python.org/3/library/inspect.html)
* [logging](https://docs.python.org/3/library/logging.html)

## Tests
* the python test framework [pytest](https://docs.pytest.org/en/latest/) is used
* run the tests from the head directory by `pytest tests/`

## Linter
* the python linter [flake8](https://pypi.org/project/flake8/) is used with the call `flake8 --statistics --ignore E501,E402,E221,F401`
* -> the maximum length of the line and imports at the very beginning of the -py files are ignored
* -> imported but unused warning from `__init__.py` files
* the linter is not included in the CI pipeline, but it is recommended to use it

## Continous integration
* the CI pipeline was set up following a [realpython tutorial](https://realpython.com/python-continuous-integration/) 
