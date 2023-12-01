import json


def fix_json_general(str_content: str):
    """
    json 형식의 문자열을 수정합니다.
    :param str_content: 문제가 있는 json 형식의 문자열
    :return: 수정된 json 형식의 문자열
    """
    dict_json = eval(str_content)
    return dict_json


def read_json(path_json, encoding='utf-8'):
    """
    json 파일을 읽어서 dict로 반환합니다.
    :param path_json: json 파일 경로
    :param encoding: 인코딩
    :return: dict
    """
    with open(path_json, 'r', encoding=encoding) as file:
        content = file.read()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return fix_json_general(content)
    
    
def get_dict_value(dict_target, item_key):
    """ 
    item_key에 해당하는 값 하나만 가져온다.
    :param dict_target: dict
    :param item_key: 트리 구조의 key를 .으로 구분한 문자열
    """
    path_list = item_key.split('.')

    position_now = dict_target
    for path_item in path_list[:-1]:
        key_list = [key for key in position_now.keys() if str(key) == path_item]
        if len(key_list) == 0:
            return None

        position_now = position_now[key_list[0]]
        if type(position_now) != dict:
            return None

    for key in position_now.keys():
        if str(key) == path_list[-1]:
            return position_now[key]
    return None


def get_dict_values(dict_target, item_key):
    """ 
    item_key에 해당하는 값들은 싸그리 긁어다 가져온다.
    해당 키가 리스트로 반복되는 구조 안에 있는경우 사용한다.
    :param dict_target: dict
    :param item_key: 트리 구조의 key를 .으로 구분한 문자열
    """
    if type(dict_target) != dict:
        return []

    values = []
    path_list = item_key.split('.')

    target = dict_target
    for idx, path_item in enumerate(path_list[:-1]):
        key_list = [key for key in target.keys() if key == path_item]
        if len(key_list) == 0:
            return []

        target = target[path_item]
        if type(target) == list:
            for target_item in target:
                values += get_dict_values(target_item, '.'.join(path_list[idx+1:]))
            return values

    last_key = path_list[-1]
    if type(target) != dict or last_key not in target.keys():
        return []
    return [target[last_key]]

