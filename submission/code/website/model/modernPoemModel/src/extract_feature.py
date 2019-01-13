import mxnet as mx
import numpy as np
import cv2
from vgg_mx.symbol_vgg import VGG
from caffe_io import Transformer
from collections import namedtuple
import symbol_sentiment
import config
import os

ctx = [mx.cpu()] if len(config.gpus) == 0 else [mx.gpu(int(i)) for i in config.gpus.split(',')]

feature_names = ['object', 'scene', 'Sentiment']
Batch = namedtuple('Batch', ['data'])

def data_trans(img, shape, mu):
    transformer = Transformer({'data': shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_mean('data', mu)
    transformer.set_raw_scale('data', 255)
    transformed_image = transformer.preprocess('data', img)
    return transformed_image

def crop_lit_centor(img, mu, img_len = 224):
    [n,m,_]=img.shape
    if m>n:
        m = int(m*256/n)
        n = 256
    else:
        n = int(n*256/m)
        m = 256
    return data_trans(cv2.resize(img,(m,n))/255.0,(1,3,n,m), mu)[:,int((n-img_len)/2):int((n+img_len)/2),int((m-img_len)/2):int((m+img_len)/2)]

def get_mod(output_name = 'relu7_output', sym = None, img_len = 224):
    if sym is None:
        vgg = VGG()
        sym = vgg.get_symbol(num_classes = 1000, 
                  blocks = [(2, 64),
                            (2, 128),
                            (3, 256), 
                            (3, 512),
                            (3, 512)])
        internals = sym.get_internals()
        sym = internals[output_name]

    mod = mx.module.Module(
            context = ctx,
            symbol = sym,
            data_names = ("data", ),
            label_names = ()
    )

    mod.bind(data_shapes = [("data", (1, 3, img_len, img_len))], for_training = False)

    return mod


scene_model = get_mod()
scene_model.load_params('./model/modernPoemModel/models/scene.params')

sentiment_model = get_mod(sym = symbol_sentiment.get_sym(), img_len = 227)
sentiment_model.load_params('./model/modernPoemModel/models/Sentiment.params')


def get_scene_feature(img):
    mu = np.array([105.487823486,113.741088867,116.060394287])
    transformed_img = crop_lit_centor(img, mu)
    transformed_img = transformed_img[None]
    scene_model.forward(Batch([mx.nd.array(transformed_img)]), is_train = False)
    outputs = scene_model.get_outputs()[0].asnumpy()
    return outputs

def get_sentiment_feature(img):
    mu = np.array([97.0411,105.423,111.677])
    transformed_img = crop_lit_centor(img, mu, img_len = 227)
    transformed_img = transformed_img[None]
    sentiment_model.forward(Batch([mx.nd.array(transformed_img)]), is_train = False)
    outputs = sentiment_model.get_outputs()[0].asnumpy()
    return outputs

def extract_feature(image_file,reludir):
    img = cv2.imread(image_file)
    assert img is not None, IOError(
            'The file `{}` may be not an image'.format(image_file))
    # img.shape: H, W, T
    if img.ndim == 2:
        # gray image
        img = np.stack([img, img, img], axis=2)
    else:
        if img.ndim == 3 and img.shape[2] in [3, 4]:
            if img.shape[2] == 4:
                # remove alpha channel
                img = img[:, :, :3]
        else:
            raise Exception('Invalid Image `{}` whose shape is {}'.format(image_file, img.shape))

    obj_feat = np.load(reludir).reshape(1,4096)
    scene_feat = get_scene_feature(img)
    sentiment_feat = get_sentiment_feature(img)

    image_features = [obj_feat, sentiment_feat, scene_feat]
    img_feature = np.hstack(image_features)
    return img_feature

