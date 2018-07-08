#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import cv2

if __name__ == '__main__':
    import configparser

    config = configparser.ConfigParser()
    config.read('authentication.ini')
    save_dir = config['param']['save_dir']
    save_dir_postprocess = save_dir + '_postprocess'
    if not os.path.exists(save_dir_postprocess):
        os.mkdir(save_dir_postprocess)

    for image_name in os.listdir(save_dir):

        image = cv2.imread(os.path.join(save_dir, image_name))

        if image is None:
            print('not found {}'.format(image_name))
            continue

        # name decorate
        if len(image_name.split('?')) > 1:
            image_name = image_name.split('?')[0]

        if not (image_name.endswith('.jpg') or image_name.endswith('.png') or image_name.endswith('.JPG') or image_name.endswith('.jpeg')):
            image_name = image_name + '.jpg'

        # resize & center crop
        aspect = image.shape[1] / image.shape[0]
        if aspect > 1:
            resize_to = (int(224 * aspect), 224)
        else:
            resize_to = (224, int(224 / aspect))

        image_resized = cv2.resize(image, resize_to)
        center_x = int(image_resized.shape[1] / 2)
        center_y = int(image_resized.shape[0] / 2)

        image_cropped = image_resized[center_y -
                                      112:center_y + 112, center_x - 112:center_x + 112]
        cv2.imwrite(os.path.join(save_dir_postprocess,
                                 image_name), image_cropped)
