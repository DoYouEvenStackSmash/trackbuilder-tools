#!/usr/bin/python3
import cv2

import sys
def open_file_list(filename):
  f = open(filename)
  s = f.readlines()
  f.close()
  s = [i.rstrip("\n") for i in s]
  return s

def convert_image(file_list):
  for infile in file_list:
    read = cv2.imread(infile)
    outfile = infile.split('/')[-1][:-3] + 'png'
    cv2.imwrite(outfile, read, [cv2.IMWRITE_PNG_COMPRESSION, 0])

def main():
  s = open_file_list(sys.argv[1])
  convert_image(s)

main()
  
