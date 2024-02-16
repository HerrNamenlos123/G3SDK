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

// include required headers
#include <AzCore/Component/ComponentApplicationBus.h>
#include <AzQtComponents/Components/FilteredSearchWidget.h>
#include <AzToolsFramework/UI/PropertyEditor/ReflectedPropertyEditor.hxx>
#include <EMotionFX/Source/ActorManager.h>
#include <EMotionStudio/EMStudioSDK/Source/EMStudioManager.h>
#include <EMotionStudio/EMStudioSDK/Source/NodeHierarchyWidget.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/ActorInfo.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/MeshInfo.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/NamedPropertyStringValue.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/NodeGroupInfo.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/NodeInfo.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/NodeWindowPlugin.h>
#include <EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/SubMeshInfo.h>
#include <MCore/Source/StringConversions.h>
#include <QTreeWidget>


namespace EMStudio
{
    NodeWindowPlugin::NodeWindowPlugin()
        : EMStudio::DockWidgetPlugin()
        , mSelectCallback(nullptr)
        , mUnselectCallback(nullptr)
        , mClearSelectionCallback(nullptr)
        , mDialogStack(nullptr)
        , mHierarchyWidget(nullptr)
        , m_propertyWidget(nullptr)
    {
    }


    NodeWindowPlugin::~NodeWindowPlugin()
    {
        // unregister the command callbacks and get rid of the memory
        GetCommandManager()->RemoveCommandCallback(mSelectCallback, false);
        GetCommandManager()->RemoveCommandCallback(mUnselectCallback, false);
        GetCommandManager()->RemoveCommandCallback(mClearSelectionCallback, false);
        delete mSelectCallback;
        delete mUnselectCallback;
        delete mClearSelectionCallback;
    }


    EMStudioPlugin* NodeWindowPlugin::Clone()
    {
        return new NodeWindowPlugin();
    }

    void NodeWindowPlugin::Reflect(AZ::ReflectContext* context)
    {
        NamedPropertyStringValue::Reflect(context);
        SubMeshInfo::Reflect(context);
        MeshInfo::Reflect(context);
        NodeInfo::Reflect(context);
        NodeGroupInfo::Reflect(context);
        ActorInfo::Reflect(context);
    }


    // init after the parent dock window has been created
    bool NodeWindowPlugin::Init()
    {
        // create and register the command callbacks only (only execute this code once for all plugins)
        mSelectCallback                 = new CommandSelectCallback(false);
        mUnselectCallback               = new CommandUnselectCallback(false);
        mClearSelectionCallback         = new CommandClearSelectionCallback(false);

        GetCommandManager()->RegisterCommandCallback("Select", mSelectCallback);
        GetCommandManager()->RegisterCommandCallback("Unselect", mUnselectCallback);
        GetCommandManager()->RegisterCommandCallback("ClearSelection", mClearSelectionCallback);

        // create the dialog stack
        AZ_Assert(!mDialogStack, "Expected an unitialized mDialogStack, was this function called more than once?");
        mDialogStack = new MysticQt::DialogStack();

        // add the node hierarchy
        mHierarchyWidget = new NodeHierarchyWidget(mDock, false);
        mHierarchyWidget->setObjectName("EMFX.NodeWindowPlugin.NodeHierarchyWidget.HierarchyWidget");
        mHierarchyWidget->GetTreeWidget()->setMinimumWidth(100);
        mDialogStack->Add(mHierarchyWidget, "Hierarchy", false, true);

        // add the node attributes widget
        m_propertyWidget = aznew AzToolsFramework::ReflectedPropertyEditor(mDialogStack);
        m_propertyWidget->setObjectName("EMFX.NodeWindowPlugin.ReflectedPropertyEditor.PropertyWidget");
        m_propertyWidget->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Fixed);
        m_propertyWidget->SetAutoResizeLabels(true);
        mDialogStack->Add(m_propertyWidget, "Node Attributes", false, true, true, false);

        // prepare the dock window
        mDock->setWidget(mDialogStack);
        mDock->setMinimumWidth(100);
        mDock->setMinimumHeight(100);

        // add functionality to the controls
        connect(mDock, &QDockWidget::visibilityChanged, this, &NodeWindowPlugin::VisibilityChanged);
        connect(mHierarchyWidget->GetTreeWidget(), &QTreeWidget::itemSelectionChanged, this, &NodeWindowPlugin::OnNodeChanged);

        const AzQtComponents::FilteredSearchWidget* searchWidget = mHierarchyWidget->GetSearchWidget();
        connect(searchWidget, &AzQtComponents::FilteredSearchWidget::TextFilterChanged, this, &NodeWindowPlugin::OnTextFilterChanged);

        connect(mHierarchyWidget, &NodeHierarchyWidget::FilterStateChanged, this, &NodeWindowPlugin::UpdateVisibleNodeIndices);

        // reinit the dialog
        ReInit();

        return true;
    }


    // reinitialize the window
    void NodeWindowPlugin::ReInit()
    {
        const CommandSystem::SelectionList& selection       = CommandSystem::GetCommandManager()->GetCurrentSelection();
        EMotionFX::ActorInstance*           actorInstance   = selection.GetSingleActorInstance();

        // reset the node name filter
        mHierarchyWidget->GetSearchWidget()->ClearTextFilter();
        mHierarchyWidget->GetTreeWidget()->clear();
        
        m_propertyWidget->ClearInstances();
        m_propertyWidget->InvalidateAll();

        if (actorInstance)
        {
            mHierarchyWidget->Update(actorInstance->GetID());
            m_actorInfo.reset(aznew ActorInfo(actorInstance));
            m_propertyWidget->AddInstance(m_actorInfo.get(), azrtti_typeid(m_actorInfo.get()));
        }

        AZ::SerializeContext* serializeContext = nullptr;
        AZ::ComponentApplicationBus::BroadcastResult(serializeContext, &AZ::ComponentApplicationBus::Events::GetSerializeContext);
        if (!serializeContext)
        {
            AZ_Error("EMotionFX", false, "Can't get serialize context from component application.");
            return;
        }

        m_propertyWidget->Setup(serializeContext, nullptr, false);
        m_propertyWidget->show();
        m_propertyWidget->ExpandAll();
        m_propertyWidget->InvalidateAll();
    }


    void NodeWindowPlugin::OnNodeChanged()
    {
        // get access to the current selection list and clear the node selection
        CommandSystem::SelectionList& selection = CommandSystem::GetCommandManager()->GetCurrentSelection();
        selection.ClearNodeSelection();
        m_selectedNodeIndices.clear();

        AZStd::vector<SelectionItem>& selectedItems = mHierarchyWidget->GetSelectedItems();

        EMotionFX::ActorInstance*   selectedInstance    = nullptr;
        EMotionFX::Node*            selectedNode        = nullptr;

        for (const SelectionItem& selectedItem : selectedItems)
        {
            const uint32                actorInstanceID = selectedItem.mActorInstanceID;
            const char*                 nodeName        = selectedItem.GetNodeName();
            EMotionFX::ActorInstance*   actorInstance   = EMotionFX::GetActorManager().FindActorInstanceByID(actorInstanceID);

            if (actorInstance == nullptr)
            {
                continue;
            }

            EMotionFX::Actor*           actor   = actorInstance->GetActor();
            EMotionFX::Node*            node    = actor->GetSkeleton()->FindNodeByName(nodeName);

            if (node && mHierarchyWidget->CheckIfNodeVisible(actorInstance, node))
            {
                if (selectedInstance == nullptr)
                {
                    selectedInstance = actorInstance;
                }
                if (selectedNode == nullptr)
                {
                    selectedNode = node;
                }

                // add the node to the node selection
                selection.AddNode(node);
                m_selectedNodeIndices.emplace(node->GetNodeIndex());
            }
            else if (node == nullptr && actorInstance)
            {
                if (selectedInstance == nullptr)
                {
                    selectedInstance = actorInstance;
                }
                if (selectedNode == nullptr)
                {
                    selectedNode = node;
                }
            }
        }

        if (selectedInstance == nullptr)
        {
            GetManager()->SetSelectedJointIndices(m_selectedNodeIndices);
            return;
        }

        m_propertyWidget->ClearInstances();
        m_propertyWidget->InvalidateAll();

        if (selectedNode)
        {
            // show the node information in the lower property widget
            m_nodeInfo.reset(aznew NodeInfo(selectedInstance, selectedNode));
            m_propertyWidget->AddInstance(m_nodeInfo.get(), azrtti_typeid(m_nodeInfo.get()));
        }
        else
        {
            m_actorInfo.reset(aznew ActorInfo(selectedInstance));
            m_propertyWidget->AddInstance(m_actorInfo.get(), azrtti_typeid(m_actorInfo.get()));
        }

        AZ::SerializeContext* serializeContext = nullptr;
        AZ::ComponentApplicationBus::BroadcastResult(serializeContext, &AZ::ComponentApplicationBus::Events::GetSerializeContext);
        if (!serializeContext)
        {
            AZ_Error("EMotionFX", false, "Can't get serialize context from component application.");
            return;
        }

        m_propertyWidget->Setup(serializeContext, nullptr, false);
        m_propertyWidget->show();
        m_propertyWidget->ExpandAll();
        m_propertyWidget->InvalidateAll();

        // pass the selected node indices to the manager
        GetManager()->SetSelectedJointIndices(m_selectedNodeIndices);
    }


    // reinit the window when it gets activated
    void NodeWindowPlugin::VisibilityChanged(bool isVisible)
    {
        if (isVisible)
        {
            ReInit();
        }
    }


    void NodeWindowPlugin::OnTextFilterChanged(const QString& text)
    {
        MCORE_UNUSED(text);
        //GetManager()->SetNodeNameFilterString( FromQtString(text).AsChar() );
        UpdateVisibleNodeIndices();
    }


    // update the array containing the visible node indices
    void NodeWindowPlugin::UpdateVisibleNodeIndices()
    {
        // reset the visible nodes array
        m_visibleNodeIndices.clear();

        // get the currently selected actor instance
        const CommandSystem::SelectionList& selection       = CommandSystem::GetCommandManager()->GetCurrentSelection();
        EMotionFX::ActorInstance*           actorInstance   = selection.GetSingleActorInstance();
        if (actorInstance == nullptr)
        {
            // make sure the empty visible nodes array gets passed to the manager, an empty array means all nodes are shown
            GetManager()->SetVisibleJointIndices(m_visibleNodeIndices);
            return;
        }

        AZStd::string filterString = mHierarchyWidget->GetSearchWidgetText();
        AZStd::to_lower(filterString.begin(), filterString.end());
        const bool showNodes        = mHierarchyWidget->GetDisplayNodes();
        const bool showBones        = mHierarchyWidget->GetDisplayBones();
        const bool showMeshes       = mHierarchyWidget->GetDisplayMeshes();

        // get access to the actor and the number of nodes
        EMotionFX::Actor* actor = actorInstance->GetActor();
        const uint32 numNodes = actor->GetNumNodes();

        // reserve memory for the visible node indices
        m_visibleNodeIndices.reserve(numNodes);

        // extract the bones from the actor
        MCore::Array<uint32> boneList;
        actor->ExtractBoneList(actorInstance->GetLODLevel(), &boneList);

        // iterate through all nodes and check if the node is visible
        AZStd::string nodeName;
        for (uint32 i = 0; i < numNodes; ++i)
        {
            EMotionFX::Node* node = actor->GetSkeleton()->GetNode(i);

            // get the node name and lower case it
            nodeName = node->GetNameString();
            AZStd::to_lower(nodeName.begin(), nodeName.end());

            const uint32        nodeIndex   = node->GetNodeIndex();
            EMotionFX::Mesh*    mesh        = actor->GetMesh(actorInstance->GetLODLevel(), nodeIndex);
            const bool          isMeshNode  = (mesh);
            const bool          isBone      = (boneList.Find(nodeIndex) != MCORE_INVALIDINDEX32);
            const bool          isNode      = (isMeshNode == false && isBone == false);

            if (((showMeshes && isMeshNode) ||
                 (showBones && isBone) ||
                 (showNodes && isNode)) &&
                (filterString.empty() || nodeName.find(filterString) != AZStd::string::npos))
            {
                // this node is visible!
                m_visibleNodeIndices.emplace(nodeIndex);
            }
        }

        // pass it over to the manager
        GetManager()->SetVisibleJointIndices(m_visibleNodeIndices);
    }

    //-----------------------------------------------------------------------------------------
    // command callbacks
    //-----------------------------------------------------------------------------------------

    bool ReInitNodeWindowPlugin()
    {
        EMStudioPlugin* plugin = EMStudio::GetPluginManager()->FindActivePlugin(NodeWindowPlugin::CLASS_ID);
        if (plugin == nullptr)
        {
            return false;
        }

        NodeWindowPlugin* nodeWindow = (NodeWindowPlugin*)plugin;

        // is the plugin visible? only update it if it is visible
        if (GetManager()->GetIgnoreVisibility() || !nodeWindow->GetDockWidget()->visibleRegion().isEmpty())
        {
            nodeWindow->ReInit();
        }

        return true;
    }

    bool NodeWindowPlugin::CommandSelectCallback::Execute(MCore::Command* command, const MCore::CommandLine& commandLine)           { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
    bool NodeWindowPlugin::CommandSelectCallback::Undo(MCore::Command* command, const MCore::CommandLine& commandLine)              { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
    bool NodeWindowPlugin::CommandUnselectCallback::Execute(MCore::Command* command, const MCore::CommandLine& commandLine)         { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
    bool NodeWindowPlugin::CommandUnselectCallback::Undo(MCore::Command* command, const MCore::CommandLine& commandLine)            { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
    bool NodeWindowPlugin::CommandClearSelectionCallback::Execute(MCore::Command* command, const MCore::CommandLine& commandLine)   { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
    bool NodeWindowPlugin::CommandClearSelectionCallback::Undo(MCore::Command* command, const MCore::CommandLine& commandLine)      { MCORE_UNUSED(command); MCORE_UNUSED(commandLine); return ReInitNodeWindowPlugin(); }
} // namespace EMStudio

#include <EMotionFX/Tools/EMotionStudio/Plugins/StandardPlugins/Source/NodeWindow/moc_NodeWindowPlugin.cpp>
