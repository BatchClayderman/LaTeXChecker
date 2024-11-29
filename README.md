# LaTeXChecker

This is an implementation for checking LaTeX source files in the mode of multiple typesetting styles for one manuscript. 

## checkCite.py (LaTeXChecker v1.0)

This script is used to check the LaTeX files without understanding them. 

This script will no longer be under maintenance. 

Please use the later versions. 

## checkLaTeX.py (LaTeXChecker v1.1 - v1.9)

This script is used to check the LaTeX files, supporting complex structures. 

Here are some incomplete implementations based on baseline ideas. 

### v1.3

In this version, some functions are accomplished. 

However, it is not an optimal way to handle LaTeX checking tasks. 

This version of the script cannot run. It acts as a thought provider here. 

### v1.5

The ``Pointer`` and the ``Structure`` are separated. 

Compared with ``v1.3``, the codes are more readable and the thought is more feasible. 

This version of the script cannot run. It acts as a thought provider here. 

### v1.7

This is the last version before v2.0, which leads to the mature structure-building idea. 

The active mode is used in the parsing with the character-by-character reading. 

## LaTeXChecker (LaTeXChecker v2.0 - v2.9)

Start to be a mature checker with file tracking and structure recognition. 

### v2.0

This is the initial version of ``LaTeXChecker.py`` that supports complex structures with understanding the LaTeX files. 

### v2.1

Interaction is accomplished in this version. 

Initial support to command definitions is added. 

More complex situations are considered during the resolution. 

### v2.3 (20241111)

Add support for label and citation checking, covering parts of the functions in LaTeXChecker v1.0. 

### v2.4 (20241112)

Cover all the checking functions in LaTeXChecker v1.0. 

Add support to check whether all the structures are closed. 

Fix bugs in the stack of the pointer. 

Support more commands. 

### v2.5 (20241116)

Adjust the style of the connection lines. 

Fix some bugs. 

Change the behaviors for ``.gv`` files. Revise the extension ``.gz`` to ``.gv``. 

Change the option recognition mode to the non-case-sensitive one. 

### v2.6 (20241124)

Fix the bug of using ``\end{document}`` to end sections and subsections. 

Print the information on the leaving structure node mentioned above for debugging information via a queue. 

Add support for newly defined environments. 

### v2.7 (20241130)

Formalize the main body ``\xxx{yyy}`` recognition. 
