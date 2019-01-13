import sys
sys.path.append("./model/modernPoemModel/src")
import extract_feature
import generate_poem

def get_poem(image_file,reludir):
    img_feature = extract_feature.extract_feature(image_file,reludir)
    return generate_poem.generate_poem(img_feature)




