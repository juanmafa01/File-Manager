class File:
    def __init__(self, name, path, is_folder=True):
        self.name = name
        self.path = path
        self.child = []
        self.is_folder = is_folder