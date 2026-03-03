class Vote:

    def __init__(self):
        self.ia_approve_count = 0
        self.ia_reject_count = 0

    def add_vote(self, is_approve: bool):
        if is_approve: self.ia_approve_count = self.ia_approve_count + 1
        else: self.ia_reject_count = self.ia_reject_count + 1

    def has_decided(self) -> bool:
        return (self.ia_approve_count + self.ia_reject_count) > 0

    def get_decision(self) -> bool:
        print(f"Approvations_count: {self.ia_approve_count}, rejects_count: {self.ia_reject_count}")
        decision = self.ia_reject_count < self.ia_approve_count
        self.ia_approve_count = 0
        self.ia_reject_count = 0
        return decision
