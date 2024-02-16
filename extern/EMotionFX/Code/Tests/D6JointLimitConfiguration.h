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

#include <AzFramework/Physics/Joint.h>

namespace EMotionFX
{
    // Add so that RagdollNodeInspectorPlugin::PhysXCharactersGemAvailable() will return the correct value
    // We duplicated the D6JointLimitConfiguration because it doesn't exist in the test environment.
    class D6JointLimitConfiguration
        : public Physics::JointLimitConfiguration
    {
    public:
        AZ_CLASS_ALLOCATOR(D6JointLimitConfiguration, AZ::SystemAllocator, 0);
        // This uses the same uuid as the production D6JointLimitConfiguration.
        // The Ragdoll UI uses this UUID to see if physx is available.
        AZ_RTTI(D6JointLimitConfiguration, "{90C5C23D-16C0-4F23-AD50-A190E402388E}", Physics::JointLimitConfiguration);

        static void Reflect(AZ::ReflectContext* context);
        const char* GetTypeName() override { return "D6 Joint"; }

        float m_swingLimitY = 45.0f; ///< Maximum angle in degrees from the Y axis of the joint frame.
        float m_swingLimitZ = 45.0f; ///< Maximum angle in degrees from the Z axis of the joint frame.
        float m_twistLimitLower = -45.0f; ///< Lower limit in degrees for rotation about the X axis of the joint frame.
        float m_twistLimitUpper = 45.0f; ///< Upper limit in degrees for rotation about the X axis of the joint frame.
    };
} // namespace EMotionFX
