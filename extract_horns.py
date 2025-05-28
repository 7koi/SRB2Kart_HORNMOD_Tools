#!/usr/bin/env python3

import os
import sys
import json
import shutil
import zipfile


def clean_line(line):
    cleaned_line = line.replace(' = ', ': ').replace('\\"', '').replace('\\', '\\\\').replace('base: ', '"base":' ).replace('name: ', '"name":' ).replace('info: ', '"info":' ).replace('extags: ', '"extags":' )
    # remove comments from the end of the line
    while cleaned_line[::-1].find('--') != -1 and cleaned_line[::-1].find('--') < cleaned_line[::-1].find('}'):
        comment_index = cleaned_line[::-1].find('--')
        cleaned_line = cleaned_line[:len(cleaned_line)-comment_index-len('--')]
    cleaned_line = cleaned_line.strip()
    if cleaned_line[-1] == ',':
        cleaned_line = cleaned_line[:-1]
    return cleaned_line


def windows_filename(filename):
    for a in '/\\:*"?<>|':
        filename = filename.replace(a, '')
    return filename


if __name__ == '__main__':
    source_path = sys.argv[1]
    index_path = sys.argv[2]
    ds_paths = {}
    with zipfile.ZipFile(source_path, 'r') as pk3_file:
        files = pk3_file.namelist()
        for filename in files:
            split_filename = filename.split('/')
            stripped_filename = split_filename[-1].upper().replace('.OGG', '')
            if stripped_filename.startswith('DS'):
                ds_paths[stripped_filename] = filename
        with pk3_file.open(index_path, 'r') as horninfo_file:
            horninfo_lines = horninfo_file.read().decode('utf-8').split('\n')
            hell = False
            for line in horninfo_lines:
                if 'HORNMOD_AddHorns' in line:
                    hell = False
                elif 'HORNMOD_AddHellHorns' in line:
                    hell = True
                elif '{' in line and not line.strip().startswith('--'):
                    cleaned_line = clean_line(line)
                    print(cleaned_line)
                    info_obj = json.loads(cleaned_line)
                    horn_filename = info_obj['name'].replace('sfx_', 'DS').upper()
                    horn_target_filename = windows_filename(info_obj['info']) + '.ogg'

                    if horn_filename in ds_paths:
                        horn_source_path = ds_paths[horn_filename]

                    if os.path.exists(os.path.join('horns', horn_target_filename)) or os.path.exists(os.path.join('hellhorns', horn_target_filename)):
                        print("WARNING: we've already seen this horn")
                    else:
                        horn_target_path = os.path.join('hellhorns' if hell else 'horns', horn_target_filename)
                        try:
                            print(f"Extracting {horn_source_path} to {horn_target_path}")
                            with pk3_file.open(horn_source_path, 'r') as source_file:
                                with open(horn_target_path, 'wb') as dest_file:
                                    shutil.copyfileobj(source_file, dest_file)
                            #pk3_file.extract(horn_source_path, horn_target_path)
                        except FileNotFoundError:
                            print("WARNING: file not found")
