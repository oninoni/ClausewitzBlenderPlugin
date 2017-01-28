import io
from . import (tree, utils)

class PdxFile():
    def __init__(self, filename):
        self.filename = filename
        self.fileReference = None
        self.rawData = []
        self.nodes = []
        self.dataTree = tree.Tree(tree.TreeNode("root"))

    def read(self):
        self.fileReference = io.open(self.filename, "rb")
        self.rawData = self.fileReference.read()

        self.__parse__()

    def __parse__(self):
        offset = 0

        data = self.rawData.lstrip(b"@@b@")

        buffer = utils.BufferReader(data)
        rootNode = tree.TreeNode("root")

        self.dataTree = tree.Tree(rootNode)
        self.ReadObject(rootNode, buffer, -1)

        self.dataTree.print()
        self.fileReference.close()

    def ReadProperty(self, treeNode: tree.TreeNode, buffer: utils.BufferReader):
        name = ""
        dataCount = 0
        stringType = 1
        propertyData = []

        lowerBound = buffer.GetCurrentOffset()
        nameLength = buffer.NextInt8()

        for i in range(1, nameLength + 1):
            name += buffer.NextChar()

        name = utils.TranslatePropertyName(name)

        char = buffer.NextChar()

        if char == "i":
            dataCount = buffer.NextUInt32()

            for i in range(0, dataCount):
                propertyData.append(buffer.NextInt32())
        elif char == "f":
            dataCount = buffer.NextUInt32()

            for i in range(0, dataCount):
                propertyData.append(buffer.NextFloat32())
        elif char == "s":
            stringValue = ""
            stringType = buffer.NextUInt32()
            dataCount = buffer.NextUInt32()

            stringValue = utils.ReadNullByteString(buffer)

            propertyData.append(stringValue)

        newNode = tree.TreeNode(name)
        newNode.value = propertyData

        upperBound = buffer.GetCurrentOffset()

        if name == "pdxasset":
            asset = PdxAsset()
            asset.bounds = (lowerBound, upperBound)
            self.nodes.append(asset)

        treeNode.append(newNode)

    def ReadObject(self, treeNode: tree.TreeNode, buffer: utils.BufferReader, depth):
        objectName = ""
        char = buffer.NextChar()
        
        while not buffer.IsEOF() and char == '[':
            depth += 1
            char = buffer.NextChar()
        
        node = treeNode
            
        if depth >= 0:
            objectName = char + utils.ReadNullByteString(buffer)

            node = tree.TreeNode(objectName)
            treeNode.append(node)
            
        while not buffer.IsEOF():
            if char == "[":
                self.ReadObject(node, buffer, depth + 1)
            elif char == "!":
                nextProperty = utils.ReadNullByteString(buffer, True)
                if nextProperty == "pdxasset":
                    self.ReadAsset(buffer)
                else:
                    self.ReadProperty(node, buffer)

            if not buffer.IsEOF():
                char = buffer.NextChar()

    def ReadAsset(self, buffer: utils.BufferReader):
        lowerBound = buffer.GetCurrentOffset()

        asset = PdxAsset()
        utils.ReadNullByteString(buffer)
        buffer.GetNextChar()
        asset.value = buffer.NextUInt32()

        upperBound = buffer.GetCurrentOffset()

        asset.bounds = (lowerBound, upperBound)
        self.nodes.append(asset)

class PdxAsset():
    def __init__(self):
        self.bounds = (0,0)
        self.value = 0

class PdxMesh():
    def __init__(self, name, blenderName):
        self.bounds = (0,0)
        self.name = name
        self.blenderName = blenderName
        self.blenderMesh = None
        self.verts = []
        self.faces = []
        self.tangents = []
        self.normals = []
        self.locators = []
        self.uv_coords = []
        self.material = None

class PdxLocators():
    def __init__(self):
        self.locators  = []

class PdxLocator():
    def __init__(self, name, pos):
        self.bounds = (0,0)
        self.name = name
        self.pos = pos        
    