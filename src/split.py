#!/usr/bin/python3

import json
import random
import sys
from categories import *
def json_loader(filename):
  s = []
  f = open(filename)
  s = f.readlines()
  f.close()
  s = "".join([i.rstrip("\n") for i in s])
  s = json.loads(s)
  return s

isolate_name = lambda name: name.split('/')[-1]

def unpack_loco(loco_dicts):
  img_list,img_dict = [],{}
  sz_dict = {}
  print(len(loco_dicts))
  for loco_dict in loco_dicts:

    # print(loco_dict)
    for img in loco_dict['images']:
      fn = isolate_name(img['file_name'])
      img_dict[fn] = []
      sz_dict[fn] = (img['width'],img['height'])
      img_list.append(fn)

    #

    for anno in loco_dict['annotations']:
      img_dict[img_list[anno['image_id']]].append(anno)
    
  return img_dict, img_list, sz_dict

def shuffle(img_dict, img_list, sz_dict):
  '''
  splits loco data into train, valid, test at a 70/10/20 split
  '''
  tr, va, ts = 0,0,0
  tr = int(0.7 * len(img_list))
  va = int((len(img_list) - tr) * 0.3)
  ts = int(len(img_list) - (tr + va))  # for completeness, not necessary
  i = 0
   
  random.shuffle(img_list)
  tr_L = img_list[i : i + tr]
  i = i + tr
  
  va_L = img_list[i : i + va]
  i = i + va
  
  ts_L = img_list[i:]

  train = get_loco(tr_L, img_dict,sz_dict)
  valid = get_loco(va_L, img_dict,sz_dict)
  test = get_loco(ts_L, img_dict,sz_dict)
  return train, valid, test

def get_loco(namelist, img_dict, sz_dict):
  '''
  constructs loco json from a list of filenames
  '''
  img_list, anno_list = [],[]
  for fn in namelist:
    annos = img_dict[fn]
    w,h = sz_dict[fn]
    for a in annos:
      a['image_id'] = len(img_list)
      a['id'] = len(anno_list)
      anno_list.append(a)
    
    img = { 'id': len(img_list), 
            'file_name' : fn,
            'width' :w ,
            'height': h}
    img_list.append(img)
  
  loco = {'categories': CATEGORIES, 'images' : img_list, 'annotations' : anno_list}
  return loco

def merge_files(file_list):
  locos = []
  # print(file_list)
  for f in file_list:
    locos.append(json_loader(f))
  # print(loco_dicts)
  print(locos[-1])
  img_dict, img_list, sz_dict = unpack_loco(locos)
  out = get_loco(img_list, img_dict, sz_dict)
  f = open("merged.json", "w")
  f.write(json.dumps(out,indent=2))
  f.close()


def process_dict():
  filename = sys.argv[2]
  s = json_loader(filename)
    
  imd, iml, sz_dict = unpack_loco([s])
  train, valid, test = shuffle(imd, iml, sz_dict)

  # write files
  f = open(f'train_{filename}', "w")
  f.write(json.dumps(train, indent=2))
  f.close()
  f = open(f'valid_{filename}',"w")
  f.write(json.dumps(valid, indent=2))
  f.close()
  f = open(f'test_{filename}',"w")
  f.write(json.dumps(test, indent=2))
  f.close()

def do_split():
  command = sys.argv[1]
  if command == 'split':
    if len(sys.argv) == 3:
      process_dict()
    elif len(sys.argv) < 3:
      print("need to specify a file to split")
    else:
      print("can only split one file at a time")
  elif command == 'merge':
    if len(sys.argv) < 4:
      print("cannot merge file alone. add another?")
    else:
      merge_files(sys.argv[2:])
  else:
    print("no idea")
'''
def main():
  # argv[0] is program
  command = sys.argv[1]
  match command:
    case 'split':
      if len(sys.argv) == 3:
        process_dict()
      elif len(sys.argv) < 3:
        print("need to specify a file to split")
      else:
        print("can only split one file at a time")
    
    case 'merge':
      if len(sys.argv) < 4:
        print("cannot merge file alone. add another?")
      else:
        merge_files(sys.argv[2:])
    
    case 'convert':
      print("todo")
    case other:
      print("unknown command")
'''
# main()
do_split()

# process_dict()