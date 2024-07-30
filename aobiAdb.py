import os
from sys import exit
from random import uniform
from re import findall
from time import localtime, sleep
try:
	from numpy import array
	from cv2 import CHAIN_APPROX_SIMPLE, COLOR_RGB2GRAY, contourArea, cvtColor, findContours, minEnclosingCircle, RETR_EXTERNAL, THRESH_BINARY, threshold
	from uiautomator2 import connect_usb
except Exception as e:
	print("Failed importing related libraries. Details are as follows. \n{0}".format(e))
	print("Please press the enter key to exit. ")
	input()
	exit(-1)
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class AndroidController:
	def __init__(self:object, isAlert:bool = True, stateDict = {-1:"[X] ", 0:"[I] ", 1:"[V] "}) -> None:
		self.isAlert = isAlert
		self.stateDict = stateDict
	def initAdb(self:object) -> bool:
		try:
			self.device = connect_usb()
			self.printWithState("Connect to the device successfully: {0}. ".format(self.device.info), 1)
			return True
		except Exception as e:
			self.printWithState("Error connecting to the device. Details are as follows. \n{0}".format(e), -1)
			return False
	
	# Basic API #
	def captureScreen(self:object, targetFilePath:str = None) -> array:
		if targetFilePath:
			try:
				self.device.screenshot(targetFilePath)
				self.printWithState("Capture the screenshot to \"{0}\" successfully. ".format(targetFilePath), 1)
				return True
			except Exception as e:
				self.printWithState("Error capturing the screenshot to \"{0}\". Details are as follows. \n{1}".format(targetFilePath, e), -1)
				return False
		else:
			try:
				image = self.device.screenshot()
				self.printWithState("Capture the screenshot successfully. ", 1)
				return array(image)
			except Exception as e:
				self.printWithState("Error capturing the screenshot. Details are as follows. \n{0}".format(e), -1)
				return False
	def imitateSingleClickCoordinate(self:object, xInput:int, yInput:int) -> str:
		if isinstance(xInput, int) and isinstance(yInput, int):
			x = xInput % self.device.info["displayWidth"]
			y = yInput % self.device.info["displayHeight"]
			try:
				self.device.click(x, y)
				self.printWithState("Click on the coordinate ({0}, {1}) successfully. ".format(x, y), 1)
				return True
			except Exception as e:
				self.printWithState("Failed clicking on the coordinate ({0}, {1}). ".format(x, y), -1)
				return False
		else:
			return False
	def imitateSingleClickRatio(self:object, xRatio:float, yRatio:float) -> str:
		if isinstance(xRatio, float) and isinstance(yRatio, float):
			x = int(xRatio * self.device.info["displayWidth"]) % self.device.info["displayWidth"]
			y = int(yRatio * self.device.info["displayHeight"]) % self.device.info["displayHeight"]
			try:
				self.device.click(x, y)
				self.printWithState("Click on the coordinate ({0}, {1}) successfully. ".format(x, y), 1)
				return True
			except Exception as e:
				self.printWithState("Failed clicking on the coordinate ({0}, {1}). ".format(x, y), -1)
				return False
		else:
			return False
	def pause(self:object, *pars:list) -> bool:
		if len(pars) == 1:
			if isinstance(pars[0], (float, int)) and pars[0] >= 0:
				t = pars[0]
			else:
				return False
		elif len(pars) == 2:
			if isinstance(par[0], (float, int)) and isinstance(par[1], (float, int)) and 0 <= pars[0] <= pars[1]:
				t = uniform(pars[0], pars[1])
			else:
				return False
		elif len(pars) == 3:
			if all([isinstance(par, (float, int)) for par in pars]) and 0 <= pars[0] + pars[1] <= pars[0] + pars[2]:
				t = uniform(pars[0] + pars[1], pars[0] + pars[2])
			else:
				return False
		else:
			return False
		try:
			self.printWithState("Sleep for {0} second(s). ".format(t), 1)
			sleep(t)
			return True
		except KeyboardInterrupt:
			return False
	
	# Aobi API #
	def aobiRobTradeBlind(self:object, row:int = 0, column:int = 0, loopCounter:int = None) -> int:
		if row in (0, 1) and column in (0, 1, 2, 3, 4):
			x = 0.375 + 0.100 * row
			y = 0.425
			cnt = 0
			try:
				while (cnt < loopCounter if isinstance(loopCounter, int) else True):
					self.imitateSingleClickRatio(x, y)
					self.pause(0.005, -0.001, 0.001)
					self.imitateSingleClickRatio(0.325, 0.550)
					self.pause(0.005, -0.001, 0.001)
					self.imitateSingleClickRatio(0.600, 0.675)
					self.pause(0.005, -0.001, 0.001)
					self.imitateSingleClickRatio(0.750, 0.150)
					self.pause(0.005, -0.001, 0.001)
			except KeyboardInterrupt:
				self.printWithState("The process is interrupted by users. ", 0)
			return cnt
		else:
			self.printWithState("Values of row and column are invalid. ", -1)
			return -1
	def aobiTimeCounter(self:object, toolID:int, loopCounter:int = None) -> int:
		if toolID in list(range(10)):
			x = 0.075 * (toolID + 1)
		else:
			self.printWithState("The tool ID should be an integer within $[0, 10)$. ", -1)
			return -1
		y = 0.925
		cnt = 1
		self.imitateSingleClickRatio(0.375, 0.925)
		self.pause(0.05, -0.01, 0.01)
		self.imitateSingleClickRatio(0.300, 0.825)
		self.pause(0.05, -0.01, 0.01)
		self.imitateSingleClickRatio(x, y)
		self.pause(0.05, -0.01, 0.01)
		try:
			while (cnt < loopCounter if isinstance(loopCounter, int) else True):
				self.imitateSingleClickRatio(0.375, 0.925)
				self.pause(0.05, -0.01, 0.01)
				self.imitateSingleClickRatio(x, y)
				self.pause(0.05, -0.01, 0.01)
		except KeyboardInterrupt:
			self.printWithState("The process is interrupted by users. ", 0)
		self.printWithState("Finish clicking for {0} times. ".format(cnt), 1)
		return cnt
	def aobiMusicCar(self:object, ringCount:int) -> int:
		# Locate white rings #
		img = self.captureScreen()
		grayImg = cvtColor(img, COLOR_RGB2GRAY)
		_, binaryImg = threshold(grayImg, 254, 255, THRESH_BINARY)
		contours, _ = findContours(binaryImg, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
		minArea = 1000
		contours = [cnt for cnt in contours if contourArea(cnt) > minArea]
		circles = [minEnclosingCircle(cnt) for cnt in contours]
		centers = [(int(x), int(y)) for (x, y), _ in circles]
		centers.sort(key = lambda x:x[0])
		if len(centers) in (4, 6, 8):
			self.printWithState("{0} rings are retrieved: {1}. ".format(len(centers), centers), 1)
		else:
			self.printWithState("The count of rings should be 4, 6, or 8. ", -1)
			return -1
		
		while True:
			for center in centers:
				self.device.click(center[0], center[1])
		return 0
	
	# Interact API #
	def printWithState(self:object, msg:str, state:int) -> bool:
		if self.isAlert and state in self.stateDict:
			print("{0}{1}".format(self.stateDict[state], msg.replace("\n", "\n\t")))
			return True
		else:
			return False
	def interact(self:object) -> None:
		print("*** Enter Interact Mode ***")
		while True:
			try:
				toExec = input(">>> ")
				if toExec in ("break", "exit", "quit"):
					break
				else:
					exec(toExec)
			except Exception as e:
				print(e)
		print("*** Exit Interact Mode ***")

def main() -> int:
	adbCtrl = AndroidController()
	if not adbCtrl.initAdb():
		print("*** No active devices are connected. Please press the enter key to exit. ***")
		input()
		return EXIT_FAILURE
	lt = localtime()
	ltStr = "{0:0>4}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}".format(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
	print("*** The program starts at {0}. Please press the enter key to exit. ***".format(ltStr))
	adbCtrl.captureScreen(ltStr + ".png")
	adbCtrl.aobiRobTradeBlind()
	#adbCtrl.aobiTimeCounter(4)
	#adbCtrl.aobiMusicCar(4)
	adbCtrl.interact()
	lt = localtime()
	ltStr = "{0:0>4}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}".format(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
	adbCtrl.captureScreen(ltStr + ".png")
	print("*** The program finished at {0}. Please press the enter key to exit. ***".format(ltStr))
	input()
	return EXIT_SUCCESS



if __name__ == "__main__":
	exit(main())