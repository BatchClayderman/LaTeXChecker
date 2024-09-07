# checkCite

This is a set of small toolkits that I use most. 

## adjustCalendar.py

This script can help handle some calendar issues in bulk. 

It can be used to remove online course arrangements from the calendar. 

## aobiAdb.py

This script is used for Android automatic control based on uiautomator2. 

Currently, this script is no longer under maintenance due to some limitations. 

This script cannot follow the Android screen in real time. 

No multiple points are supported while I expect to have ``p1, p2 = Point(), Point()``, ``p1.click(x, y)``, ``p2.wrap(x1, y1, x2, y2)``, and ``Point.commit(p1, p2)``. 

## checkCite.py

This script is used to check the LaTeX files without understanding the LaTeX files. 

This script will no longer be under maintenance. 

Please use the later versions. 

## checkLaTeX.py

This script is used to check the LaTeX files, supporting complex structures. 

### v1.0

Please refer to ``checkCite.py``. 

### v1.3

In this version, some functions are accomplished. 

However, it is not an optimal way to handle LaTeX checking tasks. 

This version of the script cannot run. It acts as a thought provider here. 

### v1.5

The ``Pointer`` and the ``Structure`` are separated. 

Compared with ``v1.3``, the codes are more readable and the thought is more feasible. 

This version of the script cannot run. It acts as a thought provider here. 

### v2.0

This is the initial version of ``checkLaTeX.py`` that supports complex structures with understanding the LaTeX files. 

## WinOS.py

This script is a tool used very frequently on the Windows platform. 

## compareDirectory.py

This script is used to compare two directories. 

1) It skips some unsynchronized folders through the hierarchical traversal method to avoid traversing the contents of unsynchronized folders to achieve a pruning effect (it takes me an entire night to finish). 
   
2) Referring to an ACM expert's algorithm for comparing version numbers, this script uses the ``list. pop (0)`` in the middle procedure and the ``not any`` in the end procedure to accelerate the operation (it takes me about ten minutes to finish). 

3) Report relative paths about added, removed, conflicted, erroneous, and different items (it takes me about a minute to finish). 

4) This script compares file contents using SHA256 hash values instead of comparing each byte to speed up. Although both methods require traversing entire files, the method of using hash functions saves time by reducing the number of ``if`` executions (it takes me a minute to finish). 

5) This script provides a multi-level progress report structure (it seems that this feature takes me the same amount of time as the sum of the previous four points).

### v1.0

The initial version of ``compareDirectory.py``. 

It can run on Linux but does not support Linux totally. 

### v2.0

The comparison for Linux operating systems is supported. 

Each soft link is regarded as a normal file during the comparison. 

The situation that the operating system is case sensitive but the switch of case sensitive is turned off manually is considered. 

### v3.0

The script is reconstructed using multiple classes. 
