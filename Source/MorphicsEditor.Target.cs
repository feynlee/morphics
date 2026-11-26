using UnrealBuildTool;

public class MorphicsEditorTarget : TargetRules
{
	public MorphicsEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("Morphics");
	}
}
