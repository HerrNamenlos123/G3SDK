# G3SDK

This is an experimental project for tinkering with the Genome Engine by Piranha Bytes, used in Gothic 3. The goal was to hook into the Gothic 3 Engine with the intention of fixing bugs and allowing more modifications.

This repository contains some of my attempts, with some successes and failures. It is not meant to do something specific, but you can use it as a starter if you want to get into it.

Some important links:
 - https://github.com/georgeto/gothic3sdk
 - https://www.baltr.de/rimy3d/
 - https://www.baltr.de/rimy3d/help/en/xcmsh.htm
 - https://forum.xentax.com/viewtopic.php?t=9369

I copied all the files into this repository, so many paths in batch scripts will be wrong and you will have to adjust them.

## The C++ project 

The C++ project builds a DLL that is loaded into Gothic by attaching the G3Loader DLL to `Engine.dll`. Engine.dll, because Gothic.exe was already hooked by some other system patches and it conflicted. See `G3Dll.bat`, `G3DllUndo.bat`. A console will pop up when you start Gothic now.

Then, a second C++ DLL is compiled, which is dynamically loaded by the first when you press F2. This means you can hot-reload your C++ DLL while Gothic is running. Be aware that many function calls are detoured and routed through the DLL, and the DLL will hook and unhook these functions. If by chance you unload the DLL using F3, while the engine is inside a detoured function, Gothic will crash. Depending on which functions you hook into and how much time is spent in your detours, it is more likely or less likely to crash. This is simply meant to speed up development time.

Microsoft Detours library is used to redirect any function call between DLL boundaries into a user defined function, and then you can either redirect it back into the original function (which means you do the default plus something additional), or you simply return in your detour, which means you essentially completely skip or disable an engine function. Every function that has an exported function signature can be detoured.

## Extra-resources

`extra-resources` contains disassembled versions of the Gothic DLLs, there you see all function signatures of all DLLs that are imported and exported. A python program was used to demangle them using visual studio tools.

You will need these function signatures in order to hook into these functions in C++.

## Other library

Also take a look at https://github.com/HerrNamenlos123/GenomeScript. It has the same goal of quickly iterating with function detouring, but it implements it via hot-reloaded lua scripts and it is a much more elaborate attempt that got further than this repository.

## Ghidra

Here is also a `ghidra` subfolder, which contains a Ghidra project. I put in a lot of effort to decompile the original Gothic 3 DLLs. My main target were classes such as PS_Animation and anything animation related, as well as a bit of the entity component system and general data types such as BCString.

## xmot file format

One of many goals was to reverse engineer the .xmot file format. All other file formats of Gothic have already been reverse engineered. Just .xmot not, which prevents modders from changing animations, which prevents a whole bunch of bug fixes.

This attempt is also here, so make sure to look into the `xmot` folder. There is a python file which is a file converter, and it can half-way decode a .xmot file, and then re-encode it back. This means it might be possible to change values. However, only parts of the file are decoded yet and many parts of the file format are still black boxes.

https://web.archive.org/web/20230513172524/https://forum.xentax.com/viewtopic.php?t=9369 is very valuable.
It is saved locally at [Animation researching - XenTaX](xmot/animation_researching_xentax.htm).

## You need help?

As said, I copied all files into this repository and did not do any more work afterwards. If you need any help getting the project to compile, feel free to contact me at herrnamenlos123@gmail.com or in an issue. 

I really wanted to get into the engine in order to make Gothic what it should have been, but sadly my time was prioritized differently at some point. But if you ask me I will gladly try to get the project to work, for now it is just a silent reference.
