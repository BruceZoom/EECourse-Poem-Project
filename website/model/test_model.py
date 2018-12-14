from skimage import io

def load_image(filename):
    img = io.imread(filename)
    io.imshow(img)
