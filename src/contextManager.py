import os
from langchain.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage

from data.job import Job

class ContextManager:
    
    def __init__(self, job: Job, ignore_files: list[str]):
        self.job = job
        self.steps_messages: list[list[tuple[str, str]]] = []
        self.scan_files(ignore_files)

    def get_context(self, mask: list[bool] = None) -> list[tuple[str, str]]:
        if mask is None:
            return self.steps_messages[self.job.current]
        raise Exception("not implemented yet")
        # if len(mask) != len(self.messages):
        #     raise Exception(f"Invalid job mask, len_mask: {len(mask)} != {len(self.messages)}")
        # return [
        #     message if mask[i] else None
        #     for i, message in enumerate(self.messages)
        # ]

    def add_response_messages(self, response_messages: list[tuple[str, str]]):
        if len(self.steps_messages) < self.job.current + 1:
            self.steps_messages.append(response_messages)
        else:
            self.steps_messages[self.job.current].extend(response_messages)

    def add_message(self, role:str, text: str):
        index = self.job.current
        print(f"index: {index}, steps: {len(self.steps_messages)}")
        if len(self.steps_messages) < index + 1:
            self.steps_messages.append([(role, text)])
        else: self.steps_messages[index].append((role, text))

    def delete_last_steps(self, to_delete: int | None):
        if to_delete is None: return
        while to_delete > 0:
            self.steps_messages.pop()
            to_delete = to_delete -1

    def scan_files(self, ignore_files: list[str]) -> None:
        self.files = []
        if not os.path.isabs(self.job.root):
            raise Exception("Path is not absolute")
        if not os.path.isdir(self.job.root):
            raise Exception("Directory not found")

        for root, dirs, files in os.walk(self.job.root):
            dirs[:] = [d for d in dirs if d not in ignore_files]
            for filename in files:
                if filename in ignore_files:
                    continue

                # Process the file (e.g., read, write, etc.)
                file_path = os.path.join(root, filename)
                filtered = file_path.replace(self.job.root, "")
                self.files.append(filtered)