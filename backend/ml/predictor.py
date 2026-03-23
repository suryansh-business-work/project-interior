import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import json
import os
from typing import Dict, List, Tuple
from ml.model import InteriorStyleClassifier
from app.config import settings, STYLE_CLASSES


class StylePredictor:
    """Handles loading the trained model and making predictions."""

    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.class_mapping = None
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    @classmethod
    def get_instance(cls) -> "StylePredictor":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self):
        model_path = settings.MODEL_PATH
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}. Predictions will use fallback.")
            return False

        mapping_path = os.path.join(os.path.dirname(model_path), "class_mapping.json")
        if os.path.exists(mapping_path):
            with open(mapping_path) as f:
                self.class_mapping = json.load(f)
        else:
            self.class_mapping = {
                "idx_to_class": {str(i): name for i, name in enumerate(STYLE_CLASSES)}
            }

        num_classes = len(self.class_mapping["idx_to_class"])
        self.model = InteriorStyleClassifier.load_trained(model_path, num_classes, str(self.device))
        print(f"Model loaded on {self.device}")
        return True

    def predict(self, image_path: str, top_k: int = 5) -> Dict:
        if self.model is None:
            return self._fallback_prediction()

        image = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]

        top_probs, top_indices = torch.topk(probabilities, top_k)
        idx_to_class = self.class_mapping["idx_to_class"]

        top_styles = []
        for prob, idx in zip(top_probs.cpu().numpy(), top_indices.cpu().numpy()):
            style_name = idx_to_class[str(idx)]
            top_styles.append({
                "style": style_name,
                "confidence": round(float(prob) * 100, 2)
            })

        return {
            "predicted_style": top_styles[0]["style"],
            "confidence": top_styles[0]["confidence"],
            "top_styles": top_styles
        }

    def _fallback_prediction(self) -> Dict:
        """Fallback when model is not loaded - returns default modern style."""
        return {
            "predicted_style": "modern",
            "confidence": 0.0,
            "top_styles": [{"style": "modern", "confidence": 0.0}],
            "note": "Model not loaded. Using fallback."
        }


# Design knowledge base for generating suggestions
DESIGN_KNOWLEDGE = {
    "asian": {
        "colors": ["warm neutrals", "earth tones", "red accents", "black", "gold"],
        "materials": ["bamboo", "silk", "rice paper", "teak wood", "stone"],
        "furniture": ["low platform beds", "shoji screens", "tatami mats", "zen garden elements"],
        "tips": "Focus on minimalism, natural materials, and balance. Use clean lines with organic textures."
    },
    "coastal": {
        "colors": ["ocean blue", "sandy beige", "white", "coral", "seafoam green"],
        "materials": ["driftwood", "rattan", "linen", "jute", "sea glass"],
        "furniture": ["slipcovered sofas", "wicker chairs", "distressed wood tables"],
        "tips": "Create a relaxed, breezy atmosphere. Layer blue and white tones with natural textures."
    },
    "contemporary": {
        "colors": ["neutral palette", "bold accent colors", "gray", "white", "black"],
        "materials": ["glass", "metal", "polished concrete", "lacquered surfaces"],
        "furniture": ["smooth curved sofas", "geometric coffee tables", "sculptural lighting"],
        "tips": "Keep spaces open and uncluttered. Mix textures for interest while maintaining clean lines."
    },
    "craftsman": {
        "colors": ["warm earth tones", "forest green", "burgundy", "amber", "cream"],
        "materials": ["quarter-sawn oak", "art glass", "natural stone", "copper"],
        "furniture": ["built-in bookcases", "mission-style chairs", "wide-plank flooring"],
        "tips": "Celebrate handcraftsmanship. Use built-ins and expose natural wood grain throughout."
    },
    "eclectic": {
        "colors": ["vibrant mix", "jewel tones", "unexpected combinations"],
        "materials": ["mixed metals", "global textiles", "vintage finds", "modern art"],
        "furniture": ["mix of vintage and modern pieces", "global decor", "statement art"],
        "tips": "Boldly mix periods and styles. Maintain cohesion through color palette or shared element."
    },
    "farmhouse": {
        "colors": ["white", "cream", "sage green", "dusty blue", "warm wood tones"],
        "materials": ["shiplap", "reclaimed wood", "galvanized metal", "cotton", "linen"],
        "furniture": ["farmhouse tables", "apron-front sinks", "barn doors", "open shelving"],
        "tips": "Combine rustic charm with modern comfort. Use vintage-inspired elements with clean backgrounds."
    },
    "french-country": {
        "colors": ["soft yellows", "lavender", "light blue", "cream", "sage"],
        "materials": ["toile", "linen", "carved wood", "wrought iron", "natural stone"],
        "furniture": ["carved armoires", "upholstered bergère chairs", "rustic dining tables"],
        "tips": "Create warmth with weathered finishes and soft patterns. Mix elegant with rustic."
    },
    "industrial": {
        "colors": ["gray", "black", "rust", "brown", "metallic"],
        "materials": ["exposed brick", "steel beams", "concrete", "raw wood", "metal pipe"],
        "furniture": ["factory-style lighting", "metal bar stools", "reclaimed wood tables"],
        "tips": "Celebrate raw materials and architectural elements. Leave ductwork and pipes exposed."
    },
    "mediterranean": {
        "colors": ["terracotta", "cobalt blue", "warm yellow", "olive green", "cream"],
        "materials": ["terracotta tile", "wrought iron", "mosaic", "stucco", "natural stone"],
        "furniture": ["heavy wood pieces", "arched doorways", "wrought iron chandeliers"],
        "tips": "Use warm earth tones with colorful accents. Incorporate arches and textured walls."
    },
    "mid-century-modern": {
        "colors": ["mustard yellow", "teal", "olive green", "burnt orange", "walnut"],
        "materials": ["walnut wood", "molded plywood", "fiberglass", "brass", "terrazzo"],
        "furniture": ["Eames-style chairs", "teak credenzas", "hairpin leg tables", "sputnik chandeliers"],
        "tips": "Use organic shapes and clean lines. Mix wood tones with colorful upholstery."
    },
    "modern": {
        "colors": ["white", "black", "gray", "primary accent colors"],
        "materials": ["steel", "glass", "concrete", "engineered wood", "leather"],
        "furniture": ["minimal sofas", "platform beds", "modular shelving", "pendant lights"],
        "tips": "Less is more. Focus on function and form with minimal ornamentation."
    },
    "rustic": {
        "colors": ["warm browns", "deep reds", "forest green", "cream", "tan"],
        "materials": ["rough-hewn wood", "stone", "leather", "wool", "antler"],
        "furniture": ["log beds", "stone fireplaces", "leather chairs", "wooden beams"],
        "tips": "Embrace natural imperfections. Use heavy wood and stone with warm textiles."
    },
    "scandinavian": {
        "colors": ["white", "light gray", "pale blue", "blush pink", "natural wood"],
        "materials": ["light wood (birch, pine)", "wool", "sheepskin", "linen", "ceramic"],
        "furniture": ["simple wood chairs", "modular sofas", "pendant lights", "open shelving"],
        "tips": "Maximize natural light. Keep things simple, functional, and cozy (hygge)."
    },
    "shabby-chic-style": {
        "colors": ["white", "pastel pink", "soft blue", "sage green", "cream"],
        "materials": ["distressed paint", "floral fabrics", "lace", "vintage finds"],
        "furniture": ["distressed dressers", "crystal chandeliers", "slipcovered sofas"],
        "tips": "Create charming, lived-in elegance. Layer pastels with vintage, distressed pieces."
    },
    "southwestern": {
        "colors": ["turquoise", "terracotta", "sand", "sunset orange", "cactus green"],
        "materials": ["adobe", "terracotta", "Navajo textiles", "tooled leather", "copper"],
        "furniture": ["carved wood pieces", "leather chairs", "Pueblo-style elements"],
        "tips": "Draw from desert landscapes. Use warm earth tones with bold geometric patterns."
    },
    "traditional": {
        "colors": ["rich burgundy", "navy", "forest green", "gold", "cream"],
        "materials": ["mahogany", "silk", "velvet", "marble", "crystal"],
        "furniture": ["wingback chairs", "roll-arm sofas", "pedestal tables", "ornate mirrors"],
        "tips": "Create timeless elegance with symmetry and classic patterns like damask and stripes."
    },
    "transitional": {
        "colors": ["neutral palette", "taupe", "soft blue", "gray", "cream"],
        "materials": ["mixed metals", "lacquered wood", "suede", "glass", "stone"],
        "furniture": ["clean-lined sofas", "simple tables with curves", "mix traditional and modern"],
        "tips": "Bridge traditional and contemporary. Use comfortable proportions with simplified details."
    },
    "tropical": {
        "colors": ["vibrant green", "ocean blue", "coral", "sunny yellow", "white"],
        "materials": ["bamboo", "rattan", "palm leaves", "teak", "woven fibers"],
        "furniture": ["rattan chairs", "teak outdoor furniture", "canopy beds"],
        "tips": "Bring the outdoors in. Use lush greens, bold prints, and natural materials."
    },
    "victorian": {
        "colors": ["deep ruby", "emerald green", "royal purple", "gold", "cream"],
        "materials": ["dark wood", "velvet", "brocade", "stained glass", "marble"],
        "furniture": ["tufted sofas", "carved wood beds", "ornate mirrors", "crystal chandeliers"],
        "tips": "Layer rich textures and patterns. More is more with ornate details and deep colors."
    }
}


def generate_design_suggestions(style: str, user_prompt: str = "") -> List[Dict]:
    """Generate design suggestions based on detected style and user input."""
    style_info = DESIGN_KNOWLEDGE.get(style, DESIGN_KNOWLEDGE["modern"])

    suggestions = []

    # Color Palette
    suggestions.append({
        "category": "Color Palette",
        "suggestion": f"Recommended colors: {', '.join(style_info['colors'])}",
        "style": style
    })

    # Materials
    suggestions.append({
        "category": "Materials & Textures",
        "suggestion": f"Key materials: {', '.join(style_info['materials'])}",
        "style": style
    })

    # Furniture
    suggestions.append({
        "category": "Furniture & Decor",
        "suggestion": f"Recommended pieces: {', '.join(style_info['furniture'])}",
        "style": style
    })

    # Pro Tips
    suggestions.append({
        "category": "Design Tips",
        "suggestion": style_info["tips"],
        "style": style
    })

    # Context-aware suggestion based on user prompt
    if user_prompt:
        prompt_lower = user_prompt.lower()
        if any(word in prompt_lower for word in ["bedroom", "bed", "sleep"]):
            suggestions.append({
                "category": "Room-Specific",
                "suggestion": f"For a {style} bedroom: Focus on comfortable textiles, ambient lighting, and a statement headboard using {style_info['materials'][0]}.",
                "style": style
            })
        elif any(word in prompt_lower for word in ["kitchen", "cook", "dining"]):
            suggestions.append({
                "category": "Room-Specific",
                "suggestion": f"For a {style} kitchen: Consider {style_info['materials'][1]} countertops, {style_info['colors'][0]} cabinetry, and statement pendant lighting.",
                "style": style
            })
        elif any(word in prompt_lower for word in ["living", "lounge", "sitting"]):
            suggestions.append({
                "category": "Room-Specific",
                "suggestion": f"For a {style} living room: Start with {style_info['furniture'][0]}, layer with {style_info['materials'][2]} textiles, and use {style_info['colors'][1]} as accent.",
                "style": style
            })
        elif any(word in prompt_lower for word in ["bathroom", "bath", "shower"]):
            suggestions.append({
                "category": "Room-Specific",
                "suggestion": f"For a {style} bathroom: Feature {style_info['materials'][3] if len(style_info['materials']) > 3 else style_info['materials'][0]} elements with {style_info['colors'][2]} accents.",
                "style": style
            })

    return suggestions


def get_style_description(style: str) -> str:
    """Get a brief description for a design style."""
    descriptions = {
        "asian": "Inspired by East Asian design principles—emphasizing harmony, natural materials, and minimalist elegance.",
        "coastal": "Beach-inspired living with airy, light-filled spaces featuring ocean hues and natural textures.",
        "contemporary": "Current and evolving, featuring clean lines, neutral palettes, and emphasis on space and light.",
        "craftsman": "Celebrating handcraftsmanship with rich wood tones, built-ins, and Arts & Crafts heritage.",
        "eclectic": "A bold, curated mix of styles and eras creating a unique, personal aesthetic.",
        "farmhouse": "Modern rustic charm combining vintage elements with clean, fresh backgrounds.",
        "french-country": "Warm, elegant, and rustic—merging refined French style with countryside comfort.",
        "industrial": "Raw, urban edge featuring exposed materials, metal accents, and warehouse-inspired elements.",
        "mediterranean": "Sun-drenched warmth with terracotta, mosaic tiles, and Old World European charm.",
        "mid-century-modern": "Retro-inspired design from the 1950s-60s featuring organic forms and bold colors.",
        "modern": "Clean, streamlined design focused on function, minimal ornamentation, and open space.",
        "rustic": "Natural, rugged beauty celebrating wood, stone, and other organic materials.",
        "scandinavian": "Light, airy, and functional with a focus on simplicity and hygge comfort.",
        "shabby-chic-style": "Romantic, vintage-inspired elegance with distressed finishes and pastel colors.",
        "southwestern": "Desert-inspired warmth with Native American and Spanish Colonial influences.",
        "traditional": "Timeless elegance with classic furnishings, rich colors, and symmetrical arrangements.",
        "transitional": "A sophisticated blend of traditional warmth and contemporary simplicity.",
        "tropical": "Lush, resort-inspired design bringing outdoor paradise indoors with bold botanicals.",
        "victorian": "Ornate, dramatic, and richly layered design from the Victorian era."
    }
    return descriptions.get(style, "A beautiful design style for your interior.")
