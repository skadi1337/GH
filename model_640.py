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


model_checkpoint = "nvidia/segformer-b5-finetuned-ade-640-640"
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


for yi in range(int(yMin), int(yMax) - 1, -5):
            for xi in range(int(xMin), int(xMax) + 1, 5):
                
                input_files = []
                for ji in range(5):
                    for ki in range(5):
                       input_file = pattern.replace('{x}', str(xi + ji)).replace('{y}', str(yi + ki)).replace('{z}', str(z)) + '.png'
                       input_files.append(input_file)
                # input_file = pattern.replace('{x}', str(xi)).replace('{y}', str(yi)).replace('{z}', str(z)) + '.png'
                # input_file2 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-1)).replace('{z}', str(z)) + '.png'
                # input_file3 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-1)).replace('{z}', str(z)) + '.png'
                # input_file4 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi)).replace('{z}', str(z)) + '.png'

                # = [input_file, input_file2, input_file3, input_file4]
                output_files = []

                for f in input_files:
                    output_files.append(model_f + "_" + f[:-3] + "txt")

                # output_file = model_f + "_" + input_file[:-3] + "txt"
                # output_file2 = model_f + "_" + input_file2[:-3] + "txt"
                # output_file3 = model_f + "_" + input_file3[:-3] + "txt"
                # output_file4 = model_f + "_" + input_file4[:-3] + "txt"

                file_paths = []
                
                for f in input_files:
                    file_paths.append(os.path.join(source_folder_id, f))
                


                # file_path = os.path.join(source_folder_id, input_file)
                    
                out_paths = []
                for f in output_files:
                    out_paths.append(os.path.join(destination_folder_path, f))

                # out_path = os.path.join(destination_folder_path, output_file)

                for f in file_paths:
                    start_time = time.time()
                    while not os.path.exists(f):
                      if time.time() - start_time >= 120:
                        exit(-120)
                      time.sleep(1)

                # start_time = time.time()
                # while not os.path.exists(file_path):
                #     if time.time() - start_time >= 120:
                #       exit(-120)
                #     time.sleep(1)

                all_exist = True
                for path in out_paths:
                    if not os.path.exists(path):
                        all_exist = False
                        break

                if all_exist:
                    for path in out_paths:
                        print(path)
                        sys.stdout.flush()
                    continue
                
                # if (os.path.exists(out_paths[0]) and os.path.exists(out_paths[1]) and os.path.exists(out_paths[2]) and os.path.exists(out_paths[3])):
                #     print(out_paths[0])
                #     sys.stdout.flush()
                  
                #     print(out_paths[1])
                #     sys.stdout.flush()

                #     print(out_paths[2])
                #     sys.stdout.flush()

                #     print(out_paths[3])
                #     sys.stdout.flush()


                #    continue

                binary_images = []

                for j in range(4):
                    result_image = Image.new("RGB", (640, 640))

                # 5 10 15 20 25
                # 4 9  14 19 24
                # 3 8  13 18 23
                # 2 7  12 17 22
                # 1 6  11 16 21
                    if j == 1:
                        result_image.paste(file_paths[0],  (0,   0  ))
                        result_image.paste(file_paths[1],  (0,   256))
                        result_image.paste(file_paths[2],  (0,   512))
                        result_image.paste(file_paths[5],  (256, 0  ))
                        result_image.paste(file_paths[6],  (256, 256))
                        result_image.paste(file_paths[7],  (256, 512))
                        result_image.paste(file_paths[10], (512, 0  ))
                        result_image.paste(file_paths[11], (512, 256))
                        result_image.paste(file_paths[12], (512, 512))
                    if j == 2:
                        result_image.paste(file_paths[2],  (0,   0  ))
                        result_image.paste(file_paths[3],  (0,   256))
                        result_image.paste(file_paths[4],  (0,   512))
                        result_image.paste(file_paths[7],  (256, 0  ))
                        result_image.paste(file_paths[8],  (256, 256))
                        result_image.paste(file_paths[9],  (256, 512))
                        result_image.paste(file_paths[12], (512, 0  ))
                        result_image.paste(file_paths[13], (512, 256))
                        result_image.paste(file_paths[14], (512, 512))
                    if j == 3:
                        result_image.paste(file_paths[10],  (0,   0  ))
                        result_image.paste(file_paths[11],  (0,   256))
                        result_image.paste(file_paths[12],  (0,   512))
                        result_image.paste(file_paths[15],  (256, 0  ))
                        result_image.paste(file_paths[16],  (256, 256))
                        result_image.paste(file_paths[17],  (256, 512))
                        result_image.paste(file_paths[20], (512, 0  ))
                        result_image.paste(file_paths[21], (512, 256))
                        result_image.paste(file_paths[22], (512, 512))
                    if j == 4:
                        result_image.paste(file_paths[12],  (0,   0  ))
                        result_image.paste(file_paths[13],  (0,   256))
                        result_image.paste(file_paths[14],  (0,   512))
                        result_image.paste(file_paths[17],  (256, 0  ))
                        result_image.paste(file_paths[18],  (256, 256))
                        result_image.paste(file_paths[19],  (256, 512))
                        result_image.paste(file_paths[22], (512, 0  ))
                        result_image.paste(file_paths[23], (512, 256))
                        result_image.paste(file_paths[24], (512, 512))




                    input_tensor = transform(result_image)
                    input_batch = input_tensor.unsqueeze(0).to(device)


                    #input_batch = input_batch.to(next(model.parameters()).device)

                    output = model(pixel_values=input_batch)

                    logits = output.logits.cpu()

                    upsampled_logits = nn.functional.interpolate(logits,
                        size=result_image.size[::-1], # (height, width)
                        mode='bilinear',
                        align_corners=False)

                    segmentation_map = output

                    def ade_palette():
                        return [[0, 0, 0], [255, 255, 255], [145, 145, 145]]

                    # Second, apply argmax on the class dimension
                    seg = upsampled_logits.argmax(dim=1)[0]
                    color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8) # height, width, 3


                    palette = np.array(ade_palette())
                    for label, color in enumerate(palette):
                        color_seg[seg == label, :] = color

                    #resized_image = cv2.resize(color_seg, (256, 256))
                    gray_image = cv2.cvtColor(color_seg, cv2.COLOR_BGR2GRAY)
                    _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)

                    binary_images.append(binary_image)



                # image1 = binary_image[256:, :256]
                # image2 = binary_image[:256, :256]
                # image3 = binary_image[:256, 256:]
                # image4 = binary_image[256:, 256:]


                #images = [image2, image1, image4, image3]

                for i in range(len(binary_images)):
                  contours, _ = cv2.findContours(binary_images[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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


                  with open(out_paths[i], 'w') as file:
                    for contour in smoothed_contours:
                      for element in contour:
                        line = ' '.join(f'{point[0]},{point[1]},' for point in element)
                        file.write(line)
                      file.write(";")
                    file.close()

                  # black_image = np.zeros((256, 256), dtype=np.uint8)
                  # cv2.drawContours(black_image, smoothed_contours, -1, (255, 255, 255), 2)

                  # cv2.imwrite(out_path + ".png", black_image)



                ###############################
                #       RETURN THIS LATER     #
                ##############################
                #   print(out_paths[i])
                #   sys.stdout.flush()



                  #color_seg_image = Image.fromarray(color_seg)
                  #color_seg_image.save(out_path + ".png")

                  # destination_file_path = os.path.join(destination_folder_path, file_name)
                  # color_seg_image = Image.fromarray(color_seg)
                  # color_seg_image.save(destination_file_path)
                

                

                    







# for file_name in os.listdir(source_folder_id):
#     file_path = os.path.join(source_folder_id, file_name)

#     if file_name.lower().endswith('.png'):
#       image = Image.open(file_path).convert("RGB")

#       input_tensor = transform(image)
#       input_batch = input_tensor.unsqueeze(0).to(device)


#       #input_batch = input_batch.to(next(model.parameters()).device)

#       output = model(pixel_values=input_batch)

#       logits = output.logits.cpu()

#       upsampled_logits = nn.functional.interpolate(logits,
#                 size=image.size[::-1], # (height, width)
#                 mode='bilinear',
#                 align_corners=False)

#       segmentation_map = output

#       def ade_palette():
#         return [[0, 0, 0], [255, 255, 255], [145, 145, 145]]

#       # Second, apply argmax on the class dimension
#       seg = upsampled_logits.argmax(dim=1)[0]
#       color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8) # height, width, 3
#       palette = np.array(ade_palette())
#       for label, color in enumerate(palette):
#         color_seg[seg == label, :] = color

#       destination_file_path = os.path.join(destination_folder_path, file_name)
#       color_seg_image = Image.fromarray(color_seg)
#       color_seg_image.save(destination_file_path)
      
#       print("done:" + file_name)