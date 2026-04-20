import os
import torch
from PIL import Image
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    CLIPProcessor,
    CLIPModel
)

# ---------------- FORCE OFFLINE MODE ----------------
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

print("🔒 Forced HuggingFace OFFLINE mode\n")

# ---------------- VERIFY IMAGE ----------------
IMAGE_PATH = "test.jpg"

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"❌ Image not found: {IMAGE_PATH}")

image = Image.open(IMAGE_PATH).convert("RGB")
print(f"✅ Using LOCAL image: {os.path.abspath(IMAGE_PATH)}")
print(f"📐 Image size: {image.size}\n")

# ---------------- LOAD MODELS (LOCAL ONLY) ----------------
print("📦 Loading BLIP & CLIP models from LOCAL cache...")

blip_model_name = "Salesforce/blip-image-captioning-base"
clip_model_name = "openai/clip-vit-base-patch32"

blip_processor = BlipProcessor.from_pretrained(
    blip_model_name,
    local_files_only=True
)
blip_model = BlipForConditionalGeneration.from_pretrained(
    blip_model_name,
    local_files_only=True
)

clip_processor = CLIPProcessor.from_pretrained(
    clip_model_name,
    local_files_only=True
)
clip_model = CLIPModel.from_pretrained(
    clip_model_name,
    local_files_only=True
)

print("✅ Models loaded from cache (NO internet used)\n")

# ---------------- BLIP CAPTION (STRICT IMAGE MODE) ----------------
print("📝 Generating caption using YOUR image...")

inputs = blip_processor(
    images=image,
    return_tensors="pt"
)

with torch.no_grad():
    output_ids = blip_model.generate(
        **inputs,
        max_new_tokens=40,
        do_sample=False
    )

caption = blip_processor.decode(
    output_ids[0],
    skip_special_tokens=True
)

print(f"➡️ BLIP Caption: {caption}\n")

# ---------------- CLIP CLASSIFICATION ----------------
labels = [
    "a classroom",
    "a person using a laptop",
    "a dog",
    "a cat",
    "a group of students",
    "a street scene",
    "blue sky"
]

clip_inputs = clip_processor(
    text=labels,
    images=image,
    return_tensors="pt",
    padding=True
)

with torch.no_grad():
    clip_outputs = clip_model(**clip_inputs)

probs = clip_outputs.logits_per_image.softmax(dim=1)[0]

print("🔍 CLIP Zero-Shot Results:")
for label, prob in zip(labels, probs):
    print(f"→ {label}: {prob.item():.4f}")

print("\n✅ OFFLINE BLIP + CLIP test COMPLETED (LOCAL IMAGE USED)")
