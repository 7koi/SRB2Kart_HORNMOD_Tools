#!/usr/bin/env python3

import os
import sys
import shutil
import hashlib
import zipfile


def horns_to_lua(horns, hell=False):
    lua = ''
    for ogg_file, ogg_hash in horns:
        horn_name = ogg_file.replace('"', '').replace('\\', '')
        lua += f'HORNMOD_Add{"Hell" if hell else ""}Horns({{base = 1, name = "sfx_{ogg_hash.lower()}", info = "{horn_name}"}})\r\n'
    return lua


def copy_horns_to_archive(sourcedir, destdir, archive):
    horns = []
    for ogg_file in os.listdir(sourcedir):
        if '.gitignore' in ogg_file:
            continue
        ogg_path = os.path.join(sourcedir, ogg_file)
        ogg_hash = hashlib.sha1(ogg_file.encode('utf-8')).hexdigest()[:6].upper()
        if ogg_file.lower().endswith('.ogg'):
            ogg_file = ogg_file[:-4]
        horns.append((ogg_file, ogg_hash))
        with open(ogg_path, 'rb') as source_file:
            with archive.open(os.path.join(destdir, f'DS{ogg_hash}.ogg'), 'w') as dest_file:
                shutil.copyfileobj(source_file, dest_file)
    return horns


if __name__ == '__main__':
    output_filename = sys.argv[1]
    assert not os.path.exists(output_filename)

    with zipfile.ZipFile(output_filename, 'w') as output_pk3_file:
        output_pk3_file.mkdir('horns')
        output_pk3_file.mkdir('hellhorns')

        horns = copy_horns_to_archive('horns', 'horns', output_pk3_file)
        hellhorns = copy_horns_to_archive('hellhorns', 'hellhorns', output_pk3_file)
        lua_lines = horns_to_lua(horns)
        hell_lua_lines = horns_to_lua(hellhorns, hell=True)
        lua_text = lua_lines + hell_lua_lines
        output_pk3_file.mkdir('lua')
        with output_pk3_file.open(os.path.join('lua', 'basehorns.lua'), 'w') as lua_file:
            lua_file.write(lua_text.encode('utf-8'))
