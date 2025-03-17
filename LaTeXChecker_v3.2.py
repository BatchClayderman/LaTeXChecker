import os
from sys import argv, executable, exit
from re import findall
from subprocess import Popen
from time import perf_counter, sleep
PLATFORM = __import__("platform").system().upper()
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
CLEAR_SCREEN_COMMAND = ("CLS" if PLATFORM == "WINDOWS" else "clear") if __import__("sys").stdin.isatty() else None
STARTUP_COMMAND_FORMAT = "START \"\" \"{0}\" \"{1}\" \"{2}\"" if PLATFORM == "WINDOWS" else "\"{0}\" \"{1}\" \"{2}\" &"


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
Fatal = DebugLevel({"character":"F", "name":"Fatal", "symbol":"[F]", "value":60})
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
	def __getTxt(self:object, filePath:str) -> str|None: # get ``*.txt`` content
		for coding in ("utf-8", "ANSI", "utf-16", "gbk"): # codings (add more codings here if necessary)
			try:
				with open(filePath, "r", encoding = coding) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				continue
			except:
				return None
		return None
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
	def getCurrentLine(self:object) -> str:
		return self.__lines[self.__lineIdx] if self.isInitialized() and self.__lineIdx < len(self.__lines) else None
	def getRemainingChars(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx + 1:] if self.isInitialized() and self.__lineIdx < len(self.__lines) else None
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
		return bool(self.__pointerNodeStack) and isinstance(self.__currentPointerNode, PointerNode)
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
			while len(self.__pointerNodeStack) > 1: # no need to consider the switch again; keep the main file in the stack
				if self.__pointerNodeStack[-1].nextChar():
					return True
				elif not self.__pointerNodeStack[-1].isEOF(): # there is a following line but there is not a following character
					return False
				self.__pointerNodeStack.pop()
				self.__currentPointerNode = self.__pointerNodeStack[-1] # move the pointer
			if self.__pointerNodeStack[0].nextChar(): # all the opened non-main files report EOF
				return True
			else:
				return False # the main file
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
			while len(self.__pointerNodeStack) > 1: # keep the main file in the stack
				if self.__pointerNodeStack[-1].nextLine():
					return True
				self.__pointerNodeStack.pop()
				self.__currentPointerNode = self.__pointerNodeStack[-1] # move the pointer
			if self.__pointerNodeStack[0].nextLine(): # all the opened non-main files report the end of lines
				return True
			else:
				return False # the main file
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
	def getCurrentLine(self:object) -> str:
		return self.__currentPointerNode.getCurrentLine() if self.isInitialized() else None
	def getRemainingCharactersInTheCurrentLineOfTheCurrentFile(self:object) -> str:
		return self.__currentPointerNode.getRemainingChars() if self.isInitialized() else None
	def getCurrentLocation(self:object) -> tuple:
		if self.isInitialized():
			tp = self.__currentPointerNode.getCurrentLocation()
			return (os.path.relpath(str(tp[0]), self.__baseFolderPath), tp[1], tp[2]) if isinstance(tp, tuple) else None
		else:
			return None
	def getCurrentLocationDescription(self:object) -> str:
		tp = self.getCurrentLocation()
		return ("Char {0}, Line {1}, File \"{2}\"".format(tp[2], tp[1] + 1, tp[0]) if tp[2] >= 0 else "Line {1}, File \"{2}\"".format(tp[2], tp[1] + 1, tp[0])) if isinstance(tp, tuple) else None
	def addPointerNode(self:object, filePath:str, canCallAgain:bool = True) -> bool:
		if not self.isInitialized():
			self.__lastError = "The instance of ``Pointer`` has not been initialized. "
			return False
		elif not isinstance(filePath, str):
			self.__lastError = "The passed file path is not a string. "
			return False
		elif not isinstance(canCallAgain, bool):
			self.__lastError = "The flag for calling the pointer node adding method function is unclear. "
			return False
		strippedFilePath = filePath.replace("\"", "").strip()
		absFilePath = os.path.abspath(strippedFilePath if os.path.isabs(strippedFilePath) else os.path.join(self.__baseFolderPath, strippedFilePath))
		if absFilePath in self.__pointerNodeStack:
			self.__lastError = "The file \"{0}\" has been in the stack for resolving. Please check and make sure that there are no recursive calls. ".format(absFilePath).replace("\\", "\\\\")
			return False
		pointerNode = PointerNode(absFilePath, parentPointerNode = self.__currentPointerNode)
		if pointerNode.initialize() and self.__currentPointerNode.addChildPointerNode(pointerNode):
			self.__currentPointerNode = pointerNode
			self.__pointerNodeStack.append(pointerNode)
			self.__lastError = "Currently, there are no errors. "
			return True
		elif canCallAgain and not strippedFilePath.endswith(".bib") and not strippedFilePath.endswith(".tex"): # call again for the ``.tex`` extension added
			return self.addPointerNode(strippedFilePath + ".tex", False)
		else:
			self.__lastError = "Failed to initialize the call to \"{0}\". ".format(absFilePath).replace("\\", "\\\\")
			return False
	def getBaseFolderPath(self:object) -> str:
		return self.__baseFolderPath
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
		self.__media = None # initialization flag
		self.__parent = parent if isinstance(parent, StructureNode) else None
	def initialize(self:object) -> bool:
		if self.__header:
			if "Root" == self.__header:
				self.__type = "Root"
				self.__descriptor = None
			elif self.__header.startswith("\\begin{") and self.__header.endswith("}"):
				self.__type = "Environment"
				self.__descriptor = self.__header[7:-1] # cannot compile "\\begin{ equation }" in LaTeX
			elif self.__header.startswith("\\documentclass"):
				self.__type = "DocumentClass"
				self.__descriptor = None
			elif (																						\
				(																					\
					self.__header.startswith("\\section{") or self.__header.startswith("\\section*{")					\
					or self.__header.startswith("\\subsection{") or self.__header.startswith("\\subsection*{")			\
					or self.__header.startswith("\\subsubsection{") or self.__header.startswith("\\subsubsection*{")		\
				)																					\
				and self.__header.endswith("}")															\
			):
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
			self.__media = {}
			return True
		else:
			self.__type = None # avoid re-initialization
			self.__children = None # avoid re-initialization
			self.__media = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return isinstance(self.__type, str) and isinstance(self.__children, list) and isinstance(self.__media, dict)
	def addChildStructureNode(self:object, structureNode:object) -> bool:
		if self.isInitialized() and isinstance(structureNode, StructureNode):
			self.__children.append(structureNode)
			return True
		else:
			return None
	def isFooterAccepted(self:object, footer:str) -> bool:
		if self.isInitialized() and isinstance(footer, str):
			if "Root" == footer or footer.startswith("\\documentclass"):
				return self.__type in ("DocumentClass", "Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
			elif "\\begin{thebibliography}" == footer:
				return self.__type in ("Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
			elif "\\end{document}" == footer:
				return self.__type in ("Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*") or "Environment" == self.__type and "document" == self.__descriptor
			elif footer.startswith("\\end{") and footer.endswith("}"):
				return (
					"Environment" == self.__type and footer[5:-1] == self.__descriptor
					or "document" == footer[5:-1] and self.__type in ("Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
				)
			elif (footer.startswith("\\section{") or footer.startswith("\\section*{") or footer.startswith("\\subsection{") or footer.startswith("\\subsection*{") or footer.startswith("\\subsubsection") or footer.startswith("\\subsubsection*")) and footer.endswith("}"):
				if self.__type in ("Section", "Section*"):
					return footer.startswith("\\section{") or footer.startswith("\\section*{") # only "\\section" and "\\section*" are allowed
				elif self.__type in ("Subsection", "Subsection*"):
					return footer.startswith("\\section{") or footer.startswith("\\section*{") or footer.startswith("\\subsection{") or footer.startswith("\\subsection*{") # >=
				elif self.__type in ("Subsubsection", "Subsubsection*"):
					return True # all the three are accepted
				else:
					return False
			elif footer in ("$", "$$"):
				return "Equation" == self.__type and footer == self.__descriptor
			elif "\\)" == footer:
				return "Equation" == self.__type and "\\(" == self.__descriptor
			elif "\\]" == footer:
				return "Equation" == self.__type and "\\[" == self.__descriptor
			else: # Root etc. 
				return False
		else:
			return None
	def setFooter(self:object, footer:str) -> bool:
		bRet = self.isFooterAccepted(footer)
		if bRet and self.__header not in ("DocumentClass", "Section", "Section*", "Subsection", "Subsubsection"): # the "documentclass" and section-like structures do not require footnotes
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
	def addMedia(self:object, mediumType:str) -> bool:
		if self.isInitialized() and isinstance(mediumType, str):
			self.__media.setdefault(mediumType, 0)
			self.__media[mediumType] += 1
			return True
		else:
			return None
	def getType(self:object) -> str:
		return self.__type # return None if it is None
	def getDescriptor(self:object) -> str|None:
		return self.__descriptor # return None if it is None
	def getMedia(self:object, mediumType:str|tuple|list|None = None) -> int|tuple:
		if self.isInitialized():
			if mediumType is None:
				return tuple(self.__media.items())
			elif isinstance(mediumType, str):
				return self.__media[mediumType] if mediumType in self.__media else 0
			elif isinstance(mediumType, tuple):
				return tuple((self.__media[m] if m in self.__media else 0) for m in mediumType if isinstance(m, str))
			elif isinstance(mediumType, list):
				return [(self.__media[m] if m in self.__media else 0) for m in mediumType if isinstance(m, str)]
			else:
				return None
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
	def addMedia(self:object, mediumType:str) -> bool:
		if isinstance(mediumType, str):
			bRet = True
			pStructureNode = self.__currentStructureNode
			while pStructureNode != self.__rootStructureNode:
				bRet = pStructureNode.addMedia(mediumType) and bRet
				pStructureNode = pStructureNode.getParent()
			bRet = pStructureNode.addMedia(mediumType) and bRet # the root
			return bRet
		else:
			return False
	def addStructureNode(self:object, header:str) -> bool:
		if self.isInitialized() and isinstance(header, str):
			while (																									\
				(																									\
					(																								\
						header.startswith("\\documentclass") or header.startswith("\\section{") or header.startswith("\\section*{")			\
						or header.startswith("\\subsection{") or header.startswith("\\subsection*{")									\
						or header.startswith("\\subsubsection{") or header.startswith("\\subsubsection*{")							\
					)																								\
					and header.endswith("}") or "\\begin{thebibliography}" == header											\
				) and self.__currentStructureNode.isFooterAccepted(header)													\
			): # go back to the parent node if the footer is accepted
				self.__currentStructureNode = self.__currentStructureNode.getParent()
			structureNode = StructureNode(header = header, parent = self.__currentStructureNode)
			if structureNode.initialize() and self.__currentStructureNode.addChildStructureNode(structureNode):
				self.__currentStructureNode = structureNode
				return True
			else:
				return False
		else:
			return None
	def canLeaveCurrentStructureNode(self:object, footer:str) -> bool:
		if self.isInitialized() and isinstance(footer, str):
			return self.__currentStructureNode != self.__rootStructureNode and self.__currentStructureNode.isFooterAccepted(footer)
		else:
			return None
	def leaveCurrentStructureNode(self:object, footer:str = "", leavingQueue:list = []) -> bool:
		if isinstance(leavingQueue, list):
			leavingQueue.clear()
		else:
			return None
		bRet = self.canLeaveCurrentStructureNode(footer)
		if bRet:
			if footer == "\\end{document}":
				while self.canLeaveCurrentStructureNode(footer):
					self.__currentStructureNode.setFooter(footer)
					leavingQueue.append(str(self.__currentStructureNode))
					self.__currentStructureNode = self.__currentStructureNode.getParent()
			else:
				self.__currentStructureNode.setFooter(footer)
				leavingQueue.append(str(self.__currentStructureNode))
				self.__currentStructureNode = self.__currentStructureNode.getParent()
		return bRet
	def getCurrentStructureNodeDescription(self:object) -> str:
		return str(self.__currentStructureNode) if self.isInitialized() else None
	def endStructure(self:object) -> bool:
		while self.canLeaveCurrentStructureNode("Root"):
			self.leaveCurrentStructureNode("Root")
		return self.__currentStructureNode == self.__rootStructureNode
	def getMedia(self:object, mediumType:str|tuple|list|None = None, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(mediumType, (str, tuple, list, None)) and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__rootStructureNode, indentationCount)]
			res = []
			while stack:
				node, level = stack.pop()
				if isinstance(node, StructureNode) and node.isInitialized():
					r = node.getMedia(mediumType)
					if isinstance(r, int) and r >= 1: # pruning
						res.append("{0}{1} -> {2}".format(indentationSymbol * level, node, r))
						stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None
	def getTree(self:object, mode:str = "A", indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(mode, str) and mode in ("A", "B", "D") and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__rootStructureNode, indentationCount)]
			res = []
			if "D" == mode:
				while stack:
					node, level = stack.pop()
					if isinstance(node, str): # also shows the text
						res.append("{0}Text({1})".format(indentationSymbol * level, len(node)))
					elif node.isInitialized():
						res.append("{0}{1}".format(indentationSymbol * level, node))
						stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			elif "B" == mode:
				while stack:
					node, level = stack.pop() # only shows some necessary items
					if isinstance(node, StructureNode) and node.isInitialized() and node.getType() in ("Root", "DocumentClass", "Environment", "Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*"):
						res.append("{0}{1}".format(indentationSymbol * level, node))
						stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			else:
				while stack:
					node, level = stack.pop()
					if isinstance(node, StructureNode) and node.isInitialized():
						nodeType = node.getType()
						if nodeType in ("Root", "DocumentClass", "Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*"):
							res.append("{0}{1}".format(indentationSymbol * level, nodeType)) # only shows the type
							stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
						elif "Environment" == nodeType:
							res.append("{0}{1}".format(indentationSymbol * level, node.getDescriptor())) # only shows the descriptor
							stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None

class Checker:
	def __init__(self:object, mainTeXPath:str = None, debugLevel:DebugLevel|int = Debug, workflows:str|None = None) -> object:
		self.__mainTeXPath = os.path.abspath(mainTeXPath.replace("\"", "")) if isinstance(mainTeXPath, str) else None # transfer to the absolute path
		self.__pointer = None
		self.__structure = None
		self.__definitions = {}
		self.__labels = {}
		self.__citations = {}
		if isinstance(debugLevel, DebugLevel):
			self.__debugLevel = debugLevel
		else:
			try:
				self.__debugLevel = DebugLevel({"value":int(debugLevel)})
			except:
				self.__debugLevel = Debug
				self.__print("The debug level specified is invalid. It is defaulted to {0} ({1}). ".format(self.__debugLevel.name, self.__debugLevel.value), Warning)
		if isinstance(workflows, str) and workflows:
			self.__workflows = workflows
			self.__print("Preset workflows are \"{0}\". ".format(self.__workflows), Info)
		else:
			self.__workflows = None
		self.__flag = False
	def __print(self:object, strings:str|object, debugLevel:DebugLevel = Info, indentationSymbol:str = "\t", indentationCount:int = 0) -> bool:
		if isinstance(debugLevel, DebugLevel) and isinstance(indentationSymbol, str) and isinstance(indentationCount, int):
			if debugLevel >= self.__debugLevel:
				try:
					print("\n".join(["{0} {1}{2}".format(debugLevel, (indentationSymbol * indentationCount if indentationCount >= 1 else ""), string) for string in str(strings).split("\n")]))
					return True
				except: # avoid exceptions in __str__
					return None
			else:
				return False
		else:
			return None
	def __input(self:object, strings:str, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		try:
			return input("\n".join(["{0} {1}{2}".format(Prompt, (indentationSymbol * indentationCount if isinstance(indentationSymbol, str) and isinstance(indentationCount, int) and indentationCount >= 1 else ""), string) for string in str(strings).splitlines()]))
		except KeyboardInterrupt:
			print() # print an empty line
			self.__print("The input process was interrupted by users. None will be returned as the default value. ", Warning)
			return None
		except BaseException as e:
			self.__print("The input process was interrupted by the following exceptions. ", Error)
			self.__print(e, Error, indentationCount = 1)
			return None
	def __skipSpaces(self:object, lineSwitch:bool = True) -> bool:
		if isinstance(lineSwitch, bool):
			while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"): # skip spaces in the current line
				self.__pointer.nextChar(fileSwitch = False)
			if self.__pointer.hasNextChar(fileSwitch = False): # remaining non-space characters exist
				return True
			elif lineSwitch: # allow a line separator
				if self.__pointer.hasNextLine(fileSwitch = False):
					self.__pointer.nextLine(fileSwitch = False)
					while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"): # skip spaces in the following line
						self.__pointer.nextChar(fileSwitch = False)
					if self.__pointer.hasNextChar(fileSwitch = False):
						return True
					else:
						self.__print("There should be only at most a line between the command definition command and the command but there are two more at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
						return False
				else:
					self.__print("While scanning the command, the file reports an EOF signal at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
					return False
			else:
				self.__print("There should be non-space characters at the end of the line at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
		else:
			return None
	def __fetchBraces(self:object, fileSwitch:bool = False) -> str:
		if not isinstance(fileSwitch, bool) or not self.__pointer.hasNextChar(fileSwitch = fileSwitch):
			return (False, "")
		if "{" == self.__pointer.getNextChar(fileSwitch = fileSwitch):
			layer, mainBody = 1, "{"
			self.__pointer.nextChar(fileSwitch = fileSwitch)
			while True:
				if self.__pointer.hasNextChar(fileSwitch = fileSwitch):
					ch = self.__pointer.getNextChar(fileSwitch = fileSwitch)
					mainBody += ch
					if "\\" == ch:
						if self.__pointer.hasNextChar(fileSwitch = fileSwitch):
							self.__pointer.nextChar(fileSwitch = fileSwitch)
							mainBody += self.__pointer.getCurrentChar()
						elif self.__pointer.hasNextLine(fileSwitch = fileSwitch):
							self.__pointer.nextLine(fileSwitch = fileSwitch)
							mainBody += "\n"
						else:
							self.__print("A missing \"}\" is detected when scanning the main body at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
							return False
					elif "{" == ch:
						layer += 1
					elif "}" == ch:
						layer -= 1
						if 0 == layer:
							break
					elif "%" == ch:
						if self.__pointer.hasNextLine(fileSwitch = fileSwitch):
							self.__pointer.nextLine(fileSwitch = fileSwitch)
						else:
							self.__print("There are not following lines after the \"%\" symbol at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
							return False
					self.__pointer.nextChar(fileSwitch = fileSwitch)
				elif self.__pointer.hasNextLine(fileSwitch = fileSwitch):
					self.__pointer.nextLine(fileSwitch = fileSwitch)
					mainBody += "\n"
				else:
					self.__print("An EOF signal is reported during scanning the main body at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
					return (False, mainBody)
			return (True, mainBody)
		elif "\\" == self.__pointer.getNextChar(fileSwitch = fileSwitch):
			mainBody = "\\"
			self.__pointer.nextChar(fileSwitch = fileSwitch)
			while True:
				if self.__pointer.hasNextChar(fileSwitch = fileSwitch):
					ch = self.__pointer.getNextChar(fileSwitch = fileSwitch)
					if "A" <= ch <= "Z" or "a" <= ch <= "z":
						mainBody += ch
					else:
						break
					self.__pointer.nextChar(fileSwitch = fileSwitch)
				else:
					break
			return (True, mainBody)
		else:
			self.__pointer.nextChar(fileSwitch = fileSwitch)
			return (True, self.__pointer.getCurrentChar())
	def __convertEscaped(self:object, string:str) -> str:
		if isinstance(string, str):
			vec = list(string)
			d = {"\\":"\\\\", "\"":"\\\"", "\'":"\\\'", "\a":"\\a", "\b":"\\b", "\f":"\\f", "\n":"\\n", "\r":"\\r", "\t":"\\t", "\v":"\\v"}
			for i, ch in enumerate(vec):
				if ch in d:
					vec[i] = d[ch]
				elif not ch.isprintable():
					vec[i] = "\\x" + hex(ord(ch))[2:]
			return "".join(vec)
		else:
			return str(string)
	def __handleBibTeX(self:object) -> bool:
		while True:
			if self.__pointer.hasNextChar(fileSwitch = False) and "@" == self.__pointer.getNextChar(fileSwitch = False):
				# Citation #
				line = self.__pointer.getCurrentLine()
				if "{" in line and "," in line:
					citation = line[line.index("{") + 1:line.index(",")]
				else:
					self.__print("A line starting with \"@\" contains unexpected citation information at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Warning)
					if self.__pointer.hasNextLine(fileSwitch = False):
						self.__pointer.nextLine(fileSwitch = False)
						continue # stop reading citation content and operating the dict
					else:
						self.__pointer.nextLine() # will switch to the parent pointer
						return True
				
				# Citation Content #
				citationContent = ""
				while self.__pointer.hasNextLine(fileSwitch = False):
					self.__pointer.nextLine(fileSwitch = False)
					if self.__pointer.hasNextChar(fileSwitch = False) and "}" == self.__pointer.getNextChar(fileSwitch = False):
						citationContent = citationContent[:-1] # remove the last "\n"
						break
					else:
						citationContent += self.__pointer.getCurrentLine().strip() + "\n"
				
				# Handle Dict #
				if citation in self.__citations:
					if self.__citations[citation][0] is None:
						self.__citations[citation][0] = citationContent
					elif isinstance(self.__citations[citation][0], list):
						self.__citations[citation][0].append(citationContent)
						self.__print(																													\
							"The citation \"{0}\" has already been defined {1} but is defined again at {2}. ".format(													\
								self.__convertEscaped(citation), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
							), Warning																												\
						)
					else:
						self.__citations[citation][0] = [self.__citations[citation][0], citationContent]
						self.__print("The citation \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(citation), self.__pointer.getCurrentLocationDescription()), Warning)
				else:
					self.__citations[citation] = [citationContent, 0] # [citationContent, citeCount]
					self.__print("A new citation \"{0}\" is added by BibTeX at {1}. ".format(self.__convertEscaped(citation), self.__pointer.getCurrentLocationDescription()), Debug)
			if self.__pointer.hasNextLine(fileSwitch = False):
				self.__pointer.nextLine(fileSwitch = False)
			else:
				self.__pointer.nextLine() # will switch to the parent pointer
				return True
	def __resolve(self:object) -> bool:
		self.__pointer = Pointer(self.__mainTeXPath)
		self.__structure = Structure()
		self.__definitions.clear()
		self.__labels.clear()
		self.__citations.clear()
		self.__flag = False
		self.__exitCode = EXIT_SUCCESS
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
							if buffer in ("\\section", "\\subsection", "\\subsubsection") and self.__pointer.hasNextChar(fileSwitch = False) and "*" == self.__pointer.getNextChar(fileSwitch = False): # section*-like structures
								buffer += "*"
								self.__pointer.nextChar(fileSwitch = False)
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
							elif buffer in ("\\begin", "\\bibliography", "\\end", "\\input", "\\section", "\\section*", "\\subsection", "\\subsection*", "\\subsubsection", "\\subsubsection*"):
								commandName = buffer[1:] # for judging environments
								if not self.__skipSpaces():
									return False
								flag, mainBody = self.__fetchBraces()
								buffer = "\\" + commandName + mainBody if mainBody.startswith("{") else "\\" + commandName + "{" + mainBody + "}"
								if "begin" == commandName:
									if self.__structure.addStructureNode(buffer):
										self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
										if buffer == "\\begin{thebibliography}":
											self.__pointer.nextChar()
											if not self.__skipSpaces():
												return False
											self.__pointer.nextChar()
											ch = self.__pointer.getCurrentChar()
											if "{" == ch:
												layerCount = 1
												while layerCount:
													if self.__pointer.hasNextChar():
														self.__pointer.nextChar()
														ch = self.__pointer.getCurrentChar()
														if "{" == ch:
															layerCount += 1
														elif "}" == ch:
															layerCount -= 1
														elif "\\" == ch:
															if self.__pointer.hasNextChar():
																self.__pointer.nextChar()
															elif self.__pointer.hasNextLine():
																self.__pointer.nextLine()
															else:
																self.__print(																													\
																	"An EOF signal is reported while scanning the escaped placeholder(s) in the \"{{}}\" for the \"\\begin{thebibliography}\" command at {0}. ".format(	\
																		self.__pointer.getCurrentLocationDescription()																				\
																	), Error																													\
																)
																return False
													elif self.__pointer.hasNextLine():
														self.__pointer.nextLine()
													else:
														self.__print(																														\
															"An EOF signal is reported while scanning the non-escaped placeholder(s) in the \"{{}}\" for the \"\\begin{thebibliography}\" command at {0}. ".format(	\
																self.__pointer.getCurrentLocationDescription()																					\
															), Error																														\
														)
											else:
												if "\\" == ch: # handle the placeholder in the form of "\\#"
													if self.__pointer.hasNextChar():
														self.__pointer.nextChar()
													elif self.__pointer.hasNextLine():
														self.__pointer.nextLine()
													else:
														self.__print("An EOF signal is reported while scanning the character after \"\\\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
														return False
												while True:
													if self.__pointer.hasNextChar():
														ch = self.__pointer.getNextChar()
														if ch in (" ", "\t"):
															self.__pointer.nextChar()
														elif "\\" == ch:
															remainingLine = self.__pointer.getRemainingCharactersInTheCurrentLineOfTheCurrentFile()
															if remainingLine.startswith("\\bibitem"):
																break
															else:
																self.__print(																											\
																	"Without a pair of \"{{}}\" surrounded, the \"\\bibitem\" command instead of others should be right after the placeholder at {0}. ".format(	\
																		self.__pointer.getCurrentLocationDescription()																		\
																	), Error																											\
																)
														else:
															self.__print(																								\
																"Without a pair of \"{{}}\" surrounded, the \"\\bibitem\" command should be right after the placeholder at {0}. ".format(		\
																	self.__pointer.getCurrentLocationDescription()															\
																), Error																								\
															)
															return False
													elif self.__pointer.hasNextLine():
														self.__pointer.nextLine()
													else:
														self.__print("An EOF signal is reported while scanning the citations at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
														return False
									else:
										self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
										return False
								elif "bibliography" == commandName:
									if self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1]) or self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1] + ".bib"):
										self.__print("A new Bib pointer node \"{0}\" is added. ".format(self.__pointer.getCurrentLocation()[0]), Debug)
										if self.__handleBibTeX():
											break # break the loop for fetching the string within the {} to avoid moving to the next character repeatedly
										else:
											return False
									else:
										self.__print("Failed to add a Bib pointer node at {0}. Details are as follows. \n{1}".format(self.__pointer.getCurrentLocationDescription(), self.__pointer.getLastError()), Warning)
								elif "end" == commandName:
									if self.__structure.canLeaveCurrentStructureNode(buffer):
										leavingQueue = []
										self.__structure.leaveCurrentStructureNode(buffer, leavingQueue = leavingQueue)
										if len(leavingQueue) >= 2:
											self.__print("With \"{0}\": ".format(buffer), Debug)
											for nodeDescription in leavingQueue:
												self.__print("Leave current structure node [{0}]. ".format(nodeDescription), Debug, indentationCount = 1)
										else:
											self.__print("Leave current structure node [{0}] with \"{1}\". ".format(leavingQueue[0], buffer), Debug)
									else:
										self.__print(																							\
											"Cannot end the current environment [{0}] with command \"{1}\" at {2}. ".format(								\
												self.__structure.getCurrentStructureNodeDescription(), buffer, self.__pointer.getCurrentLocationDescription()		\
											), Error																							\
										)
										return False
								elif "input" == commandName:
									if self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1]):
										self.__print("A new TeX pointer node \"{0}\" is added. ".format(self.__pointer.getCurrentLocation()[0]), Debug)
									else:
										self.__print("Failed to add a TeX pointer node at {0}. Details are as follows. ".format(self.__pointer.getCurrentLocationDescription()), Warning)
										self.__print(self.__pointer.getLastError(), Warning, indentationCount = 1)
								else:
									self.__structure.addStructureNode(buffer)
							elif buffer in ("\\bibitem", "\\label", "\\ref", "\\eqref"):
								if not self.__skipSpaces():
									return False
								
								# Fetch #
								self.__pointer.nextChar(fileSwitch = False)
								if "{" == self.__pointer.getCurrentChar():
									label = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											if ch in ("\\", "{"):
												self.__print(																									\
													"An unexpected character \"{0}\" appears while scanning the {1} at {2}. ".format(										\
														self.__convertEscaped(ch), "citation" if "\\bibitem" == buffer else "label", self.__pointer.getCurrentLocationDescription()	\
													), Error																									\
												)
												return False
											elif "}" == ch:
												break
											else:
												label += ch
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											label += "\n"
											while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"):
												self.__pointer.nextChar(fileSwitch = False)
												citation += self.__pointer.getCurrentChar()
											if not self.__pointer.hasNextChar(fileSwitch = False):
												self.__print("Two or more consecutive line breaks are not allowed during the label scanning at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
										else:
											self.__print("An EOF signal is reported while scanning the label at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
								elif "\\label" == buffer and self.__structure.getCurrentStructureNodeDescription() in ("Environment(equation)", "Environment(equation*)"):
									self.__print("Must use a \"{{\" to follow the \"\\label\" command in the equation environment at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								else:
									label = self.__pointer.getCurrentChar()
								
								# Handle #
								if "\\bibitem" == buffer:
									# Environment Check #
									if "Environment(thebibliography)" != self.__structure.getCurrentStructureNodeDescription():
										self.__print("The command \"\\bibitem\" should only be used in the \"thebibliography\" environment. ", Warning)
										# return False
									
									# Fetch Citation Content #
									citationContent = ""
									while True:
										if self.__pointer.hasNextChar():
											ch = self.__pointer.getNextChar()
											if "\\" == ch:
												remainingLine = self.__pointer.getRemainingCharactersInTheCurrentLineOfTheCurrentFile()
												if remainingLine.startswith("\\begin") or remainingLine.startswith("\\bibitem") or remainingLine.startswith("\\end"):
	 												break
												else:
													citationContent += "\\"
													self.__pointer.nextChar()
													if self.__pointer.hasNextChar(): # ``hasNextLine`` will be handled in the new loop automatically
														self.__pointer.nextChar()
														citationContent += self.__pointer.getCurrentChar()
											elif "&" == ch:
												citationContent += "&"
												self.__print("Please use \"\\&\" in the citation content at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Warning)
											else:
												citationContent += ch
											self.__pointer.nextChar()
										elif self.__pointer.hasNextLine():
											self.__pointer.nextLine()
											citationContent += "\n"
									
									# Handle Dict #
									if label in self.__citations:
										if self.__citations[label][0] is None:
											self.__citations[label][0] = citationContent
										elif isinstance(self.__citations[label][0], list):
											length = len(self.__citations[label][0])
											self.__print(																													\
												"The citation \"{0}\" has already been defined {1} but is defined again at {2}. ".format(													\
													self.__convertEscaped(label), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
												), Warning																												\
											)
										else:
											self.__citations[label][0] = [self.__citations[label][0], False]
											self.__print("The citation \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Warning)
									else:
										self.__citations[label] = [citationContent, 0] # [citationContent, citeCount]
										self.__print("A new citation \"{0}\" is added via the \"\\bibitem\" command at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Debug)
								elif "\\label" == buffer:
									if label in 	self.__labels:
										if self.__labels[label][0] is None:
											self.__labels[label][0] = self.__structure.getCurrentStructureNodeDescription()
										elif isinstance(self.__labels[label][0], list):
											length = len(self.__labels[label][0])
											self.__print(																													\
												"The label \"{0}\" has already been defined {1} but is defined again at {2}. ".format(														\
													self.__convertEscaped(label), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
												), Warning																												\
											)
											self.__labels[label][0].append(self.__pointer.getCurrentLocationDescription())
										else:
											self.__labels[label][0] = [self.__labels[label][0], self.__pointer.getCurrentLocationDescription()]
											self.__print("The label \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Warning)
									else:
										self.__labels[label] = [self.__structure.getCurrentStructureNodeDescription(), 0, 0] # [type, refCount, eqrefCount]
										self.__print("A new label \"{0}\" is added at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Debug)
								else:
									if label in self.__labels:
										self.__labels[label][2 if "\\eqref" == buffer else 1] += 1
									elif "\\eqref" == buffer:
										self.__labels[label] = [None, 0, 1] # [undefined, refCount, eqrefCount]
									else:
										self.__labels[label] = [None, 1, 0] # [undefined, refCount, eqrefCount]
							elif "\\cite" == buffer:
								if not self.__skipSpaces():
									return False
								
								# Fetch #
								if "{" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									citation = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											if ch in ("\\", "{"):
												self.__print("An unexpected character \"{0}\" appears while scanning the citation at {1}. ".format(self.__convertEscaped(ch), self.__pointer.getCurrentLocationDescription()), Error)
												return False
											elif "}" == ch:
												citations = [item.lstrip() for item in citation.split(",")]
												break
											else:
												citation += ch
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											citation += "\n"
											while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"):
												self.__pointer.nextChar(fileSwitch = False)
												citation += self.__pointer.getCurrentChar()
											if not self.__pointer.hasNextChar(fileSwitch = False):
												self.__print("Two or more consecutive line breaks are not allowed during the citation scanning at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
										else:
											self.__print("An EOF signal is reported while scanning the citation at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
								else:
									self.__pointer.nextChar(fileSwitch = False)
									citations = [self.__pointer.getCurrentChar()]
								
								# Handle #
								for citation in citations:
									if citation in self.__citations:
										self.__citations[citation][1] += 1
									else:
										self.__citations[citation] = [None, 1] # [undefined, citeCount]
									self.__structure.addMedia("Citation")
							elif buffer in ("\\newcommand", "\\renewcommand", "\\let", "\\orignewcommand"):
								# * #
								if "*" == self.__pointer.getNextChar(fileSwitch = False):
									buffer += "*"
									self.__pointer.nextChar(fileSwitch = False)
								
								# Command #
								if not self.__skipSpaces(False):
									return False
								if "{" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									if self.__pointer.hasNextChar(fileSwitch = False) and "\\" == self.__pointer.getNextChar(fileSwitch = False):
										self.__pointer.nextChar(fileSwitch = False)
										bucketFlag = True
									else:
										self.__print("The command to be defined should be right after the \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
										return False
								elif "\\" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									bucketFlag= False
								else:
									self.__print("The command to be defined should be right after the \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
									return False
								newcommand = "\\"
								while self.__pointer.hasNextChar(fileSwitch = False):
									ch = self.__pointer.getNextChar(fileSwitch = False)
									if "A" <= ch <= "Z" or "a" <= ch <= "z":
										newcommand += ch
										self.__pointer.nextChar(fileSwitch = False)
									else:
										break
								if not self.__skipSpaces(): # check after the command
									return False
								if bucketFlag:
									if "}" == self.__pointer.getNextChar(fileSwitch = False):
										self.__pointer.nextChar(fileSwitch = False)
									else:
										self.__print("A missing \"}\" is detected when scanning the command definition command at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								
								# Option count #
								if not self.__skipSpaces():
									return False
								if "[" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									if not self.__skipSpaces():
										return False
									counter = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											ch = self.__pointer.getNextChar(fileSwitch = False)
											self.__pointer.nextChar(fileSwitch = False)
											if "0" <= ch <= "9":
												counter += ch
											elif "]" == ch:
												break
											else:
												self.__print(																				\
													"Only digits instead of the character \"{0}\" can be used to indicate the option count at {1}. ".format(	\
														"\\" + ch if ch in ("\\", "\"", "\'") else ch, self.__pointer.getCurrentLocationDescription()			\
													), Error																				\
												)
												return False
										elif not self.__skipSpaces():
											return False
									try:
										counter = int(counter)
									except:
										self.__print("Cannot convert the counter \"{0}\" into a positive integer at {1}. ".format(counter, self.__pointer.getCurrentLocationDescription()), Error)
										return False
									if counter < 1 or counter > 9:
										self.__print("The count of options must be a positive integer not greater than 9. ", Error)
										return False
								else:
									counter = None
								
								# Default value for the first option #
								if not self.__skipSpaces():
									return False
								if "[" == self.__pointer.getNextChar(fileSwitch = False): # must be the default value option
									layer, defaultValue = 1, "["
									self.__pointer.nextChar(fileSwitch = False)
									while layer:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											defaultValue += ch
											if "\\" == ch:
												if self.__pointer.hasNextChar(fileSwitch = False):
													self.__pointer.nextChar(fileSwitch = False)
													defaultValue += self.__pointer.getCurrentChar()
												elif self.__pointer.hasNextLine(fileSwitch = False):
													self.__pointer.nextLine(fileSwitch = False)
													defaultValue += "\n"
												else:
													self.__print("A missing \"]\" is detected when scanning the default value option at {0}. ".self.__pointer.getCurrentLocationDescription(), Error)
													return False
											elif "[" == ch:
												layer += 1
											elif "]" == ch:
												layer -= 1
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											defaultValue += "\n"
										else:
											self.__print("An EOF signal is reported during scanning the default value at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									defaultValue = defaultValue[1:-1]
								else:
									defaultValue = None
								
								# Main command body #
								if not self.__skipSpaces():
									return False
								flag, mainBody = self.__fetchBraces()
								if flag:
									if mainBody.startswith("{") and mainBody.endswith("}"):
										mainBody = mainBody[1:-1]
									elif not mainBody.startswith("\\") and self.__pointer.hasNextChar(fileSwitch = False):
										self.__print("Only a character is accepted for the main body when there is not a pair of \"{{}}\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								else:
									return False
								self.__definitions[newcommand] = [counter, defaultValue, mainBody]
								self.__print("The value of the command \"{0}\" has been set to {1}. ".format(newcommand, self.__definitions[newcommand]), Debug)
							elif buffer in ("\\newenvironment", "\\newenvironment"):
								if not self.__skipSpaces():
									return False
								self.__pointer.nextChar()
								if self.__pointer.getCurrentChar() == "{":
									environmentName = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											ch = self.__pointer.getNextChar(fileSwitch = False)
											if "A" <= ch <= "Z" or "a" <= ch <= "z":
												environmentName += ch
												self.__pointer.nextChar(fileSwitch = False)
											elif "}" == ch:
												self.__pointer.nextChar(fileSwitch = False)
												break
											else:
												self.__print("The environment should only contain letters but it is not at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
								else:
									ch = self.__pointer.getNextChar()
									if "A" <= ch <= "Z" or "a" <= ch <= "z":
										environmentName = ch
									else:
										self.__print("The one-character environment name should only be a letter but it is not at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								for _ in range(2):
									if not self.__skipSpaces():
										return False
									self.__pointer.nextChar()
									if self.__pointer.getCurrentChar() == "{":
										layer = 1
										while layer:
											if self.__pointer.hasNextChar():
												self.__pointer.nextChar()
												ch = self.__pointer.getCurrentChar()
												if "{" == ch:
													layer += 1
												elif "}" == ch:
													layer -= 1
												elif "%" == ch:
													if self.__pointer.hasNextLine():
														self.__pointer.nextLine()
													else:
														self.__print("An EOF signal is reported while scanning a newly defined environment after an annotation symbol at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
														return False
												elif "\\" == ch:
													if self.__pointer.hasNextChar():
														self.__pointer.nextChar()
													elif self.__pointer.hasNextLine():
														self.__pointer.nextLine()
													else:
														self.__print("An EOF signal is reported while scanning the escaped character of a newly defined environment at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
														return False
											elif self.__pointer.hasNextLine():
												self.__pointer.nextLine()
											else:
												self.__print("An EOF signal is reported while scanning a newly defined environment at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
								self.__print("A new environment \"{0}\" is added. ".format(environmentName), Debug)
							else: # the command is not special
								self.__structure.addPlainText(buffer)
					else: # "\\\n"
						self.__structure.addPlainText("\\")
				elif "%" == ch: # the '\\' will be absorbed in the codes for avoiding "\\%" above if the previous char is '\\'
					self.__structure.addPlainText("\n")
					self.__pointer.nextLine()
				elif "$" == ch: # the '\\' will be absorbed in the codes for avoiding "\\$" above if the previous char is '\\'
					if self.__pointer.hasNextChar(fileSwitch = False) and "$" == self.__pointer.getNextChar(fileSwitch = False):
						self.__pointer.nextChar(fileSwitch = False)
						ch = "$$" # else: ch = "$"
					if isLeftPart:
						if self.__structure.addStructureNode(ch):
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
				if self.__structure.endStructure():
					break
				else:
					self.__print("An overall EOF signal is reported with unclosed structure [{0}]. ".format(self.__structure.getCurrentStructureNodeDescription()), Error)
					return False
		self.__flag = True
		return True
	def __printPointer(self:object) -> None:
		self.__print("Pointer: ", Info)
		self.__print(self.__pointer.getTree(), Info)
	def __printStructure(self:object, mode:str = "A") -> None:
		self.__print("Structure: ", Info)
		self.__print(self.__structure.getTree(mode), Info)
	def __setup(self:object) -> bool:
		try:
			if not isinstance(self.__mainTeXPath, str):
				tmpMainTexPath = self.__input("Please input the main tex path: ", Prompt)
				if tmpMainTexPath is None:
					self.__print("Setup canceled. ", Error)
					return False
				else:
					self.__mainTeXPath = tmpMainTexPath.replace("\"", "")
					self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTeXPath), Info)
					return self.__setup()
			elif os.path.isfile(self.__mainTeXPath):
				if os.path.splitext(self.__mainTeXPath)[1].lower() != ".tex":
					self.__print("The main tex path is set to a file whose extension is not \".tex\". ", Warning)
				return self.__resolve()
			elif os.path.isdir(self.__mainTeXPath):
				self.__print("Since a folder was specified, the program is scanning the folder now. ", Info)
				self.__print("If it takes too long time, please use \"Ctrl+C\" to stop the scanning. ", Info)
				possibleTargets = []
				try:
					for root, dirs, files in os.walk(self.__mainTeXPath):
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
							self.__print("{{0:>{0}}} = \"{{1}}\"".format(length).format(i + 1, target), Prompt, indentationCount = 1)
						self.__print("{{0:>{0}}} = I do not wish to select any of them. ".format(length).format(0), Prompt, indentationCount = 1)
					except KeyboardInterrupt:
						print() # print an empty line
						self.__print("\nPrinting is interrupted by users. The results may be incomplete. ", Warning)
					choice = self.__input("Please select a tex file as the main file to continue: ", Prompt)
					try:
						choice = int(choice)
					except:
						pass
					if choice is None or 0 == choice:
						self.__print("The main tex selection is canceled by users. ", Warning)
						return False
					elif isinstance(choice, int) and 1 <= choice <= len(possibleTargets): # ID matches
						self.__mainTeXPath = possibleTargets[choice - 1]
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTeXPath), Info)
						return self.__resolve()
					elif isinstance(choice, str) and choice in possibleTargets: # exact matches (robust matches are not designed here since some operating systems are case sensitive)
						self.__mainTeXPath = choice
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTeXPath), Info)
						return self.__resolve()
					elif isinstance(choice, str) and choice.strip("\"") in possibleTargets: # exact matches (remove the quotation marks)
						self.__mainTeXPath = choice.strip("\"")
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTeXPath), Info)
						return self.__resolve()
					else:
						try:
							self.__mainTeXPath = choice[int(choice) - 1]
							self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTeXPath), Info)
							return self.__resolve()
						except:
							self.__print("An invalid choice was selected. Failed to resolve main tex. ", Error)
							return False
				elif len(possibleTargets) == 1:
					self.__mainTeXPath = possibleTargets[0]
					self.__print("The main tex path is set to \"{0}\" automatically since there is only one tex file detected. ".format(self.__mainTeXPath), Info)
					return self.__resolve()
				else:
					self.__print("No tex files are detected under the specified folder.. ", Error)
					return False
			else:
				self.__print("Setup failed since the main tex cannot be read. ", Error)
				return False
		except KeyboardInterrupt:
			self.__print("The setup procedure is interrupted by users at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
			return False
		except BaseException as e:
			self.__print("Exceptions occurred during the setup at {0}. Details are as follows. ".format(self.__pointer.getCurrentLocationDescription()), Critical)
			self.__print(e, Critical, indentationCount = 1)
			return False
	def __selectAnOption(self:object, flag:bool) -> str:
		self.__print("\n" + "#" * 100, Prompt)
		if isinstance(flag, bool) and flag:
			d = {"B":"Build", "C":"Clear", "D":"Debug", "E":"Exit", "N":"New", "P":"Pause", "R":"Reload", "S":"Statistics", "T":"Tree"}
			self.__print(																												\
				"Obtained {0} pointer node(s), {1} abstracted/brief structure node(s), and {2} detailed structure node(s). ".format(							\
					self.__pointer.getTree().count("\n") + 1, self.__structure.getTree("B").count("\n") + 1, self.__structure.getTree("D").count("\n") + 1		\
				), Info																												\
			)
			upperLevel = self.__pointer.getBaseFolderPath()
			upperLevels = upperLevel.replace("\\", "/").split("/")
			upperLevel = os.path.join(upperLevel, "..") if len(upperLevels) <= 1 else os.sep.join(upperLevels[:-1])
			if os.path.isdir(os.path.join(upperLevel, "Content")) and os.path.isdir(os.path.join(upperLevel, "Figure")) and (															\
				os.path.isdir(os.path.join(upperLevel, "ACMConference")) or os.path.isdir(os.path.join(upperLevel, "ACMJournal")) or os.path.isdir(os.path.join(upperLevel, "Elsevier"))		\
				or os.path.isdir(os.path.join(upperLevel, "IEEEConference")) or os.path.isdir(os.path.join(upperLevel, "IEEEJournal"))												\
				or os.path.isdir(os.path.join(upperLevel, "TSP")) or os.path.isdir(os.path.join(upperLevel, "Springer")) or os.path.isdir(os.path.join(upperLevel, "Wiley"))					\
			):
				d["A"] = "Automatic"
		else:
			d = {"B":"Build", "C":"Clear", "D":"Debug", "E":"Exit", "N":"New", "P":"Pause", "R":"Reload"}
		self.__print("Possible choices are listed as follows. ", Prompt)
		for key, value in sorted(d.items()):
			self.__print("{0} = {1}".format(key, value), Prompt, indentationCount = 1)
		choices = self.__input("Please input your choice(s) to continue (non case-sensitive): ")
		if choices is None:
			choices = ""
		else:
			choices = choices.upper()
			invalid = True
			while invalid:
				for ch in choices:
					if ch not in d:
						choices = self.__input("At least one invalid choice exists. Please retry (non case-sensitive): ")
						if choices is None:
							self.__print("#" * 100 + "\n", Prompt)
							return ""
						else:
							choices = choices.upper()
							break
				else: # end naturally
					invalid = False
		self.__print("#" * 100 + "\n", Prompt)
		return choices
	def __doAutomaticBuilding(self:object) -> bool:
		# Traverse #
		mainTeXPaths, upperLevel = [], self.__pointer.getBaseFolderPath()
		upperLevels = upperLevel.replace("\\", "/").split("/")
		upperLevel = os.path.join(upperLevel, "..") if len(upperLevels) <= 1 else os.sep.join(upperLevels[:-1])
		for objectName in os.listdir(upperLevel):
			objectPath = os.path.join(upperLevel, objectName)
			if objectName in ("ACMConference", "ACMJournal", "Elsevier", "IEEEConference", "IEEEJournal", "TSP", "Springer", "Wiley"):
				mainTeXPath = None
				for subObjectName in os.listdir(objectPath):
					if os.path.splitext(subObjectName)[1].lower() == ".tex":
						if mainTeXPath is None:
							mainTeXPath = os.path.join(objectPath, subObjectName)
						else:
							break
				else: # the ``for`` breaks naturally
					mainTeXPaths.append(mainTeXPath)
		
		# Handle #
		booleans = []
		startTime = perf_counter()
		for mainTeXPath in mainTeXPaths:
			checker = Checker(mainTeXPath, debugLevel = Prompt, workflows = "BE")
			booleans.append(checker.mainBoard())
		endTime = perf_counter()
		if booleans:
			successCnt, totalCnt = booleans.count(EXIT_SUCCESS), len(booleans)
			self.__print("Successfully built {0} / {1} PDF(s) at a success rate of {2:.2f}% in {3:.3f} second(s) (including interactive time). ".format(successCnt, totalCnt, 100 * successCnt / totalCnt, endTime - startTime), Info)
			return True
		else:
			self.__print("Nothing was proceeded. ", Warning)
			self.__exitCode = EXIT_FAILURE
			return False
	def __doBuildPDF(self:object) -> bool:
		# Begin #
		if not (isinstance(self.__mainTeXPath, str) and os.path.isfile(self.__mainTeXPath)):
			self.__print("Cannot build since the main TEX file is not specified or does not exist. ", Error)
			return None
		bRets = [True] * 5
		mainTexFolderPath, mainTexFileNameExt = os.path.split(self.__mainTeXPath)
		mainTexFileName = os.path.splitext(mainTexFileNameExt)[0]
		
		# Extension #
		casCommonStyFilePath = os.path.join(mainTexFolderPath, "cas-common.sty")
		try:
			if os.path.isfile(casCommonStyFilePath):
				with open(casCommonStyFilePath, "rb") as f:
					bContent = f.read()
			else:
				bContent = None
		except BaseException as e:
			bContent = None
			self.__print("Failed to check the status of the \"cas-common.sty\" file due to exceptions. Details are as follows. ", Warning)
			self.__print(e, Warning, indentationCount = 1)
		if isinstance(bContent, bytes) and b"\\sffamily" in bContent:
			answer = self.__input(
				"The \"cas-common.sty\" is detected with the command \"\\sffamily\" in it. \n"
				+ "Would you like to replace the command \"\\sffamily\" with \"\\rmfamily\" to change the font of the text in figure captions and tables to \"Times New Roman\" [yN]? "
			)
			if isinstance(answer, str) and answer.upper() in ("Y", "YES", "TRUE", "1"):
				try:
					with open(casCommonStyFilePath, "wb") as f:
						f.write(bContent.replace(b"\\sffamily", b"\\rmfamily"))
				except BaseException as e:
					self.__print("Failed to apply the changes due to exceptions. Details are as follows. ", Error)
					self.__print(e, Error, indentationCount = 1)
		
		# Remove #
		synctexGzFilePath = os.path.join(mainTexFolderPath, mainTexFileName + ".synctex.gz")
		if os.path.isfile(synctexGzFilePath):
			try:
				os.remove(synctexGzFilePath)
			except BaseException as e:
				bRets[0] = False
				self.__print("Failed to remove the file \"{0}\" due to exceptions. Details are as follows. ".format(synctexGzFilePath), Warning)
				self.__print(e, Warning, indentationCount = 1)
		for item in os.listdir(mainTexFolderPath): # do not use the ``os.walk``
			name, ext = os.path.splitext(item)
			if name == mainTexFileName and ext in (".aux", ".blg", ".log", ".out", ".toc", ".gz"):
				assistanceFilePath = os.path.join(mainTexFolderPath, item)
				try:
					os.remove(assistanceFilePath)
				except BaseException as e:
					bRets[0] = False
					self.__print("Failed to remove the file \"{0}\" due to exceptions. Details are as follows. ".format(assistanceFilePath), Warning)
					self.__print(e, Warning, indentationCount = 1)
		
		# Compile #
		startTime = perf_counter()
		if ".bib\n" in self.__pointer.getTree() + "\n": # pdflatex -> bibtex -> pdflatex -> pdflatex
			process = Popen(["pdflatex", mainTexFileNameExt], cwd = mainTexFolderPath)
			bRets[1] = process.wait() == EXIT_SUCCESS
			process = Popen(["bibtex", mainTexFileName + ".aux"], cwd = mainTexFolderPath) # the relative path must be used
			bRets[2] = process.wait() == EXIT_SUCCESS
		process = Popen(["pdflatex", mainTexFileNameExt], cwd = mainTexFolderPath)
		bRets[3] = process.wait() == EXIT_SUCCESS
		process = Popen(["pdflatex", mainTexFileNameExt], cwd = mainTexFolderPath)
		bRets[4] = process.wait() == EXIT_SUCCESS
		endTime = perf_counter()
		timeDelta = endTime - startTime
		
		# End #
		bRet = all(bRets)
		if bRet:
			self.__print("Successfully built in {0:.9f} second(s). ".format(timeDelta), Info)
		else:
			self.__print("Failed to build. The time consumption is {0:.9f} second(s). Details are as follows. ".format(timeDelta), Warning)
			self.__print(bRets, Warning, indentationCount = 1)
			self.__exitCode = EXIT_FAILURE
		return bRet
	def __doSetDebugLevel(self:object) -> bool:
		self.__print("Current debug level is {0} ({1}). ".format(self.__debugLevel.name, self.__debugLevel.value), Prompt)
		d = {"P":Prompt, "C":Critical, "E":Error, "W":Warning, "I":Info, "D":Debug}
		for key, value in d.items():
			self.__print("{0} = {1} ({2})".format(key, value.name, value.value), Prompt, indentationCount = 1)
		ch = self.__input("Please select a debug level to continue: ")
		while ch is not None and ch.upper() not in d:
			ch = self.__input("The debug level is invalid. Please retry: ")
		if ch is None:
			self.__print("The debug level has not been changed due to the cancellation caused by users. ", Warning)
			return False
		else:
			ch = ch.upper()
			if d[ch] == self.__debugLevel:
				self.__print("No changes are made to the debug level. ", Info)
			else:
				self.__debugLevel = d[ch]
				self.__print("The debug level has been changed to {0}. ".format(self.__debugLevel), Info)
			return True
	def __printStatistics(self:object) -> bool:
		pointerTree, structureBriefTree, structureDetailedTree = self.__pointer.getTree().split("\n"), self.__structure.getTree("B").split("\n"), self.__structure.getTree("D").split("\n")
		self.__print(																							\
			"Obtained {0} pointer node(s), {1} abstracted/brief structure node(s), and {2} detailed structure node(s). ".format(		\
				len(pointerTree), len(structureBriefTree), len(structureDetailedTree)										\
			), Info																							\
		)
		
		# Tree #
		d = {}
		for line in structureDetailedTree:
			key = line.strip()
			if not key.startswith("Text(") and key not in ("Root", "Environment(algorithmic)", "Environment(tabular)"):
				if key.startswith("Environment("):
					key = key[12:-1]
					if key not in ("document", "thebibliography"):
						key = key.replace("*", "") + "(*)"
				elif "(" in key:
					key = key[:key.index("(")].replace("*", "")
				d.setdefault(key, 0)
				d[key] += 1
		self.__print(d, Info)
		
		# Commands #
		self.__print("There are {0} commands defined. ".format(len(self.__definitions)) if len(self.__definitions) > 1 else "There is 1 command defined. ", Info)
		self.__print("Commands defined: {0}".format(self.__definitions), Debug)
		
		# Labels #
		repeatedLabels, undefinedLabels, unreferencedLabels, hybridReferencedLabels = [], [], [], []
		for key, value in self.__labels.items():
			if isinstance(value[0], list):
				repeatedLabels.append(key)
			elif value[0] is None:
				undefinedLabels.append(key)
			elif value[0] in ("Environment(equation)", "Environment(equation*)") and value[1] or value[0] not in ("Environment(equation)", "Environment(equation*)") and value[2]:
				hybridReferencedLabels.append(key)
			if not (value[1] or value[2]): # can be lots of labels without being referenced
				unreferencedLabels.append(key)
		
		# Labels/Repeated #
		length = len(repeatedLabels)
		if length >= 2:
			self.__print("There are {0} repeated labels found, which are listed as follows. ".format(length), Warning)
			self.__print(repeatedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a repeated label found: \"{0}\". ".format(self.__convertEscaped(repeatedLabels[0])), Warning)
		
		# Labels/Undefined #
		length = len(undefinedLabels)
		if length >= 2:
			self.__print("There are {0} undefined labels found, which are listed as follows. ".format(length), Warning)
			self.__print(undefinedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an undefined label found: \"{0}\". ".format(self.__convertEscaped(undefinedLabels[0])), Warning)
		
		# Labels/Unreferenced #
		length = len(unreferencedLabels)
		if length >= 2:
			self.__print("There are {0} unreferenced labels found, which are listed as follows. ".format(length), Warning)
			self.__print(unreferencedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an unreferenced label found: \"{0}\". ".format(self.__convertEscaped(unreferencedLabels[0])), Warning)
		
		# Labels/Hybrid #
		length = len(hybridReferencedLabels)
		if length >= 2:
			self.__print("There are {0} hybrid referenced labels found, which are listed as follows. ".format(length), Warning)
			self.__print(hybridReferencedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a hybrid referenced label found: \"{0}\". ".format(self.__convertEscaped(hybridReferencedLabels[0])), Warning)
		
		self.__print("Labels defined for referencing: {0}".format(self.__labels), Info)
		
		# Citations #
		repeatedCitations, undefinedCitations, uncitedCitations, similarCitations, citationBodies = [], [], [], [], {}
		for key, value in self.__citations.items():
			if isinstance(value[0], list):
				repeatedCitations.append(key)
			elif value[0] is None:
				undefinedCitations.append(key)
			else:
				stripped = value[0].strip()
				citationBodies.setdefault(stripped, [])
				citationBodies[stripped].append(key)
			if not value[1]:
				uncitedCitations.append(key)
		for value in citationBodies.values():
			if len(value) >= 2:
				similarCitations.append(value)
		
		# Citations/Repeated #
		length = len(repeatedCitations)
		if length >= 2:
			self.__print("There are {0} repeated citation entries found, which are listed as follows. ".format(length), Warning)
			self.__print(repeatedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a repeated citation entry found: \"{0}\". ".format(self.__convertEscaped(repeatedCitations[0])), Warning)
		
		# Citations/Undefined #
		length = len(undefinedCitations)
		if length >= 2:
			self.__print("There are {0} undefined citations found, which are listed as follows. ".format(length), Warning)
			self.__print(undefinedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an undefined citation found: \"{0}\". ".format(self.__convertEscaped(undefinedCitations[0])), Warning)
		
		# Citations/Uncited #
		length = len(uncitedCitations)
		if length >= 2:
			self.__print("There are {0} uncited citations found, which are listed as follows. ".format(length), Warning)
			self.__print(uncitedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an uncited citation found: \"{0}\". ".format(self.__convertEscaped(uncitedCitations[0])), Warning)
		
		# Citations/Similar #
		length = len(similarCitations)
		if length >= 2:
			self.__print("There are {0} citations found with similar content, which are listed as follows. ".format(length), Warning)
			self.__print(similarCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a citation found with similar content: {0}. ".format(self.__convertEscaped(similarCitations[0])), Warning)
		
		# Citations/Overall #
		self.__print("Here are the statistics for the medium type \"Citation\". \n{0}".format(self.__structure.getMedia("Citation")), Info)
		self.__print("Citations defined for citing: {0}".format(self.__citations), Debug)
		
		return True
	def __handleFolder(self:object, fd:str) -> bool:
		folder = str(fd)
		if not folder:
			return True
		elif os.path.exists(folder):
			return os.path.isdir(folder)
		else:
			try:
				os.makedirs(folder)
				return True
			except:
				return False
	def __drawTree(self:object, strings:str, path:str) -> bool:
		if isinstance(strings, str) and isinstance(path, str):
			try:
				Digraph = __import__("graphviz").Digraph
			except:
				self.__print("Cannot import ``Digraph`` from ``graphviz``. Please resolve the environments before drawing. ", Error)
				self.__exitCode = EXIT_FAILURE
				return False
			g = Digraph("Tree", filename = path, node_attr = {"shape":"plain"})
			style = "<<table border=\"1\" cellspacing=\"0\"><tr><td port=\"f0\">{0}</td></tr><tr><td port=\"f1\">{1}</td></tr><tr><td port=\"f2\">{2}</td></tr></table>>"
			g.node("0", label = style.format("0", "Root", " "))
			nodeCount, stack = 0, [(0, 0)] # (node, tab)
			for string in strings.splitlines()[1:]:
				tabCount = string.count("\t")
				if 1 <= tabCount <= stack[-1][1] + 1:
					while stack and stack[-1][1] >= tabCount: # find the parent node
						stack.pop()
					nodeCount += 1
					g.node(str(nodeCount), label = style.format(str(nodeCount), string.lstrip(), " "))
					g.edge(str(stack[-1][0]), str(nodeCount), headport = "n", tailport = "s")
					stack.append((nodeCount, tabCount))
				else:
					self.__print("Failed to draw the tree since the tree indentation is incorrect. ", Error)
					self.__exitCode = EXIT_FAILURE
					return False
			g.attr(margin = "0", rankdir = "TB", splines = "line", overlap = "scale")
			try:
				g.view()
				return True
			except BaseException as e:
				self.__print("Cannot save the tree due to the following exception. ", Error)
				self.__print(e, Error, indentationCount = 1)
				self.__exitCode = EXIT_FAILURE
				return False
		else:
			self.__print("As no trees are passed to the drawer, the drawing has not been done. \nPlease make sure that the checker has already constructed the trees correctly. ", Error)
			self.__exitCode = EXIT_FAILURE
			return False
	def __doPrintTree(self:object) -> bool:
		if self.__flag:
			self.__print("Possible tree drawing options are as follows. ", Prompt)
			d = {																																		\
				"PP":"Print the pointer", "PSA":"Print the structure abstract", "PSB":"Print the structure briefly", "PSD":"Print the structure in detail", 								\
				"DP":"Draw/Dump the pointer", "DSA":"Draw/Dump the structure abstract", "DSB":"Draw/Dump the structure briefly", "DSD":"Draw/Dump the structure in detail", 	\
				"R":"Return"																																\
			}
			for key, value in d.items():
				self.__print("{0} = {1}".format(key, value), Prompt, indentationCount = 1)
			ch = self.__input("Please select an option to continue (non case-sensitive): ")
			while ch is not None and ch.upper() not in d:
				ch = self.__input("The option is invalid. Please retry (non case-sensitive): ")
			if ch is None:
				self.__print("Nothing has been proceeded due to the cancellation caused by users. ", Warning)
				return False
			else:
				ch = ch.upper()
			if "P" == ch[0]:
				if "P" == ch[1]:
					self.__printPointer()
				else:
					self.__printStructure(ch[2])
				return True
			elif "D" == ch[0]:
				path = self.__input("Please input a \".gv\" file path to save the figure (leave it empty for default values): ")
				# while not (isinstance(path, str) and (not path or path.endswith(".gv"))):
				#	path = self.__input("The previous input is invalid. Please input a \".gv\" file path to save the figure (leave it empty for default values): ")
				if path is None:
					self.__print("The operation is canceled by users. ", Warning)
					self.__exitCode = EXIT_FAILURE
					return False
				else:
					path = path.replace("\"", "")
					if path.lower().endswith(".gv.pdf"):
						path = path[:-4]
					elif not path.lower().endswith(".gv"):
						path += ".gv"
					self.__print("The path for drawing or dumping the tree is set to \"{0}\". ".format(path), Debug)
					if (os.path.exists(path) or os.path.exists(path + ".pdf")):
						answer = self.__input("The target path seems to exist. Overwrite or not [yN]? ")
						if answer is None or answer.upper() not in ("Y", "YES", "TRUE", "OK", "1"):
							self.__print("Users cancel the operation due to the file's existence. ", Warning)
							self.__exitCode = EXIT_FAILURE
							return False
					if self.__handleFolder(os.path.split(path)[0]):
						return self.__drawTree(self.__pointer.getTree() if "P" == ch[1] else self.__structure.getTree(ch[2]), path if path else ("pointer.gv" if "P" == ch[1] else "structure.gv"))
					else:
						self.__print("Failed to save the tree since the parent folder is not created. ", Error)
						self.__exitCode = EXIT_FAILURE
						return False
			else:
				return False
		else:
			self.__print("No trees were built since the resolving has not been processed yet. ", Error)
			self.__exitCode = EXIT_FAILURE
			return False
	def mainBoard(self:object) -> bool:
		self.__setup()
		while True:
			if isinstance(self.__workflows, str) and self.__workflows:
				choices = self.__workflows
				self.__workflows = None
			else:
				choices = self.__selectAnOption(self.__flag)
			for ch in choices:
				if "A" == ch:
					self.__doAutomaticBuilding()
				elif "B" == ch:
					self.__doBuildPDF()
				elif "C" == ch:
					clearScreen()
				elif "D" == ch:
					self.__doSetDebugLevel()
				elif "E" == ch:
					return self.__exitCode if self.__flag else EOF
				elif "N" == ch:
					self.__mainTeXPath = None
					self.__pointer = None
					self.__structure = None
					self.__flag = False
					self.__setup()
				elif "P" == ch:
					self.__input("Please press the enter key to continue. ")
				elif "R" == ch:
					self.__pointer = None
					self.__structure = None
					self.__flag = False
					self.__setup() # still call ``__setup``
				elif "S" == ch:
					self.__printStatistics()
				elif "T" == ch:
					self.__doPrintTree()


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
	if len(argv) >= 3:
		processPool = [os.system(STARTUP_COMMAND_FORMAT.format(executable, __file__, mainTeXPath)) for mainTeXPath in argv[1:]]
		print(																									\
			"As multiple options were given, {0} child processes have been launched, where {1} succeeded and {2} failed. ".format(		\
				len(processPool), 																					\
				processPool.count(EXIT_SUCCESS), 																	\
				len(processPool) - processPool.count(EXIT_SUCCESS)													\
			)																									\
		)
		preExit()
		return EXIT_SUCCESS if not any(processPool) else EXIT_FAILURE
	else:
		checker = Checker(argv[1] if 2 == len(argv) else None)
		checker.mainBoard()
		preExit()
		return EXIT_SUCCESS if checker else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())