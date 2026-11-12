FROM python:3.12-slim
RUN pip install --no-cache-dir "wyoming==1.8.*" "sherpa-onnx==1.12.*" numpy
WORKDIR /app
COPY falafel_wyoming /app/falafel_wyoming
EXPOSE 10300
ENTRYPOINT ["python", "-m", "falafel_wyoming.server"]
CMD ["--model-dir", "/models/falafel", "--model-name", "falafel-0.6b-int8", "--threads", "8"]
