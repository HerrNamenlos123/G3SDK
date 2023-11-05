import bvhio
import json

with open('xmot.json', 'r') as f:
    file = f.read()
    data = json.loads(file)

# First build a new, cleaner asset array

assets = []

# We want this frametime and that many frames
frametime = 1/25
frameCount = 56

for i in range(len(data['assets'])):
    asset = data['assets'][i]

    if asset["type"] == "ANIMATION_FRAMES":      # The next asset is a frame asset, so we merge it into the current asset
        if asset["frame_type"] == "LR":          # Rotation asset
            assets[-1]["rotation"] = asset
        elif asset["frame_type"] == "LP":        # Position asset
            assets[-1]["position"] = asset
    else: # A normal vector type
        assets.append(asset)

def findTwoKeyframesToInterpolate(frames, time):
    lower = None
    upper = frames[0]       # The first keyframe is the upper one

    index = 1
    while time > upper[0] and index < len(frames):  # Find the first keyframe that is larger than the time
        lower = upper
        upper = frames[index]
        index += 1

    if lower is None:       # If we are at the beginning of the animation, we just take the first keyframe
        lower = upper

    if time > upper[0]:     # If we are at the end of the animation, we just take the last keyframe
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
for asset in assets:
    if "rotation" in asset:                     # Interpolate rotation keyframes
        asset["rotation"]["keyframes"] = []

        # We do it for every keyframe we want to have
        for i in range(frameCount):
            time = i * frametime
            
            # Find the two keyframes we want to interpolate between
            lower, upper = findTwoKeyframesToInterpolate(asset["rotation"]["frames"], time)

            x = map(time, lower[0], upper[0], lower[1], upper[1])
            y = map(time, lower[0], upper[0], lower[2], upper[2])
            z = map(time, lower[0], upper[0], lower[3], upper[3])
            w = map(time, lower[0], upper[0], lower[4], upper[4])

            asset["rotation"]["keyframes"].append([time, x, y, z, w])       # CHANGE THIS

            if "Arm_Arm_2" in asset["label"] and i % 18 == 0:
                print(f"{asset['label']} {time}    [{i}]   ---->>   {x} {y} {z} {w}")

    if "position" in asset:                     # Interpolate position keyframes
        asset["position"]["keyframes"] = []

        # We do it for every keyframe we want to have
        for i in range(frameCount):
            time = i * frametime
            
            # Find the two keyframes we want to interpolate between
            lower, upper = findTwoKeyframesToInterpolate(asset["position"]["frames"], time)

            x = map(time, lower[0], upper[0], lower[1], upper[1])
            y = map(time, lower[0], upper[0], lower[2], upper[2])
            z = map(time, lower[0], upper[0], lower[3], upper[3])

            asset["position"]["keyframes"].append([time, x, y, z])


# Loads the file into a deserialized tree structure.
bvh = bvhio.readAsBvh('untitled.bvh')
bvh.FrameTime = frametime
bvh.FrameCount = frameCount

for joint, index, depth in bvh.Root.layout():

    asset = None
    for i in range(len(assets)):
        if not "label" in assets[i]:
            continue
        if assets[i]["label"] == joint.Name:
            asset = assets[i]
            break
    if asset == None:
        continue

    if "rotation" in asset:
        for frame in range(frameCount):
            joint.Keyframes[frame].Rotation = asset["rotation"]["keyframes"][frame][1:]
    # if "position" in asset:
    #     for frame in range(frameCount):
    #         joint.Keyframes[frame].Position = asset["position"]["keyframes"][frame][1:]
    #         print(joint.Keyframes[frame].Position)

    while len(joint.Keyframes) > frameCount:
        joint.Keyframes.pop()

for a in assets:
    if "_Leg_Hip_1" in a["label"]:
        print(json.dumps(a, indent=4))

# Stores the modified bvh
bvhio.writeBvh('untitled-modified.bvh', bvh, percision=6)
