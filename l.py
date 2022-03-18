from PIL import Image
a = Image.open("img/Style/backgrounds/g3.png")
a.resize((4000, 2000))
a.save("test.png")
