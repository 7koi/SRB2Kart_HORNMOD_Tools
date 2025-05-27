#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import hashlib
import subprocess
import urllib.request


def horns_to_lua(horns, hell=False):
    lua = ''
    for ogg_file, ogg_hash in horns:
        horn_name = ogg_file.replace('"', '').replace('\\', '')
        lua += f'HORNMOD_Add{"Hell" if hell else ""}Horns({{base = 1, name = "sfx_{ogg_hash.lower()}", info = "{horn_name}"}})\r\n'
    return lua


def copy_horns(sourcedir, destdir):
    horns = []
    for ogg_file in os.listdir(sourcedir):
        if ogg_file == '.gitignore':
            continue
        ogg_path = os.path.join(sourcedir, ogg_file)
        ogg_hash = hashlib.sha1(ogg_file.encode('utf-8')).hexdigest()[:6].upper()
        if ogg_file.lower().endswith('.ogg'):
            ogg_file = ogg_file[:-4]
        horns.append((ogg_file, ogg_hash))
        shutil.copy(ogg_path, os.path.join(destdir, f'DS{ogg_hash}.ogg'))
    return horns


def clean_dir(dirpath):
    for horn_filename in os.listdir(dirpath):
        os.remove(os.path.join(dirpath, horn_filename))


if __name__ == '__main__':
    output_filename = sys.argv[1]
    assert not os.path.exists(output_filename)
    stock_hornmod_path = os.path.join('resources', 'KL_HORNMOD-CE_V2.pk3')
    if not os.path.exists(stock_hornmod_path):
        print(f'{stock_hornmod_path} not found. Attempting to download...')
        urllib.request.urlretrieve('https://mb.srb2.org/addons/hornmod-championship-edition.2418/download', stock_hornmod_path)
        with open(stock_hornmod_path, 'rb') as stock_hornmod_file:
            stock_hornmod_hash = hashlib.sha512(stock_hornmod_file.read())
            assert stock_hornmod_hash.hexdigest() == 'fff66dd83bd2da9863904b18ca6d20498829796f95ed37d17449a7236d1cd4e42fe683a7624a64d92f58d69ef00e80d13a365ade6a38be80da80a7f122155e6c'
        print(f'{stock_hornmod_path} downloaded and verified!')

    working_dir = 'working_directory'
    os.mkdir(working_dir)
    shutil.unpack_archive(stock_hornmod_path, format='zip', extract_dir=working_dir)
    nephorns_path = os.path.join(working_dir, 'nephorns')
    clean_dir(nephorns_path)
    clean_dir(os.path.join(working_dir, 'horns'))
    clean_dir(os.path.join(working_dir, 'hellhorns'))

    os.remove(os.path.join(working_dir, 'lua', 'basehorns.lua'))

    shutil.copy(os.path.join('resources', 'init.lua'), working_dir)

    horns = copy_horns('horns', nephorns_path)
    hellhorns = copy_horns('hellhorns', nephorns_path)
    lua_lines = horns_to_lua(horns)
    hell_lua_lines = horns_to_lua(hellhorns, hell=True)
    lua_text = lua_lines + hell_lua_lines
    with open(os.path.join(working_dir, 'lua', 'basehorns.lua'), 'w') as lua_file:
        lua_file.write(lua_text)

    cwd = os.getcwd()
    os.chdir(working_dir)
    subprocess.run(['zip', '-r', os.path.join('..', output_filename)] + glob.glob('*'))
    os.chdir(cwd)

    shutil.rmtree(working_dir)
