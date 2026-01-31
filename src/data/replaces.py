
class Replaces:

    def __init__(self, sanitize_path):
        self.sanitize_path = sanitize_path
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

    def replace(self, filepath:str, old:str, new:str) -> str:
        file_path = self.sanitize_path(filepath)
        try:
            # Read old content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Correct old content
            new_content = content.replace(old.strip(), new.strip())
            # Check correction
            if new_content == content: 
                return "Failed"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                return "Correction applied, text changed."
        except Exception as e:
            return "Path incorrect, be sure to use a full path"