
class Replaces:

    def __init__(self):
        self.replaces = {}
        self.current_max_id = 0
    
    def add_replace(self, filepath, old, new):
        self.replaces.update({self.current_max_id: [filepath, old, new]})
        self.current_max_id = self.current_max_id + 1

    def undo_replace(self, id: int) -> str:
        try:
            replace = self.replaces.pop(id)
        except Exception as e:
            return "Correction id not found"
        if self.replace(replace[0], replace[2], replace[1]):
            "Correction Applied"
        else:
            raise Exception("Replace conflict")