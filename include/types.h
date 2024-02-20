#pragma once

#include "framework.h"
#include "commontypes.h"
#include <spdlog/fmt/bundled/format.h>

#include "Engine.h"
#include "SharedBase.h"
#include "Script.h"

struct eCResourceAnimationMotion_PS;

struct eCWrapper_emfx2Motion::eSMotionDesc {
    eCResourceAnimationMotion_PS* m_Motion;
    bCString m_MotionFileName;
    int m_MotionOwner;
};

class eCVirtualFileHook {
public:
    GEBool Open(bCString const& path, bEFileCreationMode mode, GEU8 a_u8ReadOnly);

    DETOUR_DECLARE_MEMBER(Open, "Engine.dll", "?Open@eCVirtualFile@@UAE_NABVbCString@@W4bEFileCreationMode@@E@Z")
};

class eCVisualAnimationLoDHook {
public:
    bEResult Read(bCIStream&);

    DETOUR_DECLARE_MEMBER(Read, "Engine.dll", "?Read@eCVisualAnimationLoD@@UAE?AW4bEResult@@AAVbCIStream@@@Z")
};

class eCVisualAnimation_PSHook {
public:    
    bEResult Read(bCIStream&);
    void PlayMotion(eCWrapper_emfx2Actor::eEMotionType, eCWrapper_emfx2Motion::eSMotionDesc*);

    DETOUR_DECLARE_MEMBER(Read, "Engine.dll", "?Read@eCVisualAnimation_PS@@UAE?AW4bEResult@@AAVbCIStream@@@Z")
    DETOUR_DECLARE_MEMBER(PlayMotion, "Engine.dll", "?PlayMotion@eCVisualAnimation_PS@@QAEXW4eEMotionType@eCWrapper_emfx2Actor@@PAUeSMotionDesc@eCWrapper_emfx2Motion@@@Z")
};

class eCVisualAnimationFactoryHook {
public:    
    bEResult Read(bCIStream&);

    DETOUR_DECLARE_MEMBER(Read, "Engine.dll", "?Read@eCVisualAnimationFactory@@QAE?AW4bEResult@@AAVbCIStream@@@Z")
};

class eCWrapper_emfx2MotionHook {
public:    
    bEResult LoadMotion(eCArchiveFile& file);

    DETOUR_DECLARE_MEMBER(LoadMotion, "Engine.dll", "?LoadMotion@eCWrapper_emfx2Motion@@QAE?AW4bEResult@@AAVeCArchiveFile@@@Z")
};

class EntityHook {
public:
    void DoDamage(Entity const&, GEU32, gEDamageType);
    bCString GetDisplayName() const;

    DETOUR_DECLARE_MEMBER(DoDamage, "Script.dll", "?DoDamage@Entity@@QAEXABV1@KW4gEDamageType@@@Z")
    DETOUR_DECLARE_MEMBER(GetDisplayName, "Script.dll", "?GetDisplayName@Entity@@QBE?AVbCString@@XZ")
};

class MusicHook {
public:
    bool TriggerExplore() {
        TRACE("");
        return (this->*TriggerExplore_original)();
    }

    bool TriggerFight() {
        TRACE("");
        //return true;
        return (this->*TriggerFight_original)();
    }

    bool TriggerRevolution() {
        TRACE("");
        return (this->*TriggerRevolution_original)();
    }

    bool TriggerShowdown() {
        TRACE("");
        return (this->*TriggerShowdown_original)();
    }

    bool TriggerSituation(const bCString& str) {
        TRACE("str = {}", str);
        return (this->*TriggerSituation_original)(str);
    }

    bool TriggerVictory() {
        TRACE("");
        return (this->*TriggerVictory_original)();
    }

    DETOUR_DECLARE_MEMBER(TriggerExplore, "Script.dll", "?TriggerExplore@Music@@QAE_NXZ")
    DETOUR_DECLARE_MEMBER(TriggerFight, "Script.dll", "?TriggerFight@Music@@QAE_NXZ")
    DETOUR_DECLARE_MEMBER(TriggerRevolution, "Script.dll", "?TriggerRevolution@Music@@QAE_NXZ")
    DETOUR_DECLARE_MEMBER(TriggerShowdown, "Script.dll", "?TriggerShowdown@Music@@QAE_NXZ")
    DETOUR_DECLARE_MEMBER(TriggerSituation, "Script.dll", "?TriggerSituation@Music@@QAE_NABVbCString@@@Z")
    DETOUR_DECLARE_MEMBER(TriggerVictory, "Script.dll", "?TriggerVictory@Music@@QAE_NXZ")

    static void detour(bool detach) {
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerExplore);
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerFight);
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerRevolution);
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerShowdown);
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerSituation);
        DETOUR_EXTERN_MEMBER(MusicHook, TriggerVictory);
    }
};

static void detour(bool detach) {

    DETOUR_EXTERN_MEMBER(eCVirtualFileHook, Open);
    DETOUR_EXTERN_MEMBER(eCVisualAnimationLoDHook, Read);
    DETOUR_EXTERN_MEMBER(eCVisualAnimation_PSHook, Read);
    DETOUR_EXTERN_MEMBER(eCVisualAnimation_PSHook, PlayMotion);
    DETOUR_EXTERN_MEMBER(eCVisualAnimationFactoryHook, Read);
    DETOUR_EXTERN_MEMBER(eCWrapper_emfx2MotionHook, LoadMotion);
    DETOUR_EXTERN_MEMBER(EntityHook, DoDamage);
    DETOUR_EXTERN_MEMBER(EntityHook, GetDisplayName);

    MusicHook::detour(detach);

    //DETOUR_EXTERN_MEMBER(eCVisualAnimation_PS, PlayMotion, "Engine.dll", "?PlayMotion@eCVisualAnimation_PS@@QAEXW4eEMotionType@eCWrapper_emfx2Actor@@PAUeSMotionDesc@eCWrapper_emfx2Motion@@@Z");
    //DETOUR_EXTERN_MEMBER(eCVisualAnimationLoD, Read, "Engine.dll", "?Read@eCVisualAnimationLoD@@UAE?AW4bEResult@@AAVbCIStream@@@Z");
    //DETOUR_EXTERN_MEMBER(eCVisualAnimation_PS, Read, "Engine.dll", "?Read@eCVisualAnimation_PS@@UAE?AW4bEResult@@AAVbCIStream@@@Z");
    //DETOUR_EXTERN_MEMBER(eCVirtualFile, Open, "Engine.dll", "?Open@eCVirtualFile@@UAE_NABVbCString@@W4bEFileCreationMode@@E@Z");

    //DETOUR_EXTERN_MEMBER(bCFile, Open, "SharedBase.dll", "?Open@bCFile@@UAE_NABVbCString@@W4bEFileCreationMode@@@Z");
    //DETOUR_EXTERN_MEMBER(eCVisualAnimationFactory, GetMainActorFileName, "Engine.dll", "?GetMainActorFileName@eCVisualAnimationFactory@@QBEABVbCString@@XZ");
    //DETOUR_EXTERN_MEMBER(eCVisualAnimationFactory, SetMainActorFileName, "Engine.dll", "?SetMainActorFileName@eCVisualAnimationFactory@@QAEXABVbCString@@@Z");
    //DETOUR_EXTERN_MEMBER(eCVisualAnimationFactory, Read, "Engine.dll", "?Read@eCVisualAnimationFactory@@QAE?AW4bEResult@@AAVbCIStream@@@Z");
    //DETOUR_EXTERN_MEMBER(eCApplication, GetInstance, "Engine.dll", "?GetInstance@eCApplication@@SGAAV1@XZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, GetCurrentCamera, "Engine.dll", "?GetCurrentCamera@eCApplication@@QAEAAVeCCameraBase@@XZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, UpdateTick, "Engine.dll", "?UpdateTick@eCApplication@@IAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, PlayVideo, "Engine.dll", "?PlayVideo@eCApplication@@QAEXABVbCString@@@Z");
    //DETOUR_EXTERN_MEMBER(eCApplication, Run, "Engine.dll", "?Run@eCApplication@@QAE?AW4bEResult@@XZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, Process, "Engine.dll", "?Process@eCApplication@@QAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, IsInitialised, "Engine.dll", "?IsInitialised@eCApplication@@SG_NXZ");
    //DETOUR_EXTERN_MEMBER(eCApplication, OnRun, "Engine.dll", "?OnRun@eCApplication@@UAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCModuleAdmin, Process, "Engine.dll", "?Process@eCModuleAdmin@@QAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCModuleAdmin, PostProcess, "Engine.dll", "?PostProcess@eCModuleAdmin@@QAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCEntityAdmin, Process, "Engine.dll", "?Process@eCEntityAdmin@@QAEXXZ");
    //DETOUR_EXTERN_MEMBER(eCEntityAdmin, EnableProcessing, "Engine.dll", "?EnableProcessing@eCEntityAdmin@@QAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntityAdmin, UpdateProcessingRangeEntity, "Engine.dll", "?UpdateProcessingRangeEntity@eCEntityAdmin@@QAEXPAVeCEntity@@AAV?$bTSmallArray@PAVeCEntity@@@@1@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, EnterProcessingRange, "Engine.dll", "?EnterProcessingRange@eCEntity@@IAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, ExitProcessingRange, "Engine.dll", "?ExitProcessingRange@eCEntity@@IAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, PreProcess, "Engine.dll", "?PreProcess@eCEntity@@QAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, Process, "Engine.dll", "?Process@eCEntity@@QAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, PostProcess, "Engine.dll", "?PostProcess@eCEntity@@QAEX_N@Z");
    //DETOUR_EXTERN_MEMBER(eCEntity, HasProcessingRangeEntered, "Engine.dll", "?HasProcessingRangeEntered@eCEntity@@QBE_NXZ");
    //DETOUR_EXTERN_MEMBER(eCEntity, IsEnabled, "Engine.dll", "?IsEnabled@eCEntity@@QBE_NXZ");
    //DETOUR_EXTERN_MEMBER(eCPVSPrefetcher3, GetNonDeactivationCell, "Engine.dll", "?GetNonDeactivationCell@eCPVSPrefetcher3@@QAEPAVeCPVSCellItem@@XZ");
    //DETOUR_EXTERN_MEMBER(bCTimer, GetTimeStamp, "SharedBase.dll", "?GetTimeStamp@bCTimer@@SGKXZ");
    //DETOUR_EXTERN_MEMBER(bCMemoryAdmin, GetInstance, "SharedBase.dll", "?GetInstance@bCMemoryAdmin@@SGAAV1@XZ");
}
