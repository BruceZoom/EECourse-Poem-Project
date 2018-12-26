import sys
sys.path.append("./model/modernPoemModel/src")
from extract_feature import *
from generate_poem import *

def get_poem(image_file,reludir):
    img_feature = extract_feature(image_file,reludir)
    return generate_poem(img_feature)




