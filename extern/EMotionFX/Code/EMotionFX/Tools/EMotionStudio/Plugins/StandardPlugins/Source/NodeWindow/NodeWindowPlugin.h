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

#if !defined(Q_MOC_RUN)
#include <EMotionFX/CommandSystem/Source/SelectionCommands.h>
#include <EMotionStudio/EMStudioSDK/Source/DockWidgetPlugin.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/StandardPluginsConfig.h>
#include <MysticQt/Source/DialogStack.h>
#endif


namespace AzToolsFramework
{
    class ReflectedPropertyEditor;
}

namespace EMStudio
{
    // forward declaration
    class ActorInfo;
    class NodeHierarchyWidget;
    class NodeInfo;

    /**
     *
     *
     */
    class NodeWindowPlugin
        : public EMStudio::DockWidgetPlugin
    {
        Q_OBJECT
        MCORE_MEMORYOBJECTCATEGORY(NodeWindowPlugin, MCore::MCORE_DEFAULT_ALIGNMENT, MEMCATEGORY_STANDARDPLUGINS);

    public:
        enum
        {
            CLASS_ID = 0x00000357
        };

        NodeWindowPlugin();
        ~NodeWindowPlugin();

        // overloaded
        const char* GetCompileDate() const override         { return MCORE_DATE; }
        const char* GetName() const override                { return "Joint outliner"; }
        uint32 GetClassID() const override                  { return CLASS_ID; }
        const char* GetCreatorName() const override         { return "Amazon"; }
        float GetVersion() const override                   { return 1.0f;  }
        bool GetIsClosable() const override                 { return true;  }
        bool GetIsFloatable() const override                { return true;  }
        bool GetIsVertical() const override                 { return false; }

        // overloaded main init function
        void Reflect(AZ::ReflectContext* context) override;
        bool Init() override;
        EMStudioPlugin* Clone() override;
        void ReInit();

    public slots:
        void OnNodeChanged();
        void VisibilityChanged(bool isVisible);
        void OnTextFilterChanged(const QString& text);

        void UpdateVisibleNodeIndices();

    private:
        // declare the callbacks
        MCORE_DEFINECOMMANDCALLBACK(CommandSelectCallback);
        MCORE_DEFINECOMMANDCALLBACK(CommandUnselectCallback);
        MCORE_DEFINECOMMANDCALLBACK(CommandClearSelectionCallback);

        CommandSelectCallback*              mSelectCallback;
        CommandUnselectCallback*            mUnselectCallback;
        CommandClearSelectionCallback*      mClearSelectionCallback;

        MysticQt::DialogStack*              mDialogStack;
        NodeHierarchyWidget*                mHierarchyWidget;
        AzToolsFramework::ReflectedPropertyEditor* m_propertyWidget;

        AZStd::string                       mString;
        AZStd::string                       mTempGroupName;
        AZStd::unordered_set<AZ::u32> m_visibleNodeIndices;
        AZStd::unordered_set<AZ::u32> m_selectedNodeIndices;

        AZStd::unique_ptr<ActorInfo>        m_actorInfo;
        AZStd::unique_ptr<NodeInfo>         m_nodeInfo;
    };
} // namespace EMStudio
