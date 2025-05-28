#!/usr/bin/env python3

import os
import io
import sys
import shutil
import hashlib
import zipfile
import urllib.error
import urllib.request


def verify_bytes(data, hash_func, target_hash):
    myhash = hash_func(data)
    return myhash.hexdigest() == target_hash


if __name__ == '__main__':
    output_filename = sys.argv[1]
    assert not os.path.exists(output_filename)
    stock_hornmod_path = os.path.join('resources', 'KL_HORNMOD-CE_V2.pk3')
    if not os.path.exists(stock_hornmod_path):
        print(f'{stock_hornmod_path} not found. Attempting to download...')
        try:
            urllib.request.urlretrieve('https://mb.srb2.org/addons/hornmod-championship-edition.2418/download', stock_hornmod_path)
        except urllib.error.HTTPError:
            print('Failed to download! You should manually download KL_HORNMOD-CE_V2.pk3 from https://mb.srb2.org/addons/hornmod-championship-edition.2418/download and put it into the resources directory.')
            sys.exit(1)
        else:
            print(f'{stock_hornmod_path} downloaded.')

    with open(stock_hornmod_path, 'rb') as stock_hornmod_file:
        stock_hornmod_data = stock_hornmod_file.read()
    assert verify_bytes(stock_hornmod_data, hashlib.md5, 'd09a7b1c6ae1a284b46aab170d0fb809') # I'm not a fan of md5, but the SRB2Kart forums use md5 for mod hashes
    assert verify_bytes(stock_hornmod_data, hashlib.sha512, 'fff66dd83bd2da9863904b18ca6d20498829796f95ed37d17449a7236d1cd4e42fe683a7624a64d92f58d69ef00e80d13a365ade6a38be80da80a7f122155e6c')
    print(f'{stock_hornmod_path} verified!')

    with zipfile.ZipFile(io.BytesIO(stock_hornmod_data), 'r') as input_pk3_file:
        with zipfile.ZipFile(output_filename, 'w') as output_pk3_file:
            def copy_packed_file(input_path, output_path):
                with input_pk3_file.open(input_path, 'r') as source_file:
                    with output_pk3_file.open(output_path, 'w') as dest_file:
                        shutil.copyfileobj(source_file, dest_file)
            for filepath in input_pk3_file.namelist():
                if filepath.lower().startswith('sfx') or filepath.lower().startswith('sprites'):
                    copy_packed_file(filepath, filepath)
            output_pk3_file.mkdir('lua')
            for filename in ['hornmod-ce.lua', 'config.lua', 'pseudorng.lua']:
                copy_packed_file('lua/' + filename, 'lua/' + filename)
