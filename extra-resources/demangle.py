import sys
import os
import asyncio
import time
import random

numLinesTotal = 0
numLines = 0

async def demangle(symbol) -> str:
    output = os.popen("undname \"" + symbol + "\"").readlines()
    for line in output:
        if line.find("is :- \"") != -1:
            return line[7:-1]
    return symbol

async def provide_demangling(line) -> str:
    groups = " ".join(line.split(" ")).split()

    symbol = groups[-1]
    demangled = await demangle(symbol)
    return line[0:-1] + "    ==>   " + demangled + "\n"


async def process(line) -> str:
    groups = " ".join(line.split(" ")).split()

    # If the line starts with a tab and a bracket and has not more than 3 character groups 
    if len(line) > 2:
        if line[0] == '\t' and line[1] == '[' and len(groups) <= 3:
            return await provide_demangling(line)
    
    # Otherwise, if the line has in total 3 groups of characters and both first are hex numbers
    if len(groups) == 3:
        try:
            int(groups[0], 16)
            int(groups[1], 16)
            return await provide_demangling(line)
        except:
            pass

    return line

async def process_line(line):
    global numLines
    global numLinesTotal

    result = await process(line)
    numLines += 1
    print("Progress: " + str(numLines) + "/" + str(numLinesTotal), end="\r")
    return result

async def main():
    global numLinesTotal

    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
        numLinesTotal = len(lines)

        # output = ""
        # for line in lines:
        #     result = await process(line)
        #     print(result, end="")
        #     output += result
        output = await asyncio.gather(*(process_line(line) for line in lines))
        output = "".join(output)

        with (open(sys.argv[2], 'w')) as f:
            f.write(output)

if __name__ == "__main__":
    print(f"{sys.argv[1]} -> {sys.argv[2]}")
    asyncio.run(main())

# cls && python C:\Users\zachs\Projects\G3Dll\demangle.py "C:\Program Files (x86)\Steam\steamapps\common\Gothic 3\SCM.dll.txt" "C:\Users\zachs\Projects\G3Dll\SCM.dll.txt"