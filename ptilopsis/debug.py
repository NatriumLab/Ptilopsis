import sys

class Observer:
    def __init__(self, initial_value):
        self.value = initial_value
    
    def __set__(self, value):
        last = sys._getframe(1)
        print(f"{last.f_code.co_filename}:{last.f_lineno}: change '{self.value}' to '{value}'")
        self.value = value
    
    def __get__(self):
        last = sys._getframe(1)
        print(f"{last.f_code.co_filename}:{last.f_lineno}: got '{self.value}'")
        return self.value