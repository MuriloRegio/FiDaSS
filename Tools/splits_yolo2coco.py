from copy import deepcopy
import json
import os


img_size = (512, 512)
obj_template = {
    "info"        : None,
    "license"     : [],
    "categories"  : [],
    "images"      : [],
    "annotations" : []
}



info = {
    "year"        : 2022,
    "version"     : "2022-C1",
    "description" : "Firearm Threat Detection dataset",
    "contributor" : "DaVInt",
    "url"         : "https://www.inf.pucrs.br/davint/",
    "date_created": "2021/06/01"
}
obj_template["info"] = info

license = {
    "id"   : 0,
    "name" : "Free License",
    "url"  : "https://www.inf.pucrs.br/davint"
}
obj_template["license"].append(license)

category = {
    "id"   : 0,
    "name" : "FirearmThreat",
    "supercategory" : "Threat"
}
obj_template["categories"].append(category)



img_template = {
    "id"        : None,
    "width"     : img_size[0],
    "height"    : img_size[1],
    "file_name" : None,
    "license"   : 0
}

annot_template = {
    "id"           : None,
    "image_id"     : None,
    "category_id"  : 0,
    "segmentation" : [],
    "area"         : None,
    "bbox"         : None,
    "iscrowd"      : 0
}



train_obj = deepcopy(obj_template)
val_obj   = deepcopy(obj_template)
test_obj  = deepcopy(obj_template)


def main():
for obj, split in zip([train_obj, val_obj, test_obj], ["splits/tiny-training-C1.txt", "splits/tiny-validation.txt", "splits/tiny-test.txt"]):
    with open(split, "r") as infile:
        files = [os.path.basename(file).replace('.jpg','.txt') for file in infile.read().split("\n")]

    img_id   = -1
    annot_id = -1

    # for file in os.listdir('Final/selected_labels'):
    for file in files:
        fpath = os.path.join('Final/selected_labels', file)
        img_id += 1

        this_img = deepcopy(img_template)
        this_img['id'] = img_id
        this_img['file_name'] = file.replace('.txt', '.jpg')
        obj["images"].append(this_img)

        with open(fpath, 'r') as infile:
            for line in infile.read().split('\n'):
                if len(line) == 0: 
                    continue

                annot_id += 1
                this_annot = deepcopy(annot_template)
                this_annot["id"] = annot_id
                this_annot["image_id"] = img_id

                c, x, y, w, h = line.split(' ')
                x,y,w,h = float(x),float(y),float(w),float(h)

                x = round((x-w/2) * img_size[0])
                y = round((y-h/2) * img_size[1])

                w = round(w * img_size[0])
                h = round(h * img_size[1])

                # x1 = round((x+w/2) * img_size[0])
                # x2 = round((x-w/2) * img_size[0])

                # y1 = round((y+h/2) * img_size[1])
                # y2 = round((y-h/2) * img_size[1])


                this_annot["area"] = w*h
                this_annot["bbox"] = [x,y,w,h]
                obj["annotations"].append(this_annot)

                # import cv2
                # img = cv2.imread(fpath.replace("labels","images").replace('.txt','.jpg'))
                # img = cv2.resize(img, img_size)
                # cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 3)

                # cv2.imshow("img", img)
                # cv2.waitKey(0)
                # exit(0)


    with open("train.json", "w") as outfile:
        json.dump(train_obj, outfile)

    with open("test.json", "w") as outfile:
        json.dump(test_obj, outfile)

    with open("val.json", "w") as outfile:
        json.dump(val_obj, outfile)