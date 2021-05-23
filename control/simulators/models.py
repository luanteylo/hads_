class Models:

    def __init__(self, threshold):
        self.threshold = threshold

    def compute_next_position(self):
        pass

    def get_current_position(self):
        pass

    def check_status(self):
        return self.get_current_position() > self.threshold
