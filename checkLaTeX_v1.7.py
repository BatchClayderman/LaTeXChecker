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
	def __str__(self:object) -> str:
		return str(self.symbol)
Prompt = DebugLevel({"character":"P", "name":"Prompt", "symbol":"[P]", "value":100})
Critical = DebugLevel({"character":"C", "name":"Critical", "symbol":"[C]", "value":50})
Error = DebugLevel({"character":"E", "name":"Error", "symbol":"[E]", "value":40})
Warning = DebugLevel({"character":"W", "name":"Warning", "symbol":"[W]", "value":30})
Info = DebugLevel({"character":"I", "name":"Info", "symbol":"[I]", "value":20})
Debug = DebugLevel({"character":"D", "name":"Info", "symbol":"[D]", "value":10})

class PointerNode:
	def __init__(self:object, filePath:str, lineIdx:int = 0, charIdx:int = 0, parentPointerNode:object = None) -> object:
		self.__filePath = os.path.abspath(str(filePath).replace("\"", "")) # must be an absolute path since __eq__ needs to use it
		self.__lineIdx = lineIdx if isinstance(lineIdx, int) and lineIdx >= -1 else 0 # -1 stands for empty file
		self.__charIdx = charIdx if isinstance(charIdx, int) and charIdx >= -1 else 0 # -1 stands for empty line
		self.__parentPointerNode = parentPointerNode if isinstance(parentPointerNode, PointerNode) else None
		self.__children = None # initialization flag
		self.__lines = None # initialization flag
		self.__remainingRequiredCount = 0
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
			self.__children = None # avoid re-initialization
			self.__lines = None # avoid re-initialization
			return False
		else:
			self.__children = []
			self.__lines = content.splitlines()
			if self.__lines:
				if self.__lineIdx < 0:
					self.__lineIdx = 0
				elif self.__lineIdx >= len(self.__lines):
					self.__lineIdx = len(self.__lines) - 1
				if self.__lines[self.__lineIdx]:
					if self.__charIdx < 0:
						self.__charIdx = 0
					elif self.__charIdx >= len(self.__lines[self.__lineIdx]):
						self.__charIdx = len(self.__lines[self.__lineIdx]) - 1
				else:
					self.__charIdx = -1
			else:
				self.__lineIdx, self.__charIdx = -1, -1
			return True
	def isInitialized(self:object) -> bool:
		return isinstance(self.__children, list) and isinstance(self.__lines, list)
	def hasNextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			lineIdx, charIdx = self.__lineIdx, self.__charIdx
			while requiredOffset:
				charIdx += 1
				if 0 <= lineIdx < len(self.__lines):
					if 0 <= charIdx < len(self.__lines[lineIdx]):
						requiredOffset -= 1
					elif lineSwitch:
						lineIdx += 1
						charIdx = -1
					else:
						self.__remainingRequiredCount = requiredOffset
						return False
				else:
					self.__remainingRequiredCount = requiredOffset
					return False # No more lines
			self.__remainingRequiredCount = 0
			return True
		else:
			return False
	def hasNextLine(self:object, offset:int = 1) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			lineIdx = self.__lineIdx
			while requiredOffset:
				lineIdx += 1
				if 0 <= lineIdx < len(self.__lines):
					if self.__lines[lineIdx]:
						requiredOffset -= 1
				else:
					self.__remainingRequiredCount = requiredOffset
					return False # No more lines
			self.__remainingRequiredCount = 0
			return True
		else:
			return False
	def getCurrentChar(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx] if self.isInitialized() and 0 <= self.__lineIdx < len(self.__lines) and 0 <= self.__charIdx < len(self.__lines[self.__lineIdx]) else None
	def getCurrentLocation(self:object) -> tuple:
		return (self.__filePath, self.__lineIdx, self.__charIdx) if self.isInitialized() else None
	def getNextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> str:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			lineIdx, charIdx = self.__lineIdx, self.__charIdx
			sRet = ""
			while requiredOffset:
				charIdx += 1
				if 0 <= lineIdx < len(self.__lines):
					if 0 <= charIdx < len(self.__lines[lineIdx]):
						requiredOffset -= 1
						sRet += self.__lines[lineIdx][charIdx]
					elif lineSwitch:
						lineIdx += 1
						charIdx = -1
					else:
						self.__remainingRequiredCount = requiredOffset
						return sRet
				else:
					self.__remainingRequiredCount = requiredOffset
					return sRet # No more lines
			self.__remainingRequiredCount = 0
			return sRet
		else:
			return ""
	def nextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			lineIdx, charIdx = self.__lineIdx, self.__charIdx
			while requiredOffset:
				charIdx += 1
				if 0 <= lineIdx < len(self.__lines):
					if 0 <= charIdx < len(self.__lines[lineIdx]):
						requiredOffset -= 1
					elif lineSwitch:
						lineIdx += 1
						charIdx = -1
					else:
						self.__remainingRequiredCount = requiredOffset
						return False
				else:
					self.__remainingRequiredCount = requiredOffset
					return False # No more lines
			self.__lineIdx, self.__charIdx = lineIdx, charIdx
			self.__remainingRequiredCount = 0
			return True
		else:
			return False
	def nextLine(self:object, offset:int = 1) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			lineIdx = self.__lineIdx
			while requiredOffset:
				lineIdx += 1
				if 0 <= lineIdx < len(self.__lines):
					if self.__lines[lineIdx]:
						requiredOffset -= 1
				else:
					self.__remainingRequiredCount = requiredOffset
					return False # No more lines
			self.__lineIdx, self.__charIdx = lineIdx, 0
			self.__remainingRequiredCount = 0
			return True
		else:
			return False
	def getRemainingRequiredCount(self:object) -> int:
		return self.__remainingRequiredCount if self.isInitialized() else None
	def addChildPointerNode(self:object, pointerNode:object) -> bool:
		if isinstance(pointerNode, PointerNode) and pointerNode.isInitialized():
			self.__children.append(pointerNode)
			return True
		else:
			return False
	def getFilePath(self:object) -> str:
		return self.__filePath if self.isInitialized() else None
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
		self.__pointerNodeStack = [] # stack (stack[0] is the root)
		self.__pointerNodeStack.append(PointerNode(absRootFilePath)) # write separately to avoid absence of this attribute caused by exceptions in PointerNode
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
		return isinstance(self.__currentPointerNode, PointerNode)
	def hasNextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			stack = self.__pointerNodeStack[::]
			while stack:
				node = stack.pop()
				if node.hasNextChar(requiredOffset, lineSwitch):
					return True
				else:
					requiredOffset -= node.getRemainingRequiredCount()
			return False
		else:
			return False
	def hasNextLine(self:object, offset:int = 1) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			stack = self.__pointerNodeStack[::]
			while stack:
				node = stack.pop()
				if node.hasNextLine(requiredOffset):
					return True
				else:
					requiredOffset -= node.getRemainingRequiredCount()
			return False
		else:
			return False
	def getCurrentChar(self:object) -> str:
		return self.__currentPointerNode.getCurrentChar() if self.isInitialized() else None
	def getCurrentLocation(self:object) -> tuple:
		if self.isInitialized():
			tp = self.__currentPointerNode.getCurrentLocation()
			return (os.path.relpath(str(tp[0]), self.__baseFolderPath), tp[1], tp[2]) if isinstance(tp, tuple) else None
		else:
			return None
	def getCurrentLocationDescription(self:object) -> str:
		tp = self.getCurrentLocation()
		return "Char {0}, Line {1}, File \"{2}\"".format(tp[2], tp[1], tp[0]) if isinstance(tp, tuple) else None
	def getNextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> str:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			sRet = ""
			stack = self.__pointerNodeStack[::]
			while stack:
				node = stack.pop()
				sRet += node.getNextChar(requiredOffset, lineSwitch)
				remainingRequiredCount = node.getRemainingRequiredCount()
				if remainingRequiredCount:
					requiredOffset -= remainingRequiredCount
				else:
					return sRet
			return sRet
		else:
			return ""
	def nextChar(self:object, offset:int = 1, lineSwitch:bool = True) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			stack = self.__pointerNodeStack[::]
			while stack:
				node = stack.pop()
				if node.nextChar(requiredOffset, lineSwitch):
					self.__pointerNodeStack = stack
					return True
				else:
					requiredOffset -= node.getRemainingRequiredCount()
			return False
		else:
			return False
	def nextLine(self:object, offset:int = 1) -> bool:
		if isinstance(offset, int) and offset >= 1 and self.isInitialized():
			requiredOffset = offset
			stack = self.__pointerNodeStack[::]
			while stack:
				node = stack.pop()
				if node.nextLine(requiredOffset):
					selfl.__pointerNodeStack = stack
					return True
				else:
					requiredOffset -= node.getRemainingRequiredCount()
			return False
		else:
			return False
	def addPointerNode(self:object, filePath:str) -> bool:
		if not self.isInitialzed():
			self.__lastError = "The instance of ``Pointer`` has not been initialized. "
			return False
		absFilePath = str(filePath).replace("\"", "")
		absFilePath = os.path.abspath(absFilePath if os.path.isabs(absFilePath) else os.path.join(self.__baseFolderPath, absFilePath))
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
		return str(self.__lastError)
	def leaveCurrentPointerNode(self:object) -> bool:
		if self.isInitialized() and len(self.__pointerNodeStack) > 1:
			self.__pointerNodeStack.pop()
			self.__currentPointerNode = self.__pointerNodeStack[-1]
			return True
		else:
			return False
	def getTree(self:object, indentationCount:int = 0, indentationSymbol:str = "\t") -> str:
		if isinstance(indentationCount, int) and indentationCount >= 0 and "\r" not in indentationSymbol and "\n" not in indentationSymbol and self.isInitialized():
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
	def __init__(self:object, header:str = "", body:str = "", footer:str = "") -> object:
		self.__header = str(header).strip()
		self.__body = str(body)
		self.__footer = str(footer).strip()
		self.__type = None # initialization flag
		self.__descriptor = None
		self.__children = None # initialization flag
	def initialize(self:object) -> bool:
		if self.__header.startswith("\\begin{") and "}" in self.__header:
			self.__type = "Environment"
			self.__descriptor = self.__header[7:self.__latexCommand.index("}")].strip()
		elif self.__header in ("$$", "$", "\\[", "\\("):
			self.__type = "Equation"
			self.__descriptor = self.__header
		else:
			self.__type = "Text"
			self.__descriptor = None
		self.__children = []
		return True
	def isInitialized(self:object) -> bool:
		return isinstance(self.__type, str) and isinstance(self.__children, list)
	def addChildStructureNode(self:object, structureNode:object) -> bool:
		if self.isInitialized() and isinstance(structureNode, StructureNode):
			self.__children.append(structureNode)
			return True
		else:
			return False
	def isFooterAccepted(self:object, footer:str) -> bool:
		if not self.isInitialized():
			return False
		strippedFooter = str(footer).strip()
		if strippedFooter.startswith("\\end{") and "}" in strippedFooter:
			return "Environment" == self.__type and strippedFooter[5:strippedFooter.index("}")] == self.__descriptor
		elif strippedFooter in ("$$", "$", "\\[", "\\("):
			return "Equation" == self.__type and strippedFooter == self.__descriptor
		else:
			return "Text" == self.__type and "" == strippedFooter
	def setFooter(self:object, footer:str) -> bool:
		if self.isFooterAccepted(footer):
			self.__footer = str(footer).strip()
			return True
		else:
			return False
	def getChildren(self:object, isReversed:bool = False) -> list:
		return (self.__children[::-1] if isReversed else self.__children[::]) if self.isInitialized() else None
	def __str__(self:object) -> str:
		return "{0}({1})".format(self.__type, self.__descriptor)

class Structure:
	def __init__(self:object) -> object:
		self.__rootStructureNode = None # initialization flag
		self.__currentStructureNode = None # initialization flag
	def initialize(self:object) -> bool:
		self.__rootStructureNode = StructureNode()
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
		if self.isInitialized():
			self.__currentStructureNode.addPlainText(strings)
			return True
		else:
			return False
	def addStructureNode(self:object, header:str = "", body:str = "", footer:str = "") -> bool:
		if self.isInitialized():
			structureNode = StructureNode(header = header, body = body, footer = footer)
			if structureNode.initialize() and self.__currentStructureNode.addChildStructureNode(structureNode):
				self.__currentStructureNode = structureNode
				self.__structureNodeStack.append(structureNode)
				return True
			else:
				return False
		else:
			return False
	def canLeaveCurrentStructureNode(self:object, footer:str = "") -> bool:
		return self.isInitialized() and self.__currentStructureNode.isFooterAccepted(footer) and len(self.__structureNodeStack) > 1
	def leaveCurrentStructureNode(self:object, footer:str = "") -> bool:
		if self.canLeaveCurrentStructureNode(footer):
			self.__currentStructureNode.setFooter(footer)
			self.__structureNodeStack.pop()
			self.__currentStructureNode = self.__structureNodeStack[-1]
			return True
		else:
			return False
	def getTree(self:object, indentationCount:int = 0, indentationSymbol:str = "\t") -> str:
		if isinstance(indentationCount, int) and indentationCount >= 0 and "\r" not in indentationSymbol and "\n" not in indentationSymbol and self.isInitialized():
			stack = [(self.__rootStructureNode, 0)]
			res = []
			while stack:
				node, level = stack.pop()
				if node.isInitialized():
					res.append("{0}{1}".format(str(indentationSymbol) * level, node))
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
	def __print(self:object, strings:str, dbgLevel:DebugLevel = Info, indentationCount:int = 0, indentationSymbol:str = "\t") -> bool:
		debugLevel = dbgLevel if isinstance(dbgLevel, DebugLevel) else Info
		if debugLevel >= self.__debugLevel:
			print("{0} {1}{2}".format(debugLevel, (str(indentationSymbol) * indentationCount if isinstance(indentationCount, int) and indentationCount >= 1 else ""), strings))
			return True
		else:
			return False
	def __input(self:object, strings:str, indentationCount:int = 0, indentationSymbol:str = "\t") -> str:
		try:
			return input("{0} {1}{2}".format(Prompt, (str(indentationSymbol) * indentationCount if isinstance(indentationCount, int) and indentationCount >= 1 else ""), strings))
		except KeyboardInterrupt:
			print()
			self.__print("The input process was interrupted by users. None will be returned as the default value. ", Warning)
			return None
	def __resolve(self:object) -> bool:
		self.__flag = False
		self.__pointer = Pointer(self.__mainTexPath)
		self.__structure = Structure()
		if not self.__pointer.initialize():
			self.__print("Failed to initialize the main tex file. Please check if the file can be read. ", Error)
			return False
		isLeftPart = True # indicate the "$" or "$$" got is the left part or not
		while self.__pointer.hasNextChar():
			if not self.__pointer.hasNextChar(lineSwitch = False): # if there is not a character following the current character in this line
				self.__structure.addPlainText("\n")
				self.__pointer.nextLine() # switch to the next line
				continue
			self.__pointer.nextChar()
			ch = self.__pointer.getCurrentChar()
			print(ch)
			input(ch)
			if "\\" == ch:
				if self.__pointer.getNextChar(3, False) == "end" or self.__pointer.getNextChar(5, False) == "begin":
					isBeginner = self.__pointer.getNextChar(1, False) == "b" # to speed up
					s = "begin" if isBeginner else "end"
					self.__pointer.nextChar(5 if isBeginner else 3, False)
					if self.__pointer.hasNextChar():
						if not self.__pointer.hasNextChar(lineSwitch = False): # not in the same line
							self.__pointer.nextLine() # allow at most one empty line and a next line must exist if there is a next char with the line switch on while not with the line switch off
						if self.__pointer.hasNextChar(lineSwitch = False): # in the same line
							self.__pointer.nextChar(1, False)
							ch = self.__pointer.getCurrentChar()
							if ch == "{":
								escapeFlag = False
								environmentName = "" # to avoid "\begin{}"/"\end{}" and record the name
								while self.__pointer.hasNextChar(lineSwitch = False):
									self.__pointer.nextChar(1, False)
									ch = self.__pointer.getCurrentChar()
									if ch == "\\":
										if escapeFlag:
											self.__print("An invalid \"\\\\\" command is used in \"\\{0}{{}}\" at {1}. ".format(s, self.__pointer.getCurrentLocationDescription()), Error)
											return False
										else:
											environmentName += "\\"
											escapeFlag = True
									elif ch == "}":
										break
									elif "A" <= ch <= "Z" or "a" <= ch <= "z":
										environmentName += ch
										escapeFlag = False
									else:
										self.__print("An invalid character \'{0}\' is used in \"\\{1}{{}}\" at {2}. ".format(ch, s, self.__pointer.getCurrentLocationDescription()), Error)
										return False
								else:
									self.__print("The line is ended at {0} while handling the \"\\{1}{{}}\" command. ".format(self.__pointer.getCurrentLocationDescription(), s), Error)
									return False
								if escapeFlag: # to avoid "\begin{...\}"/"\end{...\}"
									self.__print("The \"\\}\" is not allowed in environment names but used at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								if environmentName:
									if isBeginner:
										if self.__structure.addStructureNode(header = "\\begin{{{0}}}".format(environmentName)):
											self.__print("A new structure node is added: \"\\begin{{{0}}}\". ".format(environmentName), Debug)
										else:
											self.__print("Failed to initialize a new structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									else:
										if self.__structure.leaveCurrentStructureNode(footer = "\\end{{{0}}}".format(environmentName)):
											self.__print("Leave current structure node with \"\\end{{{0}}}\". ".format(environmentName), Debug)
										else:
											self.__print("Failed to leave the current structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
								else:
									self.__print("An empty environment name is detected at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
							elif ch.strip():
								self.__print("An invalid \"\\{0}\" command is detected at {1}. ".format(s, self.__pointer.getCurrentLocationDescription()), Error)
								return False
						else:
							self.__print("There are too many lines after the \"\\{0}\" command at {1}. At most one empty line is accepted. ".format(s, self.__pointer.getCurrentLocationDescription()), Error)
							return False
					else:
						self.__print("The resolving ended while scanning use of \"\\{0}\". ".format(s), Error)
						return False
				elif self.__pointer.getNextChar(1, False) in ("(", "[", ")", "]"):
					self.__pointer.nextChar(1, False)
					ch = self.__pointer.getCurrentChar()
					if ch in ("(", "["):
						if self.__structure.addStructureNode(header = "\\{0}".format(ch)):
							self.__print("A new structure node is added: \"\\{0}\". ".format(ch), Debug)
						else:
							self.__print("Failed to initialize a new structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
							return False
					else: # ch in (")", "]")
						if self.__structure.leaveCurrentStructureNode(footer = "\\{0}".format(ch)):
							self.__print("Leave current structure node with \"\\{0}\". ".format(ch), Debug)
						else:
							self.__print("Failed to leave the current structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
							return False
				else: # plain text (avoid "\\")
					self.__structure.addPlainText("\\")
					if self.__pointer.hasNextChar(lineSwitch = False):
						self.__pointer.nextChar()
						self.__structure.addPlainText(self.__pointer.getCurrentChar())
					elif self.__pointer.hasNextLine():
						self.__pointer.nextLine()
						self.__structure.addPlainText("\n")
			elif "$" == ch: # if the previous char is '\', the '\' will be absorted in the codes for avoiding "\\" above
				if self.__pointer.getNextChar(1, False) == "$":
					self.__pointer.nextChar(lineSwitch = False)
					ch = "$$" # else: ch = "$"
				if isLeftPart:
					if self.__structure.addStructureNode(header = ch):
						self.__print("A new structure node is added: \"{0}\". ".format(ch), Debug)
					else:
						self.__print("Failed to initialize a new structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
						return False
				else:
					if self.__structure.leaveCurrentStructureNode(footer = ch):
						self.__print("Leave current structure node with \"{0}\". ".format(ch), Debug)
					else:
						self.__print("Failed to leave the current structure node at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
						return False
				isLeftPart = not isLeftPart # switch to the other part
			else:
				self.__structure.addPlainText(ch)
		self.__flag = True
	def printPointer(self:object) -> None:
		print(self.__pointer.getTree())
	def printStructure(self:object) -> None:
		print(self.__structure.getTree())
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
		except Exception as e:
			self.__print("Exceptions occurred during the setup. Details are as follows. ", Critical)
			self.__print(e, Critical, 1)
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
		print(													\
			"As multiple options were given, {0} child processes have been launched, where {1} succeeded and {2} failed. ".format(	\
				len(processPool), 										\
				processPool.count(EXIT_SUCCESS), 								\
				len(processPool) - processPool.count(EXIT_SUCCESS)						\
			)												\
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