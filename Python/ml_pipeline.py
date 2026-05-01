# ml_pipeline.py
import os
import torch
from PIL import Image
from transformers import (
    BlipProcessor, BlipForConditionalGeneration,
    CLIPProcessor, CLIPModel
)

# Force Offline Mode
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Load Models
BLIP_MODEL = "Salesforce/blip-image-captioning-base"
CLIP_MODEL = "openai/clip-vit-base-patch32"

blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL, local_files_only=True, use_fast=True)
blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL, local_files_only=True)

clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL, local_files_only=True, use_fast=True)
clip_model = CLIPModel.from_pretrained(CLIP_MODEL, local_files_only=True)

def process_image(image_path, labels=None, max_words=40):
    image = Image.open(image_path).convert("RGB")

    # --- BLIP CAPTION (Unlocked for length) ---
    blip_inputs = blip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        blip_output = blip_model.generate(
            **blip_inputs,
            max_new_tokens=max_words, # Uses the slider value
            min_new_tokens=max_words // 2, # Forces at least half the length
            repetition_penalty=1.3 # Prevents the model from getting stuck on one word
        )
    caption = blip_processor.decode(blip_output[0], skip_special_tokens=True)

    # --- CLIP CLASSIFICATION ---
    if labels is None:
        labels = ["a scene", "indoor", "outdoor"] # Default fallback

    clip_inputs = clip_processor(text=labels, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        clip_outputs = clip_model(**clip_inputs)

    probs = clip_outputs.logits_per_image.softmax(dim=1)[0]
    top_results = sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)[:5]

    # Return as separate pieces for the UI
    return {
        "caption": caption,
        "predictions": top_results
    }
