# -*- coding: utf-8 -*-
from __future__ import division

import zlib
import struct
from collections import namedtuple

import numpy as np


LCF_VERSION = 0x11CEb001

LcfHeader = namedtuple('LcfHeader', 'version bpp w h bsize_w bsize_h nf cdata_left dsize')
LcfBlock = namedtuple('LcfBlock', 'hdr frame_deltas frames')


class LcfFrame(object):
    def __init__(self, frame, block, block_idx, frame_idx):
        self.frame = frame
        self.block = block
        self.block_idx = block_idx
        self.frame_idx = frame_idx
        self.delta = block.frame_deltas[frame_idx]

    def get_array(self):
        hdr = self.block.hdr
        arr = np.ndarray(shape=(0, hdr.w, 3), dtype=np.uint8)
        for y, ypos in enumerate(xrange(0, hdr.h, hdr.bsize_h)):
            hei = min(hdr.h - ypos, hdr.bsize_h)
            line = np.ndarray(shape=(hei, 0, 3), dtype=np.uint8)
            for x, xpos in enumerate(xrange(0, hdr.w, hdr.bsize_w)):
                # wid = min(hdr.w - xpos, hdr.bsize_w)
                line = np.concatenate((line, self.frame[x][y]), axis=1)
            arr = np.concatenate((arr, line), axis=0)
        return arr


class BadBlock(Exception):
    pass


class CorruptedBlock(BadBlock):
    pass


def read(fd, size):
    data = fd.read(size)
    if len(data) != size:
        raise BadBlock("Cannot read %s bytes from file" % size)
    return data


def read_block(fd):
    hdr = LcfHeader(*struct.unpack('iiiiiiiii', read(fd, 9 * 4)))
    if hdr.version != LCF_VERSION:
        raise BadBlock("Wrong LCF version")
    if hdr.nf < 1 or hdr.nf > 1024:
        raise BadBlock("Wrong number of frames")
    if hdr.bpp != 16:
        raise CorruptedBlock("Wrong bits per pixel")
    frame_deltas = [struct.unpack('i', read(fd, 4))[0] for f in xrange(hdr.nf)]
    cdata = read(fd, hdr.cdata_left)
    decompress = zlib.decompressobj()
    data = decompress.decompress(cdata)
    if hdr.dsize != len(data):
        raise CorruptedBlock("Wrong uncompressed data size")
    # Decode slices
    bytespersample = (hdr.bpp + 7) // 8
    # Setup frames as blocks of ns_x * ns_y slices
    ns_x = (hdr.w + hdr.bsize_w - 1) // hdr.bsize_w
    ns_y = (hdr.h + hdr.bsize_h - 1) // hdr.bsize_h
    frames = [[[[] for y in xrange(ns_y)] for x in xrange(ns_x)] for f in xrange(hdr.nf)]
    sp = 0
    for y, ypos in enumerate(xrange(0, hdr.h, hdr.bsize_h)):
        hei = min(hdr.h - ypos, hdr.bsize_h)
        for x, xpos in enumerate(xrange(0, hdr.w, hdr.bsize_w)):
            wid = min(hdr.w - xpos, hdr.bsize_w)
            sz1 = hei * wid * bytespersample
            cnt = 0
            for i in xrange(hdr.nf):
                if cnt > 0:
                    cnt -= 1
                else:
                    buff = data[sp:sp + sz1]
                    if len(buff) != sz1:
                        raise CorruptedBlock("Wrong size read!")
                    arr = np.fromstring(buff, dtype=np.uint16)
                    lvalid = np.zeros(arr.size * 3, np.uint8)
                    lvalid.view()[0::3] = (arr << 3) & 0xf8
                    lvalid.view()[1::3] = (arr >> 3) & 0xfc
                    lvalid.view()[2::3] = (arr >> 8) & 0xf8
                    lvalid.shape = (hei, wid, 3)
                    sp += sz1
                    if i < hdr.nf - 1:
                        cnt = ord(data[sp])
                        sp += 1
                frames[i][x][y] = lvalid
    if sp != len(data):
        print "Not all data consumed (%s/%s)!" % (sp, len(data))
    return LcfBlock(hdr, frame_deltas, frames)


def process(filename):
    blocks = []
    with open(filename) as fd:
        while True:
            try:
                blocks.append(read_block(fd))
            except CorruptedBlock as e:
                print(e)
                break
            except BadBlock:
                break
    return [LcfFrame(f, b, i, j) for i, b in enumerate(blocks) for j, f in enumerate(b.frames)]
