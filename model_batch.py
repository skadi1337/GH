from transformers import SegformerForSemanticSegmentation
import torch
from PIL import Image
from torchvision import transforms
from torch import nn
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import sys
import cv2


if not torch.cuda.is_available():
   print("warning: no cuda driver")
   sys.stdout.flush()


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

xMin = int(sys.argv[1])
yMin = int(sys.argv[2])
xMax = int(sys.argv[3])
yMax = int(sys.argv[4])
z = int(sys.argv[5])
pattern = os.path.basename(sys.argv[6])
model_f = sys.argv[7]



model_file = os.path.join(os.getcwd(), 'models', model_f)
source_folder_id = os.path.join(os.getcwd(), 'downloads')
destination_folder_path = os.path.join(os.getcwd(), 'outputs')


model_checkpoint = "nvidia/segformer-b0-finetuned-ade-512-512"
id2label = {0: "background", 1: "greenhouse"}
label2id = {label: id for id, label in id2label.items()}
num_labels = len(id2label)
model = SegformerForSemanticSegmentation.from_pretrained(
    model_checkpoint,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True
)


model.to(device)


if torch.cuda.is_available():
    model.load_state_dict(torch.load(model_file))
else:
   model.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))

model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
])

batch_size = 10  # Set the desired batch size
string_len = 60 # to allocate

input_tensors = []
file_paths = [[(' ' * string_len) for _ in range(4)] for _ in range(batch_size)]
out_paths  = [[(' ' * string_len) for _ in range(4)] for _ in range(batch_size)]

for yi in range(int(yMin), int(yMax) - 1, -2):
            for xi in range(int(xMin), int(xMax) + 1, 2):
                

                st = time.time()
                input_file = pattern.replace('{x}', str(xi)).replace('{y}', str(yi)).replace('{z}', str(z)) + '.png'
                input_file2 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-1)).replace('{z}', str(z)) + '.png'
                input_file3 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-1)).replace('{z}', str(z)) + '.png'
                input_file4 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi)).replace('{z}', str(z)) + '.png'

                et = time.time()
                sys.stderr.write('Time replace pattern: ')
                sys.stderr.write(str(et - st) + '\n')
                sys.stderr.flush()

                st = time.time()
                input_files = [input_file, input_file2, input_file3, input_file4]

                output_files = []
                for f in input_files:
                    output_files.append(model_f + "_" + f[:-3] + "txt")


                j = len(input_tensors)

                for i in range(4):
                    file_paths[j][i] = os.path.join(source_folder_id, input_files[i])
                
                    
                for i in range(4):
                    out_paths[j][i] = os.path.join(destination_folder_path, output_files[i])

                et = time.time()

                sys.stderr.write('Time load arrays: ')
                sys.stderr.write(str(et - st) + '\n')
                sys.stderr.flush()
                
                st = time.time()
                if (os.path.exists(out_paths[j][0]) and os.path.exists(out_paths[j][1]) and os.path.exists(out_paths[j][2]) and os.path.exists(out_paths[j][3])):
                    print(out_paths[j][0])
                    sys.stdout.flush()
                  
                    print(out_paths[j][1])
                    sys.stdout.flush()

                    print(out_paths[j][2])
                    sys.stdout.flush()

                    print(out_paths[j][3])
                    sys.stdout.flush()


                    continue
                
                et = time.time()
                sys.stderr.write('Time check if exists: ')
                sys.stderr.write(str(et - st) + '\n')
                sys.stderr.flush()

                st = time.time()

                for f in file_paths[j]:
                    start_time = time.time()
                    while not os.path.exists(f):
                      if time.time() - start_time >= 120:
                        exit(-120)
                      time.sleep(1)
                
                et = time.time()
                sys.stderr.write('Time w8 files: ')
                sys.stderr.write(str(et - st) + '\n')
                sys.stderr.flush()
                
                
                st = time.time()
                
                image1 = Image.open(file_paths[j][0])
                image2 = Image.open(file_paths[j][1])
                image3 = Image.open(file_paths[j][2])
                image4 = Image.open(file_paths[j][3])

                result_image = Image.new("RGB", (512, 512))

                result_image.paste(image1, (0, 0))
                result_image.paste(image2, (0, 256))
                result_image.paste(image3, (256, 256))
                result_image.paste(image4, (256, 0))

                input_tensor = transform(result_image)
                input_tensors.append(input_tensor)

                et = time.time()

                sys.stderr.write('Time to load: ')
                sys.stderr.write(str(et - st) + '\n')
                sys.stderr.flush()


                if len(input_tensors) < batch_size:
                   continue
                   
                
                st = time.time()

                input_batch = torch.stack(input_tensors, dim=0).to(device)

                output = model(pixel_values=input_batch)

                logits = output.logits.cpu()

                upsampled_logits = nn.functional.interpolate(logits,
                    size=result_image.size[::-1], # (height, width)
                    mode='bilinear',
                    align_corners=False)

                def ade_palette():
                  return [[0, 0, 0], [255, 255, 255], [145, 145, 145]]
                

                segmentation_maps = upsampled_logits.argmax(dim=1)
                
                et = time.time()

                sys.stderr.write('Time to process: ')
                sys.stderr.write(str(et - st))
                sys.stderr.flush()


                st = time.time()
                for l in range(j):

                    # Second, apply argmax on the class dimension
                    seg = segmentation_maps[l]
                    color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8) # height, width, 3

                    palette = np.array(ade_palette())
                    for label, color in enumerate(palette):
                        color_seg[seg == label, :] = color


                    gray_image = cv2.cvtColor(color_seg, cv2.COLOR_BGR2GRAY)
                    _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)

                    image1 = binary_image[256:, :256]
                    image2 = binary_image[:256, :256]
                    image3 = binary_image[:256, 256:]
                    image4 = binary_image[256:, 256:]

                    images = [image2, image1, image4, image3]

                    for i in range(4):
                        contours, _ = cv2.findContours(images[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        smoothed_contours = contours

                        # for contour in contours:
                        #     # Approximate the contour with a smoother curve
                        #     epsilon = 0.01 * cv2.arcLength(contour, True)
                        #     approx = cv2.approxPolyDP(contour, epsilon, True)

                        #     # Check if the contour is closed
                        #     is_convex = cv2.isContourConvex(approx)

                        #     if is_convex:
                        #       smoothed_contours.append(approx)

                        #sys.stderr.write(str(smoothed_contours))
                        #sys.stdout.flush()


                        with open(out_paths[l][i], 'w') as file:
                            for contour in smoothed_contours:
                                for element in contour:
                                    line = ' '.join(f'{point[0]},{point[1]},' for point in element)
                                    file.write(line)
                                file.write(";")
                            file.close()



                        print(out_paths[l][i])
                        sys.stdout.flush()

                input_tensors.clear()
                et = time.time()

                sys.stderr.write('Time to save: ')
                sys.stderr.write(str(et - st))
                sys.stderr.flush()

                

                

                    
