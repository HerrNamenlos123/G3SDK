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

#include <EMotionFX/Source/Actor.h>
#include <EMotionFX/Source/ActorInstance.h>
#include <EMotionFX/Source/Node.h>
#include <EMotionFX/Source/Skeleton.h>
#include <gtest/gtest.h>
#include <Tests/SystemComponentFixture.h>
#include <Tests/TestAssetCode/SimpleActors.h>
#include <Tests/TestAssetCode/ActorFactory.h>

namespace EMotionFX
{
    class SkeletonNodeSearchTests
        : public SystemComponentFixture
    {
    public:
        void SetUpActor(int numJoint)
        {
            /*
             * This creates an Actor with following hierarchy.
             *
             * 0("rootJoint")-----1-----2-----3-----4
             *
             */
            m_actor = ActorFactory::CreateAndInit<SimpleJointChainActor>(numJoint);
            m_skeleton = m_actor->GetSkeleton();
        }

    public:
        AZStd::unique_ptr<SimpleJointChainActor> m_actor = nullptr;
        Skeleton* m_skeleton = nullptr;
    };

    TEST_F(SkeletonNodeSearchTests, FindNode)
    {
        SetUpActor(5);

        // Try to find all 5 nodes by name.
        Node* testNode = m_skeleton->FindNodeByName("rootJoint");
        Node* indexNode = m_skeleton->FindNodeByID(0);
        EXPECT_TRUE(testNode) << "rootJoint should be found in skeleton.";
        testNode = m_skeleton->FindNodeByName("joint1");
        EXPECT_TRUE(testNode) << "joint1 should be found in skeleton.";
        testNode = m_skeleton->FindNodeByName("joint2");
        EXPECT_TRUE(testNode) << "joint2 should be found in skeleton.";
        testNode = m_skeleton->FindNodeByName("joint3");
        EXPECT_TRUE(testNode) << "joint3 should be found in skeleton.";
        testNode = m_skeleton->FindNodeByName("joint4");
        EXPECT_TRUE(testNode) << "joint4 should be found in skeleton.";
    }

    TEST_F(SkeletonNodeSearchTests, RemoveNode)
    {
        SetUpActor(5);
        Node* testNode = nullptr;

        // Try to find rootJoint by name after deleting other nodes.
        for (AZ::u32 i = 0; i < 5; ++i)
        {
            const AZStd::string nodeName = m_skeleton->GetNode(0)->GetNameString();
            m_skeleton->RemoveNode(0);
            testNode = m_skeleton->FindNodeByName(nodeName);
            EXPECT_FALSE(testNode) << nodeName.c_str() << " should not be found in skeleton after being removed.";
        }
        EXPECT_EQ(m_skeleton->GetNumNodes(), 0) << "Skeleton should have zero nodes.";
    }

    TEST_F(SkeletonNodeSearchTests, SetNode)
    {
        SetUpActor(6);
        Node* testNode = Node::Create("testNode", m_skeleton);
        m_skeleton->SetNode(5, testNode);

        Node* nodeFound = m_skeleton->FindNodeByName("testNode");
        EXPECT_EQ(testNode, nodeFound) << "testNode should be found in skeleton.";

        nodeFound = m_skeleton->FindNodeByName("joint5");
        EXPECT_FALSE(nodeFound) << "joint5 should be replaced and could not be found in skeleton.";
    }
} // namespace EMotionFX
