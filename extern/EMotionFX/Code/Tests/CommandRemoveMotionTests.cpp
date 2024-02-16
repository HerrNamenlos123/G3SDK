/*
* All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
* its licensors.
*
* For complete copyright and license terms please see the LICENSE at the root of this
* distribution (the "License"). All use of this software is governed by the License,
* or, if provided, by the license below or the license accompanying this file. Do not
* remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*
*/

#include <Tests/UI/CommandRunnerFixture.h>

#include <EMotionFX/CommandSystem/Source/CommandManager.h>
#include <EMotionFX/Tools/EMotionStudio/EMStudioSDK/Source/EMStudioManager.h>
#include <EMotionFX/Tools/EMotionStudio/Plugins/StandardPlugins/Source/MotionSetsWindow/MotionSetsWindowPlugin.h>

namespace EMotionFX
{
    class RemoveMotionDeselectsThatMotion
        : public CommandRunnerFixtureBase
    {
    };

    TEST_F(RemoveMotionDeselectsThatMotion, ExecuteCommands)
    {
        ExecuteCommands({
           "CreateMotionSet -name MotionSet0",
        });

        // Select the motion set (there is no command for this)
        EMStudio::MotionSetsWindowPlugin* motionSetsWindowPlugin = static_cast<EMStudio::MotionSetsWindowPlugin*>(EMStudio::GetPluginManager()->FindActivePlugin(EMStudio::MotionSetsWindowPlugin::CLASS_ID));
        ASSERT_TRUE(motionSetsWindowPlugin) << "Motion Window plugin not loaded";

        EMotionFX::MotionSet* motionSet = EMotionFX::GetMotionManager().FindMotionSetByID(0);
        ASSERT_TRUE(motionSet) << "Motion set with id 0 does not exist";
        motionSetsWindowPlugin->SetSelectedSet(motionSet);

        const std::string filename = "@devroot@/Gems/EMotionFX/Code/Tests/TestAssets/Rin/rin_idle.motion";
        ExecuteCommands({
            "ImportMotion -filename " + filename,
            "MotionSetAddMotion -motionSetID 0 -motionFilenamesAndIds " + filename + ";rin_idle",
            "Select -motionIndex 0",
        });
        EXPECT_TRUE(CommandSystem::GetCommandManager()->GetCurrentSelection().GetSingleMotion());

        ExecuteCommands({
            "MotionSetRemoveMotion -motionSetID 0 -motionIds rin_idle",
            "RemoveMotion -filename " + filename,
        });
        EXPECT_FALSE(CommandSystem::GetCommandManager()->GetCurrentSelection().GetSingleMotion());
    }
} // end namespace EMotionFX
