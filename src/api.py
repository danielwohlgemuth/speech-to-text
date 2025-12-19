import io
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transcriber import Transcriber
import whisper
import soundfile as sf

app = FastAPI(title="Speech-to-Text API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcriber_instances = {}

def get_transcriber(model_name: str) -> Transcriber:
    if model_name not in transcriber_instances:
        try:
            transcriber_instances[model_name] = Transcriber(model_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load model '{model_name}': {str(e)}")
    return transcriber_instances[model_name]

@app.get("/models")
async def get_available_models():
    try:
        models = whisper.available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

@app.post("/transcribe")
async def transcribe_audio(model_name: str, audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        transcriber = get_transcriber(model_name)

        audio_bytes = await audio.read()
        audio_io = io.BytesIO(audio_bytes)

        audio_data, sample_rate = sf.read(audio_io)

        if sample_rate != whisper.audio.SAMPLE_RATE:
            resampling_factor = whisper.audio.SAMPLE_RATE / sample_rate
            resampled_length = int(len(audio_data) * resampling_factor)
            indices = np.linspace(0, len(audio_data) - 1, resampled_length)
            audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data.flatten())

        transcription = transcriber.transcribe(audio_data)

        return {
            "text": transcription,
            "model": model_name,
            "sample_rate": sample_rate
        }

    except Exception as e:
        print(e, e.__traceback__)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
