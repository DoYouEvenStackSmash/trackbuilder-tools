import sys


CLS_LOC = 0
CX_LOC = 1
CY_LOC = 2
W_LOC = 3
H_LOC = 4
import cv2


def draw_yolo_boxes(image, bounding_boxes):
    # Load the image using OpenCV
    # image = cv2.imread(image_path)

    # Loop through the bounding boxes and draw them on the image
    for box in bounding_boxes:
        cls, cx, cy, w, h = box

        image_height, image_width = image.shape[:2]

        # Convert normalized YOLO coordinates to pixel coordinates
        x_min = int((cx - w / 2) * image_width)
        y_min = int((cy - h / 2) * image_height)
        x_max = int((cx + w / 2) * image_width)
        y_max = int((cy + h / 2) * image_height)

        # Center point
        center_x = int(cx * image_width)
        center_y = int(cy * image_height)

        # Define the color (green in BGR format)
        color = (0, 255, 0)
        thickness = 2

        # Draw the bounding box (rectangle)
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, thickness)

        # Draw a dot at the center
        cv2.circle(image, (center_x, center_y), 5, color, -1)  # Filled circle

        # Draw the class label
        label = str(cls)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, label, (x_min, y_min - 10), font, 0.5, color, 2)
    return image


import numpy as np


def split_y(box_tuple, secnums, MIDPOINT=0.5, mps=[0, 1]):
    # print(MIDPOINT)
    split_condition_y = lambda cy, h, mpy: cy - h / 2 <= mpy < cy + h / 2
    boxes = []
    mods = []
    new_secnums = []
    cls, cx, cy, w, h = box_tuple
    if split_condition_y(box_tuple[CY_LOC], box_tuple[H_LOC], MIDPOINT):
        new_upper_h = np.sqrt(((cy + h / 2) - (MIDPOINT)) ** 2)
        new_midpoint_upper = new_upper_h / 2 + MIDPOINT
        new_lower_h = np.sqrt(((cy - h / 2) - (MIDPOINT)) ** 2)
        new_midpoint_lower = MIDPOINT - new_lower_h / 2
        new_box_tuple_upper = (
            box_tuple[CLS_LOC],
            box_tuple[CX_LOC],
            new_midpoint_upper,
            box_tuple[W_LOC],
            new_upper_h,
        )
        new_box_tuple_lower = (
            box_tuple[CLS_LOC],
            box_tuple[CX_LOC],
            new_midpoint_lower,
            box_tuple[W_LOC],
            new_lower_h,
        )
        boxes.extend([new_box_tuple_lower, new_box_tuple_upper])
        new_secnums = np.array(mps).tolist()
        
        
    else:
        boxes.append(box_tuple)
        new_secnums = secnums
        # print(secnums)
        pass
    # print(boxes,secnums)
    return boxes, new_secnums


def split_x(box_tuple, secnums, MIDPOINT=0.5, mps=[0, 1]):
    split_condition_x = lambda cx, w, mpy: cx - w / 2 <= mpy < cx + w / 2
    boxes = []
    mods = []
    new_secnums = []
    cls, cx, cy, w, h = box_tuple
    if split_condition_x(box_tuple[CX_LOC], box_tuple[W_LOC], MIDPOINT):
        new_upper_w = np.sqrt(((cx + w / 2) - (MIDPOINT)) ** 2)
        new_midpoint_upper = new_upper_w / 2 + MIDPOINT
        new_lower_w = np.sqrt(((cx - w / 2) - (MIDPOINT)) ** 2)
        new_midpoint_lower = MIDPOINT - new_lower_w / 2
        new_box_tuple_upper = (
            box_tuple[CLS_LOC],
            new_midpoint_upper,
            box_tuple[CY_LOC],
            new_upper_w,
            box_tuple[H_LOC],
        )
        new_box_tuple_lower = (
            box_tuple[CLS_LOC],
            new_midpoint_lower,
            box_tuple[CY_LOC],
            new_lower_w,
            box_tuple[H_LOC],
        )
        boxes.extend([new_box_tuple_lower, new_box_tuple_upper])
        # print(mps)
        new_secnums = (np.array(mps)).tolist()
        mods.extend([1,1])
    else:
        boxes.append(box_tuple)
        new_secnums = secnums
        pass
    return boxes, new_secnums


def get_splits(bbox_path, image_width=640, image_height=640):
    f = open(bbox_path)
    s = f.read()
    f.close()
    s = s.split("\n")
    results = []
    for line in s:
        s1 = line.split(" ")
        cls, (cx, cy, w, h) = int(s1[0]), [float(i) for i in s1[1:]]
        results.extend(g_get_splits(cls, cx, cy, w, h))
    sortkey = lambda x: x[0]
    results = sorted(results, key=sortkey)

    for i, elem in enumerate(results):
        cls, cx, cy, w, h = elem[1]

        w = (w) * 1920 / 640
        h = h * 1080 / 540
        cx = (cx % (1 / 3)) * (1920 / 640)
        cy = (cy % (1 / 2)) * (1080 / 540)

        results[i] = (elem[0], (cls, cx, cy, w, h))
    return results



def g_get_splits(cls, cx, cy, w, h,X=3,Y=1):
    box1 = (cls, cx, cy, w, h)
    snx, sny = -1, -1
    sec = 1
    if cx < sec / X:
        snx = 0
    elif cx > (X-1)/X:
        snx = X-1
    else:
        for sec in range(2,X):
            if (sec-1) / X <= cx < sec / X:
                snx = sec-1
    
    if cy <= 1 / Y:
        sny = 0
    elif cy > (Y-1)/Y:
        sny = (Y-1) * X
    else:
        for sec in range(2,Y):
            if (sec-1)/Y <= cy < sec/Y:
                sny = X * (sec-1)

    bx = [box1]
    sx = [sny]
    # print(bx,'bx')
    boxes = zip(bx, sx)
    splitx = bx#[]
    splitx_secnums = sx#[]
    arx = splitx
    arcnum = splitx_secnums
    # basenum = []
    outer_arx = []
    outer_num = []
    for sec in range(1,Y):
        # print(sec * X)
        arx = []
        arcnum = []
        boxes = zip(splitx,splitx_secnums)
        for i,s in boxes:
            print(s)
            # base_column = (s // Y)
            x, sn = split_y(i, [s], sec/Y, [(sec-1)*X, sec*X])
            arx = arx + x
            arcnum = arcnum + sn
        bar = [i for i in zip(arx,arcnum)]
        sortkey = lambda x: x[1]
        bar = sorted(bar,key=sortkey)
        i = 0
        while i < len(bar) and bar[i][1] < sec*X:
            outer_arx.append(bar[i][0])
            outer_num.append(bar[i][1])
            i+=1
        splitx = []
        splitx_secnums = []
        for i in range(i,len(bar)):
            splitx.append(bar[i][0])
            splitx_secnums.append(bar[i][1])
    outer_arx.extend(splitx)
    outer_num.extend(splitx_secnums)
          
    splitx = outer_arx
    splitx_secnums = outer_num

    outer_arx = []
    outer_num = []
    for sec in range(1,X):
        # print(sec)
        arx = []
        arcnum = []
        boxes = zip(splitx,splitx_secnums)
        for i, s in boxes:#boxes:
            base_section = (s // X * X) # get base section + s%X
            
            x, sn = split_x(i, [s], sec / X, base_section + np.array([sec-1, sec]))
            arx = arx + x
            arcnum = arcnum + sn
            # print(s,sn)
        bar = [i for i in zip(arx,arcnum)]
        sortkey = lambda x: x[1]
        bar = sorted(bar,key=sortkey)
        i = 0
        while i < len(bar) and bar[i][1] < sec:
            outer_arx.append(bar[i][0])
            outer_num.append(bar[i][1])
            i+=1
        splitx = []
        splitx_secnums = []
        for i in range(i,len(bar)):
            splitx.append(bar[i][0])
            splitx_secnums.append(bar[i][1])
            

    outer_arx.extend(splitx)
    outer_num.extend(splitx_secnums)
          
    splitx = outer_arx
    splitx_secnums = outer_num
    
    # boxes.extend(boxes2)
    # # print(splitx_secnums)
    
    # for i, s in boxes:
    #     x, sn = split_x(i, [s], 2 / 3, [0, 1])
    #     splitx = splitx + x
    #     splitx_secnums = splitx_secnums + sn
    # # print(splitx_secnums,'sec')
    # boxes = splitx
    # print([i for i in boxes],'boxes')
    return [i for i in zip(splitx_secnums,splitx)]

def _g_get_splits(cls, cx, cy, w, h):
    box1 = (cls, cx, cy, w, h)
    snx, sny = 0, 0
    
    if cx < 1 / 3:
        snx = 0
    elif 1 / 3 <= cx < 2 / 3:
        snx = 1
    elif cx >= 2 / 3:
        snx = 2
    if cy < 1 / 2:
        sny = 0
    elif cy >= 1 / 2:
        sny = 3

    boxes = []
    bx, snx = split_y(box1, [sny], 0.5, [0, 3])
    # print(snx)
    splitx = []
    splitx_secnums = []
    for i, s in zip(bx, snx):
        x, sn = split_x(i, [s], 1 / 3, [0, 1])
        splitx = splitx + x
        splitx_secnums = splitx_secnums + sn
    # print(splitx_secnums)
    boxes = zip(splitx, splitx_secnums)
    for i, s in boxes:
        x, sn = split_x(i, [s], 2 / 3, [0, 1])
        splitx = splitx + x
        splitx_secnums = splitx_secnums + sn
    # print(splitx_secnums,'sec')
    boxes = splitx
    return [i for i in zip(splitx_secnums, boxes)]