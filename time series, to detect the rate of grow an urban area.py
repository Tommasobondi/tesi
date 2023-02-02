import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def image_display(im, titolo):
    
    plt.figure(figsize=(15,15))
    plt.imshow(im, cmap='gray')
    plt.title(titolo)
    plt.colorbar()
    plt.show()
    return

def image_display2(im1, im2, titolo):
    
    plt.figure(figsize=(15,15))
    plt.subplot(121)
    plt.imshow(im1)
    plt.title(titolo)
    plt.colorbar()
    plt.subplot(122)
    plt.imshow(im2)
    plt.title(titolo)
    plt.colorbar()
    plt.show()
    return

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def rgb2gray2(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

def image_difference(im1, im2):
    return abs(im1 - im2)

def load_image(name):
    im = mpimg.imread(name)
    return im

def get_image_name(i):
    name = 'dataset/' + str(i) + '.png'
    return name

def get_threshold(im1, im2):
    th = image_difference(im1, im2)
    th = th.mean(axis=2)
    return th

def image_difference_with_threshold(th, im1, im2):
    return abs(im1 - im2) > th

def process(im1, im2, im3):
    th = get_threshold(im1, im2)
    differences = image_difference_with_threshold(th, im2, im3)
    return differences

def process2(im1, im2, im3):
    th = get_threshold(im1, im2)
    differences = image_difference_with_threshold(th, im2, im3)
    return differences

def process_all():
    im1 = load_image(get_image_name(1))
    im2 = load_image(get_image_name(2))
    im3 = load_image(get_image_name(3))
    im4 = load_image(get_image_name(4))
    im5 = load_image(get_image_name(5))
    im6 = load_image(get_image_name(6))
    
    differences12 = process(im1, im2, im3)
    image_display(differences12, "differences12")
    differences23 = process(im2, im3, im4)
    image_display(differences23, "differences23")
    differences34 = process(im3, im4, im5)
    image_display(differences34, "differences34")
    differences45 = process(im4, im5, im6)
    image_display(differences45, "differences45")
    
    all_differences = differences12 + differences23 + differences34 + differences45
    image_display(all_differences, "all_differences")
    
    return

def process_all2():
    im1 = load_image(get_image_name(1))
    im1 = rgb2gray(im1)
    im2 = load_image(get_image_name(2))
    im2 = rgb2gray(im2)
    im3 = load_image(get_image_name(3))
    im3 = rgb2gray(im3)
    im4 = load_image(get_image_name(4))
    im4 = rgb2gray(im4)
    im5 = load_image(get_image_name(5))
    im5 = rgb2gray(im5)
    im6 = load_image(get_image_name(6))
    im6 = rgb2gray(im6)
    
    differences12 = process2(im1, im2, im3)
    image_display(differences12, "differences12")
    #differences23 = process(im2, im3, im4)
    #image_display(differences23, "differences23")
    #differences34 = process(im3, im4, im5)
    #image_display(differences34, "differences34")
    #differences45 = process(im4, im5, im6)
    #image_display(differences45, "differences45")
    
    #all_differences = differences12 + differences23 + differences34 + differences45
    #image_display(all_differences, "all_differences")
    
    return


process_all2()
