# ...existing code for imports, class, and FastAPI app...


from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
from elevenlabs import generate_elevenlabs_cloned_voice_from_retellai
from utils import Utils

app = FastAPI()


@app.post("/generate-cloned-voice")
async def generate_cloned_voice(
    retell_id: str = Form(...),
    language: str = Form("english"),
    tts_text: str = Form(...),
    voice_name: str = Form(None),
    description: str = Form(None),
    audio: UploadFile = File(...),
):
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    Utils.clear_dir(cache_dir)
    audio_path = os.path.join(cache_dir, audio.filename)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    params = {
        "retell_id": retell_id,
        "audio_path": audio_path,
        "language": language,
        "tts_text": tts_text,
        "voice_name": voice_name,
        "description": description,
    }

    result = generate_elevenlabs_cloned_voice_from_retellai(
        params, output_dir=cache_dir
    )
    tts_path = result["tts_output_path"]

    return FileResponse(
        tts_path, media_type="audio/mpeg", filename=os.path.basename(tts_path)
    )


# Main block at the end of the file
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
