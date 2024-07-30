# checkCite

This is a set of small toolkits that I use most. 

## latexChecker.py

This script is used to check the LaTeX files, supporting complex structures. 

## checkCite.py

This script is used to check the LaTeX files. 

This script will no longer be under maintenance. 

Please use the LaTeX checker. 

## WinOS.py

This script is a tool used very frequently on the Windows platform. 

## compareDirectory.py

This script is used to compare two directories. 

1) It skips some unsynchronized folders through the hierarchical traversal method to avoid traversing the contents of unsynchronized folders to achieve a pruning effect (it takes me an entire night to finish). 
   
2) Referring to an ACM expert's algorithm for comparing version numbers, this script uses the ``list. pop (0)`` in the middle procedure and the ``not any`` in the end procedure to accelerate the operation (it takes me about ten minutes to finish). 

3) Report relative paths about added, removed, conflicted, erroneous, and different items. (It takes me about a minute to finish). 

4) This script compares file contents using SHA256 hash values instead of comparing each byte to speed up. Although both methods require traversing entire files, the method of using hash functions saves time by reducing the number of ``if`` executions (it takes me a minute to finish). 

5) This script provides a multi-level progress report structure (it seems that this feature takes me the same amount of time as the sum of the previous four points). 
