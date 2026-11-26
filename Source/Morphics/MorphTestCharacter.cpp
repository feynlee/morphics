#include "MorphTestCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputCoreTypes.h"
#include "UObject/ConstructorHelpers.h"

AMorphTestCharacter::AMorphTestCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(42.f, 96.f);

	// Centered third person: the body turns to face its movement direction.
	bUseControllerRotationYaw = false;
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.f, 540.f, 0.f);
	GetCharacterMovement()->MaxWalkSpeed = 600.f;

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 380.f;
	CameraBoom->SocketOffset = FVector(0.f, 0.f, 60.f); // centered behind the character, slightly raised
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 18.f;
	CameraBoom->bUsePawnControlRotation = true;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);

	// Placeholder body: an engine cylinder sized to the capsule. Swap for a real mesh later.
	PlaceholderBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlaceholderBody"));
	PlaceholderBody->SetupAttachment(RootComponent);
	PlaceholderBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	PlaceholderBody->SetRelativeLocation(FVector(0.f, 0.f, -96.f));
	PlaceholderBody->SetRelativeScale3D(FVector(0.8f, 0.8f, 1.9f));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Cylinder.Succeeded())
	{
		PlaceholderBody->SetStaticMesh(Cylinder.Object);
	}
}

void AMorphTestCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	PlayerInputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this, &ACharacter::Jump);
	PlayerInputComponent->BindKey(EKeys::SpaceBar, IE_Released, this, &ACharacter::StopJumping);

	// Plain key axes, so the test level needs no Input Mapping asset.
	PlayerInputComponent->BindAxisKey(EKeys::W, this, &AMorphTestCharacter::MoveForward);
	PlayerInputComponent->BindAxisKey(EKeys::S, this, &AMorphTestCharacter::MoveBack);
	PlayerInputComponent->BindAxisKey(EKeys::D, this, &AMorphTestCharacter::MoveRight);
	PlayerInputComponent->BindAxisKey(EKeys::A, this, &AMorphTestCharacter::MoveLeft);
	PlayerInputComponent->BindAxisKey(EKeys::MouseX, this, &AMorphTestCharacter::Turn);
	PlayerInputComponent->BindAxisKey(EKeys::MouseY, this, &AMorphTestCharacter::LookUp);
}

void AMorphTestCharacter::Move(EAxis::Type Axis, float Value)
{
	if (Controller && Value != 0.f)
	{
		const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
		AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(Axis), Value);
	}
}

void AMorphTestCharacter::Turn(float Value)
{
	AddControllerYawInput(Value);
}

void AMorphTestCharacter::LookUp(float Value)
{
	AddControllerPitchInput(-Value);
}

AMorphTestGameMode::AMorphTestGameMode()
{
	DefaultPawnClass = AMorphTestCharacter::StaticClass();
}
