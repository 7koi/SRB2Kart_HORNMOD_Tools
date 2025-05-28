# Usage
In every hornmod, there is a Lua script that has calls to HORNMOD_AddHorns() that serves as an index of the horns within the mod. This index contains their in-archive filenames and their titles. If you have a hornmod and know the in-archive path to the index Lua script, you can extract the horns from it with this command:
`python extract_horns.py path/to/hornmod.pk3 archive/path/to/lua/horn/index`

Once you have all your horns in their respective directories, you can build your own custom booster hornmod:
`python build_hornmod.py path/to/output.pk3`

If you want to create a skeleton hornmod with 0 horns in it but all the scripts to support booster hornmods, use this command:
`python create_skeleton_hornmod.py path/to/output.pk3`
