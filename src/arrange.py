#!/usr/bin/python3
import sys
import json
import os
from pathlib import Path

def open_file(filename):
  '''
  Load json
  '''
  f = open(filename)
  s = f.readlines()
  f.close()
  s = "".join([i.rstrip('\n') for i in s])
  s = json.loads(s)
  return s

def move_files(s, target_dir):
  '''
  Move a file to target directory by appending directory path
  For use with train, valid, test.json experiments
  '''
  for img in s['images']:
    Path(f"./{img['file_name']}").rename(f"{target_dir}{img['file_name']}")
  

def main():
  '''
  Generic main method
  '''
  filename = sys.argv[1]
  sanity = filename.split("_")[0]
  dest = sys.argv[2]
  if dest[-1] != "/":
    dest = f"{dest}/"
  s = open_file(filename)
  move_files(s, dest)

main()