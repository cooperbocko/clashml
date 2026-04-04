from PIL import Image

from roboflow import Roboflow

class DetectGold:
    def __init__(self, model_id: str, env_path: str):
        self.roboflow = Roboflow(model_id, env_path)
        
    def predict(self, image: Image) -> tuple[bool, list[list]]:
        width, height = image.size
        image = Roboflow.preprocess_image(
            image,
            auto_orient=True,
            resize=True,
            width=640,
            height=640,
            grayscale=False,
            auto_adjust_contrast=True
            )
        pwidth, pheight = image.size
        
        wratio = width / pwidth
        hratio = height / pheight
        
        points = []
        
        results =  self.roboflow.predict(image)
        if results == None:
            return (False, points)
        if len(results) > 0:
            for prediction in results:
                x = prediction['x']
                y = prediction['y']
                width = prediction['width']
                height = prediction['height']
                    
                x = int((x + width/2) * wratio)
                y = int((y + height/2) * hratio)
                points.append([x,y])
            return (True, points)
        return (False, points)