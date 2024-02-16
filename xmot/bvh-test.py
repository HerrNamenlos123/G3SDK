from math import sin
import bvhio # pip install bvhio (THIS NEEDS PYTHON 3.11!!!!!)
# import bvh # pip install bvh # This is wrong!!! It can only read, but not write!!!
import json
import glm

with open('xmot.json', 'r') as f:
    file = f.read()
    data = json.loads(file)

# First build a new, cleaner asset array

sections = []

# We want this frametime and that many frames
frametime = 1/25
frameCount = 21

storedRotation = None
storedPosition = None
for i in range(len(data['content']['lma_file']['chunks'])):
    chunk = data['content']['lma_file']['chunks'][i]

    swapOrder = False
    if not swapOrder:
        if chunk["chunk_type"] == "Animation":      # This asset is a frame asset, so we merge it into the last asset, which was a MotionPart
            if chunk["chunk_content"]["frame_type"] == "LR":          # Rotation asset
                sections[-1]["rotation"] = chunk
            elif chunk["chunk_content"]["frame_type"] == "LP":        # Position asset
                sections[-1]["position"] = chunk
        else: # A MotionPart
            sections.append({ "chunk": chunk, "rotation": None, "position": None })
    # else:
    #     if chunk["chunk_id"] == 2:      # The next asset is a frame asset, so we merge it into the current asset
    #         if chunk["chunk_content"]["frame_type"] == "LR":          # Rotation asset
    #             storedRotation = chunk
    #         elif chunk["chunk_content"]["frame_type"] == "LP":        # Position asset
    #             storedPosition = chunk
    #     else: # A normal vector type
    #         assets.append(chunk)
    #         if storedRotation != None:
    #             assets[-1]["rotation"] = storedRotation
    #         if storedPosition != None:
    #             assets[-1]["position"] = storedPosition
    #         storedRotation = None
    #         storedPosition = None

def findTwoKeyframesToInterpolate(frames, time):
    lower = None
    upper = frames[0]       # The first keyframe is the upper one

    index = 1
    while time > upper["time"] and index < len(frames):  # Find the first keyframe that is larger than the time
        lower = upper
        upper = frames[index]
        index += 1

    if lower is None:       # If we are at the beginning of the animation, we just take the first keyframe
        lower = upper

    if time > upper["time"]:     # If we are at the end of the animation, we just take the last keyframe
        lower = upper

    return lower, upper

def map(value, inMin, inMax, outMin, outMax):
    if value < inMin:
        return outMin
    if value > inMax:
        return outMax
    if inMin == inMax:
        return outMin
    return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

# Now we interpolate keyframes
for section in sections:

    if section["rotation"]:                     # Interpolate rotation keyframes
        section["rotation"]["new_keyframes"] = []

        # We do it for every keyframe we want to have
        for i in range(frameCount):
            time = i * frametime
            
            # Find the two keyframes we want to interpolate between
            lower, upper = findTwoKeyframesToInterpolate(section["rotation"]["chunk_content"]["keyframes"], time)

            x = map(time, lower["time"], upper["time"], lower["rotation"]["x"], upper["rotation"]["x"])
            y = map(time, lower["time"], upper["time"], lower["rotation"]["y"], upper["rotation"]["y"])
            z = map(time, lower["time"], upper["time"], lower["rotation"]["z"], upper["rotation"]["z"])
            w = map(time, lower["time"], upper["time"], lower["rotation"]["w"], upper["rotation"]["w"])

            x = section["chunk"]["chunk_content"]["rotation"][0]
            y = section["chunk"]["chunk_content"]["rotation"][1]
            z = section["chunk"]["chunk_content"]["rotation"][2]
            w = section["chunk"]["chunk_content"]["rotation"][3]

            x = 0.9950372
            y = 0
            z = 0
            w = 0.0995037

            # x = sin(3 * time)*3

            # section["rotation"]["new_keyframes"].append([time, w, z, y, x])       # CHANGE THIS
            # section["rotation"]["new_keyframes"].append([time, y, x, z, -w])       # CHANGE THIS
            section["rotation"]["new_keyframes"].append([time, x, y, z, w])       # CHANGE THIS

            # if "Hero_Left_Leg_Hip_1" in asset["label"]:
            #     print(f"Hero_Left_Leg_Hip_1: {x} {y} {z} {w}")
            # if "Arm_Arm_2" in asset["label"] and i % 18 == 0:
            #     print(f"{asset['label']} {time}    [{i}]   ---->>   {x} {y} {z} {w}")

    if section["position"]:                     # Interpolate position keyframes
        section["position"]["new_keyframes"] = []

        # We do it for every keyframe we want to have
        for i in range(frameCount):
            time = i * frametime
            
            # Find the two keyframes we want to interpolate between
            lower, upper = findTwoKeyframesToInterpolate(section["position"]["chunk_content"]["keyframes"], time)

            x = map(time, lower["time"], upper["time"], lower["position"]["x"], upper["position"]["x"])
            y = map(time, lower["time"], upper["time"], lower["position"]["y"], upper["position"]["y"])
            z = map(time, lower["time"], upper["time"], lower["position"]["z"], upper["position"]["z"])

            section["position"]["new_keyframes"].append([time, x / 1000, y / 1000, z / 1000])






# Loads the file into a deserialized tree structure.
bvh = bvhio.readAsBvh('untitled.bvh')
bvh.FrameTime = frametime
bvh.FrameCount = frameCount

for joint, index, depth in bvh.Root.layout():

    # joint.EndSite.x = 0
    # joint.EndSite.y = 0
    # joint.EndSite.z = 0

    # if (joint.Name == "Hero_Spine_Spine_1"):
    #     print(joint.__dict__)

    while len(joint.Keyframes) > frameCount:
        joint.Keyframes.pop()

    section = None
    for s in sections:
        if s["chunk"]["chunk_content"]["label"] == joint.Name:
            section = s
            break

    if section == None:
        continue

    if section["rotation"]:
        for frame in range(frameCount):
            rot = section["rotation"]["new_keyframes"][frame][1:]
            quat = glm.quat(rot[3], rot[0], rot[1], rot[2])
            joint.Keyframes[frame].Rotation = quat 
            print(bvhio.Euler.fromQuatTo(joint.Keyframes[frame].Rotation))
    if section["position"]:
        for frame in range(frameCount):
            joint.Keyframes[frame].Position = section["position"]["new_keyframes"][frame][1:]
            # print(joint.Keyframes[frame].Position)

# for a in assets:
#     if "_Leg_Hip_1" in a["label"]:
#         print(json.dumps(a, indent=4))

# Stores the modified bvh
bvhio.writeBvh('untitled-modified.bvh', bvh, percision=6)

