import os
import hashlib
from msvcrt import getch
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


def SHA256(fpath) -> str:
	if not os.path.isfile(fpath):
		return None
	try:
		with open(fpath, "rb") as f:
			hash = hashlib.new("SHA256")
			for chunk in iter(lambda: f.read(1 << 20), b""):
				hash.update(chunk)
			return hash.hexdigest()
	except Exception as e:
		print("\"{0}\" -> {1}".format(fpath, e))
		return None

def compare(dir1, dir2, caseSensitive = True, deep = True) -> bool:
	delLists = []
	for root, dirs, files in os.walk(dir1):
		for f in files:
			source = os.path.relpath(os.path.join(root, f), dir1)
			delLists.append(source if caseSensitive else source.lower())
	addLists = []
	differLists = []
	for root, dirs, files in os.walk(dir2):
		for f in files:
			target = os.path.relpath(os.path.join(root, f), dir2)
			target = target if caseSensitive else target.lower()
			if target in delLists:
				delLists.remove(target)
				if deep and SHA256(os.path.join(dir1, target)) != SHA256(os.path.join(dir2, target)):
					differLists.append(target)
			else:
				addLists.append(target)
	print("addLists = {0}".format(addLists))
	print("delLists = {0}".format(delLists))
	if deep:
		print("differLists = {0}".format(differLists))
		print("Totally {0} added, {1} removed, and {2} different files. ".format(len(addLists), len(delLists), len(differLists)))
	else:
		print("Totally {0} added and {1} removed files. ".format(len(addLists), len(delLists)))
	fpath = input("请输入比对结果保存路径：").replace("\"", "").replace("\'", "")
	if fpath:
		with open(fpath, "w", encoding = "utf-8") as f:
			f.write("addLists = {0}\n".format(addLists))
			f.write("delLists = {0}\n".format(delLists))
			if deep:
				f.write("differLists = {0}\n".format(differLists))
				f.write("Totally {0} added, {1} removed, and {2} different files. \n".format(len(addLists), len(delLists), len(differLists)))
			else:
				f.write("Totally {0} added and {1} removed files. \n".format(len(addLists), len(delLists)))
		getch()
	if input("是否再次检查（输入“Y”回车可再次发起检查）？").upper() == "Y":
		compare(dir1, dir2, caseSensitive = caseSensitive, deep = deep)
	else:
		return not any([addLists, delLists, differLists])

def main():
	sourcePath = input("Please input sourcePath: ").replace("\"", "").replace("'", "")
	targetPath = input("Please input targetPath: ").replace("\"", "").replace("'", "")
	deep = "Y" in input("Please state whether to use deep scanning: ").upper()
	compare(sourcePath, targetPath, deep = deep)
	return EXIT_SUCCESS



if __name__ == "__main__":
	exit(main())