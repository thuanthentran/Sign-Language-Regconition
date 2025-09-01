from flask import Flask, Response, jsonify, request, send_file
import cv2
import mediapipe as mp
import json
from flask_cors import CORS
from utils.feature_extraction import *
from utils.model import ASLClassificationModel
from utils.strings import *
from tts import TextToSpeech

from config import MODEL_NAME, MODEL_CONFIDENCE

app = Flask(__name__)
CORS(app)

sentence = ""
tts = TextToSpeech()

# Load model
model = ASLClassificationModel.load_model(f"models/{MODEL_NAME}")
expression_handler = ExpressionHandler()

# Store predicted words
sentence_buffer = []

last_word = None
stable_count = 0
STABLE_THRESHOLD = 15 # Số khung hình cần thiết để từ được coi là ổn định

# Mediapipe init
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=MODEL_CONFIDENCE,
                                  min_tracking_confidence=MODEL_CONFIDENCE)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2,
                       min_detection_confidence=MODEL_CONFIDENCE,
                       min_tracking_confidence=MODEL_CONFIDENCE)

cap = cv2.VideoCapture(0)


@app.route("/video_feed")
def video_feed():
    global last_word, stable_count
    def gen():
        while True:
            success, frame = cap.read()
            if not success:
                continue

            # Convert BGR -> RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Run Mediapipe
            face_results = face_mesh.process(rgb)
            hand_results = hands.process(rgb)

            # Predict
            feature = extract_features(mp_hands, face_results, hand_results)
            expression = model.predict(feature)
            expression_handler.receive(expression)

            # Nếu có từ dự đoán thì thêm vào câu
            word = expression_handler.get_message()

            # Chỉ thêm nếu từ ổn định
            global last_word, stable_count
            if word == last_word:
                stable_count += 1
            else:
                stable_count = 0
                last_word = word

            if stable_count >= STABLE_THRESHOLD:
                if len(sentence_buffer) == 0 or sentence_buffer[-1] != word:
                    sentence_buffer.append(word)
                    print("✅ Accepted word:", word)  # log từ đã chấp nhận
                stable_count = 0  # reset sau khi đã nhận

            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/prediction")
def prediction():
    word = expression_handler.get_message()
    sentence = " ".join(sentence_buffer)
    print(f"[API CALL] word={word}, sentence={sentence}")
    return app.response_class(
    response=json.dumps({"word": word, "sentence": " ".join(sentence_buffer)}, ensure_ascii=False),
    status=200,
    mimetype='application/json'
)

@app.route("/reset")
def reset_sentence():
    sentence = ""
    return jsonify({"message": "Sentence cleared"})

@app.route("/speak")
def speak():
    sentence = " ".join(sentence_buffer)  # convert từ list sang chuỗi
    if not sentence.strip():
        sentence = "Không có câu nào để đọc."
    return tts.stream(sentence)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)