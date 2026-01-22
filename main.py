import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.responses import FileResponse, JSONResponse, Response
from typing import Literal, Optional
from generate_wallpaper import generate_wallpaper, IPHONE_RESOLUTIONS
from shortcut_generator import generate_shortcut

# Load environment variables from .env file
load_dotenv()

# API Key Authentication
API_KEY = os.getenv("API_KEY")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if one is configured."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

app = FastAPI(
    title="Hanja API",
    description="Generate wallpapers or data files with Chinese/Hanja characters.",
    version="1.0.0",
)

OUTPUT_DIR = "generated_wallpapers"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/wallpaper",
         summary="Generate a character wallpaper or data file",
         response_description="Returns the generated file or a JSON error.",
         dependencies=[Depends(verify_api_key)],
)
def create_wallpaper_endpoint(
    output_type: Literal["png", "svg", "xml"] = Query(
        "png",
        description="The type of output to generate.",
    ),
    character_list: Literal["hsk", "hanja"] = Query(
        "hsk",
        description="The character set to use.",
    ),
    character_id: Optional[int] = Query(
        None,
        description="The ID of the character to use. If not provided, a random character is chosen.",
        ge=0,
    ),
    iphone_model: str = Query(
        "iphone_13_mini",
        description=f"The iPhone model for resolution. Available models: {', '.join(IPHONE_RESOLUTIONS.keys())}",
    ),
):
    """
    Generates a wallpaper or data file based on the provided parameters.

    - **output_type**: The format of the output file (`png`, `svg`, `xml`).
    - **character_list**: The character set to draw from (`hsk` or `hanja`).
    - **character_id**: Specific character ID to use. If omitted, a random character is selected.
    - **iphone_model**: Defines the output resolution based on a preset iPhone model.
    """
    if iphone_model not in IPHONE_RESOLUTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid iPhone model. Please choose from: {', '.join(IPHONE_RESOLUTIONS.keys())}",
        )

    # Generate a unique filename
    random_id = os.urandom(4).hex()
    output_filename = f"wallpaper_{character_list}_{character_id or random_id}.{output_type}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        message = generate_wallpaper(
            output_path=output_path,
            character_id=character_id,
            iphone_model=iphone_model,
            output_type=output_type,
            character_list=character_list,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if os.path.exists(output_path):
        return FileResponse(
            output_path,
            media_type=f"image/{output_type}" if output_type != 'xml' else 'application/xml',
            filename=output_filename
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to generate the file.")

@app.get("/models",
         summary="List available iPhone models",
         response_description="A JSON object containing all available iPhone models and their resolutions.",
         dependencies=[Depends(verify_api_key)],
)
def get_models():
    """
    Returns a dictionary of all supported iPhone models and their corresponding
    resolutions (width, height).
    """
    return JSONResponse(content=IPHONE_RESOLUTIONS)


@app.get("/shortcut",
         summary="Generate an Apple Shortcut file",
         response_description="Returns a .shortcut file for Apple Shortcuts.",
         dependencies=[Depends(verify_api_key)],
)
def get_shortcut(
    api_url: str = Query(
        ...,
        description="Base URL of the deployed API (e.g., https://api.example.com)",
    ),
    iphone_model: str = Query(
        "iphone_13_mini",
        description=f"Default iPhone model for the shortcut. Available: {', '.join(IPHONE_RESOLUTIONS.keys())}",
    ),
    character_list: Literal["hsk", "hanja"] = Query(
        "hsk",
        description="Default character set for the shortcut.",
    ),
    refresh_rate: Optional[int] = Query(
        None,
        description="Auto-refresh interval in minutes. If provided, the shortcut will loop and fetch a new wallpaper at this interval.",
        ge=1,
    ),
):
    """
    Generate an Apple Shortcut (.shortcut file) preconfigured to call the API.

    The shortcut will:
    - Call `/wallpaper` with a random character
    - Set the result as the device wallpaper (both lock screen and home screen)
    - Use the parameters baked in based on the query params provided here
    - If refresh_rate is set, loop indefinitely and refresh the wallpaper at the given interval
    """
    if iphone_model not in IPHONE_RESOLUTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid iPhone model. Please choose from: {', '.join(IPHONE_RESOLUTIONS.keys())}",
        )

    shortcut_data = generate_shortcut(
        api_url=api_url,
        iphone_model=iphone_model,
        character_list=character_list,
        refresh_rate=refresh_rate,
    )

    return Response(
        content=shortcut_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=hanja_wallpaper_{character_list}.shortcut"
        },
    )


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)