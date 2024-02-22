#!/usr/bin/python3
import sys
import json
COCO = 1
YOLO = 2
class Converter:
  def yolo_to_coco(yolobox, img_w = 1, img_h = 1):
    '''
      converts: yolo format [c_x, c_y, w, h]
            to: coco format [min_x, min_y, w, h]
    '''
    coco_bbox = lambda cx,cy,w,h,img_w,img_h: [((cx - (w/2)) * img_w), (((cy - h/2)) * img_h), w*img_w, h*img_h]
    cocobox = coco_bbox(yolobox[0],yolobox[1], yolobox[2],yolobox[3], img_w, img_h)
    return cocobox

  def coco_to_yolo(cocobox):
    '''
      converts: coco format [min_x, min_y, w, h]
            to: yolo format [c_x, c_y, w, h]
    '''
    yolo_bbox = lambda minx, miny, w, h : [(minx + w/2), (miny + h/2), w, h]
    yolobox = yolo_bbox (cocobox[0], cocobox[1], cocobox[2], cocobox[3])
    return yolobox  

  def conv_box(annotations, totype = COCO):
    '''
      wrapper for conversion functions
    '''
    if totype == COCO:
      for i in range(len(annotations)):
        # annotations[i]["category_id"] = 1
        annotations[i]["bbox"] = Converter.yolo_to_coco(annotations[i]["bbox"])
    
    elif totype == YOLO:
      for i in range(len(annotations)):
        annotations[i]["bbox"] = Converter.coco_to_yolo(annotations[i]["bbox"])
    else:
      print("type not specified!")
      return
    
      
      

def conv_json(filename, totype = COCO):
  ''' 
    json conversion wrapper
  '''

  f = open(filename, "r")
  s = f.readlines()
  f.close()
  
  s = "".join([i.rstrip("\n") for i in s])
  s = json.loads(s)

  annotations = s['annotations']
  Converter.conv_box(annotations, totype)
  s['annotations'] = annotations
  
  totype_str = "COCO" if totype==COCO else "YOLO"
  fn = filename.split("/")[-1]
  
  print(f"writing {totype_str}_{fn} ....")
  f = open(f"{totype_str}_{fn}", "w")
  f.write(json.dumps(s,indent=2))
  f.close()

def main():
  if len(sys.argv) < 2:
    print("must input filename")
    exit(0)
  elif sys.argv[1].split(".")[-1] != "json":
    print("must input file with json suffix")
    exit(0)
  mode = COCO
  if len(sys.argv) < 3:
    print("no mode specified, assuming YOLO to COCO")
  
  conv_json(sys.argv[1], mode)
  
main()