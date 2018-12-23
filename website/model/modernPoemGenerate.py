import sys
sys.path.append("./model/modernPoemModel/src")
from extract_feature import *
from generate_poem import *

def get_poem(image_file):
    img_feature = extract_feature(image_file)
    return generate_poem(img_feature)




