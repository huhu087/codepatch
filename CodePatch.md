# Introduction #

**MERGE CODE MODE**

Merging is a common task for developers who rely on third-party code in their own projects.
Imagine that you are using some library «Lib version 1» in your project. Say you’ve made some changes to this library in order to meet specific needs of your project. Let’s call modified version of the library «Lib version 1 my». And now library provider is releasing «Lib version 2» - a new version of the library with some important updates and bug fixes. You also want to update your code to the newer version but since you’ve made your changes to the library code by yourself this process won’t be trivial.

Hopefully _CodePatch_ is designed precisely to handle such kinds of tasks.

To start you have to provide _CodePatch_ with following:

  * “My path” – a path where you have your modified code («Lib version 1 my» for our example),
  * “Base path” – a path with original unmodified version of the code from the provider («Lib version 1»),
  * “Their path” – a new version of code from the third-party provider («Lib version 1»),
  * “Result path” – a path where you want result files to be placed.

_CodePatch_ will walk recursively through the sub-folders and check every file it will find: binary or text.
_CodePatch_ is using three-way merge (also know as merging from a common ancestor) algorithm to merge text files. This algorithm considers changes made by you (from “My path”) and changes released by third-party provider (“Their path”) relative to the original version (“Base path”).

_CodePatch_ can call external diff program to allow you manually resolve merging conflicts in text files. We recommend you a freeware program <a href='http://www.winmerge.org'>WinMerge</a> for this purpose. You have to specify full path to merge program in "Program path" field and check "Use external program to resolve conflicts" flag.

For binaries CodePatch will use a modified file from the “My path” or “Their path” if there is only one file that has differences relative to the one from “Base path”, otherwise it will report a conflict.

After the merge is done _CodePatch_ writes statistics of performed actions into the "_codePatch.txt" from the “Result path”._

**CREATE PATCH MODE**

Create Patch mode should be used whenever you want to find out which files from your working folder specified by “My path” have been modified relative to files in the “Base path” folder. In this mode _CodePatch_ checks files and put the modified ones into the "Result path" folder.


**ACKNOWLEDGES**

CodePatch is written in <a href='http://www.python.org'>Python v2.6</a>


Windows executable file was built with <a href='http://www.py2exe.org'> py2exe </a>


CodePatch uses another project hosted on google - <a href='http://code.google.com/p/pymerge3/'> pymerge3</a>  library to merge two text files that have a common ancestor into a single file.