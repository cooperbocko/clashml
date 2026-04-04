from PIL import Image

from roboflow import Roboflow

class DetectLevel:
    def __init__(self, model_id: str, env_path: str):
        self.roboflow = Roboflow(model_id, env_path)
        
    def predict(self, image: Image) -> tuple[bool, list[list]]:
        image = Roboflow.preprocess_image(image)
        return self.roboflow.predict(image)