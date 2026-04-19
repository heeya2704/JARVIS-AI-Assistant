import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import load_dotenv
from gtts import gTTS
from elevenlabs import ElevenLabs

# Use load_dotenv() instead of dotenv_values()
load_dotenv()

# Get environment variables with defaults
AssistantVoice = os.getenv("AssistantVoice", "en-US-JennyNeural")  # Default voice
ElevenLabsAPIKey = os.getenv("ElevenLabsAPIKey")

async def TextToAudioFile(text) -> None:
    file_path = os.path.join("Data", "speech.mp3")

    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def gTTSTTS(text):
    """Free fallback TTS using Google Text-to-Speech"""
    try:
        file_path = os.path.join("Data", "speech.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)

        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(file_path)
        return True

    except Exception as e:
        print(f"gTTS error: {e}")
        return False

def elevenlabsTTS(text):
    """Fallback TTS using ElevenLabs"""
    try:
        if not ElevenLabsAPIKey:
            print("ElevenLabs API key not found.")
            return False

        file_path = os.path.join("Data", "speech.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)

        client = ElevenLabs(api_key=ElevenLabsAPIKey)
        audio = client.generate(
            text=text,
            voice="Rachel",
            model_id="eleven_monolingual_v1"
        )

        with open(file_path, "wb") as f:
            f.write(b''.join(audio))

        return True

    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return False

def TTS(Text, func=lambda r=None: True):
    file_path = os.path.join("Data", "speech.mp3")
    
    # Try edge-tts first
    try:
        asyncio.run(TextToAudioFile(Text))
    except Exception as e:
        print(f"Edge-TTS failed: {e}")
        
        # Try gTTS as fallback
        if not gTTSTTS(Text):
            # Try ElevenLabs as last resort
            if not elevenlabsTTS(Text):
                print("All TTS methods failed!")
                return False
    
    # Play the audio
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()

        while pygame.mixer.music.get_busy():
            if not func():
                break
            clock.tick(10)

        return True
        
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False
        
    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in cleanup: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)
# jar tumhala purna read karaich lavaich asel tr TTS cha use kara jar 4 or tya peksha line 
# jast lines text asel tr TTS use kra ani Short made read karacih asel tr texttosppech use kara  
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text : "))