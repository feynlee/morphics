#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "MorphFormRow.generated.h"

/** One crafting component of a Morphic (for example 2 Ember Fox ears). */
USTRUCT(BlueprintType)
struct FMorphCraftComponent
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString Item;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 Count = 1;
};

/**
 * One row of the Forms Data Table.
 * Rows come from data/forms/*.json through tools/build_datatable.py.
 * Keep the field names the same as the keys in that script's output.
 */
USTRUCT(BlueprintType)
struct FMorphFormRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString FormId;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FText DisplayName;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString Role;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString Rarity;
	/** Body-type node, for example base.walker.canine.small. Skins fit this node and its ancestors. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString BaseId;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Hp = 100.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Speed = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Power = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Defense = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FString> SkillIds;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString DefaultSkinId;
	/** Soft path of the skeletal mesh. Empty in M1 (placeholder mesh). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FSoftObjectPath Model;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString UnlockType;
	/** Crafting data for earned morphs. Empty for other unlock types. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString CraftMorphic;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString CraftSourceBoss;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FMorphCraftComponent> CraftComponents;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString CraftSpectrumId;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 CraftSpectrumAmount = 0;
};
