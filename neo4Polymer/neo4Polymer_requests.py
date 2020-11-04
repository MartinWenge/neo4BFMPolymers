import logging


logger = logging.getLogger(__name__)


class neo4PolymerRequests:
    """Python class to perform search queries on a neo4j graph data base with polymer simulation data.

    This class provides a few functions to get the results of common queries performed on a database created by neo4BFMPolymer.

    The following node types are supported
    * Polymer - a class of polymer like linear chain, star polymer, ...
    * SimulationProject - a group of simulation runs with a certain topic or setup
      like linear polymer melt or star polymer solution
    * SimulationRun - a particular run of simulations with unique parameters
    * Parameter - a simulation parameter like BoxSize that may be connected to multiple simulation runs
    * LeMonADEFeature - a feature used for simulation or evaluation by LeMonADE
    * Result - a particular result of a simulation run that may be connected to an analyzer or a tool

    The following connectivity types are available
    * CONTAINS
    * INCLUDES
    * USES
    * ANALYZED
    """

    def __init__(self, graph):
        """Constructor of the neo4PolymerRequests class

        Parameters:
            graph (py2neo.Graph): instance of the graph to access the neo4j database
        """
        self.graph = graph

        self.connectionType_polymerSimulationProject = "CONTAINS"
        self.connectionType_simTypeSimRun = "INCLUDES"
        self.connectionType_simRunParameter = "USES"
        self.connectionType_simRunResult = "ANALYZED"

        self.nodeType_parameter = "Parameter"
        self.nodeType_simulationRun = "SimulationRun"
        self.nodeType_SimulationProject = "SimulationProject"
        self.nodeType_polymer = "Polymer"
        self.nodeType_feature = "LeMonADEFeature"
        self.nodeType_result = "Result"

    def getSimulationProjectsByPolymer(self, polymerName):
        """Returns a list of simulation projects containing a certain polymer type

        Parameters:
            polymer (str): name of the polymer type

        Returns:
            pandas array of all paths containing the requested simulation runs with the respective polymer
            OR None if the polymer was not found and a list of available polymers is printed to stdout
        """
        polymerExist = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" RETURN elem.name".format(self.nodeType_polymer, polymerName))

        if polymerExist is None:
            # if polymer does not exist print a list of all polymers
            query = "MATCH(polymer:{}) RETURN polymer.name".format(self.nodeType_polymer)
            logger.debug("WARNING: {} does not exist in database. Following polymers are available:".format(polymerName))
            logger.warning(self.graph.run(query).to_data_frame().values)
            return None
        else:
            query = "MATCH (polymer:{} {{name:\"{}\"}})-[:{}]-(simProject:{}) RETURN simProject.name, polymer.name".format(
                self.nodeType_polymer,
                polymerName,
                self.connectionType_polymerSimulationProject,
                self.nodeType_SimulationProject)
            result = self.graph.run(query)
            if result is None:
                logger.debug("WARNING: no simulation projects connected to {}: {}".format(self.nodeType_polymer, polymerName))
                return None
            else:
                return result.to_data_frame()

    def getSimulationRunsBySimulationProject(self, simProjectName):
        """Returns a pandas dataframe of all simulation runs included in one project

        Paramters:
            simProject (str): full name of the simulation project

        Returns:
            pandas dataframe of all simulation runs with the available information
            OR None if simulationProject does not exits or does not include any simulationRuns
        """
        simProjectExist = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" RETURN elem.name".format(self.nodeType_SimulationProject, simProjectName))

        if simProjectExist is None:
            # if simulationProject does not exist print a list of all simulationProjects
            query = "MATCH(simProject:{}) RETURN simProject.name".format(self.nodeType_SimulationProject)
            logger.warning("WARNING: {} does not exist in database. Following SimulationProjects are available:".format(simProjectName))
            logger.warning(self.graph.run(query).to_data_frame().values)
            return None
        else:
            query = "MATCH (simProject:{} {{name:\"{}\"}})-[:{}]-(simRun:{}) RETURN simRun.name, simRun.createdOn, simRun.path, simProject.name".format(
                self.nodeType_SimulationProject,
                simProjectName,
                self.connectionType_simTypeSimRun,
                self.nodeType_simulationRun)
            result = self.graph.run(query)
            if result is None:
                logger.debug("WARNING: no simulation projects connected to {}: {}".format(self.nodeType_SimulationProject, simProjectName))
                return None
            else:
                return result.to_data_frame()

    def getSimulationRunsAndProjectByParameter(self, parameterName, parameterValue = None):
        """Returns a pandas dataframe of the "paths" from a Parameter note to the simulation project.

        Paramters:
            parameterName (str): full name of the ParamterNode name property
            parameterValue (str, optional): value of the ParamterNode to be more specific

        Returns:
            pandas dataframe of all simulation runs with the available information
            OR None if ParameterNode does not exits or does not include any simulationRuns
        """
        parameterNodeExists = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" RETURN elem.name".format(self.nodeType_parameter, parameterName))

        if parameterNodeExists is None:
            # if parameterNode does not exist print a list of all simulationProjects
            query = "MATCH(parameters:{}) RETURN parameters.name".format(self.nodeType_parameter)
            logger.warning("WARNING: {} does not exist in database. Following parameter names are available:".format(parameterName))
            logger.warning(self.graph.run(query).to_data_frame().values)
            return None
        else:
            if parameterValue is None:
                query ="""MATCH (simProject:{})-[c1:{}]->(simRun:{})-[c2:{}]->(parameter:{} {{name:\"{}\"}})
                RETURN simProject.name, simRun.name, parameter.name, parameter.value
                ORDER BY simProject.name, parameter.value
                """.format(
                    self.nodeType_SimulationProject,
                    self.connectionType_simTypeSimRun,
                    self.nodeType_simulationRun,
                    self.connectionType_simRunParameter,
                    self.nodeType_parameter,
                    parameterName
                    )
            else:
                query ="""MATCH (simProject:{})-[c1:{}]->(simRun:{})-[c2:{}]->(parameter:{} {{name:\"{}\", value:\"{}\"}})
                RETURN simProject.name, simRun.name, parameter.name, parameter.value
                """.format(
                    self.nodeType_SimulationProject,
                    self.connectionType_simTypeSimRun,
                    self.nodeType_simulationRun,
                    self.connectionType_simRunParameter,
                    self.nodeType_parameter,
                    parameterName,
                    parameterValue
                    )
            result = self.graph.run(query)
            if result is None:
                logger.debug("WARNING: Parameter nodes not connected to {} nodes".format(self.nodeType_SimulationProject))
                return None
            else:
                return result.to_data_frame()
#
