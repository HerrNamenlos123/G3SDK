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

namespace EMotionFX
{
    class Actor;
    class Node;

    /**
     * EMotion FX Actor Request Bus
     * Used for making requests to actors.
     */
    class ActorRequests
        : public AZ::EBusTraits
    {
    public:
    };

    using ActorRequestBus = AZ::EBus<ActorRequests>;

    /**
     * EMotion FX Actor Notification Bus
     * Used for monitoring events from actors.
     */
    class ActorNotifications
        : public AZ::EBusTraits
    {
    public:
        /**
         * Called whenever the motion extraction node of an actor changed.
         */
        virtual void OnMotionExtractionNodeChanged(Actor* actor, Node* newMotionExtractionNode) { AZ_UNUSED(actor); AZ_UNUSED(newMotionExtractionNode); }

        virtual void OnActorCreated(Actor* actor) { AZ_UNUSED(actor); }
        virtual void OnActorDestroyed(Actor* actor) { AZ_UNUSED(actor); }
    };

    using ActorNotificationBus = AZ::EBus<ActorNotifications>;
} // namespace EMotionFX
