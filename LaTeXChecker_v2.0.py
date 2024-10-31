import os
from sys import argv, executable, exit
from re import findall
from time import sleep
PLATFORM = __import__("platform").system().upper()
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
CLEAR_SCREEN_COMMAND = ("CLS" if PLATFORM == "WINDOWS" else "clear") if __import__("sys").stdin.isatty() else None
STARTUP_COMMAND_FORMAT = "START \"\" \"{0}\" \"{1}\" \"{2}\"" if PLATFORM == "WINDOWS" else "\"{0}\" \"{1}\" \"{2}\"&"


class DebugLevel:
	defaultCharacter = "?"
	defaultName = "*"
	defaultSymbol = "[?]"
	defaultValue = 0
	def __init__(self:object, d:dict) -> object:
		self.character = d["character"] if "character" in d else DebugLevel.defaultCharacter
		self.name = d["name"] if "name" in d else DebugLevel.defaultName
		self.symbol = d["symbol"] if "symbol" in d else DebugLevel.defaultSymbol
		self.value = d["value"] if "value" in d else DebugLevel.defaultValue
	def __eq__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value == other.value
		elif isinstance(other, (int, float)):
			return self.value == other
		else:
			return False
	def __ne__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value != other.value
		elif isinstance(other, (int, float)):
			return self.value != other
		else:
			return True
	def __lt__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value < other.value
		elif isinstance(other, (int, float)):
			return self.value < other
		else:
			raise TypeError("TypeError: '<' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __le__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value <= other.value
		elif isinstance(other, (int, float)):
			return self.value <= other
		else:
			raise TypeError("TypeError: '<=' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __gt__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value > other.value
		elif isinstance(other, (int, float)):
			return self.value > other
		else:
			raise TypeError("TypeError: '>' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __ge__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value >= other.value
		elif isinstance(other, (int, float)):
			return self.value >= other
		else:
			raise TypeError("TypeError: '>=' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __bool__(self:object) -> bool:
		return bool(self.value)
	def __int__(self:object) -> int:
		return self.value
	def __str__(self:object) -> str:
		return str(self.symbol)
Prompt = DebugLevel({"character":"P", "name":"Prompt", "symbol":"[P]", "value":100})
Critical = DebugLevel({"character":"C", "name":"Critical", "symbol":"[C]", "value":50})
Error = DebugLevel({"character":"E", "name":"Error", "symbol":"[E]", "value":40})
Warning = DebugLevel({"character":"W", "name":"Warning", "symbol":"[W]", "value":30})
Info = DebugLevel({"character":"I", "name":"Info", "symbol":"[I]", "value":20})
Debug = DebugLevel({"character":"D", "name":"Debug", "symbol":"[D]", "value":10})

class PointerNode:
	def __init__(self:object, filePath:str, parentPointerNode:object = None) -> object:
		self.__filePath = os.path.abspath(str(filePath).replace("\"", "")) # must be an absolute path since __eq__ needs to use it
		self.__lineIdx = 0 # the initialization value
		self.__charIdx = -1 # the initialization value
		self.__parentPointerNode = parentPointerNode if isinstance(parentPointerNode, PointerNode) else None
		self.__children = None # initialization flag
		self.__lines = None # initialization flag
	def __getTxt(self:object, filePath:str, index:int = 0) -> str: # get .txt content
		coding = ("utf-8", "gbk", "utf-16") # codings
		if 0 <= index < len(coding): # in the range
			try:
				with open(filePath, "r", encoding = coding[index]) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				return self.__getTxt(filePath, index + 1) # recursion
			except:
				return None
		else:
			return None # out of range
	def initialize(self:object) -> bool:
		content = self.__getTxt(self.__filePath)
		if content is None:
			self.__lines = None # avoid re-initialization
			self.__children = None # avoid re-initialization
			return False
		elif content:
			self.__lines = content.splitlines()
			self.__children = []
			return True
		else:
			self.__lines = [""]
			self.__children = []
			return True
	def isInitialized(self:object) -> bool:
		return isinstance(self.__lines, list) and isinstance(self.__children, list)
	def hasNextChar(self:object) -> bool: # only just the status of the current pointer node
		return 0 <= self.__lineIdx < len(self.__lines) and 0 <= self.__charIdx + 1 < len(self.__lines[self.__lineIdx]) if self.isInitialized() else None
	def nextChar(self:object) -> bool:
		bRet = self.hasNextChar() # judge if it is initialized and if there is a following character
		if bRet:
			self.__charIdx += 1 # increse the character count
		return bRet
	def hasNextLine(self:object) -> bool: # only just the status of the current pointer node
		return self.__lineIdx + 1 < len(self.__lines) if self.isInitialized() else None
	def nextLine(self:object) -> bool:
		bRet = self.hasNextLine() # judge if it is initialized and if there is a following line
		if bRet:
			self.__lineIdx += 1 # increase the line count
			self.__charIdx = -1 # reset the char index
		return bRet
	def isEOF(self:object) -> bool:
		return self.__lineIdx + 1 == len(self.__lines) and self.__charIdx >= 0 and self.__charIdx + 1 == len(self.__lines[self.__lineIdx]) if self.isInitialized() else None
	def getCurrentChar(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx] if self.isInitialized() and self.__lineIdx < len(self.__lines) and 0 <= self.__charIdx < len(self.__lines[self.__lineIdx]) else None
	def getNextChar(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx + 1] if self.hasNextChar() else None
	def addChildPointerNode(self:object, pointerNode:object) -> bool:
		if isinstance(pointerNode, PointerNode) and pointerNode.isInitialized():
			self.__children.append(pointerNode)
			return True
		else:
			return False
	def getFilePath(self:object) -> str:
		return self.__filePath if self.isInitialized() else None
	def getCurrentLocation(self:object) -> tuple:
		return (self.__filePath, self.__lineIdx, self.__charIdx)
	def getChildren(self:object, isReversed:bool = False) -> list:
		return (self.__children[::-1] if isReversed else self.__children[::]) if self.isInitialized() else None
	def __eq__(self:object, obj:str|object) -> bool:
		if PLATFORM == "WINDOWS":
			return isinstance(obj, PointerNode) and self.__filePath.lower() == obj.__filePath.lower() or isinstance(obj, str) and self.__filePath.lower() == obj.lower()
		else:
			return isinstance(obj, PointerNode) and self.__filePath == obj.__filePath or isinstance(obj, str) and self.__filePath == obj

class Pointer:
	def __init__(self:object, rootFilePath:str) -> object:
		absRootFilePath = os.path.abspath(str(rootFilePath).replace("\"", ""))
		self.__pointerNodeStack = [] # stack (stack[0] is the root) # initialization flag
		self.__pointerNodeStack.append(PointerNode(absRootFilePath)) # write separately to avoid the absence of this attribute caused by exceptions in PointerNode
		self.__currentPointerNode = None # initialization flag
		self.__baseFolderPath = os.path.split(absRootFilePath)[0]
		self.__lastError = "Currently, there are no errors. "
	def initialize(self:object) -> bool:
		if self.__pointerNodeStack and self.__pointerNodeStack[0].initialize():
			self.__currentPointerNode = self.__pointerNodeStack[0]
			return True
		else:
			self.__pointerNodeStack = [self.__pointerNodeStack[0]] if self.__pointerNodeStack else [] # avoid re-initialization
			self.__currentPointerNode = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return self.__pointerNodeStack and isinstance(self.__currentPointerNode, PointerNode)
	def hasNextChar(self:object, fileSwitch:bool = True) -> bool: # in the current line including "1\input{2}3"
		if self.isInitialized():
			if self.__currentPointerNode.hasNextChar():
				return True
			elif isinstance(fileSwitch, bool) and fileSwitch:
				for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextChar():
						return True
					elif not self.__pointerNodeStack[i].isEOF(): # there is a following line but there is not a following character
						return False
			return False # no following characters are followed / all the opened files report EOF
		else:
			return None # not initialized
	def nextChar(self:object, fileSwitch:bool = True) -> bool:
		bRet = self.hasNextChar(fileSwitch = fileSwitch) # judge if it is initialized and if there is a following character in the current line
		if bRet:
			while self.__pointerNodeStack: # no need to consider the switch again
				if self.__pointerNodeStack[-1].nextChar():
					return True
				elif not self.__pointerNodeStack[-1].isEOF(): # there is a following line but there is not a following character
					return False
				self.__pointerNodeStack.pop()
			return False # all the opened files report EOF
		else:
			return bRet
	def hasNextLine(self:object, fileSwitch:bool = True) -> bool:
		if self.isInitialized():
			if self.__currentPointerNode.hasNextLine():
				return True
			else:
				for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextLine():
						return True
				return False # all the opened files report EOF
		else:
			return None # not initialized
	def nextLine(self:object, fileSwitch:bool = True) -> bool:
		bRet = self.hasNextLine() # judge if it is initialized and if there is a following line
		if bRet:
			while self.__pointerNodeStack:
				if self.__pointerNodeStack[-1].nextLine():
					return True
				self.__pointerNodeStack.pop()
			return False # all the opened files report EOF
		else:
			return bRet
	def getCurrentChar(self:object) -> str:
		return self.__currentPointerNode.getCurrentChar() if self.isInitialized() else None
	def getNextChar(self:object, fileSwitch:bool = True) -> str:
		bRet = self.hasNextChar(fileSwitch = fileSwitch) # judge if it is initialized and if there is a following character in the current line
		if bRet:
			for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextChar():
						return self.__pointerNodeStack[i].getNextChar()
			return None # all the opened files report EOF
		else:
			return bRet
	def getCurrentLocation(self:object) -> tuple:
		if self.isInitialized():
			tp = self.__currentPointerNode.getCurrentLocation()
			return (os.path.relpath(str(tp[0]), self.__baseFolderPath), tp[1], tp[2]) if isinstance(tp, tuple) else None
		else:
			return None
	def getCurrentLocationDescription(self:object) -> str:
		tp = self.getCurrentLocation()
		return "Char {0}, Line {1}, File \"{2}\"".format(tp[2], tp[1], tp[0]) if isinstance(tp, tuple) else None
	def addPointerNode(self:object, filePath:str) -> bool:
		if not self.isInitialized():
			self.__lastError = "The instance of ``Pointer`` has not been initialized. "
			return False
		strippedFilePath = str(filePath).replace("\"", "").strip()
		absFilePath = os.path.abspath(strippedFilePath if os.path.isabs(strippedFilePath) else os.path.join(self.__baseFolderPath, strippedFilePath))
		if absFilePath in self.__pointerNodeStack:
			self.__lastError = "The file \"{0}\" has been in the stack for resolving. Please check and make sure that there are no recursive calls. ".format(absFilePath)
			return False
		pointerNode = PointerNode(absFilePath, parentPointerNode = self.__currentPointerNode)
		if pointerNode.initialize() and self.__currentPointerNode.addChildPointerNode(pointerNode):
			self.__currentPointerNode = pointerNode
			self.__pointerNodeStack.append(pointerNode)
			return True
		else:
			self.__lastError = "Failed to initialize the call to \"{0}\". ".format(absFilePath)
			return False
	def getLastError(self:object) -> str:
		return self.__lastError
	def getTree(self:object, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__pointerNodeStack[0], 0)]
			res = []
			while stack:
				node, level = stack.pop()
				if node.isInitialized():
					res.append("{0}{1}".format(str(indentationSymbol) * level, os.path.relpath(node.getFilePath(), self.__baseFolderPath)))
					stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None

class StructureNode:
	def __init__(self:object, header:str = "", parent:object = None) -> object:
		self.__header = header if isinstance(header, str) else ""
		self.__footer = ""
		self.__type = None # initialization flag
		self.__descriptor = None
		self.__children = None # initialization flag
		self.__parent = parent if isinstance(parent, StructureNode) else None
	def initialize(self:object) -> bool:
		if self.__header:
			if "Root" == self.__header:
				self.__type = "Root"
				self.__descriptor = None
			elif self.__header.startswith("\\begin{") and self.__header.endswith("}"):
				self.__type = "Environment"
				self.__descriptor = self.__header[7:-1].strip()
			elif self.__header.startswith("\\documentclass"):
				self.__type = "DocumentClass"
				self.__descriptor = None
			elif (self.__header.startswith("\\section{") or self.__header.startswith("\\subsection{") or self.__header.startswith("\\subsubsection{")) and self.__header.endswith("}"):
				self.__type = "S" + self.__header[2:self.__header.index("{")]
				self.__descriptor = self.__header[self.__header.index("{") + 1:-1].strip()
			elif self.__header in ("$", "$$", "\\(", "\\["):
				self.__type = "Equation"
				self.__descriptor = self.__header
			else:
				self.__type = None # avoid re-initialization
				self.__children = None # avoid re-initialization
				return False
			self.__children = []
			return True
		else:
			self.__type = None # avoid re-initialization
			self.__children = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return isinstance(self.__type, str) and isinstance(self.__children, list)
	def addChildStructureNode(self:object, structureNode:object) -> bool:
		if self.isInitialized() and isinstance(structureNode, StructureNode):
			self.__children.append(structureNode)
			return True
		else:
			return None
	def isFooterAccepted(self:object, footer:str) -> bool:
		if not self.isInitialized() or not isinstance(footer, str):
			return None
		if footer.startswith("\\documentclass"):
			return "DocumentClass" == self.__type
		elif footer.startswith("\\end{") and footer.endswith("}"):
			return "Environment" == self.__type and footer[5:footer.index("}")] == self.__descriptor
		elif (footer.startswith("\\section{") or footer.startswith("\\subsection{") or footer.startswith("\\subsubsection")) and footer.endswith("}"):
			if "Section" == self.__type:
				return footer.startswith("\\section{") # only "\\section" is allowed
			elif "Subsection" == self.__type:
				return footer.startswith("\\section{") or footer.startswith("\\subsection{") # >=
			elif "Subsubsection" == self.__type:
				return True # all the three are accepted
			else:
				return False
		elif footer in ("$", "$$"):
			return "Equation" == self.__type and footer == self.__descriptor
		elif "\\)" == footer:
			return "Equation" == self.__type and "\\(" == self.__descriptor
		elif "\\]" == footer:
			return "Equation" == self.__type and "\\[" == self.__descriptor
		else:
			return False
	def setFooter(self:object, footer:str) -> bool:
		bRet = self.isFooterAccepted(footer)
		if bRet and self.__header not in ("DocumentClass", "Section", "Subsection", "Subsubsection"): # the "documentclass" and section-like structures do not require footnotes
			self.__footer = footer
		return bRet
	def addPlainText(self:object, strings:str = "") -> bool:
		if self.isInitialized() and isinstance(strings, str):
			if self.__children and isinstance(self.__children[-1], str): # the last node is a string
				self.__children[-1] += strings
			else: # create a new string
				self.__children.append(strings)
		else:
			return None
	def getChildren(self:object, isReversed:bool = False) -> list:
		return (self.__children[::-1] if isReversed else self.__children[::]) if self.isInitialized() else None
	def getParent(self:object) -> object:
		return self.__parent
	def __str__(self:object) -> str:
		return "{0}".format(self.__type) if self.__descriptor is None else "{0}({1})".format(self.__type, self.__descriptor)

class Structure:
	def __init__(self:object) -> object:
		self.__rootStructureNode = None # initialization flag
		self.__currentStructureNode = None # initialization flag
	def initialize(self:object) -> bool:
		self.__rootStructureNode = StructureNode("Root")
		if self.__rootStructureNode.initialize():
			self.__currentStructureNode = self.__rootStructureNode
			return True
		else:
			self.__rootStructureNode = None # avoid re-initialization
			self.__currentStructureNode = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return isinstance(self.__rootStructureNode, StructureNode) and isinstance(self.__currentStructureNode, StructureNode)
	def addPlainText(self:object, strings:str = "") -> bool:
		return self.__currentStructureNode.addPlainText(strings) if self.isInitialized() else None
	def addStructureNode(self:object, header:str = "") -> bool:
		if self.isInitialized() and isinstance(header, str):
			if header.startswith("\\documentclass") or header.startswith("\\section{") or header.startswith("\\subsection{") or header.startswith("\\subsubsection{"): # go back to the parent node if the footer is accepted
				if self.__currentStructureNode.isFooterAccepted(header):
					self.__currentStructureNode = self.__currentStructureNode.getParent()
			structureNode = StructureNode(header = header, parent = self.__currentStructureNode)
			if structureNode.initialize() and self.__currentStructureNode.addChildStructureNode(structureNode):
				self.__currentStructureNode = structureNode
				return True
			else:
				return False
		else:
			return None
	def canLeaveCurrentStructureNode(self:object, footer:str = "") -> bool:
		return self.__currentStructureNode != self.__rootStructureNode and self.__currentStructureNode.isFooterAccepted(footer) if self.isInitialized() and isinstance(footer, str) else None
	def leaveCurrentStructureNode(self:object, footer:str = "") -> bool:
		bRet = self.canLeaveCurrentStructureNode(footer)
		if bRet:
			self.__currentStructureNode.setFooter(footer)
			self.__currentStructureNode = self.__currentStructureNode.getParent()
		return bRet
	def getCurrentStructureNodeDescription(self:object) -> str:
		return str(self.__currentStructureNode) if self.isInitialized() else None
	def getTree(self:object, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__rootStructureNode, indentationCount)]
			res = []
			while stack:
				node, level = stack.pop()
				if isinstance(node, str):
					res.append("{0}Text({1})".format(indentationSymbol * level, len(node)))
				elif node.isInitialized():
					res.append("{0}{1}".format(indentationSymbol * level, node))
					stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None

class Checker:
	def __init__(self:object, mainTexPath:str = None, debugLevel:DebugLevel|int = 0) -> object:
		self.__mainTexPath = os.path.abspath(mainTexPath.replace("\"", "")) if isinstance(mainTexPath, str) else None # transfer to the absolute path
		self.__pointer = None
		self.__structure = None
		if isinstance(debugLevel, DebugLevel):
			self.__debugLevel = debugLevel
		else:
			try:
				self.__debugLevel = int(debugLevel)
			except:
				self.__debugLevel = 0
				self.__print("The debug level specified is invalid. It is defaulted to 0. ", Warning)
		self.__flag = False
	def __print(self:object, strings:str|object, debugLevel:DebugLevel = Info, indentationSymbol:str = "\t", indentationCount:int = 0) -> bool:
		if (isinstance(strings, str) or hasattr(strings, "__str__")) and isinstance(debugLevel, DebugLevel) and isinstance(indentationSymbol, str) and isinstance(indentationCount, int):
			if debugLevel >= self.__debugLevel:
				print("\n".join(["{0} {1}{2}".format(debugLevel, (indentationSymbol * indentationCount if indentationCount >= 1 else ""), string) for string in str(strings).splitlines()]))
				return True
			else:
				return False
		else:
			return None
	def __input(self:object, strings:str, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		try:
			return input("\n".join(["{0} {1}{2}".format(Prompt, (indentationSymbol * indentationCount if isinstance(indentationSymbol, str) and isinstance(indentationCount, int) and indentationCount >= 1 else ""), string) for string in str(strings).splitlines()]))
		except KeyboardInterrupt:
			print()
			self.__print("The input process was interrupted by users. None will be returned as the default value. ", Warning)
			return None
		except BaseException as e:
			self.__print("The input process was interrupted by the following exceptions. ", Error)
			self.__print(e, Error, indentationCount = 1)
			return None
	def __resolve(self:object) -> bool:
		self.__flag = False
		self.__pointer = Pointer(self.__mainTexPath)
		self.__structure = Structure()
		if not self.__pointer.initialize():
			self.__print("Failed to initialize the main tex file. Please check if the file can be read. ", Error)
			return False
		if not self.__structure.initialize():
			self.__print("Failed to initialize the root structure node. ", Error)
			return False
		buffer = "" # can also use a flag to control the buffer like {0:"plainTextBuffer", 1:"commandBuffer", 2:"mandatoryArgumentBuffer", 3:"optionalArguementBuffer"}
		stack = [] # indicate the layer of {}
		isLeftPart = True # indicate the "$" or "$$" got is the left part or not
		while True:
			if self.__pointer.hasNextChar(): # if there is a character following the current character in this line
				self.__pointer.nextChar() # move to the next character
				ch = self.__pointer.getCurrentChar() # get the currenct character
				if "\\" == ch: # use the active modes
					if self.__pointer.hasNextChar(fileSwitch = False):
						if self.__pointer.getNextChar(fileSwitch = False) in ("(", "["):
							self.__structure.addStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False))
							self.__pointer.nextChar(fileSwitch = False)
						elif self.__pointer.getNextChar(fileSwitch = False) in (")", "]"):
							if not (self.__structure.canLeaveCurrentStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False)) and self.__structure.leaveCurrentStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False))):
								self.__print("Cannot end the current environment ({0}) with command \"{1}\" at {2}. ".format(self.__structure.getCurrentStructureNodeDescription(), buffer, self.__pointer.getCurrentLocationDescription()), Error)
								return False
						else:
							buffer = "\\" # initial a buffer to obtain the command
							while self.__pointer.hasNextChar(fileSwitch = False): # fetch the whole command
								ch = self.__pointer.getNextChar(fileSwitch = False)
								if "A" <= ch <= "Z" or "a" <= ch <= "z":
									buffer += ch
									self.__pointer.nextChar(fileSwitch = False)
								else:
									break
							if "\\" == buffer: # "\\"
								if "0" <= ch <= "9": # e.g. "\\0" (ch must be defined since judging whether there is a following character is done before)
									self.__pointer.nextChar(fileSwitch = False) # for printing purposes
									self.__print("A command should only contain letters but it does not at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								else: # e.g. "\\%" (absorb the next character)
									self.__pointer.nextChar(fileSwitch = False)
									self.__structure.addStructureNode("\\" + self.__pointer.getCurrentChar())
							elif "\\documentclass" == buffer:
								if self.__structure.addStructureNode(buffer):
									self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
								else:
									self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
									return False
							elif buffer in ("\\begin", "\\end", "\\input", "\\section", "\\subsection", "\\subsubsection"):
								commandName = buffer[1:] # for judging environments
								while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar() in (" ", "\t"): # skip all the spaces and tabs in the current line
									self.__pointer.nextChar(fileSwitch = False)
								if not self.__pointer.hasNextChar(fileSwitch = False): # allow one "\n" in the same file
									if self.__pointer.hasNextLine(fileSwitch = False):
										self.__pointer.nextLine(fileSwitch = False)
									else:
										self.__structure.addPlainText(buffer)
										continue
								while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar() in (" ", "\t"): # skip all the spaces and tabs in the current line
									self.__pointer.nextChar(fileSwitch = False)
								if not self.__pointer.hasNextChar(fileSwitch = False):
									if self.__pointer.hasNextLine(): # "\\input\n\n" (allow line switch here)
										self.__pointer.nextLine()
										self.__structure.addPlainText(buffer + "\n\n")
										continue
									else: # EOF
										self.__pointer.nextChar()
										continue
								if self.__pointer.hasNextChar(fileSwitch = False):
									ch = self.__pointer.getNextChar()
									if "{" == ch:
										while self.__pointer.hasNextChar(fileSwitch = False): # fetch the file path
											ch = self.__pointer.getNextChar(fileSwitch = False)
											buffer += ch
											if "}" == ch: # finish fetching
												if "begin" == commandName:
													if self.__structure.addStructureNode(header = buffer):
														self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
													else:
														self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
														return False
												elif "end" == commandName:
													if not (self.__structure.canLeaveCurrentStructureNode(buffer) and self.__structure.leaveCurrentStructureNode(buffer)):
														self.__print(																							\
															"Cannot end the current environment [{0}] with command \"{1}\" at {2}. ".format(								\
																self.__structure.getCurrentStructureNodeDescription(), buffer, self.__pointer.getCurrentLocationDescription()		\
															), Error																							\
														)
														return False
												elif "input" == commandName:
													if not self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1]):
														self.__print("Failed to add a child pointer node at {0}. Details are as follows. \n{1}".format(self.__pointer.getCurrentLocationDescription(), self.__pointer.getLastError()), Warning)
												else:
													self.__structure.addStructureNode(buffer)
												self.__pointer.nextChar(fileSwitch = False)
												break
											else:
												self.__pointer.nextChar(fileSwitch = False)
										else:
											self.__print("Pointer ends when waiting for a \"}}\" for \"{{\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									elif "\\" == ch: # "\\input\\"
										self.__structure.addPlainText(buffer)
									else:
										self.__print("An unexpected character \"{0}\" follows the \"\\{1}\" command at {2}. ".format(("\\\"" if "\"" == ch else ch), commandName, sself.__pointer.getCurrentLocationDescription()), Error)
										return False
							else: # the command is not special
								self.__structure.addPlainText(buffer)
					else: # "\\\n"
						self.__structure.addPlainText("\\")
				elif "%" == ch: # the '\\' will be absorbed in the codes for avoiding "\\%" above if the previous char is '\\'
					self.__pointer.nextLine()
				elif "$" == ch: # the '\\' will be absorbed in the codes for avoiding "\\$" above if the previous char is '\\'
					if self.__pointer.hasNextChar(fileSwitch = False) and "$" == self.__pointer.getNextChar(fileSwitch = False):
						self.__pointer.nextChar(fileSwitch = False)
						ch = "$$" # else: ch = "$"
					if isLeftPart:
						if self.__structure.addStructureNode(header = ch):
							self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
						else:
							self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(ch, self.__pointer.getCurrentLocationDescription()), Error)
							return False
					else:
						if self.__structure.canLeaveCurrentStructureNode(ch) and self.__structure.leaveCurrentStructureNode(ch):
							self.__print("Leave current structure node with \"{0}\". ".format(ch), Debug)
						else:
							self.__print("Cannot end the current environment [{0}] with command \"{1}\" at {2}. ".format(self.__structure.getCurrentStructureNodeDescription(), ch, self.__pointer.getCurrentLocationDescription()), Error)
							return False
					isLeftPart = not isLeftPart # switch to the other part
				else:
					self.__structure.addPlainText(ch)
			elif self.__pointer.hasNextLine(): # there is not a following character but a following line
				self.__structure.addPlainText("\n")
				self.__pointer.nextLine() # switch to the next line
			else: # EOF
				break
		self.__flag = True
		return True
	def printPointer(self:object) -> None:
		self.__print("Pointer: ", Info)
		self.__print(self.__pointer.getTree(), Info)
	def printStructure(self:object) -> None:
		self.__print("Structure: ", Info)
		self.__print(self.__structure.getTree(), Info)
	def setup(self:object) -> bool:
		try:
			if not isinstance(self.__mainTexPath, str):
				tmpMainTexPath = self.__input("Please input the main tex path: ", Prompt)
				if tmpMainTexPath is None:
					self.__print("Setup cancelled. ", Error)
					return False
				else:
					self.__mainTexPath = tmpMainTexPath.replace("\"", "")
					self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
					return self.setup()
			elif os.path.isfile(self.__mainTexPath):
				return self.__resolve()
			elif os.path.isdir(self.__mainTexPath):
				self.__print("Since a folder was specified, the program is scanning the folder now. ", Info)
				self.__print("If it takes too long time, please use \"Ctrl+C\" to stop the scanning. ", Info)
				possibleTargets = []
				try:
					for root, dirs, files in os.walk(self.__mainTexPath):
						for fileName in files:
							if os.path.splitext(fileName)[1].lower() in (".tex", ):
								possibleTargets.append(os.path.join(root, fileName))
				except KeyboardInterrupt:
					self.__print("Scanning is interrupted by users. The results may be incomplete. ", Warning)
				if len(possibleTargets) > 1:
					self.__print("Possible targets are listed as follows. ", Prompt)
					try:
						length = len(str(len(possibleTargets)))
						for i, target in enumerate(possibleTargets):
							self.__print("{{0:>{0}}} = \"{{1}}\"".format(length).format(i + 1, target), Prompt, 1)
						self.__print("{{0:>{0}}} = \"{{1}}\"".format(length).format(0, "I do not wish to select any of them. "), Prompt, 1)
					except KeyboardInterrupt:
						self.__print("Printing is interrupted by users. The results may be incomplete. ", Warning)
					print() # print an empty line
					choice = self.__input("Please select a tex file as the main file to continue: ", Prompt)
					if choice == 0:
						self.__print("The main tex selection is cancelled by users. ", Warning)
						return False
					elif choice in possibleTargets:
						self.__mainTexPath = choice
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
						return self.__resolve()
					else:
						try:
							self.__mainTexPath = choice[int(choice) - 1]
							self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
							return self.__resolve()
						except:
							self.__print("Invalid choice is made. Failed to resolve main tex. ", Error)
							return False
				elif len(possibleTargets) == 1:
					self.__mainTexPath = possibleTargets[0]
					self.__print("The main tex path is set to \"{0}\" automatically since there is only one tex file detected. ".format(self.__mainTexPath), Info)
					return self.__resolve()
				else:
					self.__print("No tex files are detected under the specified folder.. ", Error)
					return False
			else:
				self.__print("Setup failed since the main tex cannot be read. ", Error)
				return False
		except KeyboardInterrupt:
			self.__print("The setup procedure is interrupted by users. ", Error)
			return False
		except BaseException as e:
			self.__print("Exceptions occurred during the setup. Details are as follows. ", Critical)
			self.__print(e, Critical, indentationCount = 1)
			return False


def clearScreen(fakeClear:int = 120) -> bool:
	if CLEAR_SCREEN_COMMAND is not None and not os.system(CLEAR_SCREEN_COMMAND):
		return True
	else:
		try:
			print("\n" * int(fakeClear))
		except:
			print("\n" * 120)
		return False

def preExit(countdownTime:int = 5) -> None:
	try:
		cntTime = int(countdownTime)
		length = len(str(cntTime))
	except:
		return
	print()
	while cntTime > 0:
		print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime), end = "")
		try:
			sleep(1)
		except:
			print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(0))
			return
		cntTime -= 1
	print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime))

def main() -> int:
	clearScreen()
	if len(argv) > 2:
		processPool = [os.system(STARTUP_COMMAND_FORMAT.format(executable, __file__, mainTexPath)) for mainTexPath in argv[1:]]
		print(																															\
			"As multiple options were given, {0} child processes have been launched, where {1} succeeded and {2} failed. ".format(		\
				len(processPool), 																										\
				processPool.count(EXIT_SUCCESS), 																						\
				len(processPool) - processPool.count(EXIT_SUCCESS)																		\
			)																															\
		)
		preExit()
		return EXIT_SUCCESS if not any(processPool) else EXIT_FAILURE
	else:
		checker = Checker(argv[1] if 2 == len(argv) else None)
		checker.setup()
		checker.printPointer()
		checker.printStructure()
		preExit()
		return EXIT_SUCCESS if checker else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())
