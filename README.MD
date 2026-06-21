# ScreenWalker: Native macOS GUI Agent

ScreenWalker is a proof-of-concept "Computer Use" AI agent designed to run locally on Apple Silicon. Instead of relying on brittle web-scraping frameworks like Selenium or Playwright, this agent interacts with the computer exactly like a human does: it looks at the screen (via high-speed screenshots) and physically moves the hardware mouse to click on visual UI elements.

## 📖 Project Overview

At its core, this project utilizes **NVIDIA's LocateAnything-3B**, a hyper-optimized Vision-Language Model (VLM) trained specifically for Graphical User Interface (GUI) grounding. 

**The Architecture Loop:**
1. **The Eyes (`mss`):** Captures a sub-second screenshot of the active external monitor.
2. **The Brain (`LocateAnything-3B`):** Processes the image alongside a text query (e.g., "the browser search bar") and utilizes "Parallel Box Decoding" to instantly output the bounding box coordinates on a normalized 0-1000 grid.
3. **The Nervous System (Coordinate Math):** Translates the normalized 0-1000 grid into the exact pixel coordinates of your specific monitor.
4. **The Hands (`pyautogui`):** takes over the native operating system's Human Interface Device (HID) controls to physically move the cursor and execute keystrokes.

This architecture is entirely OS-agnostic and application-agnostic. If a button, text box, or icon is visible on the screen, ScreenWalker can find it and click it.

---

## 🚀 Quick Start & Installation

### Prerequisites
* An Apple Silicon Mac (M1/M2/M3)
* macOS Accessibility & Screen Recording permissions enabled for your Terminal/IDE.

### 1. Environment Setup
Due to strict dependency requirements in the underlying architecture, you **must** use Python 3.10.

```bash
# Install Python 3.10 via Homebrew
brew install python@3.10

# Create and activate the virtual environment
python3.10 -m venv .venv
source .venv/bin/activate