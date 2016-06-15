#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import cv2 as cv
import struct


def read_seq(path):
    
    def read_header(ifile):
        feed = ifile.read(4)
        norpix = ifile.read(24)
        version = struct.unpack('@i', ifile.read(4))
        length = struct.unpack('@i', ifile.read(4))
        assert(length != 1024)
        descr = ifile.read(512)
        params = [struct.unpack('@i', ifile.read(4))[0] for i in range(0,9)]
        fps = struct.unpack('@d', ifile.read(8))
        # skipping the rest
        ifile.read(432)
        image_ext = {100:'raw', 102:'jpg',201:'jpg',1:'png',2:'png'}
        return {'w':params[0],'h':params[1],
                'bdepth':params[2],
                'ext':image_ext[params[5]],
                'format':params[5],
                'size':params[4],
                'true_size':params[8],
                'num_frames':params[6]}
    
    ifile = open(path, 'rb')
    params = read_header(ifile)
    bytes = open(path, 'rb').read()

    # this is freaking magic, but it works
    extra = 8
    s = 1024
    seek = [0]*(params['num_frames']+1)
    seek[0] = 1024
    
    images = []
    
    for i in range(0, params['num_frames']):
        try:
            tmp = struct.unpack_from('@I', bytes[s:s+4])[0]
            s = seek[i] + tmp + extra
            if i == 0:
                val = struct.unpack_from('@B', bytes[s:s+1])[0]
                if val != 0:
                    s -= 4
                else:
                    extra += 8
                    s += 8
            seek[i+1] = s
        
            nbytes = struct.unpack_from('@i', bytes[s:s+4])[0]
            I = bytes[s+4:s+nbytes]
            
            tmp_file = '/tmp/img%d.jpg' % i
            open(tmp_file, 'wb+').write(I)
             
            img = cv.imread(tmp_file)
            #img = cv.cvtColor(img, cv.COLOR_BGR2RGB)  test if this change the color
            images.append(img)
        except:
            pass

    return images



def save_img(dname, fn, i, frame):
    #print("I am in")
    cv.imwrite('{}/{}_{}_{}.png'.format(
        out_dir, os.path.basename(dname),
        os.path.basename(fn).split('.')[0], i), frame)
    

out_dir = 'test_data/images'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
for dname in sorted(glob.glob('test_data/set*')):
    for fn in sorted(glob.glob('{}/*.seq'.format(dname))):
        #cap = cv.VideoCapture(fn)
        images = read_seq(fn)
        i = 0
        for image in images:
            #ret, frame = cap.read()
            #if not ret:
            #    print("oops")
            #    break
            save_img(dname, fn, i, image)

            i += 1
        print(fn)
