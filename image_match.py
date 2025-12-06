import os
from typing import Tuple

import torch
import clip
from PIL import Image, ImageOps
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ImageMatch:
    
    def __init__(self, db_path: str, images_path: str, resize: Tuple[int, int]):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.db_path = db_path
        self.images_path = images_path
        self.resize = resize
        self.db = None
        
        if os.path.exists(db_path):
            self.load_db()
        else:
            self.create_db()
            self.load_db()
            
    def match(self, image: str | Image.Image):
        if self.db is None:
            print('No card db!')
            return
        
        query_emb = self.get_embedding(image)

        scores = {card: cosine_similarity([query_emb], [emb])[0][0] for card, emb in self.db.items()}
        best = max(scores, key=scores.get)
        return best
        
    def load_db(self):
        path = self.db_path
        data = np.load(path)
        self.db = {name: data[name] for name in data.files}
        print(f"Loaded database with {len(self.db)} objects.")
        
    def create_db(self):
        db = {}
        for name in os.listdir(self.images_path):
            path = os.path.join(self.images_path, name)
            if not os.path.isdir(path):
                continue
            
            embeddings = []
            for img_file in os.listdir(path):
                if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
                    img_path = os.path.join(path, img_file)
                    emb = self.get_embedding(img_path)
                    embeddings.append(emb)
                    
            db[name] = np.mean(embeddings, axis = 0)
            
        print(f"Created database with {len(db)} objects.")
        np.savez(self.db_path, **db)
        
    def get_embedding(self, image: str | Image.Image):
        if isinstance(image, str):
            image = Image.open(image)
            
        image = image.resize(self.resize)
        img_color = image.convert("RGB")
        img_gray = ImageOps.grayscale(img_color).convert("RGB")
        
        imgs = [img_color, img_gray]
        embs = []
        for im in imgs:
            inp = self.preprocess(im).unsqueeze(0).to(self.device)
            with torch.no_grad():
                emb = self.model.encode_image(inp)
                emb /= emb.norm(dim=-1, keepdim=True)
            embs.append(emb.cpu().numpy()[0])
            
        return np.mean(embs, axis=0)