#!/usr/bin/python3
import json
import sys
from cutter import *
def json_loader(filename):
    """Load a JSON file and return the parsed JSON object."""
    with open(filename, 'r') as f:
        return json.load(f)

class ImageData:
    def __init__(self, filename, width, height):
        self.filename = filename
        self.width = width
        self.height = height
        self.annotations = []
        self.shift = [0.0,0.0]

    def get_text_name(self):
        # Convert the filename to the expected YOLO label filename format
        return self.filename.replace(".png", ".txt")

    def add_annotation(self, category_id, bbox):
        # Add a normalized annotation in YOLO format
        x, y, box_width, box_height = bbox
        x, y, box_width, box_height = (np.array([x, y, box_width, box_height]) / np.array([self.width,self.height,self.width,self.height])).tolist()
        center_x = x + box_width / 2
        center_y = y + box_height / 2
        self.annotations.append(ObjTuple(category_id, center_x, center_y, box_width, box_height))

    def adjust_dims(self):
        # Normalize bounding boxes to YOLO format based on image dimensions
        for annotation in self.annotations:
            annotation.adjust(self.width, self.height)

    def print_boxes(self):
        # Convert all annotations to YOLO text format for saving
        return "\n".join(annotation.dump_anno() for annotation in self.annotations)

class ObjTuple:
    def __init__(self, category_id, center_x, center_y, width, height):
        # Initialize bounding box data with category and dimensions
        self.category_id = category_id
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
    
    def get_attr(self):
        return self.category_id,self.center_x,self.center_y,self.width,self.height
    
    def adjust(self, img_width, img_height):
        # Normalize the annotation coordinates to YOLO format
        self.center_x /= img_width
        self.center_y /= img_height
        self.width /= img_width
        self.height /= img_height

    def dump_anno(self):
        # Format the annotation as a YOLO label string
        return f"{self.category_id} {self.center_x:.6f} {self.center_y:.6f} {self.width:.6f} {self.height:.6f}"

from tqdm import tqdm
def conv_to_yolo(loco):
    # Create ImageData objects from JSON data
    fdict = {}
    images = []
    for image_info in loco['images']:
        filename = image_info["file_name"]
        width, height = image_info['width'], image_info['height']
        images.append(ImageData(filename, width, height))
    
    # Add annotations to the appropriate ImageData instance
    for annotation in loco['annotations']:
        image_id = annotation['image_id']
        category_id = annotation['category_id']
        images[image_id].add_annotation(category_id, annotation['bbox'])
    annotations = []
    k = 0
    for identifier,elem in tqdm(enumerate(images),desc="Processing images..."):
        # k+=1
        # if k < 78:
        #     continue
        annotations.extend(process_image(elem,fdict))
        break
        # break
        # exit()
        # exit()
        # exit()
    new_images = []
    for i in range(len(annotations)):
      annotations[i]['id'] = i
    for k,v in fdict.items():
      new_images.append({"id":v,"file_name":k,"height":540,"width":640})
    new_loco = {"constants":{},"categories":loco['categories'],"trackmap":[],"linked_tracks":[],"images":new_images,"annotations":annotations}
    f = open("foo.json","w")
    f.write(json.dumps(new_loco,indent=2))
    f.close()
    # {
    #   "id": 0,
    #   "file_name": "./reflected_y_porkfish_2.00000005.png",
    #   "height": 1080,
    #   "width": 1920
    # },
    #   {
    #   "id": 0,
    #   "image_id": 0,
    #   "category_id": 16,
    #   "bbox": [
    #     123.61056000000002,
    #     234.61001999999996,
    #     782.11008,
    #     529.4905200000001
    #   ],
    #   "area": 414119.87295644166,
    #   "segmentation": [],
    #   "iscrowd": 0,
    #   "track_id": 0,
    #   "trackmap_index": 0,
    #   "vid_id": 0,
    #   "track_color": [
    #     255,
    #     255,
    #     255
    #   ]
    # },
import os
def to_json(box_tuple,fid=None,error=-1, sid=-1, color=(255, 255, 255)):
    # print(self.bbox)
    class_id,bbox = box_tuple[0],box_tuple[1:]
    return {
        "id": -1,
        "image_id": fid,
        "category_id": class_id,
        "bbox": bbox,
        "area": bbox[2] * bbox[3],
        "segmentation": [],
        "iscrowd": 0,
        "track_id": -1,
        "trackmap_index": -1,
        "vid_id": 0,
        "track_color": color,
        "is_displaced": False,#self.is_displaced,
        "confidence": 0,#self.confidence,
        "error": error,
        "state_id": sid,#self.state_id,
        "is_prediction": False,
    }

def check_bounds(v,p,b=[0,1]):
  if v - p/2 < b[0]:
    p = v + p/2
    v = p/2
  if v + p/2 > b[1]:
    p = 1 - (v - p/2)
    v = 1 - p/2
  return v,p

def shift_image(img_object, dx=0.0,dy=0.0):
  distance_x = dx/img_object.width
  distance_y = dy/img_object.height
  img_object.shift = [dx,dy]
  
  for i,anno in enumerate(img_object.annotations):
    (cls, cx, cy, w, h) = anno.get_attr()
    cx = cx + distance_x
    cy = cy + distance_y
    cx,w = np.array(check_bounds(cx,w))/ (1-abs(distance_x))
    cy,h = np.array(check_bounds(cy,h))/ (1-abs(distance_y))
    
    img_object.annotations[i] = ObjTuple(cls, cx, cy, w, h)
  
    
      
def process_image(img_object,fdict,X=3,Y=3):
  # img = cv2.imread(img_object.filename)
  buckets = {i:[] for i in range(X*Y)}
  # print(img_object.width)
  # print([i.get_attr() for i in img_object.annotations],'anno')
  xshift,yshift = 0,0
  shift_image(img_object,xshift,yshift)
  ans = process_annotations(img_object.annotations,X,Y)
  dims = np.array([img_object.width,img_object.height]) + np.array(img_object.shift)
  for i,elem in enumerate(ans):
    cls, cx, cy, w, h = elem[1]
    w = w * dims[0] / (dims[0]/X)
    cx = (cx%(1/X)) * (dims[0]/(dims[0]/X))
    # w = (w) *  1920/ 640
    h = h * dims[1] / (dims[1]/Y)
    cy = (cy%(1/Y)) * (dims[1]/(dims[1]/Y))
    

    ans[i] = (elem[0],(cls,cx,cy,w,h))
  # print(ans,'ans')
  # print("foo")
  # exit()
  # return
  new_images = []
  new_annotations = []
  
  for a in ans:
    buckets[a[0]].append(a[1])
    # print(a[1])
  image_path = img_object.filename
  base_name, ext = os.path.splitext(os.path.basename(image_path))
  img = cv2.imread(image_path)
  
  img_height ,img_width= img.shape[:2]
  deltah = img_height - dims[1]
  deltaw = img_width - dims[0]
  img = img[deltah:,deltaw:]
  img_height ,img_width= img.shape[:2]
  # Calculate the dimensions of each piece
  piece_width = img_width // Y
  piece_height = img_height // X

  # Create output directory
  output_dir = f"{base_name}_pieces"
  os.makedirs(output_dir, exist_ok=True)
  
  # Loop through rows and columns to save pieces
  for r, row_start in enumerate(range(0, img_height, img_height // Y)):
    for c, col_start in enumerate(range(0, img_width, img_width // X)):
      # Calculate row and column end indices
      row_end = row_start + img_height // Y
      col_end = col_start + img_width // X
      
      # Slice the image
      piece = img[row_start:row_end, col_start:col_end]
      piece_filename = os.path.join(output_dir, f"{base_name}_{r*X + c}{ext}")
      
      fdict[piece_filename] = len(fdict)
      # Optionally, process the piece (e.g., draw YOLO boxes)
      if 'buckets' in locals():  # Check if buckets are defined
        piece = draw_yolo_boxes(piece, buckets[r * X + c])
        new_annotations.extend(populate_annotations(fdict[piece_filename],buckets[r * X + c]))
      cv2.imwrite(piece_filename, piece)
      # Save the piece
  return new_annotations
      
def populate_annotations(fid,bounding_boxes,image_height=540,image_width=640):
    # Load the image using OpenCV
    # image = cv2.imread(image_path)

    # Loop through the bounding boxes and draw them on the image
    annos = []
    for box in bounding_boxes:
      
        cls, cx, cy, w, h = box
        
        # image_height, image_width = image.shape[:2]

        # Convert normalized YOLO coordinates to pixel coordinates
        # x_min = int((cx - w / 2) * image_width)
        # y_min = int((cy - h / 2) * image_height)
        # x_max = int((cx + w / 2) * image_width)
        # y_max = int((cy + h / 2) * image_height)
        w*=image_width
        h*=image_height
        # Center point
        center_x = int(cx * image_width)
        center_y = int(cy * image_height)
        annos.append(to_json((cls,center_x,center_y,w,h),fid))
    return annos
        

def process_annotations(annotations,X=3,Y=1):
    results = []
    for anno in annotations:
        results.extend(g_get_splits(*anno.get_attr(),X,Y))
    # print("\n\n",results)
    sortkey = lambda x: x[0]
    results = sorted(results,key=sortkey)
    return results
    
    return results
  
def main():
    # Load the input JSON and convert it to YOLO format
    input_json = sys.argv[1]
    loco_data = json_loader(input_json)
    conv_to_yolo(loco_data)

if __name__ == "__main__":
    main()
