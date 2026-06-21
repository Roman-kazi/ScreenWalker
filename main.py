# --- THE PHANTOM MODULE BYPASS (V2) ---
import sys
import types
from importlib.machinery import ModuleSpec

# Create an empty, fake module
dummy_decord = types.ModuleType('decord')

# Give it a fake specification card so importlib doesn't crash
dummy_decord.__spec__ = ModuleSpec(name='decord', loader=None)

# Give it empty dummy classes just in case the script looks for them
dummy_decord.VideoReader = type('VideoReader', (object,), {})
dummy_decord.cpu = lambda: None

# Inject it directly into Python's brain
sys.modules['decord'] = dummy_decord
# --------------------------------------

import torch
from transformers import AutoProcessor, AutoModel
import mss
from PIL import Image
import re
import pyautogui
import time

# Failsafe: Slam your mouse to any corner of the screen to abort the script if it goes rogue
pyautogui.FAILSAFE = True

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Booting visual cortex on: {device}")

model_id = "nvidia/LocateAnything-3B"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id, 
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
).to(device)

def execute_atomic_command(command_string: str, text_to_type: str = None):
    print(f"Executing: {command_string}")
    
    # 1. Capture the screen
    with mss.MSS() as sct:
        monitor = sct.monitors[2] # Targeting external monitor
        sct_img = sct.grab(monitor)
        screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # Save exact screen dimensions for math later
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        screen_offset_x = monitor["left"]
        screen_offset_y = monitor["top"]
    
    screenshot.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    
    # 2. Format the prompt
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": f"Locate the region that matches the following description: {command_string}."}
            ]
        }
    ]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # 3. Process and Generate
    inputs = processor(images=[screenshot], text=prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=30, 
            use_cache=True,
            tokenizer=processor.tokenizer
        )
        
    if isinstance(outputs, str):
        result = outputs
    elif isinstance(outputs, list):
        result = outputs[0]
        if isinstance(result, list):
             result = "".join([str(x) for x in result])
    else:
        result = str(outputs)
        
    print(f"Model Output: {result}")
    
    # --- 4. The Nervous System: Coordinate Translation ---
    # Extract the numbers using regex
    match = re.search(r'<box><(\d+)><(\d+)><(\d+)><(\d+)></box>', result)
    
    if match:
        x_min, y_min, x_max, y_max = map(int, match.groups())
        
        # Find the center of the box on the 0-1000 scale
        norm_center_x = (x_min + x_max) / 2
        norm_center_y = (y_min + y_max) / 2
        
        # Translate to actual screen pixels
        real_x = screen_offset_x + int((norm_center_x / 1000) * screen_width)
        real_y = screen_offset_y + int((norm_center_y / 1000) * screen_height)
        
        print(f"Target locked. Moving mouse to pixel: ({real_x}, {real_y})")
        
        # --- 5. The Hands: Physical OS Action ---
        # Move the mouse (duration=0.5 makes it move visibly like a human)
        pyautogui.moveTo(real_x, real_y, duration=0.5)
        pyautogui.click()
        
        # If we passed text to type, type it like a human
        if text_to_type:
            time.sleep(0.2) # Human reaction delay
            pyautogui.write(text_to_type, interval=0.05)
            pyautogui.press("enter")
            
        return {"status": "success", "action": "clicked"}
    else:
        print("Failed to find target on screen.")
        return {"status": "error", "action": "none"}

# Fire the POC (Make sure your browser is open on your external monitor!)
execute_atomic_command("the browser search bar", "Raspberry Pi headless setup")