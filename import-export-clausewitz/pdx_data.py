import io
from . import (tree, utils)

class PdxFile():
    def __init__(self, filename):
        self.filename = filename
        self.fileReference = None
        self.rawData = []
        self.asset = None
        self.objects = None
        self.dataTree = tree.Tree(tree.TreeNode("root"))

    def read(self):
        self.fileReference = io.open(self.filename, "rb")
        self.rawData = self.fileReference.read()

        self.__parse__()

    def __parse__(self):
        offset = 0
        status = []

        data = self.rawData.lstrip(b"@@b@")

        buffer = utils.BufferReader(data)
        
        lowerBound = buffer.GetCurrentOffset()
        char = buffer.NextChar()
        nameLength = buffer.NextInt8()

        if utils.ReadLengthPrefixedString(buffer, nameLength) != "pdxasset":
            print("Asset File is not valid.")
            return

        self.asset = PdxAsset()
        buffer.NextChar()
        newValue = buffer.NextUInt32()
        self.asset.value = newValue
        self.asset.bounds = (lowerBound, buffer.GetCurrentOffset())

        lastObject = None
        currentObject = None
        lastStatus = ""
        status.append("ROOT_OBJECT")

        while not buffer.IsEOF():
            level = 1
            char = buffer.NextChar()

            if char == "[":
                while not buffer.IsEOF():
                    char = buffer.NextChar(True)

                    if char == "[":
                        buffer.NextChar()
                        level += 1
                    else:
                        break
                
                print(level)
                name = utils.ReadNullByteString(buffer)

                if status[len(status) - 1] == "ROOT_OBJECT":
                    if name == "locator":
                        lastObject = currentObject
                        currentObject = PdxLocators()
                        status.append("LOCATORS")
                    elif name == "object":
                        lastObject = currentObject
                        currentObject = PdxObject()
                        status.append("OBJECT")
                elif status[len(status) - 1] == "LOCATORS":
                    lastObject = currentObject
                    currentObject = PdxLocator(name, (0,0))
                    status.append("LOCATOR")
                elif status[len(status) - 1] == "OBJECT":
                    lastObject = currentObject
                    currentObject = PdxShape(name)
                    status.append("SHAPE")
                elif status[len(status) - 1] == "SHAPE":
                    lastObject = currentObject
                    currentObject = PdxMesh()
                    status.append("MESH")
                elif status[len(status) - 1] == "MESH":
                    print(name)
                    if name == "aabb":
                        lastObject = currentObject
                        currentObject = PdxBounds()
                        status.append("BOUNDS")
                    elif name == "material":
                        lastObject = currentObject
                        currentObject = PdxMaterial()
                        status.append("MATERIAL")
                else:
                    status.pop()
                    continue

                print(status)

                #Property
                while not buffer.IsEOF() and buffer.NextChar(True) != "[":
                    if buffer.NextChar(True) == "!":
                        buffer.NextChar()
                        tempProperty = self.ReadProperty(buffer)

                #if not buffer.IsEOF(1) and buffer.NextChar(True) == "[":
                #    tempLevel = 1
                    
                #    while not buffer.IsEOF():
                #        char = buffer.NextChar(True, tempLevel - 1)

                #        if char == "[":
                #            tempLevel += 1
                #        else:
                #            break

                #    if tempLevel <= level:
                if len(status) > 1:
                    status.pop()

        self.fileReference.close()

    def ReadObject(self, ):
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

    def ReadProperty(self, buffer: utils.BufferReader):
        value = ""
        name = ""
        lowerBound = buffer.GetCurrentOffset()
        nameLength = buffer.NextInt8()

        for i in range(0, nameLength):
            name += buffer.NextChar()

        name = utils.TranslatePropertyName(name)

        char = buffer.NextChar()

        if char == "i":
            dataCount = buffer.NextUInt32()
            value = []

            for i in range(0, dataCount):
                value.append(buffer.NextInt32())
        elif char == "f":
            dataCount = buffer.NextUInt32()
            value = []

            for i in range(0, dataCount):
                value.append(buffer.NextFloat32())
        elif char == "s":
            stringValue = ""
            stringType = buffer.NextUInt32()
            dataCount = buffer.NextUInt32()

            value = utils.ReadNullByteString(buffer)

        return PdxProperty(name, value)
        
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

class PdxObject():
    def __init__(self):
        self.shapes = []

class PdxShape():
    def __init__(self, name):
        self.name = name
        self.mesh = None

class PdxMesh():
    def __init__(self):
        self.bounds = (0,0)
        self.blenderMesh = None
        self.verts = []
        self.faces = []
        self.tangents = []
        self.normals = []
        self.locators = []
        self.uv_coords = []
        self.material = None

class PdxMaterial():
    def __init__(self):
        self.shader = ""
        self.diff = ""
        self.n = "" #NormalMap
        self.spec = ""

class PdxBounds():
    def __init__(self):
        self.min = 0.0
        self.max = 0.0

class PdxProperty():
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PdxLocators():
    def __init__(self):
        self.locators  = []

class PdxLocator():
    def __init__(self, name, pos):
        self.bounds = (0,0)
        self.name = name
        self.pos = pos        
    