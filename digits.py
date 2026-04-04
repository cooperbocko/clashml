from PIL import Image

from roboflow import Roboflow

class DetectDigits:
    def __init__(self, model_id: str, env_path: str):
        self.roboflow = Roboflow(model_id, env_path)
        
    def predict(self, image: Image) -> str:
        image = Roboflow.preprocess_image(
            image,
            auto_orient=True,
            resize=True,
            width=640,
            height=640,
            grayscale=True,
            auto_adjust_contrast=True
        )
        digits = ''

        results = self.roboflow.predict(image)
        if results != None:
            sorted_predictions = sorted(results, key=lambda r: r['x'])
            for prediction in sorted_predictions:
                digits = digits + prediction['class']
        return digits