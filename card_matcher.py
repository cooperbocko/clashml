import os
import torch
import clip
from PIL import Image, ImageOps
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CardMatch:
    
    def __init__(self, model_dir="models", db_path="card_match_db.npz"):
        os.environ["TORCH_HOME"] = model_dir #TODO: check that is actually works?
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.db_path = db_path
        self.db = None
        
        if os.path.exists(db_path):
            self.load_db(db_path)
            print(f"Loaded database with {len(self.db)} cards.")
        else:
            print("No existing database found. Run create_card_db() first.")

    def load_db(self, db_path=None):
        path = db_path or self.db_path
        data = np.load(path)
        self.db = {name: data[name] for name in data.files}
        
    def get_card_embedding(self, image: str | Image.Image):
        if isinstance(image, str):
            image = Image.open(image)
            
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
    
    def create_card_db(self, cards_dir="images/cards"):
        db = {}
        for card_name in os.listdir(cards_dir):
            card_path = os.path.join(cards_dir, card_name)
            if not os.path.isdir(card_path):
                continue
            
            embeddings = []
            for img_file in os.listdir(card_path):
                if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
                    img_path = os.path.join(card_path, img_file)
                    emb = self.get_card_embedding(img_path)
                    embeddings.append(emb)
                    
            db[card_name] = np.mean(embeddings, axis = 0)
            
        print(f"loaded {len(db)} cards.")
        np.savez("card_match_db.npz", **db)
        
    def match(self, card_image: str | Image.Image):
        if self.db is None:
            print('No card db!')
            return
        
        query_emb = self.get_card_embedding(card_image)

        scores = {card: cosine_similarity([query_emb], [emb])[0][0] for card, emb in self.db.items()}
        best_card = max(scores, key=scores.get)

        print("\n--- Match Results ---")
        for card, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            print(f"{card:20s}: {score:.3f}")

        print(f"\n✅ Best match: {best_card}")
        return best_card
    