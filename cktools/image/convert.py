import numpy as np
import cv2


def get_trimap(
    image,
    class_ids,
    segmentations,
    class_count,
):
    """
    segmentation을 trimap으로 변환한다.
    :param image: 원본 이미지
    :param class_ids: 클래스 id
    :param segmentations: segmentation [x1, y1, x2, y2, ...]
    :param class_count: 클래스 수
    :return: trimap
    """
    color_border = class_count + 1
    # 어느정도가 적당한지 감이 안잡힘
    border_width = 5
    
    pallete = list(range(1, class_count+1))
    
    trimap = np.zeros(image.shape[:2], dtype=np.uint8)
    for class_id, segmentation in zip(class_ids, segmentations):
        polygon = np.array(segmentation, dtype=np.int32).reshape(-1, 2)
        cv2.fillPoly(trimap, [polygon], int(pallete[class_id]))
        
    region = cv2.dilate(trimap, None, iterations=border_width)
    region[trimap>0] = 0
    trimap[region>0] = color_border
    # 윤곽선에 마지막 값을 넣으면 이미지 증강처리시 영역이 외부로 나가는 경우가 발생할때 배경색이 전체를 차지 하므로 클래스 수가 모자르게 나올수 있다.
    trimap[trimap==0] = color_border+1 
    trimap -= 1
    
    return trimap[..., np.newaxis]


def scale_segmentation(segmentations, width, height, size):
    """
    segmentation을 size에 맞게 scale한다.
    :param segmentations: segmentation [x1, y1, x2, y2, ...]
    :param width: 원본 이미지의 너비
    :param height: 원본 이미지의 높이
    :param size: scale할 크기
    :return: scale된 segmentation
    """
    scale_x, scale_y = (size/factor for factor in [width, height])

    ret_val = []
    for segmentation in segmentations:
        segmentation = np.array(segmentation).reshape(-1, 2)
        segmentation[:, 0] *= scale_x
        segmentation[:, 1] *= scale_y
        ret_val.append(list(segmentation.reshape(-1).astype(int)))

    return ret_val


def image_to_array(path_files, size, channel):
    """
    이미지를 numpy array로 변환한다.
    :param path_files: 이미지 경로
    :param size: 이미지 크기
    :param channel: 채널 수
    :return: numpy array
    """
    L = len(path_files)
    out = np.empty((L, size, size, channel))

    # 같은 패턴이 반복되지만 줄인답시고 if문을 안으로 매번 비교를 반복하므로 굳이 고치지 않음
    if channel == 1:
        for i, path_file in enumerate(path_files):
            pix = cv2.imread(path_file)
            pix = cv2.cvtColor(pix, cv2.COLOR_BGR2RGB)
            pix = cv2.resize(pix, (size, size), interpolation=cv2.INTER_NEAREST)
            out[i, ..., 0] = pix
    else:
        for i, path_file in enumerate(path_files):
            pix = cv2.imread(path_file)
            pix = cv2.cvtColor(pix, cv2.COLOR_BGR2RGB)
            pix = cv2.resize(pix, (size, size), interpolation=cv2.INTER_NEAREST)
            out[i, ...] = np.array(pix)[..., :channel]
    
    # 이유는 모르겠지만 위아래를 뒤집는다
    return out[:, ::-1, ...]


def denormalize(img, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], multiply_byte=True):
    # Convert the image tensor to a numpy array
    img_np = img.numpy()

    # Denormalize the image
    img_denormalized = np.transpose(img_np, (1, 2, 0))
    img_denormalized = img_denormalized * std + mean
    img_denormalized = np.clip(img_denormalized, 0, 1)
    
    if multiply_byte:
        img_denormalized = img_denormalized * 255
    
    return img_denormalized

