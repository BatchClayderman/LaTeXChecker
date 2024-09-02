import os
from time import sleep
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = -1
inputFilePath = "test.ics"
checkerFilePath = "checker.ics"
yflin01fOutputFilePath = "yflin01f.ics"
yueryangOutputFilePath = "yueryang.ics"


class Calendar:
	def __init__(self:object, events:list = [], header:str = "", footer:str = "", starter:str = "BEGIN:VEVENT", terminator:str = "END:VEVENT") -> object:
		self.__events = [str(event) for event in events] if isinstance(events, (tuple, list)) else []
		self.__header = str(header)
		self.__footer = str(footer)
		self.__starter = str(starter)
		self.__terminator = str(terminator)
	def __getTxt(self:object, filepath:str, index:int = 0) -> str: # get .txt content
		coding = ("utf-8", "gbk", "utf-16") # codings
		if 0 <= index < len(coding): # in the range
			try:
				with open(filepath, "r", encoding = coding[index]) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				return self.__getTxt(filepath, index + 1) # recursion
			except:
				return None
		else:
			return None # out of range
	def resolveFrom(self:object, filePath:str) -> bool:
		content = self.__getTxt(str(filePath))
		if content:
			lines = content.split("\n")
			if self.__starter in lines:
				headerIdx = lines.index(self.__starter)
				header = "\n".join(lines[:headerIdx])
			else:
				print("No \"{0}\" fields are found in the file \"{1}\". ".format(self.__starter, filePath))
				return False
			if self.__terminator in lines:
				footerIdx = len(lines) - lines[::-1].index(self.__terminator)
				footer = "\n".join(lines[footerIdx:])
			else:
				print("No \"{0}\" fields are found in the file \"{1}\". ".format(self.__terminator, filePath))
				return False
			if headerIdx < footerIdx:
				starterIdx = None
				for i, line in enumerate(lines):
					if line == self.__starter:
						if starterIdx is None:
							starterIdx = i
						else:
							print("The \"{0}\" fields are overlapped at Line {1} and Line {2}. ".format(self.__starter, starterIdx, i))
							return False
					elif line == self.__terminator:
						if starterIdx is None:
							print("The \"{0}\" field at Line {1} has no matched \"{2}\" fields. ".format(self.__terminator, i, self.__starter))
							return False
						else:
							self.__events.append("\n".join(lines[starterIdx:i + 1]))
							starterIdx = None
				self.__header, self.__footer = header, footer
				print("Successfully resolve {0} events from \"{1}\". ".format(len(self.__events), filePath))
				return True
			else:
				print("The header and the footer are overlapped. ")
				return False
		else:
			print("Failed to read \"{0}\". ".format(filePath))
	def filterEventsThatContains(self:object, stringList:str|tuple|list, caseSensitive:bool = False) -> int:
		if isinstance(stringList, str):
			stringList = [stringList]
		elif not isinstance(stringList, (tuple, list)):
			return 0
		cnt = 0
		for i in range(len(self.__events) - 1, -1, -1):
			for strings in stringList:
				if caseSensitive and strings in self.__events[i] or not caseSensitive and strings.lower() in self.__events[i].lower():
					break
			else:
				del self.__events[i]
				cnt += 1
		print("Successfully remove {0} events. There are {1} events remaining. ".format(cnt, len(self.__events)))
		return cnt
	def removeEventsThatContains(self:object, stringList:str|tuple|list, caseSensitive:bool = False) -> int:
		if isinstance(stringList, str):
			stringList = [stringList]
		elif not isinstance(stringList, (tuple, list)):
			return 0
		cnt = 0
		for i in range(len(self.__events) - 1, -1, -1):
			for strings in stringList:
				if caseSensitive and strings in self.__events[i] or not caseSensitive and strings.lower() in self.__events[i].lower():
					del self.__events[i]
					cnt += 1
					break
		print("Successfully remove {0} events. There are {1} events remaining. ".format(cnt, len(self.__events)))
		return cnt
	def insertEvent(self:object, idx:int, event:str, isPrint:bool = True) -> bool:
		tmpList = str(event).split("\n")
		for i in range(len(tmpList) - 1, -1, -1): # remove empty lines
			if not tmpList.strip():
				del tmpList[i]
		finalEvent = "\n".join(tmpList[i])
		if not finalEvent.startswith(self.__starter + "\n"): # more seriously
			finalEvent = self.__starter + "\n"
		if not finalEvent.endswith("\n" + self.__terminator):
			finalEvent = "\n" + self.__terminator
		try:
			self.insert(idx, finalEvent)
			if isPrint:
				print("Successfully insert an event to Index {0}. ".format(idx))
			return True
		except Exception as e:
			if isPrint:
				print("Failed to insert an event. Details are as follows. \n{0}".format(e))
			return False
	def addEvent(self:object, event:str, isPrint:bool = True) -> bool:
		return self.insertEvent(len(self.__events), event, isPrint)
	def insertEvents(self:object, indexes:int|tuple|list, events:str|tuple|list) -> int:
		if isinstance(indexes, (tuple, list)) and isinstance(events, (tuple, list)):
			if len(indexes) == len(events):
				cnt = 0
				for idx, event in zip(indexes, events):
					if self.insertEvent(idx, event, False):
						 cnt += 1
				print("Successfully insert {0} event(s). ".format(cnt))
				return cnt
			else:
				print("No events are inserted since the length of indexes ({0}) is not the same as that of events ({1}). ".format(len(indexes), len(events)))
				return 0
		elif isinstance(indexes, int) and isinstance(events, (tuple, list)):
			return self.insertEvents([indexes] * len(events), events)
		elif isinstance(indexes, (tuple, list)) and isinstance(events, str):
			return self.insertEvents(indexes, [events] * len(indexes))
		elif isinstance(indexes, int) and isinstance(events, str):
			return self.insertEvents([indexes], [events])
		else:
			print("No events are inserted since unknown parameters are got. ")
			return 0
	def addEvents(self:object, events:str|tuple|list) -> int:
		return self.insertEvents(len(self.__events), (events[::-1] if isinstance(events, (tuple, list)) else events))
	def dumpTo(self:object, filePath:str, encoding = "utf-8") -> bool:
		try:
			with open(filePath, "w", encoding = encoding) as f:
				f.write("\n".join([self.__header] + self.__events + [self.__footer]))
			print("Successfully write to \"{0}\". ".format(filePath))
			return True
		except Exception as e:
			print("Failed to write to \"{0}\". Details are as follows. \n{1}".format(filePath, e))
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
	calendar = Calendar()
	if not calendar.resolveFrom(inputFilePath):
		preExit()
		return EOF
	bRet = calendar.dumpTo(checkerFilePath)
	calendar.removeEventsThatContains("Online Transferable Skills Programme")
	bRet = calendar.dumpTo(yflin01fOutputFilePath) and bRet
	calendar.filterEventsThatContains(["Convex Optimization", "Data Management and Information Retrieval"])
	bRet = calendar.dumpTo(yueryangOutputFilePath) and bRet
	preExit()
	return EXIT_SUCCESS if bRet else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())