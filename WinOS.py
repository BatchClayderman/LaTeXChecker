import platform
import os
import sys
import shutil
import string
import base64
import chardet
from msvcrt import getch, kbhit
from time import time, sleep
EXIT_SUCCESS = 0#操作成功结束
EXIT_FAILURE = 1#失败
EOF = (-1)



class Music:#音乐类
	def __init__(self, filePath, version = "v1"):
		self.filePath = filePath
		self.version = version
		try:
			fp = open(filePath, "rb")#必须是"rb"
			self.tags = Music.parse(fp, version)
			fp.close()
		except:
			self.tags = {}
	def getDict(self):
		return {"filePath": self.filePath, "version": self.version, "tags": self.tags}
	def __str__(self):#重载输出
		return str(self.getDict())
	@staticmethod
	def decodeData(bin_seq):#检测编码并解密
		#print(bin_seq)
		result = chardet.detect(bin_seq)
		#print(result)
		if result["confidence"] > 0:
			try:
				#return bin_seq.decode(result["encoding"])
				tmp = bin_seq.decode("gbk")
				for i in range(len(tmp) - 1, -1, -1):#去掉后面的空格
					if tmp[i] != " ":
						return tmp[:i + 1]
				else:
					return tmp
			except:
				return ""
		else:
			return ""
	@staticmethod
	def getTags(tag_data):#获取 ID3v1 tag 数据
		STRIP_CHARS = b"\x00"
		tags = {}
		tags["title"] = tag_data[3:33].strip(STRIP_CHARS)
		if (tags["title"]):
			tags["title"] = Music.decodeData(tags["title"])
		tags["artist"] = tag_data[33:63].strip(STRIP_CHARS)
		if (tags["artist"]):
			tags["artist"] = Music.decodeData(tags["artist"])
		tags["album"] = tag_data[63:93].strip(STRIP_CHARS)
		if (tags["album"]):
			tags["album"] = Music.decodeData(tags["album"])
		tags["year"] = tag_data[93:97].strip(STRIP_CHARS)
		if (tags["year"]):
			tags["year"] = Music.decodeData(tags["year"])
		tags["comment"] = tag_data[97:127].strip(STRIP_CHARS)
		if (tags["comment"]):
			tags["comment"] = Music.decodeData(tags["comment"])
		tags["genre"] = ord(tag_data[127:128])#不使用 tag_data[127] 是为了防止报数组越界的错误
		return tags
	@staticmethod
	def parse(fileObj, version = "v1"):
		fileObj.seek(0, 2)
		# ID3v1 的最大长度是 128 字节
		if (fileObj.tell() < 128):
			return False
		fileObj.seek(-128, 2)
		tag_data = fileObj.read()
		if tag_data[0:3] != b"TAG":
			return False
		return Music.getTags(tag_data)


class WinOS:
	@staticmethod
	def clearScreen(fakeClear = 120):
		if sys.stdin.isatty():#在终端
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
	@staticmethod
	def clearSpecialChar(fp, special_lists = list("\\/:*?\"<>|"), reserve_names = ["", "nul", "prn", "con", "aux"] + ["com{0}".format(i) for i in range(10)] + ["lpt{0}".format(i) for i in range(10)], target = ""):
		n_fp = os.path.splitext(os.path.split(fp)[1])[0]
		for sChar in special_lists:
			n_fp = n_fp.replace(sChar, target)
		if n_fp.lower() in reserve_names:
			n_fp = str(time()) + "_" + n_fp
		return os.path.join(os.path.split(fp)[0], n_fp + os.path.splitext(fp)[1])
	@staticmethod
	def fixlib(cb, command, inst_1 = None, inst_2 = None, version = None):
		print("未（正确）安装 " + cb + " 库，正在尝试执行安装，请确保您的网络连接正常。")
		if inst_1 == None:
			if version == None:
				os.system("\"" + sys.executable + "\" -m pip install " + cb)
			else:
				os.system("\"" + sys.executable + "\" -m pip install " + cb + "==" + version)
		else:
			os.system(inst_1)
		try:
			exec(command)
		except:
			WinOS.clearScreen()
			if platform.system().lower() == "windows" and os.popen("ver").read().upper().find("XP") == -1:#找不到相关字样
				print("安装 " + cb + " 库失败，正在尝试以管理员权限执行安装，请确保您的网络连接正常。")
				if inst_2 == None:#提权以管理员身份运行
					if version == None:
						os.system("mshta vbscript:createobject(\"shell.application\").shellexecute(\"" + sys.executable + "\",\"-m pip install " + cb + "\",\"\",\"runas\",\"1\")(window.close)")
					else:
						os.system("mshta vbscript:createobject(\"shell.application\").shellexecute(\"" + sys.executable + "\",\"-m pip install " + cb + "==" + version + "\",\"\",\"runas\",\"1\")(window.close)")
				else:
					os.system(inst_2)
				print("已弹出新窗口，确认授权并安装完成后，请按任意键继续。")
				os.system("pause>nul&cls")
				try:
					exec(command)
				except:
					print("无法正确安装 " + cb + " 库，请按任意键退出，建议稍后重新启动本程序。")
					os.system("pause>nul&cls")
					sys.exit(EOF)
			else:
				print("无法正确安装 " + cb + " 库，请按任意键退出，建议稍后重新启动本程序。")
				os.system("pause>nul&cls")
				sys.exit(EOF)
	@staticmethod
	def cdCurrentPath():
		try:
			os.chdir(os.path.abspath(os.path.dirname(__file__)))#解析进入程序所在目录
		except:
			pass
	@staticmethod
	def osWalk(target_path, extent = None, caseSen = (platform.system().lower() != "windows")):#遍历文件夹
		allPath = []
		for base_path, folder_list, file_list in os.walk(target_path):
			for file_name in file_list:
				file_path = os.path.join(base_path, file_name)
				if extent == None:#无筛选
					allPath.append(file_path)
					continue
				file_ext = file_path.rsplit(".", maxsplit = 1)
				if len(file_ext) != 2:# 没有后缀名
					if extent == "":#如果仅筛选无后缀名文件
						allPath.append(file_path)
					continue#无论是否有后缀名都进行continue
				if type(extent) == str:#字符串
					if caseSen:#大小写敏感
						if file_ext[1] == extent:
							allPath.append(file_path)
					else:#大小写不敏感
						if file_ext[1].lower() == extent.lower():
							allPath.append(file_path)
				elif type(extent) in (tuple, list, set):#常见系列数据
					if caseSen:#大小写敏感
						if file_ext[1] in extent:
							allPath.append(file_path)
					else:#大小写不敏感
						for _ext in extent:
							if file_ext[1].lower() == _ext.lower():
								allPath.append(file_path)
								break
		return allPath
	@staticmethod
	def sepClass(root_path, dic):#分类器
		rp = str(root_path).replace("\"", "").replace("\'", "").replace("\\", "/")#去掉引号并将目录分层符泛化
		if rp[-1] == "/" or rp[-1] == "\\":
			rp = rp[:-1]
		if not os.path.exists(rp):#根目录不存在
			return (False, "No such file or directory")
		rp += "/"
		errorDict = {}
		try:
			for folder in list(dic.keys()):
				if not os.path.exists(rp + folder):
					os.mkdir(rp + folder)
				for file in dic[folder]:
					try:
						shutil.move(rp + file, rp + folder)
					except Exception as ee:
						errorDict.setdefault(rp + file, ee)
			if len(errorDict) == 0:
				return True
			else:
				return (True, errorDict)
		except Exception as e:
			return (False, e)
	@staticmethod
	def changeGlobal():#切换清华源
		os.system("pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple")
		os.system("pip config set global.timeout 120")


from subprocess import call
import time
class PyTools:
	@staticmethod
	def showAll():#显示所有第三方 python 库
		with os.popen("pip list") as hdle:
			dists = hdle.read()
		print(dists)
	@staticmethod
	def outdateAll():#显示所有可升级的第三方 python 库
		os.system("pip list --outdate")
	@staticmethod
	def updateAll():#升级所有第三方 python 库
		call("python -m pip install --upgrade pip")
		with os.popen("pip list") as hdle:
			dists = hdle.read()
		package_name = [dist.split(" ")[0] for dist in dists.split("\n")][2:-1]
		print(package_name)
		for dist in package_name:
			call("pip install --upgrade " + " ".join(package_mame), shell = True)
	@staticmethod
	def debug():
		def _debug(tmp = None):
			tmp = input(">>> ") if tmp is None else tmp + "\n" + input("... ")
			try:
				exec(tmp)
			except Exception as e:
				if str(e).startswith("unexpected EOF while parsing (<string>, line"):
					_debug(tmp = tmp)
				else:
					print(e)
		while True:
			_debug()
	@staticmethod
	def getTxt(filepath, index = 0) -> str: # get .txt content
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
	@staticmethod
	def press_any_key_to_continue() -> bytes:
		while kbhit():
			getch()
		return getch()
	@staticmethod
	def preExit(countdownTime = 5) -> None:
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





if __name__ == "__main__":
	PyTools.debug()