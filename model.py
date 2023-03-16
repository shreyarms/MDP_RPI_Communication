import torch
import time
import config 

class model:
    def __init__(self,weights_path) -> None:
        self.model = torch.hub.load(".\yolov7", 'custom', weights_path, source = "local", force_reload = False, trust_repo=True)
    
    def get_results(self,images):
        results = self.model(images)
        result_table = results.pandas().xyxy[0]
        
        result_array = []

        xmin_bbox = -1
        ymin_bbox = -1
        xmax_bbox = -1
        ymax_bbox = -1
        name = -1
        
        for _, row in result_table.iterrows():
            if row["confidence"] >= 0.5:
                xmin_bbox = int(row["xmin"])
                ymin_bbox = int(row["ymin"])
                xmax_bbox = int(row["xmax"])
                ymax_bbox = int(row["ymax"])
                relative_area = abs(ymax_bbox-ymin_bbox)*abs(xmax_bbox-xmin_bbox)/(config.image_height*config.image_width)
                name = row["name"]
                confidence = row["confidence"]
                bbox = [[xmin_bbox, ymin_bbox, xmax_bbox, ymax_bbox],name,confidence,relative_area]
                result_array.append(bbox)
                result_array = sorted(result_array, key=lambda x: x[2], reverse=True)
                print(result_array)
        
        # result_array = sorted(result_array, key=lambda x: (x[2]*x[3]), reverse=True)
        return result_array
