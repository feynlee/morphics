"""Import Content/Data/Generated/Forms.json into /Game/Data/DT_Forms (row type FMorphFormRow).
Run headless (use a path without spaces for -script, or run from the editor's Python console):
  UnrealEditor-Cmd.exe Morphics.uproject -run=pythonscript -script=<path>/import_forms.py
"""
import unreal

SRC = unreal.Paths.project_content_dir() + "Data/Generated/Forms.json"
DEST_DIR, DEST_NAME = "/Game/Data", "DT_Forms"
ROW_STRUCT = unreal.load_object(None, "/Script/Morphics.MorphFormRow")

path = DEST_DIR + "/" + DEST_NAME
if unreal.EditorAssetLibrary.does_asset_exist(path):
    # Reuse the asset so a re-run refreshes the rows without a delete prompt.
    dt = unreal.load_asset(path)
else:
    factory = unreal.DataTableFactory()
    factory.struct = ROW_STRUCT
    dt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(DEST_NAME, DEST_DIR, unreal.DataTable, factory)
ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(dt, SRC, ROW_STRUCT)
unreal.EditorAssetLibrary.save_loaded_asset(dt)
print("IMPORT_RESULT ok=%s rows=%d" % (ok, len(dt.get_row_names())))
