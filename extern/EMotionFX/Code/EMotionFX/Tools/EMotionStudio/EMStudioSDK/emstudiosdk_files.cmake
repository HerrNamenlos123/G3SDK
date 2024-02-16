#
# All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
# its licensors.
#
# For complete copyright and license terms please see the LICENSE at the root of this
# distribution (the "License"). All use of this software is governed by the License,
# or, if provided, by the license below or the license accompanying this file. Do not
# remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#

set(FILES
    Source/Allocators.cpp
    Source/Allocators.h
    Source/Commands.cpp
    Source/Commands.h
    Source/DockWidgetPlugin.cpp
    Source/DockWidgetPlugin.h
    Source/EMStudioConfig.h
    Source/EMStudioCore.h
    Source/EMStudioManager.cpp
    Source/EMStudioManager.h
    Source/EMStudioPlugin.cpp
    Source/EMStudioPlugin.h
    Source/FileManager.cpp
    Source/FileManager.h
    Source/GUIOptions.cpp
    Source/GUIOptions.h
    Source/InvisiblePlugin.cpp
    Source/InvisiblePlugin.h
    Source/KeyboardShortcutsWindow.cpp
    Source/KeyboardShortcutsWindow.h
    Source/LayoutManager.cpp
    Source/LayoutManager.h
    Source/MainWindowEventFilter.h
    Source/MainWindow.cpp
    Source/MainWindow.h
    Source/MotionEventPresetManager.cpp
    Source/MotionEventPresetManager.h
    Source/PluginManager.cpp
    Source/PluginManager.h
    Source/PluginOptions.cpp
    Source/PluginOptions.h
    Source/PluginOptionsBus.h
    Source/PreferencesWindow.cpp
    Source/PreferencesWindow.h
    Source/RecoverFilesWindow.cpp
    Source/RecoverFilesWindow.h
    Source/RemovePluginOnCloseDockWidget.cpp
    Source/RemovePluginOnCloseDockWidget.h
    Source/ResetSettingsDialog.cpp
    Source/ResetSettingsDialog.h
    Source/SaveChangedFilesManager.cpp
    Source/SaveChangedFilesManager.h
    Source/ToolBarPlugin.cpp
    Source/ToolBarPlugin.h
    Source/Workspace.cpp
    Source/Workspace.h
    Source/NotificationWindow.cpp
    Source/NotificationWindow.h
    Source/NotificationWindowManager.cpp
    Source/NotificationWindowManager.h
    Source/LoadActorSettingsWindow.cpp
    Source/LoadActorSettingsWindow.h
    Source/MotionSetHierarchyWidget.cpp
    Source/MotionSetHierarchyWidget.h
    Source/MorphTargetSelectionWindow.cpp
    Source/MorphTargetSelectionWindow.h
    Source/NodeHierarchyWidget.cpp
    Source/NodeHierarchyWidget.h
    Source/NodeSelectionWindow.cpp
    Source/NodeSelectionWindow.h
    Source/MotionSetSelectionWindow.cpp
    Source/MotionSetSelectionWindow.h
    Source/UnitScaleWindow.cpp
    Source/UnitScaleWindow.h
    Source/RenderPlugin/CommandCallbacks.cpp
    Source/RenderPlugin/ManipulatorCallbacks.cpp
    Source/RenderPlugin/ManipulatorCallbacks.h
    Source/RenderPlugin/RenderLayouts.h
    Source/RenderPlugin/RenderOptions.cpp
    Source/RenderPlugin/RenderOptions.h
    Source/RenderPlugin/RenderPlugin.cpp
    Source/RenderPlugin/RenderPlugin.h
    Source/RenderPlugin/RenderUpdateCallback.cpp
    Source/RenderPlugin/RenderUpdateCallback.h
    Source/RenderPlugin/RenderViewContextMenu.cpp
    Source/RenderPlugin/RenderViewWidget.cpp
    Source/RenderPlugin/RenderViewWidget.h
    Source/RenderPlugin/RenderWidget.cpp
    Source/RenderPlugin/RenderWidget.h
)