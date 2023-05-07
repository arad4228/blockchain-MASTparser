# -*- coding: utf-8 -*-
#
# Blockchain parser
# Copyright (c) 2015-2022 Denis Leonov <466611@gmail.com>
#

from collections import OrderedDict
import os
import sys
import datetime
import hashlib
import json


def reverse(input):
    L = len(input)
    if (L % 2) != 0:
        return None
    else:
        block = ''
        L = L // 2
        for i in range(L):
            T = input[i * 2] + input[i * 2 + 1]
            block = T + block
            T = ''
        return (block);


def merkle_root(lst):  # https://gist.github.com/anonymous/7eb080a67398f648c1709e41890f8c44
    sha256d = lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest()
    hash_pair = lambda x, y: sha256d(x[::-1] + y[::-1])[::-1]
    if len(lst) == 1: return lst[0]
    if len(lst) % 2 == 1:
        lst.append(lst[-1])
    return merkle_root([hash_pair(x, y) for x, y in zip(*[iter(lst)] * 2)])


def read_bytes(file, n, byte_order='L'):
    data = file.read(n)
    if byte_order == 'L':
        data = data[::-1]
    data = data.hex().upper()
    return data


def read_varint(file):
    b = file.read(1)
    bInt = int(b.hex(), 16)
    c = 0
    data = ''
    if bInt < 253:
        c = 1
        data = b.hex().upper()
    if bInt == 253: c = 3
    if bInt == 254: c = 5
    if bInt == 255: c = 9
    for j in range(1, c):
        b = file.read(1)
        b = b.hex().upper()
        data = b + data
    return data


sys.setrecursionlimit(1000000000)

dirBlock = 'D:/BitCoinCore_Data/testnet3/blocks/'  # Directory where blk*.dat files are stored
dirResult = './result/'  # Directory where to save parsing results

# Read Folder Data for list of blockChain Data Names
# And Sorting this list
fList = os.listdir(dirBlock)
fList = [x for x in fList if (x.endswith('.dat') and x.startswith('blk'))]
fList.sort()
fList.remove("blk00215.dat")
fList.remove("blk00214.dat")

for i in fList:
    totalJsonList = OrderedDict()
    totalJsonList['Block info'] = []
    nameSrc = i
    nameblock = nameSrc.replace('.dat', '.json')
    a = 0
    t = dirBlock + nameSrc
    print('Start ' + t + ' in ' + str(datetime.datetime.now()))

    f = open(t, 'rb')
    tmpHex = ''
    fSize = os.path.getsize(t)
    while f.tell() != fSize:
        tmpHex = read_bytes(f, 4)
        block = OrderedDict()
        block['Magic number'] = tmpHex

        tmpHex = read_bytes(f, 4)
        block['Block size'] = tmpHex

        tmpPos3 = f.tell()
        tmpHex = read_bytes(f, 80, 'B')
        tmpHex = bytes.fromhex(tmpHex)
        tmpHex = hashlib.new('sha256', tmpHex).digest()
        tmpHex = hashlib.new('sha256', tmpHex).digest()
        tmpHex = tmpHex[::-1]
        tmpHex = tmpHex.hex().upper()
        block['Current Block SHA256'] = tmpHex
        f.seek(tmpPos3, 0)

        tmpHex = read_bytes(f, 4)
        block['Version number'] = tmpHex

        tmpHex = read_bytes(f, 32)
        block['Prev Block SHA256'] = tmpHex

        tmpHex = read_bytes(f, 32)
        block['MerkleRoot hash'] = tmpHex

        MerkleRoot = tmpHex
        tmpHex = read_bytes(f, 4)
        block['Time stamp'] = tmpHex

        tmpHex = read_bytes(f, 4)
        block['Difficulty'] = tmpHex

        tmpHex = read_bytes(f, 4)
        block['Random number'] = tmpHex

        tmpHex = read_varint(f)
        txCount = int(tmpHex, 16)
        block['Transactions count'] = str(txCount)
        block['TX'] = []


        tmpHex = ''
        RawTX = ''
        tx_hashes = []
        for k in range(txCount):
            tx = OrderedDict()
            tmpHex = read_bytes(f, 4)
            tx['TX version number'] = tmpHex

            RawTX = reverse(tmpHex)
            tmpHex = ''
            Witness = False
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            if bInt == 0:
                tmpB = ''
                f.seek(1, 1)
                c = 0
                c = f.read(1)
                bInt = int(c.hex(), 16)
                tmpB = c.hex().upper()
                Witness = True
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = hex(bInt)[2:].upper().zfill(2)
                tmpB = ''
            if bInt == 253: c = 3
            if bInt == 254: c = 5
            if bInt == 255: c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            inCount = int(tmpHex, 16)

            tx['Inputs count'] = tmpHex
            tmpHex = tmpHex + tmpB
            RawTX = RawTX + reverse(tmpHex)
            tx['TxData list'] = []
            for m in range(inCount):
                txInner = OrderedDict()
                tmpHex = read_bytes(f, 32)
                txInner['TX from hash'] = tmpHex

                RawTX = RawTX + reverse(tmpHex)
                tmpHex = read_bytes(f, 4)
                txInner['N output'] = tmpHex

                RawTX = RawTX + reverse(tmpHex)
                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253: c = 3
                if bInt == 254: c = 5
                if bInt == 255: c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = read_bytes(f, scriptLength, 'B')
                txInner['Input script'] = tmpHex

                RawTX = RawTX + tmpHex
                tmpHex = read_bytes(f, 4, 'B')
                txInner['Sequence number'] = tmpHex
                RawTX = RawTX + tmpHex
                tmpHex = ''
                tx['TxData list'].append(txInner)
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = b.hex().upper()
                tmpB = ''
            if bInt == 253: c = 3
            if bInt == 254: c = 5
            if bInt == 255: c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            outputCount = int(tmpHex, 16)
            tmpHex = tmpHex + tmpB
            tx['Outputs count'] = str(outputCount)

            RawTX = RawTX + reverse(tmpHex)
            for m in range(outputCount):
                tmpHex = read_bytes(f, 8)
                Value = tmpHex
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253: c = 3
                if bInt == 254: c = 5
                if bInt == 255: c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = read_bytes(f, scriptLength, 'B')
                tx['Value'] = Value
                tx['Output script'] = tmpHex

                RawTX = RawTX + tmpHex
                tmpHex = ''

            if Witness:
                for m in range(inCount):
                    tmpHex = read_varint(f)
                    WitnessLength = int(tmpHex, 16)
                    for j in range(WitnessLength):
                        tmpHex = read_varint(f)
                        WitnessItemLength = int(tmpHex, 16)
                        tmpHex = read_bytes(f, WitnessItemLength)
                        tx['Witness ' + str(m) + ' ' + str(j) + ' ' + str(WitnessItemLength)] = tmpHex

            Witness = False
            tmpHex = read_bytes(f, 4)
            tx['Lock time'] = tmpHex

            RawTX = RawTX + reverse(tmpHex)
            tmpHex = RawTX
            tmpHex = bytes.fromhex(tmpHex)
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = tmpHex[::-1]
            tmpHex = tmpHex.hex().upper()
            tx['TX hash'] = tmpHex
            tx_hashes.append(tmpHex)

            tmpHex = ''
            RawTX = ''
            block['TX'].append(tx)
        a += 1
        tx_hashes = [bytes.fromhex(h) for h in tx_hashes]
        tmpHex = merkle_root(tx_hashes).hex().upper()
        if tmpHex != MerkleRoot:
            print('Merkle roots does not match! >', MerkleRoot, tmpHex)
        totalJsonList['Block info'].append(block)

    f.close()
    with open(dirResult + nameblock, 'w', encoding="utf-8") as f:
        json.dump(totalJsonList, f, ensure_ascii=False, indent='\t')
    f.close()
