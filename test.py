class base(object):
    def prt(self):
        print("base called")
    def call_self(self):
        self.prt()
class child(base):
    asd = 100
    def prt(self):
        print("child called",self.asd)
c = child()
c.call_self()
def callc():
    c.call_self()