
class Exemplar(object):
    
    def __init__(self,function,construction):
        self.function = function
        self.construction = construction
    
    def get_construction(self):
        return self.construction
    
    def get_function(self):
        return self.function
    
    def __str__(self):
        pass
