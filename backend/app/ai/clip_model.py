import logging
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)


class CLIPEmbedder:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading CLIP model on {self.device}")
        
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
    
    def encode_image(self, image_path: str) -> np.ndarray:
        """Generate embedding for a single image"""
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # Normalize embedding
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Image encoding failed: {e}")
            return np.zeros(512)  # Return zero vector on failure
    
    def encode_images_batch(self, image_paths: List[str], batch_size: int = 8) -> np.ndarray:
        """Generate embeddings for multiple images in batches"""
        embeddings = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_embeddings = [self.encode_image(path) for path in batch_paths]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for text query"""
        try:
            inputs = self.processor(text=[text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            return np.zeros(512)
    
    def compute_similarity(self, image_embedding: np.ndarray, text_embedding: np.ndarray) -> float:
        """Compute cosine similarity between image and text embeddings"""
        return float(np.dot(image_embedding, text_embedding))
