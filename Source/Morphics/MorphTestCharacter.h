#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "MorphTestCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UStaticMeshComponent;

/** Placeholder centered third-person character for the M1 test level. WASD to move, mouse to look, Space to jump. */
UCLASS()
class AMorphTestCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AMorphTestCharacter();

protected:
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

private:
	void MoveForward(float Value) { Move(EAxis::X, Value); }
	void MoveBack(float Value) { Move(EAxis::X, -Value); }
	void MoveRight(float Value) { Move(EAxis::Y, Value); }
	void MoveLeft(float Value) { Move(EAxis::Y, -Value); }
	void Move(EAxis::Type Axis, float Value);
	void Turn(float Value);
	void LookUp(float Value);

	UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> CameraBoom;
	UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> FollowCamera;
	UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> PlaceholderBody;
};

/** Game mode that spawns AMorphTestCharacter. Set as the GameMode Override in the test map. */
UCLASS()
class AMorphTestGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AMorphTestGameMode();
};
