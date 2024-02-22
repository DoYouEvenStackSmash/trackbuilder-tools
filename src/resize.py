#!/usr/bin/python3
import json
import sys
import cv2

def resize(fn):
  '''
  Load json
  '''
  f = open(fn)
  s = f.readlines()
  f.close()
  s = "".join([i.rstrip("\n") for i in s])
  s = json.loads(s)
  return s

scale_percent = 80
def mod_images(s):
  '''
  Use cv2.resize to adjust the shape of all images in a LOCO file
  '''
  for img in s['images']:
    img1 = cv2.imread(img['file_name'])
    
    w = int(img['width'] * scale_percent / 100)
    h = int(img['height'] * scale_percent / 100)
    dim = (w, h)
    
    # change actual image size
    resized = cv2.resize(img1, dim, interpolation = cv2.INTER_AREA)
    
    # update image object
    fn = f"rz_{img['file_name'].split('/')[-1]}"
    img['file_name'] = fn
    img['height'] = h
    img['width'] = w
    
    # write image with new shape to disk
    cv2.imwrite(f"{fn}",resized)
  return s

def mod_annos(s):
  '''
  Scale annotation bounding boxes according to image_id width and height
  '''
  x = scale_percent / 100.
  for anno in s['annotations']:
    anno['bbox'] = [anno['bbox'][0] * x, anno['bbox'][1] * x, anno['bbox'][2] * x, anno['bbox'][3]* x]
    anno['area'] = anno['bbox'][2] * anno['bbox'][3]
  return s

def serialize(filename,s):
  '''
  Serialize new LOCO file
  '''
  f = open(f"rz_{filename}","w")
  f.write(json.dumps(s, indent=2))
  f.close()

def main():
  '''
  generic main 
  '''
  for fn in sys.argv[1:]:
    s = resize(fn)
    s = mod_images(s)
    s = mod_annos(s)
    serialize(fn, s)

if __name__ == '__main__':
  main()