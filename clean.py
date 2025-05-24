from sys import argv, exit
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


def main():
	delims = "\\textcolor{red}{"
	isDebug = True
	try:
		with open(argv[1], "r", encoding = "utf-8") as f:
			content = f.read()
	except:
		return EOF
	tokens = content.split(delims)
	for i in range(1, len(tokens)):
		token = tokens[i]
		if isDebug:
			print(token)
		cnt, j, length = 1, 0, len(token)
		while j < length:
			if token[j] == "{":
				cnt += 1
			elif token[j] == "}":
				cnt -= 1
				if cnt <= 0:
					tokens[i] = token[:j] + token[j + 1:]
					break
			elif token[j] == "\\":
				j += 1
			j += 1
		else:
			return EXIT_FAILURE
		if isDebug:
			print("Removed token[{0}]. ".format(j))
			print(tokens[i])
			try:
				if input("isDebug = ").upper() in ("0", "FALSE", "N", "NO"):
					isDebug = False
			except:
				return EOF
	try:
		with open(argv[2], "w", encoding = "utf-8") as f:
			f.write("".join(tokens))
		print("Successfully wrote to \"{0}\". ".format(argv[2]))
		return EXIT_SUCCESS
	except:
		return EOF



if "__main__" == __name__:
	exit(main())