# -*- coding:utf-8 -*-#
import cv2
import numpy as np
import urllib.request
import urllib.parse
import urllib
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def get_page(url):
    header={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    rq=urllib.request.Request(url,headers=header)
    try:
        content=urllib.request.urlopen(rq)
        return content
    except:
        print("FAILED WHEN OPENING "+url)
        pass


url='https://goss.veer.com/creative/vcg/veer/612/veer-307487922.jpg'
def url_to_image(url):
    resp = get_page(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    print(image.shape)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    cv2.imwrite('/Users/markdana/Desktop', image)
    return image


urllib.request.urlretrieve(url,'/Users/markdana/Desktop/3.jpg')
