import torch
import os
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_pipeline = None
_device = None


def _load_pipeline():
    """Lazy-load the Stable Diffusion pipeline on first use."""
    global _pipeline, _device
    if _pipeline is not None:
        return _pipeline

    from diffusers import StableDiffusionPipeline

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if _device == "cuda" else torch.float32

    logger.info("Loading Stable Diffusion model on %s (this may take a minute on first run)...", _device)

    _pipeline = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1-base",
        torch_dtype=dtype,
    )
    _pipeline = _pipeline.to(_device)

    # Memory optimizations
    if _device == "cuda":
        _pipeline.enable_attention_slicing()

    _pipeline.safety_checker = None
    _pipeline.requires_safety_checker = False

    logger.info("Stable Diffusion model loaded successfully on %s", _device)
    return _pipeline


def build_design_prompt(style: str, user_message: str, style_info: dict) -> str:
    """Build a rich prompt for interior design image generation."""
    colors = ", ".join(style_info.get("colors", [])[:4])
    materials = ", ".join(style_info.get("materials", [])[:3])

    prompt = (
        f"Professional interior design photograph, {style} style room. "
        f"Color palette: {colors}. "
        f"Materials: {materials}. "
        f"{user_message}. "
        "Photorealistic, high quality, architectural visualization, "
        "well-lit, magazine quality interior photography, 8k, detailed"
    )

    negative_prompt = (
        "blurry, low quality, distorted, watermark, text, logo, "
        "cartoon, anime, painting, drawing, sketch, ugly, deformed"
    )

    return prompt[:500], negative_prompt


def generate_image(
    style: str,
    user_message: str,
    style_info: dict,
    save_dir: str,
) -> Optional[str]:
    """Generate an interior design image using local Stable Diffusion model.

    Returns the relative URL path to the saved image, or None on failure.
    """
    try:
        pipe = _load_pipeline()

        prompt, negative_prompt = build_design_prompt(style, user_message, style_info)

        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            width=768,
            height=768,
        )

        image = result.images[0]

        gen_dir = os.path.join(save_dir, "generated")
        os.makedirs(gen_dir, exist_ok=True)

        filename = f"design_{uuid.uuid4().hex[:12]}.png"
        filepath = os.path.join(gen_dir, filename)
        image.save(filepath)

        logger.info("Image generated and saved: %s", filepath)
        return f"/uploads/generated/{filename}"

    except Exception as e:
        logger.error("Image generation failed: %s", str(e))
        return None
