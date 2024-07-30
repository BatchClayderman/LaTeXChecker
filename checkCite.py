import platform
import os
import sys
from re import findall
from time import sleep
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


def getTxt(filepath:str, index:int = 0) -> str: # get .txt content
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

def removeCommentLine(text) -> str: # remove comment lines
	lines = text.split("\n")
	for i, line in enumerate(lines):
		for j in range(len(line)):
			if line[j] == "%" and (0 == j or line[j - 1] != "\\"):
				lines[i] = lines[i][:j]
	return "\n".join(lines)

def clearScreen(fakeClear:int = 120) -> None:
	if sys.stdin.isatty(): # is at a console
		if platform.system().lower() == "windows":
			os.system("cls")
		elif platform.system().lower() == "linux":
			os.system("clear")
		else:
			try:
				print("\n" * int(fakeClear))
			except:
				print("\n" * 120)
	else:
		try:
			print("\n" * int(fakeClear))
		except:
			print("\n" * 120)

def press_any_key_to_continue() -> bytes:
	while kbhit():
		getch()
	return getch()

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


def loadFolder(latex_folder) -> dict:
	dicts = {}
	for root, dirs, files in os.walk(latex_folder):
		for f in files:
			filepath = os.path.join(root, f)
			if os.path.isfile(filepath):
				if filepath.lower().endswith(".tex"):
					dicts.setdefault("tex", [])
					dicts["tex"].append(filepath)
				elif filepath.lower().endswith(".bib"):
					dicts.setdefault("bib", [])
					dicts["bib"].append(filepath)
	return dicts

def checkLabels(texFilepaths, isDebug = False) -> bool:
	clearScreen()
	if type(texFilepaths) not in (tuple, list) or not texFilepaths:
		print("As no tex files are found, the checking cannot work. ")
		print("Please press any key to go back. ")
		press_any_key_to_continue()
		return None
	
	content = ""
	for texFilepath in texFilepaths:
		text = getTxt(texFilepath)
		if text is None:
			print("Read tex file \"{0}\" failed. ".format(texFilepath))
		else:
			content += removeCommentLine(text) + "\n"
	labels = [item[item.index("{") + 1:-1] for item in findall("\\\\label\\{.+?\\}", content)]
	refs = [item[item.index("{") + 1:-1] for item in findall("\\\\ref\\{.+?\\}", content)] + [item[item.index("{") + 1:-1] for item in findall("\\\\eqref\\{.+?\\}", content)]
	for i in range(len(refs) - 1, -1, -1):
		if "," in refs[i]:
			refs += [item.strip() for item in refs[i].split(",")]
			del refs[i]
	if isDebug:
		print("labels =", labels)
		print("refs =", refs)
	
	s = set()
	repeated_label = set()
	undefined_label = set()
	unreferred_label = set()
	for label in labels:
		if label in s:
			repeated_label.add(label)
		else:
			s.add(label)
		if label not in refs:
			unreferred_label.add(label)
	for ref in refs:
		if ref not in labels:
			undefined_label.add(ref)
	
	if len(s) == 1:
		print("This the label checking. There is 1 label in total. ")
	elif len(s) > 1:
		print("This the label checking. There are {0} labels in total. ".format(len(s)))
	else:
		print("This the label checking. There are no labels found. ")
	print()
	if len(repeated_label) == 1:
		print("There is a repeated label found: \"{0}\". ".format(*repeated_label))
	elif len(repeated_label) > 1:
		print("There are {0} repeated labels found. The details are as follows. \n{1}".format(len(repeated_label), repeated_label))
	else:
		print("No repeated labels are found. ")
	if len(undefined_label) == 1:
		print("There is an undefined label found: \"{0}\". ".format(*undefined_label))
	elif len(undefined_label) > 1:
		print("There are {0} undefined labels found. The details are as follows. \n{1}".format(len(undefined_label), undefined_label))
	else:
		print("No undefined labels are found. ")
	if len(unreferred_label) == 1:
		print("There is an unreferred label found: \"{0}\". ".format(*unreferred_label))
	elif len(unreferred_label) > 1:
		print("There are {0} unreferred labels found. The details are as follows. \n{1}".format(len(unreferred_label), unreferred_label))
	else:
		print("No unreferred labels are found. ")
	
	print()
	if input("Would you like to check again (input \"Y\" and enter to check again): ").upper() == "Y":
		return checkLabels(texFilepaths, isDebug = isDebug)
	else:
		return not any([repeated_label, undefined_label, unreferred_label])

def checkCitations(texFilepaths, isDebug = False) -> bool:
	clearScreen()
	if type(texFilepaths) not in (tuple, list) or not texFilepaths:
		print("As no tex files are found, the checking cannot work. ")
		print("Please press any key to go back. ")
		press_any_key_to_continue()
		return None
	
	content = ""
	for texFilepath in texFilepaths:
		text = getTxt(texFilepath)
		if text is None:
			print("Read tex file \"{0}\" failed. ".format(texFilepath))
		else:
			content += removeCommentLine(text).replace("\\newcommand{\\upcite}[1]{\\textsuperscript{\\cite{#1}}}", "").replace("\\upcite", "\\cite") + "\n"
	cites = [item[item.index("{") + 1:-1] for item in findall("\\\\cite\\{.*?\\}", content)]
	for i in range(len(cites) - 1, -1, -1):
		if "," in cites[i]:
			cites += [item.strip() for item in cites[i].split(",")]
			del cites[i]
	
	dicts = {}
	repeated_entry = []
	for line in content.split("\n"):
		targets = findall("\\\\bibitem\\{.+?\\}", line)
		if len(targets):
			target = targets[0]
			key = target[target.index("{") + 1:-1]
			if key in dicts:
				repeated_entry.append(key)
			else:
				dicts[key] = line[len(target):]
	
	space_start = []
	multiple_space = []
	end_dot = []
	repeated_content = []
	undefined_entry = set()
	uncited_entry = set()
	for key in list(dicts.keys()):
		if not dicts[key].startswith(" "):
			space_start.append(key)
		if dicts[key][:2] in ("  ", " \t"): # do not use elif
			multiple_space.append(key)
		if not dicts[key].endswith(". "): # do not use elif
			end_dot.append(key)
	for key in list(dicts.keys()):
		dicts[key] = dicts[key].strip()
	reverse_dict = {}
	for key in list(dicts.keys()):
		reverse_dict.setdefault(dicts[key], [])
		reverse_dict[dicts[key]].append(key)
	for key in list(reverse_dict.keys()):
		if len(reverse_dict[key]) > 2:
			repeated_content.append(reverse_dict[key])
	for key in list(dicts.keys()):
		if key not in cites:
			uncited_entry.add(key)
	for cite in cites:
		if cite not in dicts:
			undefined_entry.add(cite)
	
	if len(dicts) == 1:
		print("The citation checking mode is not using bib. There is 1 citation in total. ")
	elif len(dicts) > 1:
		print("The citation checking mode is not using bib. There are {0} citations in total. ".format(len(dicts)))
	else:
		print("The citation checking mode is not using bib. There are no citations found. ")
	print()
	if isDebug:
		print(dicts)
		print()
	if len(repeated_entry) == 1:
		print("There is a repeated entry: \"{0}\". ".format(repeated_entry[0]))
	elif len(repeated_entry) > 1:
		print("There are {0} repeated entries. The details are as follows. \n{1}".format(len(repeated_entry), repeated_entry))
	else:
		print("No repeated entries are found. ")
	if len(repeated_content) == 1:
		print("There is a repeated content found: \"{0}\". ".format(repeated_content[0]))
	elif len(repeated_content) > 1:
		print("There are {0} repeated contents found. The details are as follows. \n{1}".format(len(repeated_content), repeated_content))
	else:
		print("No repeated contents are found. ")
	if len(space_start) == 1:
		print("There is an entry not starting with a space: \"{0}\". ".format(space_start[0]))
	elif len(space_start) > 1:
		print("There are {0} entries not starting with a space. The details are as follows. \n{1}".format(len(space_start), space_start))
	else:
		print("No entries not starting with a space are found. ")
	if len(multiple_space) == 1:
		print("There is an entry starting with multiple spaces or tabs: \"{0}\". ".format(multiple_space[0]))
	elif len(multiple_space) > 1:
		print("There are {0} entries starting with multiple spaces or tabs. The details are as follows. \n{1}".format(len(multiple_space), multiple_space))
	else:
		print("No entries not starting with multiple spaces or tabs are found. ")
	if len(end_dot) == 1:
		print("There is an entry not ending with \". \": \"{0}\". ".format(end_dot[0]))
	elif len(end_dot) > 1:
		print("There are {0} entries not ending with \". \". The details are as follows. \n{1}".format(len(end_dot), end_dot))
	else:
		print("No entries not ending with \". \" are found. ")
	if len(undefined_entry) == 1:
		print("There is an undefined entry found: \"{0}\". ".format(*undefined_entry))
	elif len(undefined_entry) > 1:
		print("There are {0} undefined entries found. The details are as follows. \n{1}".format(len(undefined_entry), undefined_entry))
	else:
		print("No undefined entries are found. ")
	if len(uncited_entry) == 1:
		print("There is an uncited entry found: \"{0}\". ".format(*uncited_entry))
	elif len(uncited_entry) > 1:
		print("There are {0} uncited entries found. The details are as follows. \n{1}".format(len(uncited_entry), uncited_entry))
	else:
		print("No uncited entries are found. ")

	print()
	if input("Would you like to check again (input \"Y\" and enter to check again): ").upper() == "Y":
		return checkCitations(texFilepaths, isDebug = isDebug)
	else:
		return not any([repeated_entry, space_start, multiple_space, end_dot, repeated_content])

def checkBibtex(texFilepaths, bibFilepaths, isDebug = False) -> bool:
	clearScreen()
	if type(texFilepaths) not in (tuple, list) or not texFilepaths:
		print("As no tex files are found, the checking cannot work. ")
		print("Please press any key to go back. ")
		press_any_key_to_continue()
		return None
	elif type(bibFilepaths) not in (tuple, list) or not bibFilepaths:
		print("As no bib files are found, the checking cannot work. ")
		print("Please press any key to go back. ")
		press_any_key_to_continue()
		return None
	
	content = ""
	for texFilepath in texFilepaths:
		text = getTxt(texFilepath)
		if text is None:
			print("Read tex file \"{0}\" failed. ".format(texFilepath))
		else:
			content += removeCommentLine(text) + "\n"
	cites = [item[item.index("{") + 1:-1] for item in findall("\\\\cite\\{[a-z0-9,\\s]+?\\}", content)]
	for i in range(len(cites) - 1, -1, -1):
		if "," in cites[i]:
			cites += [item.strip() for item in cites[i].split(",")]
			del cites[i]
	content = ""
	for bibFilepath in bibFilepaths:
		text = getTxt(bibFilepath)
		if text is None:
			print("Read bib file \"{0}\" failed. ".format(bibFilepath))
		else:
			content += removeCommentLine(text) + "\n"
	bibs = [item[item.index("{") + 1:-1] for item in findall("@[a-z]+?\\{[a-z0-9\\s]+?,", content)]
	if isDebug:
		print("bibs =", bibs)
		print("cites =", cites)
	
	s = set()
	repeated_entry = set()
	undefined_entry = set()
	uncited_entry = set()
	for bib in bibs:
		if bib in s:
			repeated_entry.add(bib)
		else:
			s.add(bib)
		if bib not in cites:
			uncited_entry.add(bib)
	for cite in cites:
		if cite not in bibs:
			undefined_entry.add(cite)
	
	if len(s) == 1:
		print("The citation checking mode is using bib. There is 1 bib in total. ")
	elif len(s) > 1:
		print("The citation checking mode is using bib. There are {0} bibs in total. ".format(len(s)))
	else:
		print("The citation checking mode is using bib. There are no bibs found. ")
	if len(repeated_entry) == 1:
		print("There is a repeated entry found: \"{0}\". ".format(*repeated_entry))
	elif len(repeated_entry) > 1:
		print("There are {0} repeated entries found. The details are as follows. \n{1}".format(len(repeated_entry), repeated_entry))
	else:
		print("No repeated entries are found. ")
	if len(undefined_entry) == 1:
		print("There is an undefined entry found: \"{0}\". ".format(*undefined_entry))
	elif len(undefined_entry) > 1:
		print("There are {0} undefined entries found. The details are as follows. \n{1}".format(len(undefined_entry), undefined_entry))
	else:
		print("No undefined entries are found. ")
	if len(uncited_entry) == 1:
		print("There is an uncited entry found: \"{0}\". ".format(*uncited_entry))
	elif len(uncited_entry) > 1:
		print("There are {0} uncited entries found. The details are as follows. \n{1}".format(len(uncited_entry), uncited_entry))
	else:
		print("No uncited entries are found. ")
	
	print()
	if input("Would you like to check again (input \"Y\" and enter to check again): ").upper() == "Y":
		return checkBibtex(texFilepaths, bibFilepaths, isDebug = isDebug)
	else:
		return not any([repeated_entry, undefined_entry, uncited_entry])

def citationSurvey(texFilepaths, isDebug = False) -> bool:
	clearScreen()
	if type(texFilepaths) not in (tuple, list) or not texFilepaths:
		print("As no tex files are found, the checking cannot work. ")
		print("Please press any key to go back. ")
		press_any_key_to_continue()
		return None
	
	dicts = {}
	pointer = None
	for texFilepath in texFilepaths:
		text = getTxt(texFilepath)
		if text is None:
			print("Read tex file \"{0}\" failed. ".format(texFilepath))
		else:
			content = removeCommentLine(text)
			for line in content.split("\n"):
				if line.startswith("\\section{") and "}" in line[10:]:
					key = line[9:line.index("}")]
					while key.startswith(" ") or key.startswith("\t"):
						key = key[1:]
					while key.endswith(" ") or key.endswith("\t"):
						key = key[:-1]
					dicts.setdefault(key, 0)
					pointer = key
				if pointer:
					cites = [item[item.index("{") + 1:-1] for item in findall("\\\\cite\\{.+?\\}", line)]
					for i in range(len(cites) - 1, -1, -1):
						if "," in cites[i]:
							cites += [item.strip() for item in cites[i].split(",")]
							del cites[i]
					dicts[pointer] += len(cites)
	if dicts:
		for key in list(dicts.keys()):
			print("{0}\t{1}".format(key, dicts[key]))
	else:
		print("No citation data are got. ")
	
	print()
	if input("Would you like to check again (input \"Y\" and enter to check again): ").upper() == "Y":
		return citationSurvey(texFilepaths, isDebug = isDebug)
	else:
		return bool(dicts)


def mainBoard(latex_folder) -> None:
	while True:
		clearScreen()
		print("Loading information, please wait. ")
		dicts = loadFolder(latex_folder)
		clearScreen()
		print("Latex folder path: \"{0}\"".format(latex_folder))
		print("Note: Please use this script only after you have successfully compiled the LaTeX. ")
		print()
		print("Information: ")
		if "tex" in dicts:
			print("\tThere are {0} tex files in total. ".format(len(dicts["tex"])))
		else:
			print("\tThere are no tex files detected. ")
		if "bib" in dicts:
			print("\tThere are {0} bib files in total. ".format(len(dicts["bib"])))
		else:
			print("\tThere are no bib files detected. ")
		print()
		print("Possible options: ")
		print("\t0 = Go back")
		print("\t1 = Reload information")
		print("\t2 = Check labels")
		print("\t3 = Check citations")
		print("\t4 = Check bibtex")
		print("\t5 = Citation data survey")
		print("\n")
		ch = input("Please select an option to continue: ")
		if ch == "0":
			break
		elif ch == "1":
			continue
		elif ch == "2":
			checkLabels(dicts["tex"] if "tex" in dicts else None)
		elif ch == "3":
			checkCitations(dicts["tex"] if "tex" in dicts else None)
		elif ch == "4":
			checkBibtex(dicts["tex"] if "tex" in dicts else None, dicts["bib"] if "bib" in dicts else None)
		elif ch == "5":
			citationSurvey(dicts["tex"] if "tex" in dicts else None)
		else:
			print("Unknown input, please press any key to continue. ")
			press_any_key_to_continue()

def main() -> int:
	while True:
		clearScreen()
		latex_folder = input("Please input your LaTeX folder (Input \"/\" and enter to exit): ").replace("\"", "")
		if latex_folder in ("\\", "/", ":", "*", "?", "<", ">", "|"):
			break
		elif os.path.isdir(latex_folder):
			mainBoard(latex_folder)
		else:
			print("Folder \"{0}\" does not exist. ".format(latex_folder))
			print("Please press any key to continue. ")
			press_any_key_to_continue()
	preExit()
	clearScreen()
	return EXIT_SUCCESS



if __name__ == "__main__":
	if platform.system().lower() == "windows":
		from msvcrt import getch, kbhit
		sys.exit(main())
	else:
		print("This script can only run on Windows. ")
		preExit()
		clearScreen()
		sys.exit(EOF)