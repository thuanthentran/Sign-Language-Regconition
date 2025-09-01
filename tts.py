import os
from gtts import gTTS
from flask import send_file

class TextToSpeech:
    def __init__(self, language="vi"):
        self.language = language
        self.output_file = "text.mp3"

    def synthesize(self, text: str):
        """Chuyển văn bản thành file mp3"""
        if not text.strip():
            raise ValueError("Text rỗng, không thể đọc.")
        tts = gTTS(text=text, lang=self.language, slow=False)
        tts.save(self.output_file)
        return os.path.abspath(self.output_file)

    def stream(self, text: str):
        """Trả file mp3 về cho Flask response"""
        filepath = self.synthesize(text)
        return send_file(filepath, mimetype="audio/mpeg")