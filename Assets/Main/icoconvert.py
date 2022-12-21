from PIL import Image
filename = r'title.png'
img = Image.open(filename)
img.save('titles.ico')
