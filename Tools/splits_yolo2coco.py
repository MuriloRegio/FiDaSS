from copy import deepcopy
import json
import os

RM_EXT = lambda FILENAME: os.path.splitext(FILENAME)[0]


def explorePath(path):
    annots = {}

    for (dirpath, _, files) in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                annots[RM_EXT(file)] = os.path.join(dirpath, file)

    return annots

def main(labels_path, img_size, classes,
        train_list, test_list, val_list, 
        train_json, test_json, val_json):
    img_size = tuple(img_size)
    img_size = (img_size[0],img_size[0]) if len(img_size) == 1 else img_size[:2]

    annots_path = explorePath(labels_path)

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

    for idx, catName in enumerate(classes):
        category = {
            "id"   : idx,
            "name" : catName,
            "supercategory" : "Person"
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


    for obj, split in zip([train_obj, val_obj, test_obj], [train_list, val_list, test_list]):
        with open(split, "r") as infile:
            files = [os.path.basename(file) for file in infile.read().split("\n")]

        img_id   = -1
        annot_id = -1

        for file in files:
            fpath = annots_path[RM_EXT(file)]
            img_id += 1

            this_img = deepcopy(img_template)
            this_img['id'] = img_id
            this_img['file_name'] = file
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

                    this_annot["area"] = w*h
                    this_annot["bbox"] = [x,y,w,h]
                    obj["annotations"].append(this_annot)


    with open(train_json, "w") as outfile:
        json.dump(train_obj, outfile)

    with open(test_json, "w") as outfile:
        json.dump(test_obj, outfile)

    with open(val_json, "w") as outfile:
        json.dump(val_obj, outfile)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Converts a dataset with YOLO annotations to COCO annotations.")


    parser.add_argument('--labels_folder', type=str, required=True,
                help='Relative path to the directory containing annotations (may be a path to subfolders containing the annotations).')


    parser.add_argument('--train_list', type=str, required=True,
                help='Txt file containing image path of the train images.')

    parser.add_argument('--test_list', type=str, required=True,
                help='Txt file containing image path of the test images.')

    parser.add_argument('--val_list', type=str, required=True,
                help='Txt file containing image path of the validation images.')

    parser.add_argument('--img_size', type=int, nargs='+', default=[512,512],
                help='Image dimensions of the network input.')

    parser.add_argument('--train_json', type=str, default='train.json',
                help='Path to the json containing the train annotations.')

    parser.add_argument('--test_json', type=str, default='test.json',
                help='Path to the json containing the test annotations.')

    parser.add_argument('--val_json', type=str, default='val.json',
                help='Path to the json containing the validation annotations.')

    parser.add_argument('--classes', type=str, nargs='+', default=['FirearmThreat'],
                help='Name of the classes in the YOLO dataset. They should be informed in ascending order of their ID.')


    args = parser.parse_args()
    main(
        args.labels_folder, args.img_size, args.classes,
        args.train_list, args.test_list, args.val_list,
        args.train_json, args.test_json, args.val_json,
    )