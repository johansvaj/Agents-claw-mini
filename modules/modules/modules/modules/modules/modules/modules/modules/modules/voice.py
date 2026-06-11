try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer() if VOICE_AVAILABLE else None
        self.engine = pyttsx3.init() if VOICE_AVAILABLE else None
    def listen(self, timeout=5) -> str:
        if not VOICE_AVAILABLE:
            return ""
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                return self.recognizer.recognize_google(audio, language="id-ID")
            except:
                return ""
    def speak(self, text: str):
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
