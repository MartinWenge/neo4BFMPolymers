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

        Parameters:
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

    def getSimulationRunsAndProjectByParameter(self, parameterName, parameterValue=None):
        """Returns a pandas dataframe of the "paths" from a Parameter note to the simulation project.

        Parameters:
            parameterName (str): full name of the ParameterNode name property
            parameterValue (str, optional): value of the ParameterNode to be more specific

        Returns:
            pandas dataframe of all simulation runs with the available information
            OR None if ParameterNode does not exits or does not include any simulationRuns
        """
        parameterNodeExists = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" RETURN elem.name".format(self.nodeType_parameter, parameterName))

        if parameterNodeExists is None:
            # if parameterNode does not exist print a list of all simulationProjects
            query = "MATCH(parameters:{}) RETURN DISTINCT parameters.name".format(self.nodeType_parameter)
            logger.warning("WARNING: {} does not exist in database. Following parameter names are available:".format(parameterName))
            logger.warning(self.graph.run(query).to_data_frame().values)
            return None
        else:
            if parameterValue is None:
                query = """MATCH (simProject:{})-[c1:{}]->(simRun:{})-[c2:{}]->(parameter:{} {{name:\"{}\"}})
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
                query = """MATCH (simProject:{})-[c1:{}]->(simRun:{})-[c2:{}]->(parameter:{} {{name:\"{}\", value:\"{}\"}})
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

    def getParametersByPolymer(self, polymerName):
        """Returns a pandas dataframe of the parameters (indirectly) connected to a polymer node.

        Parameters:
            polymerName (str): name of the polymer node to be started with

        Returns:
            pandas dataframe of all parameter nodes
            OR None if ParameterNode does not exits
        """
        parameterNodeExists = self.graph.evaluate("MATCH (elem:{}) RETURN elem.name".format(self.nodeType_parameter))
        if parameterNodeExists is None:
            logger.warning("WARNING: {} nodes do not exist in database.")
            return None

        polymerNodeExists = self.graph.evaluate("MATCH (elem:{} {{name:\"{}\"}}) RETURN elem.name".format(self.nodeType_polymer, polymerName))
        if polymerNodeExists is None:
            # if polymer node does not exist print a list of all polymers
            query = "MATCH(polymers:{}) RETURN DISTINCT polymers.name".format(self.nodeType_polymer)
            logger.warning("WARNING: {} does not exist in database. Following polymers names are available:".format(polymerName))
            logger.warning(self.graph.run(query).to_data_frame().values)
            return None

        query = """MATCH (polymer:{} {{name:\"{}\"}})<-[c0:{}]-(simProject:{})-[c1:{}]->(simRun:{})-[c2:{}]->(parameter:{})
        RETURN DISTINCT parameter.name, parameter.value, simProject.name, polymer.name
        ORDER BY simProject.name, parameter.name, parameter.value
        """.format(
            self.nodeType_polymer,
            polymerName,
            self.connectionType_polymerSimulationProject,
            self.nodeType_SimulationProject,
            self.connectionType_simTypeSimRun,
            self.nodeType_simulationRun,
            self.connectionType_simRunParameter,
            self.nodeType_parameter
        )
        result = self.graph.run(query)
        if result is None:
            logger.debug("WARNING: Parameter nodes not connected to {} nodes".format(self.nodeType_polymer))
            return None
        else:
            return result.to_data_frame()

    def getListOfPolymers(self, limit=None):
        """Returns a pandas dataframe containing all polymers.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all Polymer nodes
            OR None if there are no Polymer nodes
        """
        if limit:
            query = "MATCH (polymer:Polymer) RETURN DISTINCT polymer.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (polymer:Polymer) RETURN DISTINCT polymer.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no Polymer nodes")
            return None

    def getListOfSimulationProjects(self, limit=None):
        """Returns a pandas dataframe containing all simulation projects.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all SimulationProjects nodes
            OR None if there are no SimulationProjects nodes
        """
        if limit:
            query = "MATCH (simProject:SimulationProject) RETURN DISTINCT simProject.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (simProject:SimulationProject) RETURN DISTINCT simProject.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no SimulationProject nodes")
            return None

    def getListOfSimulationRuns(self, limit=None):
        """Returns a pandas dataframe containing all simulation runs.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all SimulationRuns nodes
            OR None if there are no SimulationRuns nodes
        """
        if limit:
            query = "MATCH (simRun:SimulationRun) RETURN DISTINCT simRun.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (simRun:SimulationRun) RETURN DISTINCT simRun.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no SimulationRun nodes")
            return None

    def getListOfParameters(self, limit=None):
        """Returns a pandas dataframe containing all parameters.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all Parameter nodes
            OR None if there are no Parameter nodes
        """
        if limit:
            query = "MATCH (parameter:Parameter) RETURN DISTINCT parameter.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (parameter:Parameter) RETURN DISTINCT parameter.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no Parameter nodes")
            return None

    def getListOfResultTypes(self, limit=None):
        """Returns a pandas dataframe containing all result types.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all Result nodes
            OR None if there are no Result nodes
        """
        if limit:
            query = "MATCH (result:Result) RETURN DISTINCT result.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (result:Result) RETURN DISTINCT result.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no Result nodes")
            return None

    def getListOfLeMonADEFeatures(self, limit=None):
        """Returns a pandas dataframe containing all LeMonADE features.

        Parameters:
            limit (int, default None): maximum number of list entries

        Returns:
            pandas dataframe of all LeMonADEFeature nodes
            OR None if there are no LeMonADEFeature nodes
        """
        if limit:
            query = "MATCH (feature:LeMonADEFeature) RETURN DISTINCT feature.name LIMIT {}".format(int(limit))
        else:
            query = "MATCH (feature:LeMonADEFeature) RETURN DISTINCT feature.name"
        results = self.graph.run(query)

        if results:
            return results.to_data_frame()
        else:
            logger.debug("WARNING: there are no Result nodes")
            return None
#
