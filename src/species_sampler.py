#!/usr/bin/python3
import sys
import json


def load_json(filename):
  '''
  Json loader
  Returns a JSON object
  '''
  f = open(filename)
  s = f.readlines()
  f.close()
  s = json.loads("".join([i.rstrip('\n') for i in s]))
  return s

def count_species(s):
  '''
  Iterates over the annotations of a LOCO file, counting occurrences of species
  Prints out a filename, and the constituent species with their ratio to the 
  overall pool.

  Returns nothing
  '''
  categories = s['categories']
  counters = [0] * len(categories)

  get_name = lambda img : img['name']

  annos = s['annotations']
  for anno in annos:
    counters[int(anno['category_id'])] += 1
  
  for i, img in enumerate(categories):
    if counters[i] == 0:
      continue
    print(f"\t{'%.3f'%(counters[i] / len(annos))}\t{counters[i]}\t{get_name(img)}")
  print("\n")

def main():
  # json_visitor()
  count_species(load_json(sys.argv[1]))

if __name__ == '__main__':
  main()