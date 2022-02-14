FROM python:3.9
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y python3-distutils
COPY . /app
RUN pip3 install --upgrade pip
#RUN pip install torch-model-archiver
RUN pip install opencv-python
RUN pip install -r /app/requirements.txt
RUN python3 -c "import cv2"
RUN pip install -r /app/yolov5/requirements.txt
EXPOSE 8080 8081
ENV PYTHONPATH "${PYTHONPATH}:/app/yolov5/"
#RUN python /app/yolov5/models/export.py --weights /app/yolov5/weights_ASR/weights_s_640.pt --img 640 --batch 1
#RUN torch-model-archiver --model-name dobble \
#--version 0.1 --serialized-file /weights_s_640.pt \
#--handler /yolov5/torchserve_handler.py \
#--extra-files /yolov5/index_to_name.json,/yolov5/torchserve_handler.py
#RUN mv my_model_name.mar model-store/my_model_name.mar
#CMD [ "torchserve", "--start", "--model-store", "model_store", "--models", "my_model_name=my_model_name.mar" ]
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]