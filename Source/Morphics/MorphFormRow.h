#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "MorphFormRow.generated.h"

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
	/** Base category (skeleton and shared animations), for example base.quadruped. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString BaseId;
	/** Variant inside the base (size or proportion). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString VariantId;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Hp = 100.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Speed = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Power = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float Defense = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FString> SkillIds;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString DefaultSkinId;
	/** Soft path of the skeletal mesh. Empty in M1 (placeholder mesh). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FSoftObjectPath Model;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString UnlockType;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 UnlockCost = 0;
};
