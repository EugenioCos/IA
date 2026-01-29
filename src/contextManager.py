import os

class ContextManager:
    
    def __init__(self, abs_path, ignore_files):
        self.messages: list[tuple[str, str]] = []
        self.scan_files(abs_path, ignore_files)

    def get_context(self, mask: list[bool] = None) -> list[tuple[str, str]]:
        if mask is None:
            return self.messages
        raise Exception("not implemented jet")
        # if len(mask) != len(self.messages):
        #     raise Exception(f"Invalid job mask, len_mask: {len(mask)} != {len(self.messages)}")
        # return [
        #     message if mask[i] else None
        #     for i, message in enumerate(self.messages)
        # ]

    def add_messages(self, messages: list[str, str]):
        self.messages.append(messages)

    def add_message(self, text: str, role:str):
        self.messages.append((role, text))

    def scan_files(self, abs_path, ignore_files: list[str]) -> None:
        self.files = []
        if not os.path.isabs(abs_path):
            raise Exception("Path is not absolute")
        if not os.path.isdir(abs_path):
            raise Exception("Directory not found")

        for root, dirs, files in os.walk(abs_path):
            dirs[:] = [d for d in dirs if d not in ignore_files]
            for filename in files:
                if filename in ignore_files:
                    continue

                # Process the file (e.g., read, write, etc.)
                file_path = os.path.join(root, filename)
                filtered = file_path.replace(abs_path, "")
                self.files.append(filtered)