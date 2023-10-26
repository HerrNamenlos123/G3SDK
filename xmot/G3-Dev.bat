@echo off

echo Starting VSCode...
call code .
echo Starting VSCode... Done

echo Starting G3Dll VSCode...
call code "c:\Users\zachs\Projects\G3SDK"
echo Starting G3Dll VSCode... Done

echo Starting gothic3sdk VSCode...
call code "c:\Users\zachs\Projects\gothic3sdk"
echo Starting gothic3sdk VSCode... Done

echo Starting Ghidra...
call ghidra\ghidra\ghidraRun.bat
echo Starting Ghidra... Done

echo Starting Visual Studio...
start c:\Users\zachs\Projects\G3SDK\build\G3Dll.sln
echo Starting Visual Studio... Done

exit