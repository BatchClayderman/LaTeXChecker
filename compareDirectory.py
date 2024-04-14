import platform
import os
import sys	
from shutil import copy
import hashlib
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
specialFolders = ["", ".", ".."]
ncols = 100


class ProgressBar:
	def __init__(self:object, total:int, desc:str = "", postfix:str = "", ncols:int = 100) -> object:
		self.c = 0
		self.total  = total
		self.desc = str(desc)
		self.postfix = str(postfix)
		self.ncols = ncols
		self.print()
	def update(self:object, c:int) -> bool:
		if isinstance(c, int) and c >= 0:
			self.c += c
			self.print()
			return True
		else:
			return False
	def set_postfix(self:object, postfix:str) -> None:
		self.postfix = str(postfix)
	def print(self:object) -> None:
		print("\r" + str(self), end = "")
	def __str__(self:object) -> str:
		try:
			return "{0}: {1} / {2} = {3:.2f}% {4}".format(self.desc, self.c, self.total, 100 * self.c / self.total if self.c >= 0 and self.total > 0 else float("nan"), self.postfix)[:self.ncols]
		except:
			return ""


def clearScreen(fakeClear:int = 120):
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

def SHA256(fpath:str, isEcho:bool = False) -> str|Exception|None:
	if not os.path.isfile(fpath):
		return None
	try:
		with open(fpath, "rb") as f:
			hash = hashlib.new("SHA256")
			for chunk in iter(lambda: f.read(1 << 20), b""):
				hash.update(chunk)
			return hash.hexdigest()
	except Exception as e:
		if isEcho:
			print("\"{0}\" -> {1}".format(fpath, e))
		return e

def compare(rootDir1:str, rootDir2:str, dir1:str, dir2:str, compareFileContent:bool = True, caseSensitive:bool = True, indent:int = 0, flags:list = [True]) -> tuple:
	addLists, removeLists, conflictLists, exceptionLists, differLists = [], [], [], [], []
	try:
		listDir1, listDir2 = sorted([item for item in os.listdir(dir1) if item not in specialFolders]), sorted([item for item in os.listdir(dir2) if item not in specialFolders]) # 获取一层并排除特殊的文件夹
	except Exception as e:
		exceptionLists.append((os.path.relpath(dir1, rootDir1), e))
		print("\r" + " " * ncols + "\x1b[F\x1b[K", end = "") # 向上一层
		return (addLists, removeLists, conflictLists, exceptionLists, differLists)
	pBar = ProgressBar(total = len(listDir1) + len(listDir2), desc = "Layer {0}".format(indent), ncols = ncols)
	try:
		while listDir1 and listDir2:
			if listDir1[0] == listDir2[0] or not caseSensitive and listDir1[0].lower() == listDir2[0].lower(): # 相同情况比较属性（目录或文件）是否一致
				target1, target2 = os.path.join(dir1, listDir1[0]), os.path.join(dir2, listDir2[0])
				if os.path.isdir(target1) and os.path.isdir(target2): # 都是文件夹则递归
					print() # 向下一层
					tRet = compare(rootDir1, rootDir2, target1, target2, compareFileContent = compareFileContent, caseSensitive = caseSensitive, indent = indent + 1, flags = flags)
					addLists.extend(tRet[0])
					removeLists.extend(tRet[1])
					conflictLists.extend(tRet[2])
					exceptionLists.extend(tRet[3])
					differLists.extend(tRet[4])
					del tRet # 手动释放内存
					if not flags[0]:
						raise KeyboardInterrupt
				elif os.path.isfile(target1) and os.path.isfile(target2): # 都是文件
					if compareFileContent:
						sha1 = SHA256(target1)
						sha2 = SHA256(target2)
						if isinstance(sha1, str) and isinstance(sha2, str):
							if sha1 != sha2:
								differLists.append(os.path.relpath(target1, rootDir1))	
						else:
							exceptionLists.append((os.path.relpath(target1, rootDir1), (sha1, sha2)))
				else: # 属性（目录或文件）不同
					conflictLicts.append(os.path.relpath(target1, rootDir1))
				listDir1.pop(0)
				listDir2.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(2)
			elif listDir1[0] < listDir2[0]: # 第一个目标小
				target1 = os.path.join(dir1, listDir1[0])
				removeLists.append(os.path.relpath(target1, rootDir1)) # 标记为删除
				listDir1.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(1)
			elif listDir1[0] > listDir2[0]: # 第二个目标小
				target2 = os.path.join(dir2, listDir2[0])
				addLists.append(os.path.relpath(target2, rootDir2)) # 标记为增加
				listDir2.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(1)
		if listDir1:
			removeLists.extend([os.path.relpath(os.path.join(dir1, item), rootDir1) for item in listDir1])
			pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
			pBar.update(len(listDir1))
		elif listDir2:
			addLists.extend([os.path.relpath(os.path.join(dir2, item), rootDir2) for item in listDir2])
			pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
			pBar.update(len(listDir2))
		print("\r" + " " * ncols + "\x1b[F\x1b[K", end = "") # 向上一层
	except KeyboardInterrupt:
		flags[0] = False
	return (addLists, removeLists, conflictLists, exceptionLists, differLists)

def doCompare(dir1:str, dir2:str, compareFileContent:bool = True, caseSensitive:bool = True) -> bool:
	clearScreen()
	if not os.path.isdir(dir1):
		print("源文件夹不存在：\"{0}\"".format(dir1))
	elif not os.path.isdir(dir2):
		print("目标文件夹不存在：\"{0}\"".format(dir2))
	elif dir1 == dir2 or not caseSensitive and dir1.lower() == dir2.lower():
		print("源文件夹路径和目标文件夹路径相同。")
	else:
		print("源文件夹：\"{0}\"".format(dir1))
		print("目标文件夹：\"{0}\"".format(dir2))
		print()
		flags = [True]
		addLists, removeLists, conflictLists, exceptionLists, differLists = compare(dir1, dir2, dir1, dir2, compareFileContent = compareFileContent, caseSensitive = caseSensitive, flags = flags)
		if not flags[0]:
			print("\nThe process is interrupted by users. ")
		print()
		print("addLists = {0}".format(addLists))
		print("removeLists = {0}".format(removeLists))
		print("conflictLists = {0}".format(conflictLists))
		print("exceptionLists = {0}".format(exceptionLists))
		if compareFileContent:
			print("differLists = {0}".format(differLists))
			print("Totally {0} added, {1} removed, {2} conflicted, {3} erroneous, and {4} different items. ".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
		else:
			print("Totally {0} added, {1} removed, {2} conflicted, and {3} erroneous items. ".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists)))
		fpath = input("\n如有需要，请输入比对结果保存路径（留空跳过）：").replace("\"", "")
		if fpath:
			try:
				with open(fpath, "w", encoding = "utf-8") as f:
					f.write("Source = \"{0}\"\n".format(dir1))
					f.write("Target = \"{0}\"\n".format(dir2))
					f.write("addLists = {0}\n".format(addLists))
					f.write("removeLists = {0}\n".format(removeLists))
					f.write("conflictLists = {0}\n".format(conflictLists))
					f.write("exceptionLists = {0}\n".format(exceptionLists))
					if compareFileContent:
						f.write("differLists = {0}\n".format(differLists))
						f.write("Totally {0} added, {1} removed, and {2} different files. \n".format(len(addLists), len(removeLists), len(differLists)))
					else:
						f.write("Totally {0} added and {1} removed files. \n".format(len(addLists), len(removeLists)))
				print("保存成功！")
			except Exception as e:
				print("保存失败，异常信息如下：")
				print(e)
		if compareFileContent and differLists and input("\n是否从源文件夹向目标文件夹同步（输入“Y”回车可同步）？").upper() == "Y":
			successCnt, totalCnt = 0, 0
			for item in differLists:
				totalCnt += 1
				try:
					copy(os.path.join(dir1, item), os.path.join(dir2, item))
					successCnt += 1
				except Exception as e:
					print("Failed copying \"{0}\" to \"{1}\". Details are as follows. \n{2}".format(os.path.join(dir1, item), os.path.join(dir2, item), e))
			print("同步完成，同步成功率：{0} / {1} = {2}%。".format(successCnt, totalCnt, 100 * successCnt / totalCnt)) # 不存在 0 除情况
	if input("\n是否再次检查（输入“Y”回车可再次发起检查）？").upper() == "Y":
		return doCompare(dir1, dir2, compareFileContent = compareFileContent, caseSensitive = caseSensitive)
	else:
		try:
			return not any([addLists, removeLists, conflictLists, exceptionLists, differLists])
		except: # 未定义变量
			return None

def main() -> int:
	sourcePath = input("请输入源文件夹路径：").replace("\"", "")
	targetPath = input("请输入目标文件夹路径：").replace("\"", "")
	compareFileContent = "Y" in input("请选择是否需要比较文件内容（输入“Y”表示“是”）：").upper()
	caseSensitive = "Y" in input("请选择大小写是否敏感（输入“Y”表示“是”）：").upper()
	bRet = doCompare(sourcePath, targetPath, compareFileContent = compareFileContent, caseSensitive = caseSensitive)
	clearScreen()
	return EXIT_SUCCESS if bRet else EXIT_FAILURE



if __name__ == "__main__":
	sys.exit(main())