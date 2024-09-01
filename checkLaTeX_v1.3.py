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

class Include:
	def __init__(self:object) -> object:
		self.__included = {} # 
	def compress(self:object, target:str, callby:str, lineCount:int, chCount:int) -> bool:
		if isinstance(target, str) and isinstance(callby, str) and isinstance(lineCount, int) and isinsttance(chCount, int) and os.path.isabs(target) and os.path.isabs(callby):
			if target in self.__included:
				return False
			else:
				self.__included[target] = (callby, lineCount, chCount)
		else:
			return False
	def __str__(self:object) -> str:
		return str(self.__included)

class Structure:
	def __init__(self:object, name:str, content:str, filepath:str, debugLevel:int = 0) -> object:
		self.__name = str(name).replace("\"", "").replace("'", "").replace("\n", "").replace("\r", "")
		self.__content = str(content)
		self.__filepath = str(filepath)
		if isinstance(debugLevel, DebugLevel):
			self.__debugLevel = debugLevel
		else:
			try:
				self.__debugLevel = int(debugLevel)
			except:
				self.__debugLevel = 0
				self.__printWithStatus("The debug level specified is invalid. It is defaulted to 0. ", Warning)
		self.__lines = None
		self.__children = []
	def __printWithStatus(self:object, strings:str, status:int|DebugLevel = Info) -> bool:
		if isinstance(status, DebugLevel):
			if status >= self.__debugLevel:
				print("{0} {1}".format(status, strings))
			return True
		elif isinstance(status, int) and status >= 0:
			print("{0} {1}".format("\t" * status, strings))
			return True
		else:
			print(strings)
			return False
	def __locateTarget(self:object, target:str, i:int = 0, j:int = 0, useStack:bool = False) -> tuple:
		m, n, length = i, j, len(self.__lines)
		escapeFlag = False
		while m < length:
			line = self.__lines[m]
			lineLength = len(line)
			while n <  lineLength:
				ch = line[n]
				if ch == "\\":
					if escapeFlag: # "\\"
						escapeFlag = False
					elif line[n:].replace(" ", "").replace("\t", "").startswith(target):
						cnt = len(target)
						while cnt:
							if line[n] not in (" ", "\t"):
								cnt -= 1
							n += 1
						self.__printWithStatus("Locate at ({0}, {1}). ".format(m, n), Debug)
						return (m, n)
				elif ch == "%":
					if escapeFlag:
						escapeFlag = False
					else:
						break		
				elif escapeFlag:
					escapeFlag = False
				n += 1
			n = 0
			m += 1
		self.__printWithStatus("Locate at (float(\"inf\"), float(\"inf\")). ", Debug)
		return (float("inf"), float("inf")) # not found
	def __fetchContent(self:object, startLineIdx:int, startCharIdx:int, endLineIdx:int = float("inf"), endCharIdx:int = float("inf")) -> str: # a closed interval
		# pre-process #
		if not self.__lines:
			return ""
		length = len(self.__lines)
		if startLineIdx == -float("inf") or isinstance(startLineIdx, int) and startLineIdx < -length:
			startLineIndex = 0
		elif isinstance(startLineIdx, int) and -length <= startLineIdx < length:
			startLineIndex = length + startLineIdx if startLineIdx < 0 else startLineIdx
		else: # including situations of right over bound, float("inf"), and unexpected types
			return ""
		startLineLength = len(self.__lines[startLineIndex])
		if startCharIdx == -float("inf") or isinstance(startCharIdx, int) and startCharIdx < -startLineLength:
			startCharIndex = 0
		elif isinstance(startCharIdx, int) and -startLineLength <= startCharIdx < startLineLength:
			startCharIndex = startLineLength + startCharIdx if startCharIdx < 0 else startCharIdx
		elif startCharIdx == float("inf") or isinstance(startCharIdx, int) and startCharIdx >= startLineLength: # right over bound
			startCharIndex = startLineLength
		else: # unexpected types
			return ""
		if endLineIdx == float("inf") or isinstance(endLineIdx, int) and endLineIdx >= length:
			endLineIndex = length
		elif isinstance(endLineIdx, int) and -length <= endLineIdx < length:
			endLineIndex = length + endLineIdx if endLineIdx < 0 else endLineIdx
		else: # including situations of left over bound, -float("inf"), and unexpected types
			return ""
		endLineLength = len(self.__lines[endLineIndex]) if endLineIndex < length else 0
		if endCharIdx == float("inf") or isinstance(endCharIdx, int) and endCharIdx >= endLineLength:
			endCharIndex = endLineLength
		elif isinstance(endCharIdx, int) and -endLineLength <= endCharIdx < endLineLength:
			endCharIndex = endLineLength + endCharIdx if endCharIdx < 0 else endCharIdx
		elif endCharIdx == -float("inf") and isinstance(endCharIdx, int) and endCharIdx < -endLineLength:
			endCharIndex = 0
		else: # unexpected types
			return ""
		
		# process #
		self.__printWithStatus("Try to fetch the closed interval [({0}, {1}):({2}, {3})]. ".format(startLineIndex, startCharIndex, endLineIndex, endCharIndex), Debug)
		if startLineIndex > endLineIndex:
			return ""
		elif endLineIndex == startLineIndex:
			return self.__lines[startLineIndex][startCharIndex:endCharIndex + 1]
		else:
			return "\n".join([self.__lines[startLineIndex][startCharIndex:]] + self.__lines[startLineIndex + 1:endLineIndex] + ([self.__lines[endLineIndex][:endLineIndex + 1]] if endLineIndex < length else []))
	def __handleLatexCommand(self:object, latexCommand:str, madatoryOptions:list, optionalOptions:list, i:int, j:int) -> tuple:
		if latexCommand == "\\documentclass":
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			m, n = self.__locateTarget("\\documentclass", i, j)
			self.__children.append(Structure("documentclass", self.__fetchContent(i, j, m, n), self.__filepath))
			self.__children[-1].resolve()
			return (m, n)
		elif latexCommand.startswith("\\begin{"):
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			m, n = self.__locateTarget("\\end{" + latexCommand[7:], i, j, True)
			self.__children.append(Structure(latexCommand[7:-1], self.__fetchContent(i, j, m, n), self.__filepath))
			self.__children[-1].resolve()
			return (m, n)
		elif latexCommand  == "\\section":
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			m, n = self.__locateTarget("\\section", i, j)
			self.__children.append(Structure(",".join(madatoryOptions), self.__fetchContent(i, j, m, n), self.__filepath))
			self.__children[-1].resolve()
			return (m, n)
		elif latexCommand  == "\\subsection":
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			m, n = self.__locateTarget("\\subsection", i, j)
			self.__children.append(Structure(",".join(madatoryOptions), self.__fetchContent(i, j, m, n), self.__filepath))
			self.__children[-1].resolve()
			return (m, n)
		elif latexCommand  == "\\subsubsection":
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			m, n = self.__locateTarget("\\subsubsection", i, j)
			self.__children.append(Structure(",".join(madatoryOptions), self.__fetchContent(i, j, m, n), self.__filepath))
			self.__children[-1].resolve()
			return (m, n)
		elif latexCommand == "\\input":
			self.__printWithStatus("Got LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
			target = ",".join(madatoryOptions).replace("\"", "").replace("'", "")
			if os.path.splitext(target)[1].lower() not in (".txt", ".tex"):
				target = target + ".tex"
			if not os.path.isabs(target):
				target = os.path.join(os.path.split(self.__filepath)[0], target)
			self.__printWithStatus("Resolve the file: \"{0}\". ".format(target), Debug)
			checker = Checker(target, debugLevel = self.__debugLevel)
			checker.setup()
			print(checker.getStructure())
			self.__children += checker.getStructure().getChildren()
			return (i, j)
		else:
			return (i, j)
	def resolve(self:object) -> bool:
		self.__children.clear() # reset
		skipToI, skipToJ = None, None # control skipping
		self.__lines = self.__content.split("\n")
		i, length = 0, len(self.__lines)
		while i < length: # use while to make the index variable i controllable
			line = self.__lines[i]
			lineLength = len(line)
			if skipToJ is None:
				j = 0
			else: # i and j were skipped together
				j = skipToJ
				skipToJ = None # reset
			escapeFlag = False
			while j < lineLength: # use while to make the index variable j controllable
				if line[j] == "\\":
					if escapeFlag:
						escapeFlag = False
					else:
						startLocation = j
						j += 1
						while j < lineLength and ("A" <= line[j] <= "Z" or "a" <= line[j] <= "z"):
							j += 1
						endLocation = j
						if endLocation - startLocation <= 1: # escape
							escapeFlag =True
						else: # LaTeX command
							latexCommand = line[startLocation:endLocation]
							if latexCommand == "\\begin":
								if j < lineLength and line[j] == "{":
									latexCommand += "{"
									j += 1
									allowSpace = True
									while j < lineLength:
										if line[j] == "}":
											latexCommand += "}"
											j += 1
											self.__printWithStatus("The \"\\begin\" command has been merged to {0}. ".format(latexCommand), Debug)
											break
										elif "0" <= line[j] <= "9" or "A" <= line[j] <= "Z" or "a" <= line[j] <= "z":
											allowSpace = False
											latexCommand += line[j]
										elif line[j] in (" ", "\t"):
											if not allowSpace:
												self.__printWithStatus("An unexpected space or \"\\t\" is detected in the \"\\begin\" command at ({0}, {1}). ".format(i, j), Error)
												return False
										else:
											self.__printWithStatus("The \"\\begin\" command at ({0}, {1}) is invalid with unexpected characters. ".format(i, j), Error)
										j += 1
									else:
										self.__printWithStatus("The \"{\" of the \"\\begin\" command at ({0}, {1}) is not closed. ".format(i, j), Error)
										return False
								else:
									self.__printWithStatus("The \"\\begin\" command at ({0}, {1}) is invalid without \"{\". ".format(i, j), Error)
									return False
							madatoryFlag, optionalFlag = False, False # to avoid {}[]{} or []{}[]
							madatoryOptions, optionalOptions = [], []
							while j < lineLength: # Here the variable escapeFlag must be False
								if line[j] == "{":
									if madatoryFlag:
										break
									else:
										j += 1
										startLocation = j
										bracketCount = 0
										while j < lineLength:
											if line[j] == "{":
												if escapeFlag:
													escapeFlag = False
												else:
													bracketCount += 1
											elif line[j] == "}":
												if escapeFlag:
													escapeFlag = False
												elif bracketCount == 0: # get the full list of madatory options
													endLocation = j
													madatoryOptions = line[startLocation:endLocation].strip().split(",")
													j += 1
													break
												else:
													bracketCount -= 1
											elif line[j] == "\\":
												escapeFlag = True
											j += 1
								elif line[j] == "[":
									if optionalFlag:
										break
									else:
										j += 1
										startLocation = j
										bracketCount = 0
										while j < lineLength:
											if line[j] == "[":
												if escapeFlag:
													escapeFlag = False
												else:
													bracketCount += 1
											elif line[j] == "]":
												if escapeFlag:
													escapeFlag = False
												elif bracketCount == 0: # get the full list of optional options
													endLocation = j
													optionalOptions = line[startLocation:endLocation].replace(" ", "").replace("\t", "").split(",")
													j += 1
													break
												else:
													bracketCount -= 1
											elif line[j] == "\\":
												escapeFlag = True
											j += 1
								elif line[j] in (" ", "\t"):
									j += 1	
								else: # not options
									break
							self.__printWithStatus("Sent LaTeX Command: " + latexCommand + "{" + ",".join(madatoryOptions) + "}[" + ",".join(optionalOptions) + "]", Debug)
							skipToI, skipToJ = self.__handleLatexCommand(latexCommand, madatoryOptions, optionalOptions, i, j)
							if skipToI is not None:
								break # stop parsing the current line and skip to the specified line
				elif line[j] == "%":
					if escapeFlag:
						escapeFlag = False
					else:
						break # ignore the comments and start to consider the next line
				else:
					escapeFlag = False
				if skipToJ is None:
					j += 1
				else:
					j = skipToJ
					skipToJ = None # reset
			if skipToI is None:
				i += 1
			else:
				i = skipToI
				skipToI = None # reset
		return True
	def getChildren(self:object) -> list:
		return self.__children
	def printTree(self:object, depth:int = 0) -> None:
		print("\t" * depth + self.__name)
		for child in self.__children:
			child.printTree(depth + 1)
	def __str__(self:object) -> str:
		return "Structure(\"{0}\", children = [{1}])".format(self.__name, ", ".join([str(child) for child in self.__children]))

class Checker:
	def __init__(self:object, mainTexPath:str = None, debugLevel:DebugLevel|int = 0) -> object:
		self.__mainTexPath = os.path.abspath(mainTexPath) if isinstance(mainTexPath, str) else None # transfer to the absolute path
		self.__structure = None
		if isinstance(debugLevel, DebugLevel):
			self.__debugLevel = debugLevel
		else:
			try:
				self.__debugLevel = int(debugLevel)
			except:
				self.__debugLevel = 0
				self.__printWithStatus("The debug level specified is invalid. It is defaulted to 0. ", Warning)
		self.__flag = False
	def getTxt(self:object, filepath:str, index:int = 0) -> str: # get .txt content
		coding = ("utf-8", "gbk", "utf-16") # codings
		if 0 <= index < len(coding): # in the range
			try:
				with open(filepath, "r", encoding = coding[index]) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				return getTxt(filepath, index + 1) # recursion
			except:
				return None
		else:
			return None # out of range
	def clearScreen(self:object, fakeClear:int = 120) -> bool:
		if CLEAR_SCREEN_COMMAND is not None and not os.system(CLEAR_SCREEN_COMMAND):
			return True
		else:
			try:
				print("\n" * int(fakeClear))
			except:
				print("\n" * 120)
			return False
	def __printWithStatus(self:object, strings:str, status:int|DebugLevel = Info) -> bool:
		if isinstance(status, DebugLevel):
			if status >= self.__debugLevel:
				print("{0} {1}".format(status, strings))
			return True
		elif isinstance(status, int) and status >= 0:
			print("{0} {1}".format("\t" * status, strings))
			return True
		else:
			print(strings)
			return False
	def __inputWithStatus(self:object, strings:str, status:int|DebugLevel = Prompt) -> str:
		try:
			if isinstance(status, DebugLevel):
				return input("{0} {1}".format(status, strings))
			elif isinstance(status, int) and status >= 0:
				return input("{0} {1}".format("\t" * status, strings))
			else:
				return None
		except KeyboardInterrupt:
			self.__printWithStatus("", 0)
			self.__printWithStatus("The input process was interrupted by users. None will be returned as the default value. ", Warning)
			return None
	def __resolve(self:object) -> bool:
		content  = self.getTxt(self.__mainTexPath)
		if content is None:
			self.__printWithStatus("The main tex file \"{0}\" cannot be read successfully. ".format(self.__mainTexPath), Error)
			return False
		#self.clearScreen()
		self.__printWithStatus("Starting to resolve, please wait. If it takes too long time, please use \"Ctrl+C\". ".format(self.__mainTexPath), Info)
		try:
			self.__structure = Structure("Root", content, self.__mainTexPath, debugLevel = self.__debugLevel)
			self.__flag = self.__structure.resolve()
			if self.__flag:
				self.__printWithStatus("Successfully resolved the main tex. ", Info)
				self.__printWithStatus(self.__structure, Debug)
			else:
				self.__printWithStatus("Failed to resolve the main tex. ", Error)
			return self.__flag
		except KeyboardInterrupt:
			self.__printWithStatus("Resolving is interrupted by users. Functions cannot be used. ", Warning)
			return False
	def setup(self:object) -> bool:
		try:
			#self.clearScreen()
			if not isinstance(self.__mainTexPath, str):
				tmpMainTexPath = self.__inputWithStatus("Please input the main tex path: ", Prompt)
				if tmpMainTexPath is None:
					self.__printWithStatus("Setup cancelled. ", Error)
					return False
				else:
					self.__mainTexPath = tmpMainTexPath
					self.__printWithStatus("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
					return self.setup()
			elif os.path.isfile(self.__mainTexPath):
				return self.__resolve()
			elif os.path.isdir(self.__mainTexPath):
				self.__printWithStatus("Since a folder was specified, the program is scanning the folder now. ", Info)
				self.__printWithStatus("If it takes too long time, please use \"Ctrl+C\" to stop the scanning. ", Info)
				possibleTargets = []
				try:
					for root, dirs, files in os.walk(self.__mainTexPath):
						for filename in files:
							if os.path.splitext(filename)[1].lower() in (".tex", ):
								possibleTargets.append(os.path.join(root, filename))
				except KeyboardInterrupt:
					self.__printWithStatus("Scanning is interrupted by users. The results may be incomplete. ", Warning)
				if len(possibleTargets) > 1:
					self.__printWithStatus("Possible targets are listed as follows. ", Prompt)
					try:
						for i, target in enumerate(possibleTargets):
							self.__printWithStatus("[{0}] \"{1}\"".format(i + 1, target), 1)
					except KeyboardInterrupt:
						self.__printWithStatus("Printing is interrupted by users. The results may be incomplete. ", Warning)
					self.__printWithStatus("", 1) # print an empty line
					choice = self.__inputWithStatus("Please select a tex file as the main file to continue: ", Prompt)
					if choice in possibleTargets:
						self.__mainTexPath = choice
						self.__printWithStatus("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
						return self.__resolve()
					else:
						try:
							self.__mainTextPath = choice[int(choice) - 1]
							self.__printWithStatus("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
							return self.__resolve()
						except:
							self.__printWithStatus("Invalid choice is made. Failed to resolve main tex. ", Error)
							return False
				elif len(possibleTargets) == 1:
					self.__printWithStatus("The main tex path is set to \"{0}\" automatically since there is only one tex file detected. ".format(self.__mainTexPath), Info)
					return self.__resolve()
				else:
					self.__printWithStatus("No tex files are detected under the specified folder.. ", Error)
					return False
			else:
				self.__printWithStatus("Setup failed since the main tex cannot be read. ", Error)
				return False
		except Exception as e:
			self.__printWithStatus("Exceptions occurred during the setup. Details are as follows.  ", Critical)
			self.__printWithStatus(e, 1)
			return False
	def getStructure(self:object) -> Structure:
		return self.__structure


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
		checker = Checker(argv[1] if len(argv) == 2 else None)
		checker.setup()
		print("Structure: ")
		checker.getStructure().printTree(1)
		preExit()
		return EXIT_SUCCESS if checker else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())