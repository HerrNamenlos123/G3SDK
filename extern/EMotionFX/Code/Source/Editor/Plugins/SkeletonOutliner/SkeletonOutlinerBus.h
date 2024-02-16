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

#include <AzCore/EBus/EBus.h>
#include <EMotionFX/Source/Actor.h>
#include <EMotionFX/Source/ActorInstance.h>
#include <QMenu>
#include <QModelIndexList>


namespace EMotionFX
{
    class SkeletonModel;

    /**
     * EMotion FX Skeleton Outliner Request Bus
     * Used for making requests to skeleton outliner.
     */
    class SkeletonOutlinerRequests
        : public AZ::EBusTraits
    {
    public:
        virtual Node* GetSingleSelectedNode() { return nullptr; }
        virtual QModelIndex GetSingleSelectedModelIndex() { return QModelIndex(); }
        virtual AZ::Outcome<const QModelIndexList&> GetSelectedRowIndices() { return AZ::Failure(); }
        virtual SkeletonModel* GetModel() = 0;

        virtual void DataChanged([[maybe_unused]] const QModelIndex& modelIndex) {}
        virtual void DataListChanged([[maybe_unused]] const QModelIndexList& modelIndexList) {}
    };

    using SkeletonOutlinerRequestBus = AZ::EBus<SkeletonOutlinerRequests>;

    /**
     * EMotion FX Skeleton Outliner Notification Bus
     * Used for monitoring events from the skeleton outliner.
     */
    class SkeletonOutlinerNotifications
        : public AZ::EBusTraits
    {
    public:
        virtual void SingleNodeSelectionChanged([[maybe_unused]] Actor* actor, [[maybe_unused]] Node* node) {}
        virtual void ZoomToJoints([[maybe_unused]] ActorInstance* actorInstance, [[maybe_unused]] const AZStd::vector<Node*>& joints) {}
        virtual void JointSelectionChanged() {}

        virtual void OnContextMenu([[maybe_unused]] QMenu* menuconst, [[maybe_unused]] const QModelIndexList& selectedRowIndices) {}
    };

    using SkeletonOutlinerNotificationBus = AZ::EBus<SkeletonOutlinerNotifications>;
} // namespace EMotionFX