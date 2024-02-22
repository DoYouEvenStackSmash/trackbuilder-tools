#!/usr/bin/python3
import json
import sys
import time
def json_loader(filename):

  '''
  Load json file
  Returns a json object
  '''
  s = []
  f = open(filename)
  s = f.readlines()
  f.close()
  s = json.loads("".join([i.rstrip("\n") for i in s]))
  return s

class ImageData:
  def __init__(self, filename, w, h):
    self.filename = filename
    self.w = w
    self.h = h
    self.annotations = []

  def get_text_name(self):
    return self.filename[:-3]+"txt"

  def get_name(self):
    print(self.filename)
  
  def get_dims(self):
    print(self.w,self.h)

  def add_annotation(self, c, bbox):
    self.annotations.append(ObjTuple(c, bbox[0],bbox[1],bbox[2],bbox[3]))

  def adjust_dims(self):
    for i in range(len(self.annotations)):
      self.annotations[i].adjust(self.w,self.h)

  def print_boxes(self):
    # print(self.filename)
    strs = []
    for i in self.annotations:
      # print("\t",end="")
      strs.append(i.dump_anno())
    return "\n".join(strs)

class ObjTuple:
  def __init__(self, c, cx,cy,w,h):
    self.anno = [c,cx,cy,w,h]

  def adjust(self,w,h):
    self.anno = [self.anno[0],self.anno[1] / w, self.anno[2] / h, self.anno[3] / w, self.anno[4] / h]

  def dump_anno(self):
    return f'{self.anno[0]} {self.anno[1]} {self.anno[2]} {self.anno[3]} {self.anno[4]}'

def conv_to_yolo(loco):
  images = []
  for i in loco['images']:
    name = i["file_name"].split('/')[-1]
    w,h = i['width'],i['height']
    images.append(ImageData(name,w,h))
  for i in images:
    # i.get_name()
    print(i.get_text_name())
    i.get_dims()
  
  for i in loco['annotations']:
    ID = i['image_id']
    c = i['category_id']
    images[ID].add_annotation(c, i['bbox'])
  
  for i in images:
  #   # i.print_boxes()
    i.adjust_dims()
  #   i.print_boxes()
  # filehandles = []
  for i in images:
    f = open(i.get_text_name(),"w")
    data = i.print_boxes()
    f.write(data)
    f.close()
    
  

def main():
  s = json_loader(sys.argv[1])
  conv_to_yolo(s)

main()