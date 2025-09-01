class ExpressionHandler:

    MAPPING = {
        "bình_thường": "",
        "cảm_ơn": "cảm ơn",
        "xin_chào": "xin chào ‍",
        "yêu": "yêu",
        "không": "không",
        "mẹ": "mẹ",
        "bố": "bố",
        "bà": "bà",
        "tạm_biệt": "tạm biệt",
        "xin_lỗi": "xin lỗi",
        "ba": "ba",
        "hai": "hai",
        "một": "một",
        "bốn": "bốn"
    }

    def __init__(self):
        # Save the current message and the time received the current message
        self.current_message = ""

    def receive(self, message):
        self.current_message = message

    def get_message(self):
        return ExpressionHandler.MAPPING.get(self.current_message, "")
