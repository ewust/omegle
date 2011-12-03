
import socket
import asyncore
import struct
import random
import time
import urllib
import captcha



gl_name = 'A'
def get_new_name():
    global gl_name
    ret = gl_name
    gl_name = chr(ord(gl_name)+1)
    return ret


class OmegleClient(asyncore.dispatcher):
    def __init__(self, name=None):
        asyncore.dispatcher.__init__(self)
        self.hit_crossdomain()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(("odo-bucket.omegle.com", 1365))
        if name == None:
            name = hex(random.randint(0, 0xffffff))[2:]
            name = get_new_name()
        self.buffer = ""
        self.name = name
        self.is_writeable = True
        self.partners = []
        

    def hit_crossdomain(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("odo-bucket.omegle.com", 843))
        while 1: 
            tmp = sock.recv(0xffff)
            if len(tmp) == 0:
                break
        sock.close()
        return
        

    def reconnect(self):
        self.hit_crossdomain()
        self.buffer = ""
        self.is_writeable = True
        #self.name = hex(random.randint(0, 0xffffff))[2:]
        self.name = get_new_name()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(("odo-bucket.omegle.com", 1365))            

    def add_partner(self, partner):
        self.partners.append(partner)

    def handle_connect(self):
        print '%s handle_connect' % self.name
        self.send_msg("omegleStart", "web-flash?rcs=1&spid=&abtest=")
                #746573743d26756e69713d3133323237393533383839343933353
                #836373026746573747365743d313332323238363736342e303126
                #7465737474733d31333232373935333838

    def send_partners(self, cmd, msg):
        for p in self.partners:
            p.send_msg(cmd, msg)

    def handle_message(self, cmd, msg):
        t = time.strftime('%I:%M:%S %p')
        if cmd == 'm':
            print "(%s) %s: %s" % (t, self.name, msg)
            self.send_partners('s', msg)
        elif cmd == 't':
            #print "(%s) %s is typing" % (t, self.name)
            self.send_partners(cmd, msg)
        elif cmd == 'd':
            print "(%s) %s disconnected" % (t, self.name)
            self.close()
            self.reconnect()
        elif cmd == 'w':
            print "(%s) waiting for %s to connect..."  % (t, self.name)
        elif cmd == 'c':
            print "(%s) %s connected" % (t, self.name)
        elif cmd == 'count':
            #print '(%s) %s strangers online' % (t, msg)
            pass
        elif cmd == 'st':
            pass #stopped typing
        elif cmd == 'suggestSpyee':
            pass # bleh
        elif cmd == 'recaptchaRequired':
            # Well, shit
            pubkey = msg.split('=')[1]
            url = "http://www.google.com/recaptcha/api/challenge?k=%s&ajax=1&cahcestop=%f" % (pubkey, random.random())
            obj = urllib.urlopen(url).read()
            for line in obj.split('\n'):
                if line.replace(' ', '').startswith('challenge'):
                    challenge = line.split("'")[1]
                    url = "http://www.google.com//recaptcha/api/image?c=%s" % (challenge)
                    print "(%s) %s captcha required %s" % (t, self.name, url)
    
            answer = captcha.Captcha.show(url)

            response = "challenge=%s&response=%s" % (challenge, answer)
            self.send_msg('recaptcha', response) 
            
        elif cmd == 'recaptchaRejected':
            print '(%s) Captcha rejected - try harder' % (t)
            self.close()
            self.reconnect()
        else:
            print "(%s) %s unknown cmd '%s': %s" % (t, self.name, cmd, msg)


    def readable(self):
        return True

    def writable(self):
        return self.is_writeable

    def handle_write(self): 
        if self.buffer:
            sent = self.send(self.buffer)
            self.buffer = self.buffer[sent:]
        if len(self.buffer) == 0:
            self.is_writeable = False
        

    def handle_read(self):
        pkt = self.recv(0xffff)
        if len(pkt) == 0:
            print '(%s) %s error: closed' % (time.strftime('%I:%M:%S %p'), self.name)
            self.close()
            self.reconnect() 
            return
        cmd_len, = struct.unpack('!b', pkt[0])
        cmd = pkt[1:1+cmd_len]
        msg_len, = struct.unpack('!h', pkt[cmd_len+1:cmd_len+3])
        msg = ""
        if msg_len > 0:
            msg = pkt[cmd_len+3:cmd_len+3+msg_len]
        
        self.handle_message(cmd, msg)    
        

    def send_msg(self, cmd, msg):
        pkt = struct.pack('!b', len(cmd))
        pkt += cmd
        pkt += struct.pack('!h', len(msg))
        pkt += msg

        self.buffer += pkt
        self.is_writeable = True


    def disconnect(self):
        self.send_msg('d', "")
    
    def typing(self):
        self.send_msg('t', "")



