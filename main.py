import torch
from transformers import AutoProcessor, AutoModel
import mss
from PIL import Image

# Route computation to Apple Silicon
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Booting visual cortex on: {device}")

# Download and load the model (this will take a few minutes on the first run)
model_id = "nvidia/LocateAnything-3B"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id, 
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
).to(device)

def execute_atomic_command(command_string: str):
    print(f"Executing: {command_string}")
    
    # 1. Capture the screen via MSS
    with mss.MSS() as sct:
        monitor = sct.monitors[2] # Remember to change to 1 if testing on your built-in display!
        sct_img = sct.grab(monitor)
        # Convert raw capture to RGB for the model
        screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    
    # This keeps the aspect ratio but limits the longest edge to 1024 pixels
    screenshot.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    print(f"Resized screenshot to: {screenshot.size} for memory-safe processing.")
    
    # 2. Format the prompt correctly for a Vision-Language Model
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": f"Locate the region that matches the following description: {command_string}."}
            ]
        }
    ]
    
    # Let the processor inject the necessary <image> tokens and formatting
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # 3. Process and Generate
    inputs = processor(images=[screenshot], text=prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        # Fast mode generation
        outputs = model.generate(**inputs, max_new_tokens=30, use_cache=True, tokenizer=processor.tokenizer)
        
    if isinstance(outputs, str):
        result = outputs
    elif isinstance(outputs, list):
        # It likely returned a list containing the decoded string
        result = outputs[0]
        if isinstance(result, list):
             # Just in case it returned a nested list of string tokens
             result = "".join([str(x) for x in result])
    else:
        # Absolute fallback if it returns something unexpected
        result = str(outputs)
        
    print(f"Model Output: {result}")
    
    # 4. (Next step: Parse the <box> formatting and pass coordinates to pyautogui)

# Fire the POC
execute_atomic_command("the browser search bar")