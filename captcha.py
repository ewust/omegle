import gtk
import urllib

class Captcha:
    def __init__(self):
        pass
        
    @staticmethod
    def show(url):
        img = urllib.urlopen(url).read()
        f = open('/tmp/recaptcha.jpg', 'w')
        f.write(img)
        f.close()

        win = gtk.Window()
        image = gtk.Image()
        image.set_from_file('/tmp/recaptcha.jpg')
        win.add(image)
        image.show()
        win.show()

        answer = raw_input()
        win.hide()
        return answer
