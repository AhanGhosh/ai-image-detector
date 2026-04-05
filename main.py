from fastapi import FastAPI, File, UploadFile
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import io

app = FastAPI()

# --- STEP 1: DEFINE THE SKELETON ---
def load_trained_model(weights_path):
    # Initialize ResNet50
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2) 
    
    # Load weights
    state_dict = torch.load(weights_path, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    model.eval()
    return model

# --- STEP 2: LOAD THE MODELS ---
try:
    print("🚀 Initializing AI Engines...")
    model1 = load_trained_model("filter_model.pth")
    model2 = load_trained_model("ai_detector_model.pth")
    print("✅ Models Loaded and Ready!")
except Exception as e:
    print(f"❌ ERROR LOADING MODELS: {e}")

# --- STEP 3: PREPROCESSING ---
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        # --- STAGE 1: Filter (Digital vs Natural) ---
        out1 = model1(input_tensor)
        idx1 = out1.argmax().item()
        
        # DEBUG: See what's happening in your terminal
        print(f"DEBUG: Model 1 Index -> {idx1}")

        # Based on your Streamlit order: 0=Digital, 1=Natural
        if idx1 == 0: 
            return {
                "digital_check": "Fake: Digitally Created/Manipulated",
                "ai_check": "Filtered by Stage 1"
            }

        # --- STAGE 2: AI Detector (AI vs Real) ---
        # Runs only if Model 1 predicted Index 1 (Natural)
        out2 = model2(input_tensor)
        idx2 = out2.argmax().item()
        
        print(f"DEBUG: Model 2 Index -> {idx2}")

        # Based on your Streamlit order: 0=AI_Generated, 1=Camera_Real
        if idx2 == 0:
            res2 = "Fake: AI Generated Image"
        else:
            res2 = "Real: Authentic Camera Image"

    return {
        "digital_check": "Passed (Natural Image)",
        "ai_check": res2
    }