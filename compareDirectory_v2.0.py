import platform
import os
from sys import stdin, exit
from shutil import copy, copytree, rmtree
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
	if stdin.isatty(): # is at a console
		if platform.system().upper() == "WINDOWS":
			os.system("cls")
		elif platform.system().upper() == "LINUX":
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

def getRelPath(path:str, start:str) -> str:
	try:
		return os.path.relpath(path, start)
	except:
		return os.path.abspath(path)

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
		listDir1, listDir2 = sorted([item for item in os.listdir(dir1) if item not in specialFolders], key = lambda x:x.upper()), sorted([item for item in os.listdir(dir2) if item not in specialFolders], key = lambda x:x.upper()) # 获取一层并排除特殊的文件夹
		assistDir1, assistDir2 = (listDir1[::], listDir2[::]) if caseSensitive else ([item.upper() for item in listDir1], [item.upper() for item in listDir2]) # handle issues of repeated directories and the switch of case sensitivity
		setDir1 = set(assistDir1)
		if len(setDir1) != len(assistDir1):
			for ele in sorted(setDir1, key = lambda x:x.upper()):
				if assistDir1.count(ele) > 1:
					while ele in assistDir1:
						idx = assistDir1.index(ele)
						cItem = getRelPath(os.path.join(dir1, listDir1[idx]), rootDir1)
						if cItem not in conflictLists:
							conflictLists.append(cItem)
						del assistDir1[idx]
						del listDir1[idx]
					while ele in assistDir2:
						idx = assistDir2.index(ele)
						cItem = getRelPath(os.path.join(dir2, listDir2[idx]), rootDir2)
						if cItem not in conflictLists:
							conflictLists.append(cItem)
						del assistDir2[idx]
						del listDir2[idx]
		setDir2 = set(assistDir2)
		if len(setDir2) != len(assistDir2):
			for ele in sorted(setDir2, key = lambda x:x.upper()):
				if assistDir2.count(ele) > 1:
					while ele in assistDir1:
						idx = assistDir1.index(ele)
						cItem = getRelPath(os.path.join(dir1, listDir1[idx]), rootDir1)
						if cItem not in conflictLists:
							conflictLists.append(cItem)
						del assistDir1[idx]
						del listDir1[idx]
					while ele in assistDir2:
						idx = assistDir2.index(ele)
						cItem = getRelPath(os.path.join(dir2, listDir2[idx]), rootDir2)
						if cItem not in conflictLists:
							conflictLists.append(cItem)
						del assistDir2[idx]
						del listDir2[idx]
	except Exception as e:
		exceptionLists.append((getRelPath(dir1, rootDir1), e))
		print("\r" + " " * ncols + "\x1b[F\x1b[K", end = "") # 向上一层
		return (addLists, removeLists, conflictLists, exceptionLists, differLists)
	pBar = ProgressBar(total = len(listDir1) + len(listDir2), desc = "Layer {0}".format(indent), postfix = "(a, r, c, e, d) = (0, 0, 0, 0, 0)", ncols = ncols)
	try:
		while listDir1 and listDir2:
			if listDir1[0] == listDir2[0] or not caseSensitive and listDir1[0].upper() == listDir2[0].upper(): # 相同情况比较属性（目录或文件）是否一致
				target1, target2 = os.path.join(dir1, listDir1[0]), os.path.join(dir2, listDir2[0])
				if os.path.islink(target1) and os.path.islink(target2): # 都是软链接
					if compareFileContent:
						try:
							if not (										\
								caseSensitive and os.readlink(target1) == os.readlink(target2)				\
								or not caseSensitive and os.readlink(target1).upper() == os.readlink(target2).upper()		\
							):
								differLists.append(getRelPath(target1, rootDir1))
						except Exception as e:
							exceptionLists.append((getRelPath(target1, rootDir1), e))
				elif os.path.isdir(target1) and os.path.isdir(target2): # 都是文件夹则递归
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
								differLists.append(getRelPath(target1, rootDir1))
						else:
							exceptionLists.append((getRelPath(target1, rootDir1), (sha1, sha2)))
				else: # 属性（目录或文件）不同
					conflictLists.append(getRelPath(target1, rootDir1))
				listDir1.pop(0)
				listDir2.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(2)
			elif listDir1[0] < listDir2[0]: # 第一个目标小
				target1 = os.path.join(dir1, listDir1[0])
				removeLists.append(getRelPath(target1, rootDir1)) # 标记为删除
				listDir1.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(1)
			elif listDir1[0] > listDir2[0]: # 第二个目标小
				target2 = os.path.join(dir2, listDir2[0])
				addLists.append(getRelPath(target2, rootDir2)) # 标记为增加
				listDir2.pop(0)
				pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
				pBar.update(1)
		if listDir1:
			removeLists.extend([getRelPath(os.path.join(dir1, item), rootDir1) for item in listDir1])
			pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
			pBar.update(len(listDir1))
		elif listDir2:
			addLists.extend([getRelPath(os.path.join(dir2, item), rootDir2) for item in listDir2])
			pBar.set_postfix("(a, r, c, e, d) = ({0}, {1}, {2}, {3}, {4})".format(len(addLists), len(removeLists), len(conflictLists), len(exceptionLists), len(differLists)))
			pBar.update(len(listDir2))
		print("\r" + " " * ncols + "\x1b[F\x1b[K", end = "") # 向上一层
	except KeyboardInterrupt:
		flags[0] = False
	except Exception as e:
		print("\nExceptions occurred. Details are as follows. \n{0}".format(e))
		print("Please press the enter key to continue. ")
		input()
		flags[0] = None
	return (addLists, removeLists, conflictLists, exceptionLists, differLists)

def selectOperation(addFlag:bool, removeFlag:bool, differFlag:bool) -> int:
	print("\n可供选择的操作如下（“删除”指直接删除而非移至回收站）：")
	if addFlag:
		print("\t1 = 从目标文件夹删除目标文件夹拥有而源文件夹没有的文件（源 → 目标）")
		print("\t2 = 从目标文件夹向源文件夹复制目标文件夹拥有而源文件夹没有的文件（目标 → 源）")
	if removeFlag:
		print("\t3 = 从源文件夹向目标文件夹复制源文件夹拥有而目标文件夹没有的文件（源 → 目标）")
		print("\t4 = 从源文件夹删除源文件夹拥有而目标文件夹没有的文件（目标 → 源）")
	if differFlag:
		print("\t5 = 从源文件夹向目标文件夹同步内容不同的文件（源 → 目标）")
		print("\t6 = 从目标文件夹向源文件夹同步内容不同的文件（目标 → 源）")
	print("\t7 = 保存对比结果")
	print("\t8 = 重新发起检查（原有配置）")
	print("\t9 = 发起新的检查")
	print("\t0 = 退出程序")
	print()
	iRet = input("请选择一项以继续：")
	while True:
		if iRet in (str(i) for i in range(10)):
			if iRet in "7890" or input("即将执行操作 {0}，为确保不是误触，请输入“Y”（区分大小写）回车以再次确认：".format(iRet)) == "Y":
				return int(iRet)
			else:
				iRet = input("输入取消，请重新输入：")
		else:
			iRet = input("无效输入，请重试：")

def doRemove(folder:str, targetList:list) -> bool:
	successCnt, totalCnt = 0, 0
	for item in targetList:
		totalCnt += 1
		toRemoveFp = os.path.join(folder, item)
		try:
			if os.path.isdir(toRemoveFp):
				rmtree(toRemoveFp)
			else:
				os.remove(toRemoveFp)
			successCnt += 1
		except Exception as e:
			print("Failed removing \"{0}\". Details are as follows. \n{1}".format(toRemoveFp, e))
	print("删除完成，删除成功率：{0} / {1} = {2}%。".format(successCnt, totalCnt, 100 * successCnt / totalCnt)) # 不存在 0 除情况
	return successCnt == totalCnt

def doCopy(dir1:str, dir2:str, targetList:list) -> bool:
	successCnt, totalCnt = 0, 0
	for item in targetList:
		totalCnt += 1
		sourceFp = os.path.join(dir1, item)
		targetFp = os.path.join(dir2, item)
		try:
			if os.path.isdir(sourceFp):
				copytree(sourceFp, targetFp)
			else:
				copy(sourceFp, targetFp)
			successCnt += 1
		except Exception as e:
			print("Failed copying \"{0}\" to \"{1}\". Details are as follows. \n{2}".format(sourceFp, targetFp, e))
	print("复制完成，复制成功率：{0} / {1} = {2}%。".format(successCnt, totalCnt, 100 * successCnt / totalCnt)) # 不存在 0 除情况
	return successCnt == totalCnt

def doCompare(dir1:str, dir2:str, compareFileContent:bool = True, caseSensitive:bool = True, state:list = [True]) -> bool:
	clearScreen()
	if not os.path.isdir(dir1):
		print("源文件夹不存在：\"{0}\"\n请按回车键返回。".format(dir1))
		input()
		return None
	elif not os.path.isdir(dir2):
		print("目标文件夹不存在：\"{0}\"\n请按回车键返回。".format(dir2))
		input()
		return None
	elif dir1 == dir2 or not caseSensitive and dir1.upper() == dir2.upper():
		print("源文件夹路径和目标文件夹路径相同，请按回车键返回。")
		input()
		return None
	else:
		print("源文件夹：\"{0}\"".format(dir1))
		print("目标文件夹：\"{0}\"".format(dir2))
		print()
		flags = [True]
		addLists, removeLists, conflictLists, exceptionLists, differLists = compare(dir1, dir2, dir1, dir2, compareFileContent = compareFileContent, caseSensitive = caseSensitive, flags = flags)
		if not flags[0]:
			print("\nThe process is interrupted due to the above exception. " if flags[0] is None else "\nThe process is interrupted by users. ")
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
		while True:
			choice = selectOperation(bool(addLists), bool(removeLists), bool(differLists))
			if choice == 1:
				doRemove(dir2, addLists)
			elif choice == 2:
				doCopy(dir2, dir1, addLists)
			elif choice == 3:
				doCopy(dir1, dir2, removeLists)
			elif choice == 4:
				doRemove(dir1, removeLists)				
			elif choice == 5:
				doCopy(dir1, dir2, differLists)
			elif choice == 6:
				doCopy(dir2, dir1, differLists)
			elif choice == 7:
				fpath = input("请输入比对结果保存路径（留空取消）：").replace("\"", "")
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
						print("Successfully save to \"{0}\". ".format(fpath))
					except Exception as e:
						print("Failed saving to \"{0}\". Details are as follows. \n{1}".format(fpath, e))
			elif choice == 8:
				return doCompare(dir1, dir2, compareFileContent = compareFileContent, caseSensitive = caseSensitive, state = state)
			elif choice == 9:
				try:
					return not any([addLists, removeLists, conflictLists, exceptionLists, differLists])
				except: # 未定义变量
					return None
			elif choice == 0:
				state[0] = False
				try:
					return not any([addLists, removeLists, conflictLists, exceptionLists, differLists])
				except: # 未定义变量
					return None

def main() -> int:
	try:
		state = [True]
		while state[0]:
			clearScreen()
			sourcePath = input("请输入源文件夹路径：").replace("\"", "")
			targetPath = input("请输入目标文件夹路径：").replace("\"", "")
			compareFileContent = input("请选择是否需要比较文件内容（输入“Y”表示“是”）：").upper() in ("1", "Y")
			caseSensitive = input("请选择大小写是否敏感（输入“Y”表示“是”）：").upper() in ("1", "Y")
			bRet = doCompare(sourcePath, targetPath, compareFileContent = compareFileContent, caseSensitive = caseSensitive, state = state)
		clearScreen()
		return EXIT_SUCCESS if bRet else EXIT_FAILURE
	except Exception as e:
		try:
			print("Unexpected exceptions occurred in the main function. Details are as follows. \n{0}\nPlease press the enter key to exit. ".format(e))
			input()
			clearScreen()
		except:
			pass
		finally:
			return EOF



if __name__ == "__main__":
	exit(main())