import mxnet as mx
import numpy as np
import cv2
from vgg_mx.symbol_vgg import VGG
from caffe_io import Transformer
from collections import namedtuple
import symbol_sentiment
import config

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
        print(internals)


    mod = mx.module.Module(
            context = ctx,
            symbol = sym,
            data_names = ("data", ),
            label_names = ()
    )



    mod.bind(data_shapes = [("data", (1, 3, img_len, img_len))], for_training = False)

    return mod

object_model = get_mod()
print(object_model)
object_model.load_params('/Users/markdana/Desktop/EECourse-Poem-Project/website/model/modernPoemModel/models/object.params')


def get_obj_feature(img):
    mu = np.array([104,117,123])
    transformed_img = crop_lit_centor(img, mu)
    transformed_img = transformed_img[None]

    s=object_model.forward(Batch([mx.nd.array(transformed_img)]), is_train = False)
    outputs = object_model.get_outputs()[0].asnumpy()
    print(s)
    return outputs


img='/Users/markdana/Downloads/12.jpg'
img = cv2.imread(img)

out=get_obj_feature(img)[0]

print(type(out))
print(out.shape)
print(sum(out))

for x in out:
    print(x)
