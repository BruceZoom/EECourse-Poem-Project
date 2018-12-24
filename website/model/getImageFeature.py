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
import imageFeatureModel.vgg16_torch
from imageFeatureModel.catagories_hybrid1365 import *

def hook_feature(module, input, output):
    features_blobs.append(np.squeeze(output.data.cpu().numpy()))

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

def load_hybrid_model():
    model_file = './model/imageFeatureModel/vgg16_hybrid1365.pth'
    model = imageFeatureModel.vgg16_torch.vgg16_torch
    model.load_state_dict(torch.load(model_file))
    model.eval()
    return model

def load_heatmap_model():
    model_file = './model/imageFeatureModel/wideresnet18_places365.pth.tar'
    import imageFeatureModel.wideresnet
    model = imageFeatureModel.wideresnet.resnet18(num_classes=365)
    checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()
    features_names = ['layer4','avgpool'] # the last conv layer of the resnet
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_feature)
    return model

W_attribute = np.load('./model/imageFeatureModel/W_sceneattribute_wideresnet18.npy')
features_blobs = []
hybridModel = load_hybrid_model()
heatmapModel = load_heatmap_model()
tf = returnTF()

def getHybridFeature(img_url):
    img = Image.open(img_url)
    input_img = V(tf(img).unsqueeze(0))*255
    logit = hybridModel.forward(input_img)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)
    probs=probs.numpy()
    idx=idx.numpy()
    scene=[]
    object=[]
    io_image=0

    for i in range(1365):
        if(len(object)>5):break
        if (idx[i]<=999):object.append([classes[idx[i]],probs[i]])

    for i in range(1365):
        if(len(scene)>5):break
        if (idx[i]>999):
            scene.append([classes[idx[i]],probs[i]])
            io_image+=labels_IO[idx[i]-1000]

    io_image = io_image/6 # vote for the indoor or outdoor
    if io_image<0.5:
        return object,scene,'室内'
    else:return object,scene,'室外'

def getHeatmap(img_url):
    img = Image.open(img_url)
    input_img = V(tf(img).unsqueeze(0))

    logit = heatmapModel.forward(input_img)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)
    idx=idx.numpy()

    params = list(heatmapModel.parameters())
    weight_softmax = params[-2].data.numpy()
    weight_softmax[weight_softmax<0] = 0

    responses_attribute = W_attribute.dot(features_blobs[1])
    idx_a = np.argsort(responses_attribute)
    attributeList=[labels_attribute[idx_a[i]] for i in range(-1,-10,-1)]

    CAMs = returnCAM(features_blobs[0], weight_softmax, [idx[0]])
    img = cv2.imread(img_url)
    height, width, _ = img.shape
    heatmap = cv2.applyColorMap(cv2.resize(CAMs[0],(width, height)), cv2.COLORMAP_JET)
    result = heatmap * 0.4 + img * 0.5
    heatmap_url='./static/heatmap/'+os.path.basename(img_url)
    cv2.imwrite(heatmap_url,result)
    return attributeList,heatmap_url





