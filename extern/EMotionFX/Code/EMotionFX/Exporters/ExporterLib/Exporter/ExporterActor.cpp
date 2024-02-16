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

#include <AzCore/Debug/Timer.h>
#include <AzCore/Serialization/ObjectStream.h>
#include <AzCore/Serialization/SerializeContext.h>
#include <AzCore/Serialization/EditContext.h>
#include <AzCore/Serialization/Utils.h>
#include <AzCore/Component/ComponentApplicationBus.h>
#include "Exporter.h"
#include <EMotionFX/Source/Actor.h>
#include <EMotionFX/Source/SimulatedObjectSetup.h>
#include <EMotionFX/Source/ActorInstance.h>
#include <EMotionFX/Source/EventManager.h>
#include <EMotionFX/Source/Importer/ActorFileFormat.h>
#include <MCore/Source/LogManager.h>


//#define EMFX_DETAILED_SAVING_PERFORMANCESTATS

#ifdef EMFX_DETAILED_SAVING_PERFORMANCESTATS
    #define EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(TIMERNAME)      AZ::Debug::Timer TIMERNAME; TIMERNAME.Stamp();
    #define EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(TIMERNAME, TEXT)  const float saveTime = TIMERNAME.GetDeltaTimeInSeconds(); MCore::LogError("Saving %s took %.2f ms.", TEXT, saveTime * 1000.0f);
#else
    #define EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(TIMERNAME)
    #define EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(TIMERNAME, TEXT)
#endif


namespace ExporterLib
{
    void SavePhysicsSetup(MCore::MemoryFile* file, EMotionFX::Actor* actor, MCore::Endian::EEndianType targetEndianType)
    {
        AZ::SerializeContext* serializeContext = nullptr;
        AZ::ComponentApplicationBus::BroadcastResult(serializeContext, &AZ::ComponentApplicationBus::Events::GetSerializeContext);
        if (!serializeContext)
        {
            AZ_Error("EMotionFX", false, "Can't get serialize context from component application.");
            return;
        }

        AZStd::vector<AZ::u8> buffer;
        AZ::IO::ByteContainerStream<AZStd::vector<AZ::u8>> stream(&buffer);
        const bool result = AZ::Utils::SaveObjectToStream<EMotionFX::PhysicsSetup>(stream, AZ::ObjectStream::ST_BINARY, actor->GetPhysicsSetup().get(), serializeContext);
        if (result)
        {
            const AZ::u32 bufferSize = static_cast<AZ::u32>(buffer.size());

            EMotionFX::FileFormat::FileChunk chunkHeader;
            chunkHeader.mChunkID = EMotionFX::FileFormat::ACTOR_CHUNK_PHYSICSSETUP;
            chunkHeader.mVersion = 1;
            chunkHeader.mSizeInBytes = bufferSize + sizeof(AZ::u32);

            ConvertFileChunk(&chunkHeader, targetEndianType);
            file->Write(&chunkHeader, sizeof(EMotionFX::FileFormat::FileChunk));

            // Write the number of bytes again as inside the chunk processor we don't have access to the file chunk.
            AZ::u32 endianBufferSize = bufferSize;
            ConvertUnsignedInt(&endianBufferSize, targetEndianType);
            file->Write(&endianBufferSize, sizeof(AZ::u32));

            file->Write(buffer.data(), bufferSize);
        }
        else
        {
            AZ_Error("EMotionFX", false, "Cannot save physics setup. Please enable the PhysX gem.");
        }
    }

    void SaveSimulatedObjectSetup(MCore::MemoryFile* file, EMotionFX::Actor* actor, MCore::Endian::EEndianType targetEndianType)
    {
        AZ::SerializeContext* serializeContext = nullptr;
        AZ::ComponentApplicationBus::BroadcastResult(serializeContext, &AZ::ComponentApplicationBus::Events::GetSerializeContext);
        if (!serializeContext)
        {
            AZ_Error("EMotionFX", false, "Can't get serialize context from component application.");
            return;
        }

        AZStd::vector<AZ::u8> buffer;
        AZ::IO::ByteContainerStream<AZStd::vector<AZ::u8>> stream(&buffer);
        const bool result = AZ::Utils::SaveObjectToStream<EMotionFX::SimulatedObjectSetup>(stream, AZ::ObjectStream::ST_BINARY, actor->GetSimulatedObjectSetup().get(), serializeContext);
        if (result)
        {
            const AZ::u32 bufferSize = static_cast<AZ::u32>(buffer.size());

            EMotionFX::FileFormat::FileChunk chunkHeader;
            chunkHeader.mChunkID = EMotionFX::FileFormat::ACTOR_CHUNK_SIMULATEDOBJECTSETUP;
            chunkHeader.mVersion = 1;
            chunkHeader.mSizeInBytes = bufferSize + sizeof(AZ::u32);

            ConvertFileChunk(&chunkHeader, targetEndianType);
            file->Write(&chunkHeader, sizeof(EMotionFX::FileFormat::FileChunk));

            // Write the number of bytes again as inside the chunk processor we don't have access to the file chunk.
            AZ::u32 endianBufferSize = bufferSize;
            ConvertUnsignedInt(&endianBufferSize, targetEndianType);
            file->Write(&endianBufferSize, sizeof(AZ::u32));

            file->Write(buffer.data(), bufferSize);
        }
        else
        {
            AZ_Error("EMotionFX", false, "Cannot save simulated object setup. SaveObjectToStream() failed.");
        }
    }


    // save the actor to a memory file
    void SaveActor(MCore::MemoryFile* file, const EMotionFX::Actor* actorIn, MCore::Endian::EEndianType targetEndianType)
    {
        if (actorIn == nullptr)
        {
            MCore::LogError("SaveActor: Passed actor is not valid.");
            return;
        }

        // clone our actor before saving as we will modify its data
        AZStd::unique_ptr<EMotionFX::Actor> actor = actorIn->Clone();

        AZ::Debug::Timer saveTimer;
        saveTimer.Stamp();

        // save header
        SaveActorHeader(file, targetEndianType);

        // save actor info
        SaveActorFileInfo(file, actor->GetNumLODLevels(), actor->GetMotionExtractionNodeIndex(), actor->GetRetargetRootNodeIndex(), "", "", actor->GetName(), actor->GetUnitType(), targetEndianType, actor->GetOptimizeSkeleton());

        // save nodes
        EMotionFX::GetEventManager().OnSubProgressText("Saving nodes");
        EMotionFX::GetEventManager().OnSubProgressValue(35.0f);

        EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(nodeTimer);
        SaveNodes(file, actor.get(), targetEndianType);
        EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(nodeTimer, "nodes");

        SaveNodeGroups(file, actor.get(), targetEndianType);
        SaveNodeMotionSources(file, actor.get(), nullptr, targetEndianType);
        SaveAttachmentNodes(file, actor.get(), targetEndianType);

        // save materials
        EMotionFX::GetEventManager().OnSubProgressText("Saving materials");
        EMotionFX::GetEventManager().OnSubProgressValue(45.0f);

        EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(materialTimer);
        SaveMaterials(file, actor.get(), targetEndianType);
        EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(materialTimer, "materials");

        // save meshes
        EMotionFX::GetEventManager().OnSubProgressText("Saving meshes");
        EMotionFX::GetEventManager().OnSubProgressValue(50.0f);

        EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(meshTimer);
        SaveMeshes(file, actor.get(), targetEndianType);
        EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(meshTimer, "meshes");

        // save skins
        EMotionFX::GetEventManager().OnSubProgressText("Saving skins");
        EMotionFX::GetEventManager().OnSubProgressValue(75.0f);

        EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(skinTimer);
        SaveSkins(file, actor.get(), targetEndianType);
        EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(skinTimer, "skins");

        // save morph targets
        EMotionFX::GetEventManager().OnSubProgressText("Saving morph targets");
        EMotionFX::GetEventManager().OnSubProgressValue(90.0f);

        EMFX_DETAILED_SAVING_PERFORMANCESTATS_START(morphTargetTimer);
        SaveMorphTargets(file, actor.get(), targetEndianType);
        EMFX_DETAILED_SAVING_PERFORMANCESTATS_END(morphTargetTimer, "morph targets");

        SavePhysicsSetup(file, actor.get(), targetEndianType);

        SaveSimulatedObjectSetup(file, actor.get(), targetEndianType);

        const float saveTime = saveTimer.GetDeltaTimeInSeconds() * 1000.0f;
        MCore::LogInfo("Actor saved in %.2f ms.", saveTime);

        // finished sub progress
        EMotionFX::GetEventManager().OnSubProgressText("");
        EMotionFX::GetEventManager().OnSubProgressValue(100.0f);
    }


    // save the actor to disk
    bool SaveActor(AZStd::string& filename, const EMotionFX::Actor* actor, MCore::Endian::EEndianType targetEndianType)
    {
        if (filename.empty())
        {
            AZ_Error("EMotionFX", false, "Cannot save actor. Filename is empty.");
            return false;
        }

        MCore::MemoryFile memoryFile;
        memoryFile.Open();
        memoryFile.SetPreAllocSize(262144); // 256kb

        // Save the actor to the memory file.
        SaveActor(&memoryFile, actor, targetEndianType);

        // Make sure the file has the correct extension and write the data from memory to disk.
        AzFramework::StringFunc::Path::ReplaceExtension(filename, GetActorExtension());
        memoryFile.SaveToDiskFile(filename.c_str());
        memoryFile.Close();
        return true;
    }

} // namespace ExporterLib
