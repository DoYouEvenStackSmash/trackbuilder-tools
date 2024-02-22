#!/usr/bin/python3
norm_size = [8,6,6,3,1]
reflected_size = norm_size
alt_size = [i * 2 for i in norm_size]
SPECIAL = 1
ALT_SPECIAL = 2
import json
from configs import base
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

def process_file(filename, sample_rate):
  '''
  process file and sample rate, take frames at sample_rate interval
  Writes a file to disk
  Does not return anything
  '''
  if sample_rate < 0: # exlude file altogether
    print(f"skipping {filename}")
    s = json_loader(filename)
    cat = s['categories']
    path = filename.split("/")[0]
    new_filename = f'sampled_{filename.split("/")[-1]}'
    out = {"categories":cat, "images":[], "annotations": []}
    outfile = open(f'{path}/{new_filename}',"w")
    outfile.write(json.dumps(out, indent=2))
    outfile.close()
    return
  
  # preprocessing file
  s = json_loader(filename)
  images = s['images']
  annos = s['annotations']
  cat = s['categories']

  for i in range(len(images)):
    images[i]['annos'] = []
  
  for anno in annos:
    images[anno['image_id']]['annos'].append(anno)

  sampled = images[0:len(images):sample_rate]
  new_images = []
  new_annos = []
  path = filename.split("/")[0]
  new_filename = f'sampled_{filename.split("/")[-1]}'
  # load allotations per filename
  for img in sampled:
    template = {'id':len(new_images), 'file_name':img['file_name'], 'width':img['width'],'height':img['height']}
    for a in img['annos']:
      a['image_id'] = len(new_images)
      new_annos.append(a)
    new_images.append(template)
  out = {"categories":cat, "images":new_images, "annotations": new_annos}
  # create new output file with sampled_ prefix
  outfile = open(f'{path}/{new_filename}',"w")
  outfile.write(json.dumps(out, indent=2))
  outfile.close()

def process_files():
  '''
  generic main method
  '''
  for p in base:
    for k,v in p.items():
      process_file(k,v)
  
process_files()