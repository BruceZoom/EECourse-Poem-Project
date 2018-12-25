import torch
from torch.autograd import Variable as V
from torchvision import transforms as trn
from torch.nn import functional as F
import os
import numpy as np
from scipy.misc import imresize as imresize
import cv2
from PIL import Image
import sys
sys.path.append("./model")
from imageFeatureModel.catagories_hybrid1365 import *
import pretrainedmodels
import pretrainedmodels.utils as utils

def hook_resnet(module, input, output):
    features_resnet.append(np.squeeze(output.data.cpu().numpy()))

def hook_vgg(module, input, output):
    features_vgg.append(np.squeeze(output.data.cpu().numpy()))

def returnCAM(feature_conv, weight_softmax, class_idx):
    size_upsample = (256, 256)
    nc, h, w = feature_conv.shape
    output_cam = []
    for idx in class_idx:
        cam = weight_softmax[class_idx].dot(feature_conv.reshape((nc, h*w)))
        cam = cam.reshape(h, w)
        cam = cam - np.min(cam)
        cam_img = cam / np.max(cam)
        cam_img = np.uint8(255 * cam_img)
        output_cam.append(imresize(cam_img, size_upsample))
    return output_cam

def returnTF():
    tf = trn.Compose([
        trn.Resize((224,224)),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return tf

def load_object_model():
    model = pretrainedmodels.__dict__['vgg16'](num_classes=1000, pretrained='imagenet')
    model.eval()
    features_names = ['relu1']  # relu7 that acmm used, 4096 dim
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_vgg)
    return model

def load_scene_model():
    model_file = './model/imageFeatureModel/wideresnet18_places365.pth.tar'
    import imageFeatureModel.wideresnet
    model = imageFeatureModel.wideresnet.resnet18(num_classes=365)
    checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()
    features_names = ['layer4','avgpool'] # the last conv layer of the resnet
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_resnet)
    return model

W_attribute = np.load('./model/imageFeatureModel/W_sceneattribute_wideresnet18.npy')
features_vgg = []
features_resnet = []

objectModel = load_object_model()
sceneModel = load_scene_model()

tf = returnTF()#for resnet
load_img = utils.LoadImage()
tf_img = utils.TransformImage(objectModel)#for vgg

def getObjectFeature(img_url):
    input_img = load_img(img_url)
    input_tensor = tf_img(input_img)
    input_tensor = input_tensor.unsqueeze(0)
    input = torch.autograd.Variable(input_tensor,requires_grad=False)

    logit = objectModel.forward(input)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)
    probs=probs.numpy()
    idx=idx.numpy()

    objectRes=[]
    for itr in range(5):
        objectRes.append((objectClasses[idx[itr]],probs[itr]))

    relu=features_vgg[0]
    basename=os.path.basename(img_url)
    reludir = './static/relu/'+os.path.splitext(basename)[0]+'.npy'
    np.save(reludir,relu)

    return objectRes,reludir

def getSceneFeature(img_url):
    img = Image.open(img_url)
    input_img = V(tf(img).unsqueeze(0))

    logit = sceneModel.forward(input_img)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)
    probs = probs.numpy()
    idx = idx.numpy()
    print(idx)
    print(type(idx))

    io_image = np.mean(labels_IO[idx[:10]])
    sceneRes = []
    for itr in range(5):
        sceneRes.append((sceneClasses[idx[itr]], probs[itr]))

    params = list(sceneModel.parameters())
    weight_softmax = params[-2].data.numpy()
    weight_softmax[weight_softmax<0] = 0

    responses_attribute = W_attribute.dot(features_resnet[1])
    idx_a = np.argsort(responses_attribute)
    attributeList = [labels_attribute[idx_a[i]] for i in range(-1, -10, -1)]

    CAMs = returnCAM(features_resnet[0], weight_softmax, [idx[0]])
    img = cv2.imread(img_url)
    height, width, _ = img.shape
    heatmap = cv2.applyColorMap(cv2.resize(CAMs[0],(width, height)), cv2.COLORMAP_JET)
    result = heatmap * 0.4 + img * 0.5
    heatmap_url='./static/heatmap/'+os.path.basename(img_url)
    cv2.imwrite(heatmap_url,result)

    if io_image<0.5:
        return sceneRes,attributeList,heatmap_url,"室内"
    else:
        return sceneRes,attributeList,heatmap_url,"室外"





