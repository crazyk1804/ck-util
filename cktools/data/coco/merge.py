from glob import glob
import os

import numpy as np
from pandas import read_json
from tqdm import tqdm

from ck.data.parse import get_dict_value


class DataDirectory:
    def __init__(self, path_image, path_annotation):
        self._path_image = path_image
        self._path_annotation = path_annotation
        
    def __str__(self):
        return f'DataDirectory(path_image={self.path_image}, path_annotation={self.path_annotation})'
    
    @property
    def path_image(self):
        return self._path_image
    
    @property
    def path_annotation(self):
        return self._path_annotation


def merge_coco(dict_coco, data_directory: DataDirectory, data_size=None):
    """
    :param dict_coco_template: coco template
    :param data_directory: data directory
    :return: merged coco
    """
    path_image_dir, path_json_dir = data_directory.path_image, data_directory.path_annotation
    
    coco_images, coco_annotations, coco_categories = (
        dict_coco[key] for key in ['images', 'annotations', 'categories']
    )
    category_map = {coco_category['id']: {
        'name': coco_category['name'],
        'count': 0
    } for coco_category in coco_categories}

    # json 파일들을 순회하면서 coco 형식에 맞게 추가합니다.
    path_jsons = glob(os.path.join(path_json_dir, '*.json'))
    idxes = np.random.permutation(len(path_jsons))
    if data_size is not None:
        idxes = idxes[:data_size]

    bar = tqdm(idxes)
    for json_idx in bar:
        path_json = path_jsons[json_idx]
        bar.set_postfix({'path': os.path.basename(path_json_dir)})
        dict_json = read_json(path_json)
        
        # image 추가
        dict_images, dict_annotations = (
            dict_json[key] for key in ['images', 'annotations']
        )
        dict_image_id_map = {dict_image['id']: dict_image for dict_image in dict_images}
        for dict_image in dict_images:
            dict_image['id'] = len(coco_images) + 1
            dict_image['file_name'] = os.path.join(path_image_dir, dict_image['file_name'])
            coco_images.append(dict_image)

        # annotation 추가
        for dict_annotation in dict_annotations:
            dict_annotation['id'] = len(coco_annotations) + 1
            dict_annotation['iscrowd'] = 0
            
            # annotation id 수정
            dict_image = dict_image_id_map[dict_annotation['image_id']]
            dict_annotation['image_id'] = dict_image['id']

            # category id 수정
            category_id = dict_annotation['category_id']
            if category_id not in category_map.keys():
                dict_category = {'id': category_id, 'name': str(category_id)}
                coco_categories.append(dict_category)
                category_map[category_id] = {
                    'name': str(category_id),
                    'count': 0
                }
            category_map[category_id]['count'] += 1
            coco_annotations.append(dict_annotation)
            
    return category_map


def merge_category_count_map(category_count_maps):
    """
    카테고리별 데이터 수를 합칩니다.
    :param category_count_maps: category map list
    :return: merged category map
    """
    category_map_merged = {}
    for category_map in category_count_maps:
        for key in category_map.keys():
            if key not in category_map_merged.keys():
                category_map_merged[key] = category_map[key]
            else:
                category_map_merged[key]['count'] += category_map[key]['count']
    return category_map_merged


def refine_category_map(category_count_map, threshold=100):
    """
    데이터 수가 threshold 이상인 카테고리만 남깁니다.
    :param category_count_map: category map
    :param threshold: threshold
    :return: refined category map
    """
    id_seq = 1
    category_map_refined = {}
    for key in category_count_map.keys():
        if category_count_map[key]['count'] >= threshold:
            category_map_refined[key] = category_count_map[key]
            category_map_refined[key]['id'] = id_seq
            id_seq += 1
    return category_map_refined


def reset_category_id(dict_coco, category_count_map):
    """
    category id를 재정렬합니다.
    :param dict_coco: coco
    :param category_count_map: category_count_map
    """
    coco_images = dict_coco['images'].copy()
    coco_annotations = dict_coco['annotations'].copy()
    image_annotations = {dict_image['id']: [] for dict_image in coco_images}
    for dict_annotation in coco_annotations:
        image_annotations[dict_annotation['image_id']].append(dict_annotation)
    
    image_id, annotation_id = 1, 1
    bar = tqdm(enumerate(coco_images), total=len(coco_images))
    for ix, dict_image in bar:
        bar.set_postfix({'image_ix': ix})
        anns = image_annotations[dict_image['id']]
        anns_copy = anns.copy()
        for ann in anns_copy:
            category_id = ann['category_id']
            if category_id not in category_count_map.keys():
                anns.remove(ann)
                dict_coco['annotations'].remove(ann)
                continue
            ann['category_id'] = category_count_map[category_id]['id']
            ann['id'] = annotation_id
            annotation_id += 1
        
        if len(anns) == 0:
            coco_images.remove(dict_image)
            dict_coco['images'].remove(dict_image)
            continue
        dict_image['id'] = image_id
        [ann.update({'image_id': image_id}) for ann in anns]
        image_id += 1
        
    coco_categories = dict_coco['categories'].copy()
    for dict_category in coco_categories:
        if dict_category['id'] not in category_count_map.keys():
            dict_coco['categories'].remove(dict_category)
            continue
        dict_category['id'] = category_count_map[dict_category['id']]['id']


if __name__ == '__main__':
    dd = DataDirectory('path_image', 'path_annotation')
    print(dd.path_image)
    dd.path_image = 'what the fuck'
    print(dd.path_image)