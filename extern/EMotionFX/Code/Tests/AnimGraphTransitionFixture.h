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

#pragma once

#include "SystemComponentFixture.h"
#include <AzCore/std/smart_ptr/unique_ptr.h>
#include <Tests/TestAssetCode/AnimGraphFactory.h>

namespace EMotionFX
{
    class Actor;
    class ActorInstance;
    class AnimGraph;
    class AnimGraphInstance;
    class AnimGraphMotionNode;
    class AnimGraphStateMachine;
    class MotionSet;

    class AnimGraphTransitionFixture
        : public SystemComponentFixture
    {
    public:
        void SetUp() override;

        void TearDown() override;

    protected:
        AnimGraphStateMachine* m_stateMachine = nullptr;
        AnimGraphInstance* m_animGraphInstance = nullptr;
        AnimGraphMotionNode* m_motionNodeA = nullptr;
        AnimGraphMotionNode* m_motionNodeB = nullptr;
        AZStd::unique_ptr<Actor> m_actor;
        AZStd::unique_ptr<TwoMotionNodeAnimGraph> m_animGraph;
        MotionSet* m_motionSet = nullptr;
        ActorInstance* m_actorInstance = nullptr;
    };
}
