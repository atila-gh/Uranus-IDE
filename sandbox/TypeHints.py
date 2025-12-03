# main.py
x = 42
y = "hello"

def foo():
    return "bar"

class MyClass:
    a = 15
    def __init__(self, x, y):
        self.x = x
        self.y = y

o = MyClass('salam', (2,3,4,5))

if __name__ == "__main__":
    
    for name, value in list(globals().items()):
        if not name.startswith("__"):
            print(name, "=>", type(value))