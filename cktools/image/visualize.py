import cv2
from matplotlib import pyplot as plt

from ck.image.convert import denormalize


def draw_bbox(img, anns, dict_categories):
    """
    Args:
        img: np.array, shape=(H, W, 3)
        anns: np.array, shape=(N, 5), (x1, y1, x2, y2, cls)
        dict_categories: dict, {cls: cls_name}
    """
    for ann in anns:
        x1, y1, x2, y2, cls = [int(i.item()) for i in ann]
        if cls < 0:
            continue
        
        cls_name = dict_categories[cls]
        cv2.putText(img, cls_name, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 1), 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 1), 2)




def show_images(imgs, annots, dict_categories, num=4):
    """
    Args:
        imgs: np.array, shape=(N, H, W, 3)
        annots: np.array, shape=(N, M, 5), (x1, y1, x2, y2, cls)
        dict_categories: dict, {cls: cls_name}
        num: int, number of images to show in a row
    """
    n = imgs.shape[0]
    rows, cols = n//num, num
    fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
    
    for row, ax in enumerate(axes):
        if rows == 1:
            img = denormalize(imgs[row])
            draw_bbox(img, annots[row], dict_categories)
            ax.imshow(img)
            continue
        for col, ax in enumerate(ax):
            i = row * num + col
            img = denormalize(imgs[i])
            draw_bbox(img, annots[i], dict_categories)
            ax.imshow((img).astype(np.uint8))
    plt.show()
