import os
from pydub import AudioSegment
import requests
from configs import Configs
import json


def extrapolate_audio(input_path, output_folder, target_duration_sec=10):
    """
    Extrapolates (loops) a short audio file to at least target_duration_sec seconds.
    Args:
        input_path (str): Path to the input audio file.
        output_folder (str): Folder to save the output file.
        target_duration_sec (int): Minimum duration for the output audio in seconds.
    Returns:
        str: Path to the output audio file.
    """
    # Load audio
    audio = AudioSegment.from_file(input_path)
    target_duration_ms = target_duration_sec * 1000

    # Loop the audio until reaching the target duration
    loops = (target_duration_ms // len(audio)) + 1
    extended_audio = audio * loops
    extended_audio = extended_audio[:target_duration_ms]

    # Prepare output path
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.basename(input_path))
    extended_audio.export(output_path, format="wav")

    print(f"Extrapolated audio saved to: {output_path}")
    return output_path


def create_elevenlabs_voice_clone(api_key, name, audio_path, description=""):
    """
    Calls ElevenLabs API to create a voice clone from a reference audio file.
    Args:
        api_key (str): Your ElevenLabs API key.
        name (str): Name for the new voice.
        audio_path (str): Path to the reference audio file.
        description (str): Optional description for the voice.
    Returns:
        str: The created voice ID.
    """
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {"xi-api-key": api_key}
    files = {
        "files": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/wav"),
    }
    data = {
        "name": name,
        "description": description,
        "labels": "{}",
    }
    response = requests.post(url, headers=headers, data=data, files=files)
    response.raise_for_status()
    voice_id = response.json().get("voice_id")
    print(f"Created ElevenLabs voice with ID: {voice_id}")
    return voice_id


def elevenlabs_text_to_speech(
    api_key, voice_id, text, output_path, model_id="eleven_multilingual_v2"
):
    """
    Calls ElevenLabs API to generate TTS audio from text using a voice reference audio.
    Args:
        api_key (str): Your ElevenLabs API key.
        voice_id (str): The voice ID to use.
        text (str): The text to synthesize.
        output_path (str): Path to save the output audio file.
        model_id (str): Model to use (default: "eleven_multilingual_v2").
    Returns:
        str: Path to the saved audio file.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"TTS audio saved to: {output_path}")
    return output_path


def elevenlabs_speech_to_text(api_key, audio_path, model_id="scribe_v1"):
    """
    Transcribes audio to text using ElevenLabs Speech-to-Text API.
    Args:
        api_key (str): Your ElevenLabs API key.
        audio_path (str): Path to the audio file.
    model_id (str): Model to use (default: scribe_v1).
    Returns:
        str: Transcribed text.
    """
    url = f"https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": api_key}
    data = {"model_id": model_id}
    # Use correct parameter name 'file' and context manager
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
        response = requests.post(url, headers=headers, data=data, files=files)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"STT API error: {response.text}")
        raise
    text = response.json().get("text", "")
    print(f"Transcribed text: {text}")
    return text


def get_elevenlabs_voice_id_by_name(api_key, name):
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    voices = response.json().get("voices", [])
    for v in voices:
        if v.get("name", "").lower() == name.lower():
            return v.get("voice_id")
    return None


def generate_elevenlabs_cloned_voice_from_retellai(params):
    """
    Given params dict with keys: audio_path, voice_name, description, text
    - Extrapolates audio to 10s
    - Checks/creates voice clone
    - Generates TTS
    Returns dict with paths and voice_id
    """
    api_key = Configs.ELEVENLABS_API_KEY
    output_dir = "output"

    # Extract retell_id and audio_path
    retell_id = params["retell_id"]
    audio_path = params["audio_path"]

    # Extract name after dash
    if "-" in retell_id:
        extracted_name = retell_id.split("-", 1)[1]
    else:
        extracted_name = retell_id

    voice_name = f"Retellai-Cloned-{extracted_name}"
    description = f"Retellai Cloned {extracted_name} voice."

    # 1. Extrapolate audio
    extrapolated_path = extrapolate_audio(
        audio_path, output_dir, target_duration_sec=10
    )

    # 2. Check for existing voice by name
    voice_id = get_elevenlabs_voice_id_by_name(api_key, voice_name)
    if voice_id:
        print(f"Voice '{voice_name}' already exists with ID: {voice_id}")
    else:
        # 3. Create new voice clone
        voice_id = create_elevenlabs_voice_clone(
            api_key,
            voice_name,
            extrapolated_path,
            description,
        )

    # 4. Transcribe audio to text
    stt_text = elevenlabs_speech_to_text(api_key, audio_path)
    tts_text = (
        stt_text.strip()
        + " My voice is generated using the ElevenLabs model, based on the Retell ai voice. Feel free to ask me anything you need help with."
    )

    # 5. Generate TTS using the (new or existing) voice
    tts_output_path = os.path.join(output_dir, f"tts_{voice_name}.mp3")
    elevenlabs_text_to_speech(api_key, voice_id, tts_text, tts_output_path)
    print(f"TTS audio saved to: {tts_output_path}")
    return {
        "extrapolated_audio_path": extrapolated_path,
        "voice_id": voice_id,
        "tts_output_path": tts_output_path,
        "transcribed_text": stt_text,
        "tts_text": tts_text,
        "voice_name": voice_name,
        "description": description,
    }


# Example usage:
if __name__ == "__main__":
    # Example input: only retell_id and audio_path
    input_json = """
    {
        "retell_id": "11labs-Zuri",
        "audio_path": "input/zuri.mp3"
    }
    """
    params = json.loads(input_json)
    result = generate_elevenlabs_cloned_voice_from_retellai(params)
    print(result)
