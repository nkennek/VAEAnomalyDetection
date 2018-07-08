#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""base implementation: https://qiita.com/hirosemi/items/086f8375fd0f3fa5237b"""

import requests
import os
import math
import time
import urllib


class BingImageApi(object):

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

    def __init__(self,
                 api_key,
                 search_term,
                 save_dir,
                 num_imgs_required,
                 num_imgs_per_transaction
                 ):

        self.api_key = api_key
        self.search_term = search_term
        self.save_dir = save_dir
        self.num_imgs_required = int(num_imgs_required)
        self.num_imgs_per_transaction = int(num_imgs_per_transaction)
        self.offset = 0

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def run(self):

        max_offset = math.ceil(self.num_imgs_required /
                               self.num_imgs_per_transaction)

        for ofs in range(max_offset):
            print('{}/{} times request'.format(ofs + 1, max_offset), flush=True)

            try:
                response = self._make_a_request()
            except Exception as e:
                print(e)
                continue

            if ofs == 0 and 'totalEstimatedMatches' in response.keys():
                total_estimated_matches = response['totalEstimatedMatches']
                print('total estimated image count: {}'.format(
                    total_estimated_matches))

            values = response['value']
            for value in values:
                url = value['contentUrl']
                try:
                    self._save_image(url)
                except Exception as e:
                    print(url, e)

            time.sleep(2)

    def _make_a_request(self):
        headers = self._build_headers()
        params = self._build_params()

        response = requests.get(
            self.search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results

    def _save_image(self, image_url, timeout=10):
        response = requests.get(
            image_url, allow_redirects=True, timeout=timeout)
        # if response.status_code != 200:
        #     raise Exception("HTTP status {} at {}".format(
        #         response.status_code, image_url))

        # if 'image' not in response.headers['content-type']:
        #     raise Exception("Content-type {} at {}".format(
        #         response.headers['content-type'], image_url))

        img = response.content
        filename = image_url.split('/')[-1]
        filepath = os.path.join(self.save_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(img)

    def _build_headers(self):
        return {"Ocp-Apim-Subscription-Key": self.api_key}

    def _build_params(self):
        params = urllib.parse.urlencode({
            "q": self.search_term,
            "license": "All",
            "imageType": "photo",
            "count": self.num_imgs_per_transaction,
            "offset": self.offset * self.num_imgs_per_transaction,
            "mkt": "ja-JP",
        })
        self.offset += 1
        return params


if __name__ == '__main__':
    import configparser

    config = configparser.ConfigParser()
    config.read('authentication.ini')
    api_key = config['auth']['bing_api_key']
    param = config['param']

    api_crawler = BingImageApi(api_key, **param)
    api_crawler.run()
