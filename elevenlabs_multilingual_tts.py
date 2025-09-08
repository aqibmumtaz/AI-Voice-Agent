import os
import requests
from typing import List, Dict
from googletrans import Translator
from configs import Configs
from utils import Utils


def translate_text(text: str, dest_lang: str) -> str:
    translator = Translator()
    result = translator.translate(text, dest=dest_lang)
    return result.text


def elevenlabs_text_to_speech(
    api_key, voice_id, text, output_path, model_id="eleven_turbo_v2"
):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            # "speed": 1.0,  # Controls playback speed (1.0 = normal), default is 1.0
            "stability": 0.5,  # Controls voice consistency (0.0-1.0), default is 0.5
            "similarity_boost": 0.75,  # Controls similarity to original voice (0.0-1.0), default is 0.75
            # Optional settings below (if supported by your ElevenLabs plan/model):
            # "style": 0.0,             # Controls expressiveness (0.0-1.0)
            # "use_speaker_boost": True # Boosts speaker presence (True/False)
        },
    }
    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"TTS API error for model {model_id}, voice {voice_id}: {response.text}")
        raise
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"TTS audio: {output_path}")
    return output_path


def delete_elevenlabs_voice(api_key, voice_id):
    """
    Deletes a custom voice from ElevenLabs.
    Note: Only custom voices can be deleted, not public voices.
    If you use a public voice for TTS, ElevenLabs may clone it to 'My Voices' as a custom voice.
    This function will attempt to delete the custom voice if it exists.
    """
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {"xi-api-key": api_key}
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Deleted ElevenLabs voice: {voice_id}")
    else:
        print(f"Failed to delete voice {voice_id}: {response.text}")


def generate_multilingual_tts_for_voices(
    voice_list: List[Dict[str, str]],
    output_dir: str,
    tts_models=None,
    delete_custom_voices=False,
):
    """
    voice_list: List of dicts with keys 'voice_id', 'language', and optionally 'name'.
    text: The input text to translate and synthesize.
    output_dir: Directory to save output audio files.
    delete_custom_voices: If True, attempts to delete the voice after TTS (only works for custom voices).
    """
    api_key = Configs.ELEVENLABS_API_KEY
    os.makedirs(output_dir, exist_ok=True)
    if tts_models is None:
        tts_models = ["eleven_turbo_v2"]
    for voice in voice_list:
        voice_id = voice["voice_id"]
        language = voice["language"]
        input_text = voice["input_text"]
        print(f"\nVoice: {language} (ID: {voice_id})")
        print(f'Input text: "{input_text}"')
        success = False
        for model_id in tts_models:
            output_path = os.path.join(output_dir, f"tts_{language}_{model_id}.mp3")
            try:
                elevenlabs_text_to_speech(
                    api_key, voice_id, input_text, output_path, model_id=model_id
                )
                success = True
            except Exception as e:
                print(
                    f"Error processing voice {language} (ID: {voice_id}, Model: {model_id}): {e}"
                )
                continue
        if delete_custom_voices and success:
            delete_elevenlabs_voice(api_key, voice_id)


if __name__ == "__main__":

    # Example usage
    voice_list = [
        {
            "voice_id": "ZIlrSGI4jZqobxRKprJz",
            "language": "English",
            "input_text": "Hello, I’m your virtual assistant, here to help you anytime.",
        },
        {
            "voice_id": "uYFJyGaibp4N2VwYQshk",
            "language": "Czech",
            "input_text": "Ahoj, jsem váš virtuální asistent, jsem tu, abych vám kdykoli pomohl.",
        },
        {
            "voice_id": "ygiXC2Oa1BiHksD3WkJZ",
            "language": "Danish",
            "input_text": "Hej, jeg er din virtuelle assistent, klar til at hjælpe dig når som helst.",
        },
        {
            "voice_id": "jfwdd64Nlhnj6vcFqRHZ",
            "language": "Dutch",
            "input_text": "Hallo, ik ben je virtuele assistent, altid klaar om je te helpen.",
        },
        {
            "voice_id": "YxrwjAKoUKULGd0g8K9Y",
            "language": "French",
            "input_text": "Bonjour, je suis votre assistant virtuel, prêt à vous aider à tout moment.",
        },
        {
            "voice_id": "aTTiK3YzK3dXETpuDE2h",
            "language": "German",
            "input_text": "Hallo, ich bin Ihr virtueller Assistent und stehe Ihnen jederzeit zur Verfügung.",
        },
        {
            "voice_id": "wykE1oPxFaMrxdpOtFt6",
            "language": "Greek",
            "input_text": "Γεια σας, είμαι ο εικονικός σας βοηθός, εδώ για να σας βοηθήσω οποιαδήποτε στιγμή.",
        },
        {
            "voice_id": "1Z7Y8o9cvUeWq8oLKgMY",
            "language": "Hindi",
            "input_text": "नमस्ते, मैं आपका वर्चुअल असिस्टेंट हूँ, जो कभी भी आपकी मदद के लिए यहाँ हूँ।",
        },
        {
            "voice_id": "v70fYBHUOrHA3AKIBjPq",
            "language": "Indonesian",
            "input_text": "Halo, saya asisten virtual Anda, siap membantu Anda kapan saja.",
        },
        {
            "voice_id": "HuK8QKF35exsCh2e7fLT",
            "language": "Italian",
            "input_text": "Ciao, sono il tuo assistente virtuale, qui per aiutarti in qualsiasi momento.",
        },
        {
            "voice_id": "3JDquces8E8bkmvbh6Bc",
            "language": "Japanese",
            "input_text": "こんにちは、私はあなたのバーチャルアシスタントです。いつでもお手伝いします。",
        },
        {
            "voice_id": "4JJwo477JUAx3HV0T7n7",
            "language": "Korean",
            "input_text": "안녕하세요, 저는 언제든지 도와드릴 수 있는 가상 비서입니다.",
        },
        {
            "voice_id": "dgrgQcxISbZtq517iweJ",
            "language": "Norwegian",
            "input_text": "Hei, jeg er din virtuelle assistent, her for å hjelpe deg når som helst.",
        },
        {
            "voice_id": "EmspiS7CSUabPeqBcrAP",
            "language": "Polish",
            "input_text": "Cześć, jestem twoim wirtualnym asystentem, gotowym do pomocy w każdej chwili.",
        },
        {
            "voice_id": "tS45q0QcrDHqHoaWdCDR",
            "language": "Portuguese",
            "input_text": "Olá, sou seu assistente virtual, aqui para ajudar você a qualquer momento.",
        },
        {
            "voice_id": "AB9XsbSA4eLG12t2myjN",
            "language": "Russian",
            "input_text": "Здравствуйте, я ваш виртуальный помощник, всегда готов помочь вам.",
        },
        {
            "voice_id": "2Lb1en5ujrODDIqmp7F3",
            "language": "Spanish",
            "input_text": "Hola, soy tu asistente virtual, aquí para ayudarte en cualquier momento.",
        },
        {
            "voice_id": "x0u3EW21dbrORJzOq1m9",
            "language": "Swedish",
            "input_text": "Hej, jag är din virtuella assistent, här för att hjälpa dig när som helst.",
        },
        {
            "voice_id": "D1xRw7f8ZHedI7xJgfvz",
            "language": "Turkish",
            "input_text": "Merhaba, ben sizin sanal asistanınızım, size her zaman yardımcı olmaya hazırım.",
        },
        {
            "voice_id": "bg0e02brzo3RVUEbuZeo",
            "language": "Ukrainian",
            "input_text": "Привіт, я ваш віртуальний помічник, завжди готовий допомогти вам у будь-який час.",
        },
    ]

    output_dir = "output"
    Utils.clear_dir(output_dir)

    # List of available ElevenLabs TTS models (as of 2024-06)
    tts_models = [
        # "eleven_turbo_v2",
        "eleven_turbo_v2_5",
        # "eleven_multilingual_v2",
    ]

    # Set delete_custom_voices=True to attempt deleting voices after TTS (only works for custom voices)
    delete_custom_voices = True

    generate_multilingual_tts_for_voices(
        voice_list,
        output_dir,
        tts_models=tts_models,
        delete_custom_voices=delete_custom_voices,
    )
