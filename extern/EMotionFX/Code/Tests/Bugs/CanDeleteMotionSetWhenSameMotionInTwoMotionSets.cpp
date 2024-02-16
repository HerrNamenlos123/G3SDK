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

#include <EMotionFX/Tools/EMotionStudio/EMStudioSDK/Source/EMStudioManager.h>
#include <EMotionFX/Tools/EMotionStudio/Plugins/StandardPlugins/Source/MotionSetsWindow/MotionSetsWindowPlugin.h>
#include <EMotionFX/Tools/EMotionStudio/Plugins/StandardPlugins/Source/TimeView/TimeViewPlugin.h>
#include <EMotionFX/Source/MotionManager.h>

namespace EMotionFX
{
    class CanDeleteMotionSetWhenSameMotionInTwoMotionSetsFixture
        : public CommandRunnerFixtureBase
    {
    };

    TEST_F(CanDeleteMotionSetWhenSameMotionInTwoMotionSetsFixture, ExecuteCommands)
    {
        ExecuteCommands({
            R"str(CreateMotionSet -name MotionSet0)str",
            R"str(CreateMotionSet -name MotionSet1)str",
            R"str(MotionSetAddMotion -motionSetID 0 -motionFilenamesAndIds @devroot@/Gems/EMotionFX/Code/Tests/TestAssets/Rin/rin_idle.motion;rin_idle)str",
            R"str(MotionSetAddMotion -motionSetID 1 -motionFilenamesAndIds @devroot@/Gems/EMotionFX/Code/Tests/TestAssets/Rin/rin_idle.motion;rin_idle)str",
            R"str(MotionSetRemoveMotion -motionSetID 0 -motionIds rin_idle)str",
            R"str(RemoveMotionSet -motionSetID 0)str",
            R"str(RemoveMotion -filename @devroot@/Gems/EMotionFX/Code/Tests/TestAssets/Rin/rin_idle.motion)str",
        });

        EMStudio::MotionSetsWindowPlugin* motionSetsWindowPlugin = static_cast<EMStudio::MotionSetsWindowPlugin*>(EMStudio::GetPluginManager()->FindActivePlugin(EMStudio::MotionSetsWindowPlugin::CLASS_ID));
        ASSERT_TRUE(motionSetsWindowPlugin) << "Motion Window plugin not loaded";

        EMotionFX::MotionSet* motionSet = EMotionFX::GetMotionManager().FindMotionSetByID(1);
        motionSetsWindowPlugin->SetSelectedSet(motionSet);

        ExecuteCommands({
            R"str(Select -motionIndex 0)str",
        });

        double outTimeMax, outClipStart, outClipEnd;

        // This call should not crash
        static_cast<EMStudio::TimeViewPlugin*>(EMStudio::GetPluginManager()->FindActivePlugin(EMStudio::TimeViewPlugin::CLASS_ID))->GetDataTimes(&outTimeMax, &outClipStart, &outClipEnd);
    }
} // end namespace EMotionFX
