import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Literal, Optional
from generate_wallpaper import generate_png_bytes, generate_svg_string, generate_xml_string, get_character_data, IPHONE_RESOLUTIONS, BASE_RESOLUTION

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
    openapi_version="3.1.0",
    root_path="/hanja-api"
)

# Mount static directories
app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse, include_in_schema=False)
def root():
    """Serve the wallpaper generator page."""
    return FileResponse("static/index.html")

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
        "hanja",
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

    try:
        char_data = get_character_data(character_list, character_id)
        width, height = IPHONE_RESOLUTIONS[iphone_model]
        scale_factor = width / BASE_RESOLUTION[0]
        
        if output_type == "png":
            img_bytes = generate_png_bytes(char_data, width, height, scale_factor, character_list)
            return StreamingResponse(
                img_bytes, 
                media_type="image/png",
                headers={"Content-Disposition": f"inline; filename=wallpaper_{character_list}_{char_data['id']}.png"}
            )
        elif output_type == "svg":
            svg_string = generate_svg_string(char_data, width, height, scale_factor, character_list)
            return Response(
                content=svg_string,
                media_type="image/svg+xml",
                headers={"Content-Disposition": f"inline; filename=wallpaper_{character_list}_{char_data['id']}.svg"}
            )
        elif output_type == "xml":
            xml_string = generate_xml_string(char_data, width, height, iphone_model, character_list)
            return Response(
                content=xml_string,
                media_type="application/xml",
                headers={"Content-Disposition": f"inline; filename=wallpaper_{character_list}_{char_data['id']}.xml"}
            )
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

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


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
