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

#include <EMotionFX/Source/EventDataSyncable.h>
#include <AzCore/Serialization/EditContext.h>

namespace EMotionFX
{
    EventDataSyncable::EventDataSyncable()
        : m_hash(AZStd::hash<AZ::TypeId>()(azrtti_typeid(this)))
    {
    }

    EventDataSyncable::EventDataSyncable(const size_t hash)
        : m_hash(hash)
    {
    }

    void EventDataSyncable::Reflect(AZ::ReflectContext* context)
    {
        AZ::SerializeContext* serializeContext = azrtti_cast<AZ::SerializeContext*>(context);
        if (!serializeContext)
        {
            return;
        }

        serializeContext->Class<EventDataSyncable, EventData>()
            ->Version(1)
            ;

        AZ::EditContext* editContext = serializeContext->GetEditContext();
        if (!editContext)
        {
            return;
        }

        editContext->Class<EventDataSyncable>("EventDataSyncable", "")
            ->ClassElement(AZ::Edit::ClassElements::EditorData, "")
                ->Attribute(AZ::Edit::Attributes::AutoExpand, true)
                ->Attribute(AZ::Edit::Attributes::Visibility, AZ::Edit::PropertyVisibility::ShowChildrenOnly)
            ;
    }

    size_t EventDataSyncable::HashForSyncing(bool /*isMirror*/) const
    {
        return m_hash;
    }
} // end namespace EMotionFX
