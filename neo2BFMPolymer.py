from datetime import date
import os
import socket
import re
import neo4Polymer_bfmFileParser as bfmParser
import neo4Polymer_codmuc_RGTensorFileParser as codmucRgTParser
import neo4Polymer_linPolSol_RGFileParser as linPolSolRgParser
import neo4Polymer_singleDendr_RGFileParser as singleDendrRgTParser


class neo2BFMPolymer:
    """Python class to work on a neo4j graph data base with bfm polymer simulation data.

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

    Attributes:
        graph (py2neo.Graph): instance of the graph to access the neo4j database
        nodeMatcher (py2neo.NodeMatcher): matcher for the graph to evaluate nodes according to certain criteria.
        nodeMatcher (py2neo.RelationshipMatcher): matcher for the graph to evaluate relationships according to certain criteria.
    """
    def __init__(self, graph):
        """Constructor of the neo2BFMPolymer class

        Parameters:
            graph (py2neo.Graph): instance of the graph to access the neo4j database
        """
        self.graph = graph

        self.connectionType_polymerSimulationProject = "CONTAINS"
        self.connectionType_simTypeSimRun            = "INCLUDES"
        self.connectionType_simRunParameter          = "USES"
        self.connectionType_simRunResult             = "ANALYZED"

        self.nodeType_parameter         = "Parameter"
        self.nodeType_simulationRun     = "SimulationRun"
        self.nodeType_SimulationProject = "SimulationProject"
        self.nodeType_polymer           = "Polymer"
        self.nodeType_feature           = "LeMonADEFeature"
        self.nodeType_result            = "Result"

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## --------------    formatter functions   -------------- ###
    # ## -------------- # ## -------------- # ## -------------- ###
    def _featureName_format(self, featureName):
        '''remove template arguments from feature name'''
        idxTemplateBracket = featureName.find("<")
        if (idxTemplateBracket != -1):
            return featureName[:idxTemplateBracket]
        else:
            return featureName

    def _float_prec3_format(self, value):
        '''Helper function to define a consistent format of float value properties like in the NNInteraction Parameter Node

        Parameter:
            value (str,float): value to be converted to string containing a x.xxx formated float number

        Returns:
            formated string with a given precision to make for instance NNInteraction Parameter Node easily findable
        '''
        return "{0:.3f}".format(float(value))

    def _float_prec4_format(self, value):
        '''Helper function to define a consistent format of float value properties like in the result Nodes

        Parameter:
            value (str,float): value to be converted to string containing a x.xxxx formated float number

        Returns:
            formated string with a given precision to make for instance result Nodes easily findable
        '''
        return "{:.4f}".format(float(value))

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## --------------    utility functions   -------------- ###
    # ## -------------- # ## -------------- # ## -------------- ###
    def addNodeGeneral(self, nodeTypeName, nodeName):
        """Utility function adding a new node if it does not already exist.

        Paramters:
            nodeType (str): name of the node type
            nodeName (str): name property of the new node

        Returns:
            exit code (bool): True if node was added, False if node already exists
        """
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(nodeTypeName, nodeName)).data()
        if (len(elementExists) > 0):
            print("WARNING: node of type {} with name {} already exists!".format(nodeTypeName, nodeName))
            return False
        else:
            query = "CREATE (pl:{} {{ name: \'{}\', createdOn: \'{}\' }} )".format(nodeTypeName, nodeName, date.today())
            self.graph.run(query)
            return True

    def addParameterSimulationRunGeneral(self, simulationRunName, parameterName, parameterValue):
        '''Utility function to connect a SimulationRun node with a Parameter node of name parameterName with the value parameterValue.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            parameterName (str): name property of the Parameter node
            parameterValue (str): value property of the parameter node

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeTypeSimRun = self.nodeType_simulationRun
        nodeNameSimRun = simulationRunName

        nodeTypeParameter  = self.nodeType_parameter
        nodeNameParameter  = parameterName
        nodeValueParameter = parameterValue

        connectionType = self.connectionType_simRunParameter

        simRunExist    = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem.name".format(nodeTypeSimRun, nodeNameSimRun))
        parameterExist = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" AND elem.value=\"{}\" return elem.value".format(nodeTypeParameter, nodeNameParameter, nodeValueParameter))

        if (simRunExist == nodeNameSimRun):
            # if box does not exist, create it
            if not (parameterExist == nodeValueParameter):
                query = "CREATE (bn:{} {{ name: \'{}\', createdOn: \'{}\', value: \'{}\' }} )".format(
                    nodeTypeParameter, nodeNameParameter, date.today(), nodeValueParameter)
                self.graph.run(query)

            query = "MATCH (sr:{} {{name:\"{}\"}})-[c:{}]-(res:{} {{name:\"{}\", value:\"{}\"}}) return type(c)".format(nodeTypeSimRun, nodeNameSimRun, connectionType, nodeTypeParameter, nodeNameParameter, nodeValueParameter)
            connectionExist = self.graph.evaluate(query)
            if(connectionExist == connectionType):
                print("WARNING: Connection between {} with name {} and {} with name {} and value {} already exist.".format(nodeTypeSimRun, nodeNameSimRun, nodeTypeParameter, nodeNameParameter, nodeValueParameter))
                return False

            # if we are here, the connection can be established
            query = '''MATCH (p:{}) WHERE p.name=\"{}\" AND p.value=\"{}\"
                           MATCH (s:{}) WHERE s.name=\"{}\"
                           MERGE (s)-[r:{}]-(p)
            '''.format(nodeTypeParameter, nodeNameParameter, nodeValueParameter, nodeTypeSimRun, nodeNameSimRun, connectionType)
            self.graph.run(query)
            return True

        else:
            print("WARNING: node of type {} with name {} does not exist!".format(nodeTypeSimRun, nodeNameSimRun))
            return False

    def addResultSimulationRunGeneral(self, simulationRunName, resultName, resultString):
        '''Adding a Result node to a particular SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            resultName (str): name property of the Result node
            resultString: the value of the result node as a formated string

        Returns:
            exit code (bool): True if Result was added, False if Result already exists
                              or SimulationRun node does not exist
        '''
        nodeTypeSimRun  = self.nodeType_simulationRun
        nodeNameSimRun  = simulationRunName
        nodeTypeResult  = self.nodeType_result
        nodeNameResult  = resultName
        nodeValueResult = resultString
        connectionType  = self.connectionType_simRunResult

        simRunExist = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem.name".format(nodeTypeSimRun, nodeNameSimRun))
        resultExist = self.graph.evaluate("MATCH (simRun:{} {{name:\"{}\"}})-[rel:{}]-(n:{} {{name:\"{}\"}}) return n.name".format(nodeTypeSimRun, nodeNameSimRun, connectionType, nodeTypeResult, nodeNameResult))

        if (simRunExist == nodeNameSimRun):
            if not (resultExist == nodeNameResult):
                query = "CREATE (result:{} {{ name: \'{}\', createdOn: \'{}\', value: \'{}\' }} )".format(
                    nodeTypeResult, nodeNameResult, date.today(), nodeValueResult)
                self.graph.run(query)

                # merge simulationRun node with result node
                query = '''MATCH (result:{}) WHERE result.name=\"{}\" AND result.value=\"{}\"
                           MATCH (simRun:{}) WHERE simRun.name=\"{}\"
                           MERGE (simRun)-[r:{}]->(result)
                '''.format(nodeTypeResult, nodeNameResult, nodeValueResult, nodeTypeSimRun, nodeNameSimRun, connectionType)
                self.graph.run(query)

                return True

            else:
                print("WARNING: node of type {} with name {} is already connected to {} node {}!".format(nodeTypeSimRun, nodeNameSimRun, nodeTypeResult, nodeNameResult))
                return False

        else:
            print("WARNING: node of type {} with name {} does not exist!".format(nodeTypeSimRun, nodeNameSimRun))
            return False

    def connectParameterToFeatureGeneral(self, featureName, parameterName, parameterValue):
        '''Connect a LeMonADEFeature to a Parameter node that is stored by this feature.

        Parameters:
            featureName (str): name property of the Feature node
            parameterName (str): name property of the Parameter node
            parameterValue (str): value property of the Parameter node

        Returns:
            exit code (bool): True if Feature was added or the connection already existed
                              False if the Feature does not exist
        '''
        nodeTypeFeature  = self.nodeType_feature
        nodeNameFeature  = featureName

        nodeTypeParameter  = self.nodeType_parameter
        nodeNameParamter   = parameterName
        nodeValueParameter = parameterValue
        connectionType     = self.connectionType_simRunParameter

        featureExist   = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem.name".format(nodeTypeFeature, nodeNameFeature))
        if not (featureExist == nodeNameFeature):
            print("WARNING: node of type {} with name {} does not exist! Cannot connect to Parameter".format(nodeTypeFeature, nodeNameFeature))
            return False

        parameterExist = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" AND elem.value=\"{}\" return elem.name".format(nodeTypeParameter, nodeNameParamter, nodeValueParameter))
        if not (parameterExist == nodeNameParamter):
            print("WARNING: node of type {} with name {} and value {} does not exist! Cannot connect to Feature".format(nodeTypeParameter, nodeNameParamter, nodeValueParameter))
            return False

        connectExist = self.graph.evaluate("MATCH (feat:{} {{name:\"{}\"}})-[rel:{}]-(n:{} {{name:\"{}\", value:\"{}\"}}) return n.name".format(nodeTypeFeature, nodeNameFeature, connectionType, nodeTypeParameter, nodeNameParamter, nodeValueParameter))
        if (connectExist == nodeNameParamter):
            # connection already exist, print a message here?
            print("{} with name {} already connected to {} with name {} and value {}".format(nodeTypeFeature, nodeNameFeature, nodeTypeParameter, nodeNameParamter, nodeValueParameter))
            return True
        else:
            # merge feature node with parameter node
            query = '''MATCH (param:{}) WHERE param.name=\"{}\" AND param.value=\"{}\"
                       MATCH (feature:{}) WHERE feature.name=\"{}\"
                       MERGE (param)-[r:{}]->(feature)
            '''.format(nodeTypeParameter, nodeNameParamter, nodeValueParameter, nodeTypeFeature, nodeNameFeature, connectionType)
            self.graph.run(query)
            return True

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## --------------   add node functions   -------------- ###
    # ## -------------- # ## -------------- # ## -------------- ###
    def addNewPolymer(self, polymerName):
        """Adding a new Polymer node to the database.

        This function adds a node of type Polymer with the given name and a date tag to the database.
        If the database already contains a Polymer node with this name property, a warning is printed
        and no create query is called to avoid node doubling.

        Paramters:
            polymerName (str): name property of the new Polymer node

        Returns:
            exit code (bool): True if node was added, False if node already exists
        """
        nodeTypeName     = self.nodeType_polymer
        nodePropertyName = polymerName

        return self.addNodeGeneral(nodeTypeName, nodePropertyName)

    def addNewSimulationProject(self, SimulationProjectName):
        """Adding a new SimulationProject node to the database.

        A SimulationProject node represents a certain simulation setup such as "linear polymer melt" or "single star polymer".
        This function adds a node of type SimulationProject with the given name and a date tag to the database.
        If the database already contains a SimulationProject node with this name property, a warning is printed
        and no create query is called to avoid node doubling.

        Paramters:
            SimulationProjectName (str): name property of the new SimulationProject node

        Returns:
            exit code (bool): True if node was added, False if node already exists
        """
        nodeTypeName     = self.nodeType_SimulationProject
        nodePropertyName = SimulationProjectName

        return self.addNodeGeneral(nodeTypeName, nodePropertyName)

    def addSimulationRunToSimulationProject(self, simulationRunName, SimulationProjectName, path=None):
        '''Add a new node of Type SimulationRun to the database.

        A SimulationRun node represents a particular simulation with all its paramters, the computation details
        and - if available - a path to the simulation files.
        The parameters are connected to the SimulationRun as self-contained nodes to find simulations
        with same paramters.
        A SimulationRun must belong to a SimulationProject.
        This function adds a node of Type SimulationRun with the given name and a date tag to the database.
        If the database already contains a SimulationRun node with this name property, a warning is printed
        and no create query is called to avoid node doubling.

        Paramters:
            simulationRunName (str): name property of the new SimulationRun node
            SimulationProjectName(str): name property of the corresponding SimulationProject node

        Returns:
            exit code (bool): True if node was added, False if node already exists
        '''
        nodeTypeNameSimRun = self.nodeType_simulationRun
        nodeNameSimRun     = simulationRunName

        nodeTypeNameSimType = self.nodeType_SimulationProject
        nodeNameSimType     = SimulationProjectName

        connectionType = self.connectionType_simTypeSimRun

        if self.addNodeGeneral(nodeTypeNameSimRun, nodeNameSimRun):
            query = '''MATCH (run:{}) WHERE run.name=\"{}\"
                       MATCH (type:{}) WHERE type.name=\"{}\"
                       MERGE (type)-[r:{}]->(run)
            '''.format(nodeTypeNameSimRun, nodeNameSimRun, nodeTypeNameSimType, nodeNameSimType, connectionType)
            self.graph.run(query)

            return True
        else:
            print("WARNING: node of type {} with name {} could not be added to {}".format(nodeTypeNameSimRun, nodeNameSimRun, nodeNameSimType))
            return False

    def addPathToSimulationRun(self, simulationRunName, filePath):
        ''' Adding a path property to a SimulationRun node to find the source files.

        Parameters:
            simulationRunName (str): name property of the SimulationRun node
            filePath (str): full path to the file locations sourced for this node,
                        multiple paths may be added if there are backups
                        or different file types with different locations

        Returns:
            exit code (bool): True if node was added, False if something went wrong
        '''
        nodeTypeNameSimRun = self.nodeType_simulationRun
        nodeNameSimRun     = simulationRunName

        propertyName = "path"
        propertyValue = filePath

        # if SimulationRun node does not exist, complain and stop
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(nodeTypeNameSimRun, nodeNameSimRun)).data()
        if (len(elementExists) < 1):
            print("WARNING: node of type {} with name {} does not exist\ncannot add {}".format(nodeTypeNameSimRun, nodeNameSimRun, propertyName))
            return False
        # if SimulationRun node exists more than once, complain and stop
        if (len(elementExists) > 1):
            print("WARNING: node of type {} with name {} exists more than once".format(nodeTypeNameSimRun, nodeNameSimRun))
            return False

        # get the node properties
        nodeProperties = elementExists[0].get("elem")
        # get python dictionary of node properties
        nodePropDict = dict(nodeProperties)

        # check if path was already set and add additional property is necessary
        nodePropKeyList = list(nodePropDict.keys())
        if(propertyName in nodePropKeyList):
            # get list of property values from dict
            nodePropValuesList = list(nodePropDict.values())
            if(propertyValue in nodePropValuesList):
                print("WARNING: path {} already exists in {}".format(propertyValue, nodeNameSimRun))
                return False

            # add new paths by index like path_x
            pathIdxCounter = 1
            pathPropertyName = "path_{}".format(pathIdxCounter)
            pathNotAdded = True
            while (pathNotAdded and (pathIdxCounter < 10)):
                if (pathPropertyName in nodePropKeyList):
                    pathIdxCounter = pathIdxCounter + 1
                    pathPropertyName = "path_{}".format(pathIdxCounter)
                else:
                    # set current path property name to the variable passed to the cypher query
                    propertyName = pathPropertyName
                    pathNotAdded = False
                    print("path {} is added to {} in property named {}".format(propertyValue, nodeNameSimRun, propertyName))
                    break

        query = '''MATCH (elem:{}) WHERE elem.name=\"{}\"
                   SET elem.{} = \"{}\"
                '''.format(nodeTypeNameSimRun, nodeNameSimRun, propertyName, propertyValue)
        self.graph.run(query)
        return True

    def addFeatureToSimulationRun(self, simulationRunName, featureName):
        '''Connect a LeMonADEFeature node to a SimulationRun already present in the database.

        A LeMonADEFeature node holds the name with all template parameters of a particular feature
        used in the simulation or the evaluation tool, if LeMonADE was used here.
        The node is connected to the simulationRun and can be connected to a parameter,
        if this is set in a feature.

        Parameters:
            simulationRunName (str): name property of the SimulationRun node
            featureName (str): name property of the feature node to be connected to the SimulationRun

        Returns:
            exit code (bool): True if node was added, False if something went wrong
        '''
        nodeTypeNameSimRun = self.nodeType_simulationRun
        nodeNameSimRun     = simulationRunName

        nodeTypeFeature = self.nodeType_feature
        # truncate the feature name to skip template parameters
        nodeNameFeature = self._featureName_format(featureName)

        connectionType = self.connectionType_simRunParameter  # "USES"

        # if SimulationRun node does not exist, complain and stop
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(nodeTypeNameSimRun, nodeNameSimRun)).data()
        if (len(elementExists) < 1):
            print("WARNING: node of type {} with name {} does not exist\ncannot connect to {}".format(nodeTypeNameSimRun, nodeNameSimRun, nodeNameFeature))
            return False

        # if feature does not exist, add it
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(nodeTypeFeature, nodeNameFeature)).data()
        if (len(elementExists) < 1):
            self.addNodeGeneral(nodeTypeFeature, nodeNameFeature)

        # if connection does not exist, add it
        elementExists = self.graph.run("MATCH (sr:{} {{name: \"{}\"}} )-[c:{}]->(f:{} {{name: \"{}\"}}) return c".format(nodeTypeNameSimRun, nodeNameSimRun, connectionType, nodeTypeFeature, nodeNameFeature)).data()
        if (len(elementExists) < 1):
            query = '''MATCH (run:{}) WHERE run.name=\"{}\"
                       MATCH (feature:{}) WHERE feature.name=\"{}\"
                       MERGE (run)-[c:{}]->(feature)
            '''.format(nodeTypeNameSimRun, nodeNameSimRun, nodeTypeFeature, nodeNameFeature, connectionType)
            self.graph.run(query)
            return True
        # otherwise print a message, but return True
        else:
            print("WARNING: {} with name {} was already connected to {} with name {}".format(nodeTypeFeature, nodeNameFeature, nodeTypeNameSimRun, nodeNameSimRun))
            return True

    def connectSimulationToPolymer(self, polymerName, simulationName):
        """Connecting a node of type Polymer with a node of type SimulationProject by a CONTAINS

        A connection of type CONTAINS is added between a Polymer node and a Simulation node,
        heading in the direction of the polymer.
        The connection is only created if the nodes exist and the connection did not already exist.
        In this case, a warning is printed.

        Parameters:
            polymerName (str): name of the Polymer node
            simulationName (str): name of the SimulationProject node

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        """
        nodeType1 = self.nodeType_polymer
        nodeName1 = polymerName
        nodeType2 = self.nodeType_SimulationProject
        nodeName2 = simulationName

        connectionType = self.connectionType_polymerSimulationProject

        elementExists1 = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem.name".format(nodeType1, nodeName1))
        elementExists2 = self.graph.evaluate("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem.name".format(nodeType2, nodeName2))

        if (elementExists1 == nodeName1):
            if (elementExists2 == nodeName2):
                query = "MATCH( ({} {{ name: \'{}\'}}) <- [rel:{}] - ({} {{ name: \'{}\'}}) ) return rel".format(
                    nodeType1, nodeName1, connectionType, nodeType2, nodeName2)
                elementExists = self.graph.evaluate(query)
                if (elementExists is None):
                    query = '''MATCH (p:{}) WHERE p.name=\"{}\"
                               MATCH (s:{}) WHERE s.name=\"{}\"
                               MERGE (s)-[r:{}]->(p)
                    '''.format(nodeType1, nodeName1, nodeType2, nodeName2, connectionType)
                    self.graph.run(query)
                    return True

                else:
                    print("WARNING: connection of type {} between {} and {} already exist!".format(connectionType, nodeName1, nodeName2))
                    return False

            else:
                print("WARNING: node of type {} with name {} does not exist!".format(nodeType2, nodeName2))
                return False

        else:
            print("WARNING: node of type {} with name {} does not exist!".format(nodeType1, nodeName1))
            return False

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## -------------- add parameter functions ------------- ###
    # ## -------------- # ## -------------- # ## -------------- ###
    def addBoxSizeToSimulationRun(self, simulationRunName, boxX, boxY, boxZ):
        '''Connect a SimulationRun node with a Parameter node of name BoxSize with the given values.

        A parameter node with name BoxSize contains a value in the form "boxX x boxY x boxZ"
        used in FeatureBox of LeMonADE that can be connected to any SimulationRun node that uses this parameter.
        If the box node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            boxX (int): box dimension in x-direction
            boxY (int): box dimension in y-direction
            boxZ (int): box dimension in z-direction

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "BoxSize"
        nodeValue      = "[{}, {}, {}]".format(boxX, boxY, boxZ)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addPeriodicityToSimulationRun(self, simulationRunName, pX, pY, pZ):
        '''Connect a SimulationRun node with a Parameter node of name Periodicity with the given values.

        A parameter node with name Periodicity contains a value in the form "[pX, pY, pZ]" encoded as bool (True:0, False:1)
        used in FeatureBox of LeMonADE that can be connected to any SimulationRun node that uses this parameter.
        If the Periodicity node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            pX (bool): periodicity in x-direction (0 = periodic, 1 = non-periodic)
            pY (bool): periodicity in y-direction (0 = periodic, 1 = non-periodic)
            pZ (bool): periodicity in z-direction (0 = periodic, 1 = non-periodic)

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "Periodicity"
        nodeValue      = "[{0:d}, {1:d}, {2:d}]".format(int(pX), int(pY), int(pZ))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addVolumeFractionToSimulationRun(self, simulationRunName, volFrac):
        '''Connect a SimulationRun node with a Parameter node of name VolumeFraction with the given value.

        A parameter node with name VolumeFraction contains a float value in the form x.xxx.
        used in FeatureBox of LeMonADE that can be connected to any SimulationRun node that uses this parameter.
        If the VolumeFraction node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            volFrac (float): volume fraction of a particular component

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "VolumeFraction"
        nodeValue      = self._float_prec3_format(volFrac)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNNInteractionToSimulationRun(self, simulationRunName, epsilon):
        '''Connect a SimulationRun node with a Parameter node of name NNInteraction with the given value.

        A parameter node with name NNInteraction contains a value epsilon set in FeatureNNInteraction of LeMonADE
        that can be connected to any SimulationRun node that uses this parameter.
        If the NNInteraction node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            epsilon (float): interaction energy per nearest neighbor lattice point

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NNInteraction"
        nodeValue      = self._float_prec3_format(epsilon)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addLinearChainLengthToSimulationRun(self, simulationRunName, N):
        '''Connect a SimulationRun node with a Parameter node of name LinearChainLength with the given value.

        A parameter node with name LinearChainLength contains a value N as common parameter
        that can be connected to any SimulationRun node that uses this parameter.
        If the LinearChainLength node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            n (int): number of BFM units of a linear chain

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "LinearChainLength"
        nodeValue      = "{}".format(N)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addGraftedChainLengthToSimulationRun(self, simulationRunName, N):
        '''Connect a SimulationRun node with a Parameter node of name GraftedChainLength with the given value.

        A parameter node with name GraftedChainLength contains a value N as common parameter
        that can be connected to any SimulationRun node that uses this parameter.
        If the GraftedChainLength node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            n (int): number of BFM units of a grafted linear chain

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "GraftedChainLength"
        nodeValue      = "{}".format(N)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addDendrimerGenerationToSimulationRun(self, simulationRunName, G):
        '''Connect a SimulationRun node with a Parameter node of name DendrimerGeneration with the given value.

        A parameter node with name DendrimerGeneration contains a value G
        that can be connected to any SimulationRun node that uses this parameter.
        If the DendrimerGeneration node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            G (int): number of generations in a dendrimer molecule

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "DendrimerGeneration"
        nodeValue      = "{}".format(G)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addDendrimerSpacerLengthToSimulationRun(self, simulationRunName, S):
        '''Connect a SimulationRun node with a Parameter node of name DendrimerSpacerLength with the given value.

        A parameter node with name DendrimerSpacerLength contains a value S
        that can be connected to any SimulationRun node that uses this parameter.
        If the DendrimerSpacerLength node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            S (int): number of BFM units between two branching points of a dendrimer

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "DendrimerSpacerLength"
        nodeValue      = "{}".format(S)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addDendrimerCoreFunctionalityToSimulationRun(self, simulationRunName, Fc):
        '''Connect a SimulationRun node with a Parameter node of name DendrimerCoreFunctionality with the given value.

        A parameter node with name DendrimerCoreFunctionality contains a value Fc
        that can be connected to any SimulationRun node that uses this parameter.
        If the DendrimerCoreFunctionality node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            Fc (int): number of connections of the dendrimer core monomer (focal point)

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "DendrimerCoreFunctionality"
        nodeValue      = "{}".format(Fc)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addDendrimerBranchingPointFunctionalityToSimulationRun(self, simulationRunName, Fb):
        '''Connect a SimulationRun node with a Parameter node of name DendrimerBranchingPointFunctionality with the given value.

        A parameter node with name DendrimerBranchingPointFunctionality contains a value Fb
        that can be connected to any SimulationRun node that uses this parameter.
        If the DendrimerBranchingPointFunctionality node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            Fb (int): number of connections of the dendrimer branching points (except the focal point)

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "DendrimerBranchingPointFunctionality"
        nodeValue      = "{}".format(Fb)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addTotalNumberOfMonomersToSimulationRun(self, simulationRunName, N):
        '''Connect a SimulationRun node with a Parameter node of name TotalNumberOfMonomers with the given value.

        A parameter node with name TotalNumberOfMonomers contains a value N
        that can be connected to any SimulationRun node that uses this parameter.
        If the TotalNumberOfMonomers node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            N (int): total number of BFM units in a simulation box

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "TotalNumberOfMonomers"
        nodeValue      = "{}".format(N)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfRingsToSimulationRun(self, simulationRunName, nRings):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfRings with the given value.

        A parameter node with name NumberOfRings contains a value nRings
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfRings node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nRings (int): total number of BFM units in the ring polymer

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfRings"
        nodeValue      = "{}".format(int(nRings))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfMonomersInRingToSimulationRun(self, simulationRunName, nMonosRing):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfMonomersInRing with the given value.

        A parameter node with name NumberOfMonomersInRing contains a value nMonosRing
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfMonomersInRing node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nMonosRing (int): total number of BFM units in the ring polymer

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfMonomersInRing"
        nodeValue      = "{}".format(int(nMonosRing))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfTendomersToSimulationRun(self, simulationRunName, nTendomers):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfTendomers with the given value.

        A parameter node with name NumberOfTendomers contains a value nTendomers
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfTendomers node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nTendomers (int): number of tendomers in simulation box

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfTendomers"
        nodeValue      = "{}".format(int(nTendomers))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfCrosslinkersToSimulationRun(self, simulationRunName, nCrossLinker):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfCrosslinkers with the given value.

        A parameter node with name NumberOfCrosslinkers contains a value nCrossLinker
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfCrosslinkers node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nCrossLinker (int): number of crosslinkers in tendomer system

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfCrosslinkers"
        nodeValue      = "{}".format(int(nCrossLinker))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfLabelsPerArmToSimulationRun(self, simulationRunName, nLabels):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfLabelsPerArm with the given value.

        A parameter node with name NumberOfLabelsPerArm contains a value nLabels
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfLabelsPerArm node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nLabels (int): number of labels per tendomer arm

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfLabelsPerArm"
        nodeValue      = "{}".format(int(nLabels))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addNumberOfMonomersPerChainToSimulationRun(self, simulationRunName, nMonoPerChain):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfMonomersPerChain with the given value.

        A parameter node with name NumberOfMonomersPerChain contains a value nMonoPerChain
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfMonomersPerChain node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            nMonoPerChain (int): number of monomers per chain in tendomer system

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "NumberOfMonomersPerChain"
        nodeValue      = "{}".format(int(nMonoPerChain))

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addSpringConstantToSimulationRun(self, simulationRunName, springConst):
        '''Connect a SimulationRun node with a Parameter node of name NumberOfMonomersPerChain with the given value.

        A parameter node with name NumberOfMonomersPerChain contains a value springConst
        that can be connected to any SimulationRun node that uses this parameter.
        If the NumberOfMonomersPerChain node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            springConst (float): spring constant k of harmonic spring potential

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "SpringConstant"
        nodeValue      = self._float_prec3_format(springConst)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addSpringLengthToSimulationRun(self, simulationRunName, springLength):
        '''Connect a SimulationRun node with a Parameter node of name SpringLength with the given value.

        A parameter node with name SpringLength contains a value springLength
        that can be connected to any SimulationRun node that uses this parameter.
        If the SpringLength node does not exist, it is created and then connected to the SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            springLength (float): equilibrium length r0 of harmonic spring potential

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "SpringLength"
        nodeValue      = self._float_prec3_format(springLength)

        return self.addParameterSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## --------------   add result functions  ------------- ###
    # ## -------------- # ## -------------- # ## -------------- ###

    def addResultRadiusOfGyration(self, simulationRunName, Rg):
        '''Adding a Result node with a single value or an array of the radius of gyration of a particular SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            Rg (float,array): radius of gyration calculated for the conformations in the simulation run.

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "RadiusOfGyration"
        nodeValue      = str(Rg)  # this needs to be improved!

        return self.addResultSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addResultAsphericity(self, simulationRunName, A):
        '''Adding a Result node with a single value or an array of the asphericity of a particular SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            A (float,array): asphericity calculated for the conformations in the simulation run.

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "Asphericity"
        nodeValue      = str(A)  # this needs to be improved!

        return self.addResultSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    def addResultCenterToCenterDistribution(self, simulationRunName, c2c):
        '''Adding a Result node with an array of the center to center distances of a particular SimulationRun.

        Parameters:
            simulationRunName (str): name of the SimulationRun node
            c2c (array): radius of gyration calculated for the conformations in the simulation run.

        Returns:
            exit code (bool): True if connection was added, False if connection already exists
                              or SimulationRun node does not exist
        '''
        nodeNameSimRun = simulationRunName
        nodeName       = "c2cDistribution"
        nodeValue      = str(c2c)  # this needs to be improved!

        return self.addResultSimulationRunGeneral(nodeNameSimRun, nodeName, nodeValue)

    # ## -------------- # ## -------------- # ## -------------- ###
    # ## ----------   complex functions with helpers  --------- ###
    # ## -------------- # ## -------------- # ## -------------- ###
    def _findElementInKeyValueDataList(self, search, keyValueDataList):
        '''Helper function to extract the value of a certain key of the result list provided by the file parser.

        Paramters:
            search (str): key of the data element that may be added to the database
            keyValueDataList (list): list of data from the file parser
                                     with structure [[key1, value1], [key2, value2],...]

        Returns:
            value (if the key exists) or None
        '''
        result = [dataArrayElement[1] for dataArrayElement in keyValueDataList if dataArrayElement[0] == search]
        if result == []:  # or if not result
            print("{} not found".format(search))
            return None
        else:
            return result

    def addBFMFileToDatabase(self, simulationRunName, filename):
        '''High level user function to add nodes to the database by reading a BFM file header.

        Parameters:
            simulationRunName (str): name of the simulationRun
            filename (str): name of the BFM file

        Returns:
            True if file content was added properly
            False if errors occur
        '''
        # first check if the simulation run exists
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(self.nodeType_simulationRun, simulationRunName)).data()
        if (len(elementExists) == 0):
            print("WARNING: {} does not exist. To add data from a BFM file, the simulationRun node must exist!".format(simulationRunName))
            return False

        # check if file exists
        if(os.path.isfile(filename)):
            # get full path to filename WITHOUT backslashes!
            pathToBfmFile = "{}: {}".format(socket.gethostname(), os.path.abspath(filename))
            checkForBackslashes = pathToBfmFile.replace('\\', '/')
            if (pathToBfmFile != checkForBackslashes):
                pathToBfmFile = checkForBackslashes
                print("WARNING: replaced backslashes in filepath to slashes: {}".format(pathToBfmFile))

            # now you may add it to the simulationRun node
            self.addPathToSimulationRun(simulationRunName, pathToBfmFile)
        else:
            print("WARNING: file {} does not exist!".format(filename))
            return False

        # start the bfm file reader
        fileReader = bfmParser.neo4Polymer_BFM_fileparser(filename)

        # get the data-array
        dataArray = fileReader.parse_file()

        # extract a keywords from the data array
        # start with features to connect the parameters!

        # ## ---------  features  --------- ###
        featureKey = "feature_name"

        featureList_full = self._findElementInKeyValueDataList(featureKey, dataArray)
        # TODO: consider cases where parameter list might be usefull?
        # TODO: feature name is formatted again in the addFeatureToSimulationRun for robustness, usefull?
        featureList = [self._featureName_format(f) for f in featureList_full]

        if(featureList is not None):
            for feature in featureList:
                self.addFeatureToSimulationRun(simulationRunName, feature)
        # ## ---------  features  --------- ###

        # ## collect information from all available features
        # ## ------- FeatureMoleculesIO ## #
        featureName = "FeatureMoleculesIO"
        if (featureName in featureList):
            numOfMonomersKey = "number_of_monomers"
            numOfMonomers = self._findElementInKeyValueDataList(numOfMonomersKey, dataArray)
            if(numOfMonomers is not None):
                self.addTotalNumberOfMonomersToSimulationRun(simulationRunName, int(numOfMonomers[0]))

            # other keys provided: !bonds, !add_bonds, !remove_bonds, !mcs
        # ## ------- FeatureMoleculesIO ## #

        # ## ------- FeatureMoleculesIOUnsaveCheck ## #
        featureName = "FeatureMoleculesIOUnsaveCheck"
        if (featureName in featureList):
            numOfMonomersKey = "number_of_monomers"
            numOfMonomers = self._findElementInKeyValueDataList(numOfMonomersKey, dataArray)
            if(numOfMonomers is not None):
                self.addTotalNumberOfMonomersToSimulationRun(simulationRunName, int(numOfMonomers[0]))

            # other keys provided: !bonds, !add_bonds, !remove_bonds, !mcs
        # ## ------- FeatureMoleculesIOUnsaveCheck ## #

        # ## ------- FeatureBox ---------- ###
        featureName = "FeatureBox"
        if (featureName in featureList):
            boxSizeKeyX = "box_x"
            boxSizeX = (self._findElementInKeyValueDataList(boxSizeKeyX, dataArray))[0]

            boxSizeKeyY = "box_y"
            boxSizeY = (self._findElementInKeyValueDataList(boxSizeKeyY, dataArray))[0]

            boxSizeKeyZ = "box_z"
            boxSizeZ = (self._findElementInKeyValueDataList(boxSizeKeyZ, dataArray))[0]

            # sanity check: box size should be defined for all dimensions
            if ((boxSizeX is None) or (boxSizeX is None) or (boxSizeX is None)):
                print("WARNING: boxsize is not defined for all dimensions. Box Size node is NOT added")
            else:
                self.addBoxSizeToSimulationRun(simulationRunName, boxSizeX, boxSizeY, boxSizeZ)
                parameterName = "BoxSize"
                parameterValue = "[{}, {}, {}]".format(boxSizeX, boxSizeY, boxSizeZ)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            periodicityKeyX = "periodic_x"
            periodicityX = (self._findElementInKeyValueDataList(periodicityKeyX, dataArray))[0]

            periodicityKeyY = "periodic_y"
            periodicityY = (self._findElementInKeyValueDataList(periodicityKeyY, dataArray))[0]

            periodicityKeyZ = "periodic_z"
            periodicityZ = (self._findElementInKeyValueDataList(periodicityKeyZ, dataArray))[0]

            # sanity check: periodicity should be defined for all dimensions
            if ((periodicityX is None) or (periodicityY is None) or (periodicityZ is None)):
                print("WARNING: periodicity is not defined for all dimensions. Periodicity node is NOT added")
            else:
                self.addPeriodicityToSimulationRun(simulationRunName, periodicityX, periodicityY, periodicityZ)
                parameterName = "Periodicity"
                parameterValue = "[{0:d}, {1:d}, {2:d}]".format(int(periodicityX), int(periodicityY), int(periodicityZ))
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## ------- FeatureBox ---------- ###

        # ## ------- FeatureNNInteraction ---------- ###
        featureName = "FeatureNNInteraction"
        # TODO: this feature is deprecated, should be noted somewhere
        if (featureName in featureList):
            nn_interactionKey = "nn_interaction"
            nn_intertaction = self._findElementInKeyValueDataList(nn_interactionKey, dataArray)
            parameterName = "NNInteraction"
            if(nn_intertaction is not None):
                if(all(x == nn_intertaction[0] for x in nn_intertaction)):
                    parameterValue = self._float_prec3_format(nn_intertaction[0])
                    if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                        self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
                else:
                    print("WARNING: nn_interaction contains more than one value: {}\nTry to add all values, more Warnings may pop up".format(nn_intertaction))
                    for nn in nn_intertaction:
                        parameterValue = self._float_prec3_format(nn)
                        if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                            self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## ------- FeatureNNInteraction ---------- ###

        # ## ------- FeatureNNInteractionSc ---------- ###
        featureName = "FeatureNNInteractionSc"
        if (featureName in featureList):
            nn_interactionKey = "nn_interaction"
            nn_intertaction = self._findElementInKeyValueDataList(nn_interactionKey, dataArray)
            parameterName = "NNInteraction"
            if(nn_intertaction is not None):
                if(all(x == nn_intertaction[0] for x in nn_intertaction)):
                    parameterValue = self._float_prec3_format(nn_intertaction[0])
                    if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                        self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
                else:
                    print("WARNING: nn_interaction contains more than one value: {}\nTry to add all values, more Warnings may pop up".format(nn_intertaction))
                    for nn in nn_intertaction:
                        parameterValue = self._float_prec3_format(nn)
                        if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                            self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## ------- FeatureNNInteractionSc ---------- ###

        # ## ------- FeatureNNInteractionBcc ---------- ###
        featureName = "FeatureNNInteractionBcc"
        if (featureName in featureList):
            nn_interactionKey = "nn_interaction"
            nn_intertaction = self._findElementInKeyValueDataList(nn_interactionKey, dataArray)
            parameterName = "NNInteraction"
            if(nn_intertaction is not None):
                if(all(x == nn_intertaction[0] for x in nn_intertaction)):
                    parameterValue = nn_intertaction[0]
                    if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                        self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
                else:
                    print("WARNING: nn_interaction contains more than one value: {}\nTry to add all values, more Warnings may pop up".format(nn_intertaction))
                    for nn in nn_intertaction:
                        parameterValue = nn
                        if(self.addNNInteractionToSimulationRun(simulationRunName, parameterValue)):
                            self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## ------- FeatureNNInteractionBcc ---------- ###

        # ## -----  FeatureSystemInformationRingMelt ------ ## #
        featureName = "FeatureSystemInformationRingMelt"
        if (featureName in featureList):
            numOfRingsKey = "number_of_rings"
            numOfRings = self._findElementInKeyValueDataList(numOfRingsKey, dataArray)
            if (numOfRings is not None):
                parameterName = "NumberOfRings"
                parameterValue = numOfRings[0]
                self.addNumberOfRingsToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            numOfMonomersInRingKey = "number_of_monomers_per_ring"
            numOfMonomersInRing = self._findElementInKeyValueDataList(numOfMonomersInRingKey, dataArray)
            if (numOfMonomersInRing is not None):
                parameterName = "NumberOfMonomersInRing"
                parameterValue = numOfMonomersInRing[0]
                self.addNumberOfMonomersInRingToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## -----  FeatureSystemInformationRingMelt ------ ## #

        # ## -----  FeatureSystemInformationTendomer ------ ## #
        featureName = "FeatureSystemInformationTendomer"
        if (featureName in featureList):
            numOfTendomersKey = "number_of_tendomers"
            numOfTendomers = self._findElementInKeyValueDataList(numOfTendomersKey, dataArray)
            if (numOfTendomers is not None):
                parameterName = "NumberOfTendomers"
                parameterValue = numOfTendomers[0]
                self.addNumberOfTendomersToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            numOfCrosslinkersKey = "number_of_crosslinkers"
            numOfCrosslinkers = self._findElementInKeyValueDataList(numOfCrosslinkersKey, dataArray)
            if (numOfCrosslinkers is not None):
                parameterName = "NumberOfCrosslinkers"
                parameterValue = numOfCrosslinkers[0]
                self.addNumberOfCrosslinkersToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            numOfLabelsPerArmKey = "number_of_labels_per_arm"
            numOfLabelsPerArm = self._findElementInKeyValueDataList(numOfLabelsPerArmKey, dataArray)
            if (numOfLabelsPerArm is not None):
                parameterName = "NumberOfLabelsPerArm"
                parameterValue = numOfLabelsPerArm[0]
                self.addNumberOfLabelsPerArmToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            numOfMonomersPerChainKey = "number_of_monomers_per_chain"
            numOfMonomersPerChain = self._findElementInKeyValueDataList(numOfMonomersPerChainKey, dataArray)
            if (numOfMonomersPerChain is not None):
                parameterName = "NumberOfMonomersPerChain"
                parameterValue = numOfMonomersPerChain[0]
                self.addNumberOfMonomersPerChainToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## -----  FeatureSystemInformationTendomer ------ ## #

        # ## -----  FeatureSystemInformationDendrimer ------ ## #
        featureName = "FeatureSystemInformationDendrimer"
        if (featureName in featureList):
            generationKey = "dendrimer_generation"
            generation = self._findElementInKeyValueDataList(generationKey, dataArray)
            if (generation is not None):
                parameterName = "DendrimerGeneration"
                parameterValue = generation[0]
                self.addDendrimerGenerationToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            spacerLengthKey = "dendrimer_spacer_length"
            spacerLength = self._findElementInKeyValueDataList(spacerLengthKey, dataArray)
            if (spacerLength is not None):
                parameterName = "DendrimerSpacerLength"
                parameterValue = spacerLength[0]
                self.addDendrimerSpacerLengthToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            coreFunctionalityKey = "dendrimer_core_functionality"
            coreFunctionality = self._findElementInKeyValueDataList(coreFunctionalityKey, dataArray)
            if (coreFunctionality is not None):
                parameterName = "DendrimerCoreFunctionality"
                parameterValue = coreFunctionality[0]
                self.addDendrimerCoreFunctionalityToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            branchingPointFunctionalityKey = "dendrimer_branching_point_functionality"
            branchingPointFunctionality = self._findElementInKeyValueDataList(branchingPointFunctionalityKey, dataArray)
            if (branchingPointFunctionality is not None):
                parameterName = "DendrimerBranchingPointFunctionality"
                parameterValue = branchingPointFunctionality[0]
                self.addDendrimerBranchingPointFunctionalityToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## -----  FeatureSystemInformationDendrimer ------ ## #

        # ## -----  FeatureSpringPotentialTwoGroups ------ ## #
        featureName = "FeatureSpringPotentialTwoGroups"
        if (featureName in featureList):
            springConstKey = "spring_potential_constant"
            springConst = self._findElementInKeyValueDataList(springConstKey, dataArray)
            if (springConst is not None):
                parameterName = "SpringConstant"
                parameterValue = self._float_prec3_format(springConst[0])
                self.addSpringConstantToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            springLengthKey = "spring_potential_length"
            springLength = self._findElementInKeyValueDataList(springLengthKey, dataArray)
            if (springLength is not None):
                parameterName = "SpringLength"
                parameterValue = self._float_prec3_format(springLength[0])
                self.addSpringLengthToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## -----  FeatureSpringPotentialTwoGroups ------ ## #

        # ## -----  FeatureVirtualSpringTwoObjects ------ ## #
        # TODO: this feature is deprecated, should be noted somewhere
        featureName = "FeatureVirtualSpringTwoObjects"
        if (featureName in featureList):
            springConstKey = "virtual_spring_constant"
            springConst = self._findElementInKeyValueDataList(springConstKey, dataArray)
            if (springConst is not None):
                parameterName = "SpringConstant"
                parameterValue = self._float_prec3_format(springConst[0])
                self.addSpringConstantToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)

            springLengthKey = "virtual_spring_length"
            springLength = self._findElementInKeyValueDataList(springLengthKey, dataArray)
            if (springLength is not None):
                parameterName = "SpringLength"
                parameterValue = self._float_prec3_format(springLength[0])
                self.addSpringLengthToSimulationRun(simulationRunName, parameterValue)
                self.connectParameterToFeatureGeneral(featureName, parameterName, parameterValue)
        # ## -----  FeatureVirtualSpringTwoObjects ------ ## #

        # finally return True if no errors occurred
        return True

    def addCODMUCRgTensorFileToDatabase(self, simulationRunName, filename):
        '''High level user function to add nodes to the database by reading a radius of gyration Tensor file, using the neo4Polymer_codmuc_RGTensorFileParser.

        Parameters:
            simulationRunName (str): name of the simulationRun
            filename (str): name of the radius of gyration tensor file

        Returns:
            True if file content was added properly
            False if errors occur
        '''
        # first check if the simulation run exists
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(self.nodeType_simulationRun, simulationRunName)).data()
        if (len(elementExists) == 0):
            print("WARNING: {} does not exist. To add data from a BFM file, the simulationRun node must exist!".format(simulationRunName))
            return False

        # check if file exists
        if(os.path.isfile(filename)):
            # get full path to filename WITHOUT backslashes!
            pathToRgTFile = "{}: {}".format(socket.gethostname(), os.path.abspath(filename))
            checkForBackslashes = pathToRgTFile.replace('\\', '/')
            if (pathToRgTFile != checkForBackslashes):
                pathToRgTFile = checkForBackslashes
                print("WARNING: replaced backslashes in filepath to slashes: {}".format(pathToRgTFile))

            # now you may add it to the simulationRun node
            self.addPathToSimulationRun(simulationRunName, pathToRgTFile)
        else:
            print("WARNING: file {} does not exist!".format(filename))
            return False

        # start the bfm file reader
        fileReader = codmucRgTParser.neo4Polymer_cudmuc_RgTensor_fileparser(filename)

        # get the data-array
        dataArray = fileReader.parse_file()

        # extract a keywords from the data array
        # start with features to connect the parameters!

        # ## ---------  features  --------- ###
        featureKey = "feature_name"
        featureList = self._findElementInKeyValueDataList(featureKey, dataArray)
        if(featureList is not None):
            for feature in featureList:
                self.addFeatureToSimulationRun(simulationRunName, feature)
        # ## ---------  features  --------- ###

        # ## ---------  total number of monomers  --------- ###
        numOfMonomersKey = "number_of_monomers"
        numOfMonomers = self._findElementInKeyValueDataList(numOfMonomersKey, dataArray)
        if(numOfMonomers is not None):
            self.addTotalNumberOfMonomersToSimulationRun(simulationRunName, int(numOfMonomers[0]))
        # ## ---------  total number of monomers  --------- ###

        # ## ---------  radius of gyration squared   --------- ###
        dendrimer_rgSquaredKey = "dendrimer_Rg2"
        dendrimer_rgSquared = self._findElementInKeyValueDataList(dendrimer_rgSquaredKey, dataArray)
        graftedChains_rgSquaredKey = "graftedChains_Rg2"
        graftedChains_rgSquared = self._findElementInKeyValueDataList(graftedChains_rgSquaredKey, dataArray)
        totalMolecule_rgSquaredKey = "totalMolecule_Rg2"
        totalMolecule_rgSquared = self._findElementInKeyValueDataList(totalMolecule_rgSquaredKey, dataArray)
        if((dendrimer_rgSquared is not None) and (graftedChains_rgSquared is not None) and (totalMolecule_rgSquared is not None)):
            formatedRgString = "[[{},{}],[{},{}],[{},{}]]".format(
                "Rg^2 total codendrimer", self._float_prec4_format(float(totalMolecule_rgSquared[0])),
                "Rg^2 dendritic core", self._float_prec4_format(float(dendrimer_rgSquared[0])),
                "Rg^2 grafted chains", self._float_prec4_format(float(graftedChains_rgSquared[0]))
            )
            self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
        # ## ---------  radius of gyration squared   --------- ###

        # ## ---------  Asphericity   --------- ###
        dendrimer_asphericityKey = "dendrimer_<A>"
        dendrimer_asphericity = self._findElementInKeyValueDataList(dendrimer_asphericityKey, dataArray)
        graftedChains_asphericityKey = "graftedChains_<A>"
        graftedChains_asphericity = self._findElementInKeyValueDataList(graftedChains_asphericityKey, dataArray)
        totalMolecule_asphericityKey = "totalMolecule_<A>"
        totalMolecule_asphericity = self._findElementInKeyValueDataList(totalMolecule_asphericityKey, dataArray)
        if((dendrimer_asphericity is not None) and (graftedChains_asphericity is not None) and (totalMolecule_asphericity is not None)):
            formatedAString = "[[{},{}],[{},{}],[{},{}]]".format(
                "<A> total codendrimer", self._float_prec4_format(float(totalMolecule_asphericity[0])),
                "<A> dendritic core", self._float_prec4_format(float(dendrimer_asphericity[0])),
                "<A> grafted chains", self._float_prec4_format(float(graftedChains_asphericity[0]))
            )
            self.addResultAsphericity(simulationRunName, formatedAString)
        # ## ---------  Asphericity   --------- ###

        # finally return True if no errors occurred
        return True

    def addLinearPolymerSolutionRgFileToDatabase(self, simulationRunName, filename):
        '''High level user function to add nodes to the database by reading a radius of gyration file, using the neo4Polymer_linPolSol_Rg_fileparser.

        Parameters:
            simulationRunName (str): name of the simulationRun
            filename (str): name of the radius of gyration file

        Returns:
            True if file content was added properly
            False if errors occur
        '''
        # first check if the simulation run exists
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(self.nodeType_simulationRun, simulationRunName)).data()
        if (len(elementExists) == 0):
            print("WARNING: {} does not exist. To add data from a BFM file, the simulationRun node must exist!".format(simulationRunName))
            return False

        # check if file exists
        if(os.path.isfile(filename)):
            # get full path to filename WITHOUT backslashes!
            pathToRgFile = "{}: {}".format(socket.gethostname(), os.path.abspath(filename))
            checkForBackslashes = pathToRgFile.replace('\\', '/')
            if (pathToRgFile != checkForBackslashes):
                pathToRgFile = checkForBackslashes
                print("WARNING: replaced backslashes in filepath to slashes: {}".format(pathToRgFile))

            # now you may add it to the simulationRun node
            self.addPathToSimulationRun(simulationRunName, pathToRgFile)
        else:
            print("WARNING: file {} does not exist!".format(filename))
            return False

        # start the bfm file reader
        fileReader = linPolSolRgParser.neo4Polymer_linPolSol_Rg_fileparser(filename)

        # get the data-array
        dataArray = fileReader.parse_file()

        # extract a keywords from the data array
        # start with features to connect the parameters!

        # ## ---------  features  --------- ###
        featureKey = "feature_name"
        featureList = self._findElementInKeyValueDataList(featureKey, dataArray)
        if(featureList is not None):
            for feature in featureList:
                self.addFeatureToSimulationRun(simulationRunName, feature)
        # ## ---------  features  --------- ###

        # ## ---------  radius of gyration squared   --------- ###
        mean_rgSquaredKey = "mean_rg"
        mean_rgSquared = self._findElementInKeyValueDataList(mean_rgSquaredKey, dataArray)
        if(mean_rgSquared is not None):
            formatedRgString = "[Rg^2, {}]".format(self._float_prec4_format(mean_rgSquared[0]))
            self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
        # ## ---------  radius of gyration squared   --------- ###

        # finally return True if no errors occurred
        return True

    def addSingleDendrimerRgTFileToDatabase(self, simulationRunName, filename):
        '''High level user function to add nodes to the database by reading a radius of gyration tensor file, using the neo4Polymer_singleDendr_RGFileParser.

        Parameters:
            simulationRunName (str): name of the simulationRun
            filename (str): name of the radius of gyration file

        Returns:
            True if file content was added properly
            False if errors occur
        '''
        # first check if the simulation run exists
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(self.nodeType_simulationRun, simulationRunName)).data()
        if (len(elementExists) == 0):
            print("WARNING: {} does not exist. To add data from a BFM file, the simulationRun node must exist!".format(simulationRunName))
            return False

        # check if file exists
        if(os.path.isfile(filename)):
            # get full path to filename WITHOUT backslashes!
            pathToRgFile = "{}: {}".format(socket.gethostname(), os.path.abspath(filename))
            checkForBackslashes = pathToRgFile.replace('\\', '/')
            if (pathToRgFile != checkForBackslashes):
                pathToRgFile = checkForBackslashes
                print("WARNING: replaced backslashes in filepath to slashes: {}".format(pathToRgFile))

            # now you may add it to the simulationRun node
            self.addPathToSimulationRun(simulationRunName, pathToRgFile)
        else:
            print("WARNING: file {} does not exist!".format(filename))
            return False

        # start the bfm file reader
        fileReader = singleDendrRgTParser.neo4Polymer_singleDendrimer_RgT_fileparser(filename)

        # get the data-array
        dataArray = fileReader.parse_file()

        # extract a keywords from the data array
        # start with features to connect the parameters!

        # ## ---------  molecule part  --------- ###
        #    --------- not jet used .. ---------   #
        # moleculePartKey = "moleculePart"
        # moleculePart = self._findElementInKeyValueDataList(moleculePartKey, dataArray)
        # if(moleculePart is not None):
        #     if (len(moleculePart) == 1):
        #         currentMoleculePart = moleculePart[0]
        #     else:
        #         print("WARNING: rg tensor file contains more than one molecule part")
        #         # self.addFeatureToSimulationRun(simulationRunName, feature)
        # ## ---------  molecule part  --------- ###

        # ## ---------  radius of gyration squared   --------- ###
        mean_rgSquaredKey = "mean_rg"
        mean_rgSquared = self._findElementInKeyValueDataList(mean_rgSquaredKey, dataArray)
        if(mean_rgSquared is not None):
            formatedRgString = "[Rg^2, {}]".format(self._float_prec4_format(mean_rgSquared[0]))
            self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
        # ## ---------  radius of gyration squared   --------- ###

        # ## ---------  asphericity   --------- ###
        mean_aspericityKey = "mean_A"
        mean_aspericity = self._findElementInKeyValueDataList(mean_aspericityKey, dataArray)
        if(mean_aspericity is not None):
            formatedRgString = "[<A>, {}]".format(self._float_prec4_format(mean_aspericity[0]))
            self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
        # ## ---------  asphericity   --------- ###

        # finally return True if no errors occurred
        return True

    def _parse_line(self, line, key_dict):
        """ Utility function to apply the regex key dictionary on every line to find key value pairs

        Parameters:
            line (str): the actual line of the file or a string

        Returns:
            key and value of the regex dictionary defined in key_dict
                if something was found
            None, None otherwise
        """
        for key, rx in key_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None

    def addAnyRadiusOfGyrationFileToDatabase(self, simulationRunName, filename):
        '''High level user function to add nodes to the database by reading a radius of gyration file.

        First, the file type is detected, then the respective parser is selected and applied.

        Parameters:
            simulationRunName (str): name of the simulationRun
            filename (str): name of the radius of gyration file

        Returns:
            True if file content was added properly
            False if errors occur
        '''
                # first check if the simulation run exists
        elementExists = self.graph.run("MATCH (elem:{}) WHERE elem.name=\"{}\" return elem".format(self.nodeType_simulationRun, simulationRunName)).data()
        if (len(elementExists) == 0):
            print("WARNING: {} does not exist. To add data from a BFM file, the simulationRun node must exist!".format(simulationRunName))
            return False

        # check if file exists
        if(os.path.isfile(filename)):
            # get full path to filename WITHOUT backslashes!
            pathToRgFile = "{}: {}".format(socket.gethostname(), os.path.abspath(filename))
            checkForBackslashes = pathToRgFile.replace('\\', '/')
            if (pathToRgFile != checkForBackslashes):
                pathToRgFile = checkForBackslashes
                print("WARNING: replaced backslashes in filepath to slashes: {}".format(pathToRgFile))

            # now you may add it to the simulationRun node
            self.addPathToSimulationRun(simulationRunName, pathToRgFile)
        else:
            print("WARNING: file {} does not exist!".format(filename))
            return False

        # read a few lines of the file to detect the file type and choose the parser
        # setup unique line dict
        parser_dict = {
            "dendrimerRgTensorAnalyzer": re.compile(r'# Radius of Gyration Tensor of DendrimerRGTensorAnalyzer:[ \t]+(?P<dendrimerRgTensorAnalyzer>.*)\n'),
            "codendrimerRgTensor": re.compile(r'# ID[ \t]+Rg2[ \t]+Rgx2[ \t]+Rgy2[ \t]+Rgz2[ \t]+L1[ \t]+L2[ \t]+(?P<codendrimerRgTensor>.*)[ \t]+<A>\n'),
            "linearChainRgFile": re.compile(r'# mcs[ \t]+R_G Chain(?P<linearChainRgFile>.*)\n')
        }

        # read the first 30 lines of the file
        parser_identifier = None
        with open(filename, 'r') as file_object:
            line = "start"
            counter = 0
            while line:
                counter = counter +1
                line = file_object.readline()
                key, match = self._parse_line(line, parser_dict)
                if (match is not None):
                    parser_identifier = key
                    line = False
                if counter == 30:
                    line = False

        if (parser_identifier is not None):
            if (parser_identifier == "dendrimerRgTensorAnalyzer"):
                fileReader = singleDendrRgTParser.neo4Polymer_singleDendrimer_RgT_fileparser(filename)
            elif (parser_identifier == "codendrimerRgTensor"):
                fileReader = codmucRgTParser.neo4Polymer_cudmuc_RgTensor_fileparser(filename)
            elif (parser_identifier == "linearChainRgFile"):
                fileReader = linPolSolRgParser.neo4Polymer_linPolSol_Rg_fileparser(filename)
            else:
                print("WARNING: file {} does not match any parser routine!".format(filename))
                return False

            # get the data-array using the @abstractmethod parse_file
            dataArray = fileReader.parse_file()

            # read in generic properties
            # ## ---------  features  --------- ###
            featureKey = "feature_name"
            featureList = self._findElementInKeyValueDataList(featureKey, dataArray)
            if(featureList is not None):
                for feature in featureList:
                    self.addFeatureToSimulationRun(simulationRunName, feature)
            # ## ---------  features  --------- ###
            # ## ---------  total number of monomers  --------- ###
            numOfMonomersKey = "number_of_monomers"
            numOfMonomers = self._findElementInKeyValueDataList(numOfMonomersKey, dataArray)
            if(numOfMonomers is not None):
                self.addTotalNumberOfMonomersToSimulationRun(simulationRunName, int(numOfMonomers[0]))
            # ## ---------  total number of monomers  --------- ###
            
            # ===================
            if ((parser_identifier == "dendrimerRgTensorAnalyzer") or (parser_identifier == "linearChainRgFile")):
                # ## ---------  radius of gyration squared   --------- ###
                mean_rgSquaredKey = "mean_rg"
                mean_rgSquared = self._findElementInKeyValueDataList(mean_rgSquaredKey, dataArray)
                if(mean_rgSquared is not None):
                    formatedRgString = "[Rg^2, {}]".format(self._float_prec4_format(mean_rgSquared[0]))
                    self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
                # ## ---------  radius of gyration squared   --------- ###
                # ## ---------  asphericity   --------- ###
                mean_aspericityKey = "mean_A"
                mean_aspericity = self._findElementInKeyValueDataList(mean_aspericityKey, dataArray)
                if(mean_aspericity is not None):
                    formatedRgString = "[<A>, {}]".format(self._float_prec4_format(mean_aspericity[0]))
                    self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
                # ## ---------  asphericity   --------- ###
            # ===================

            # ===================
            if (parser_identifier == "codendrimerRgTensor"):
                # ## ---------  radius of gyration squared   --------- ###  
                dendrimer_rgSquaredKey = "dendrimer_Rg2"
                dendrimer_rgSquared = self._findElementInKeyValueDataList(dendrimer_rgSquaredKey, dataArray)
                graftedChains_rgSquaredKey = "graftedChains_Rg2"
                graftedChains_rgSquared = self._findElementInKeyValueDataList(graftedChains_rgSquaredKey, dataArray)
                totalMolecule_rgSquaredKey = "totalMolecule_Rg2"
                totalMolecule_rgSquared = self._findElementInKeyValueDataList(totalMolecule_rgSquaredKey, dataArray)
                if((dendrimer_rgSquared is not None) and (graftedChains_rgSquared is not None) and (totalMolecule_rgSquared is not None)):
                    formatedRgString = "[[{},{}],[{},{}],[{},{}]]".format(
                        "Rg^2 total codendrimer", self._float_prec4_format(float(totalMolecule_rgSquared[0])),
                        "Rg^2 dendritic core", self._float_prec4_format(float(dendrimer_rgSquared[0])),
                        "Rg^2 grafted chains", self._float_prec4_format(float(graftedChains_rgSquared[0]))
                    )
                    self.addResultRadiusOfGyration(simulationRunName, formatedRgString)
                # ## ---------  radius of gyration squared   --------- ###
                # ## ---------  Asphericity   --------- ###
                dendrimer_asphericityKey = "dendrimer_<A>"
                dendrimer_asphericity = self._findElementInKeyValueDataList(dendrimer_asphericityKey, dataArray)
                graftedChains_asphericityKey = "graftedChains_<A>"
                graftedChains_asphericity = self._findElementInKeyValueDataList(graftedChains_asphericityKey, dataArray)
                totalMolecule_asphericityKey = "totalMolecule_<A>"
                totalMolecule_asphericity = self._findElementInKeyValueDataList(totalMolecule_asphericityKey, dataArray)
                if((dendrimer_asphericity is not None) and (graftedChains_asphericity is not None) and (totalMolecule_asphericity is not None)):
                    formatedAString = "[[{},{}],[{},{}],[{},{}]]".format(
                        "<A> total codendrimer", self._float_prec4_format(float(totalMolecule_asphericity[0])),
                        "<A> dendritic core", self._float_prec4_format(float(dendrimer_asphericity[0])),
                        "<A> grafted chains", self._float_prec4_format(float(graftedChains_asphericity[0]))
                    )
                    self.addResultAsphericity(simulationRunName, formatedAString)
                # ## ---------  Asphericity   --------- ###

        # finally return True if no errors occurred
        return True 
#
