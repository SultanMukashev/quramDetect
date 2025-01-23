# quramDetect
Detection of product's components and checking if it is halal or not.

All files in `master` branch

### How to Start
```
pip install requirements.txt
```
```
python ./detector.py
```

Requests to detector.py made by:

```
 curl -X POST http://127.0.0.1:5000/process-images -H "Content-Type: multipart/form-data" -F "images=@image3.jpg" -F "images=@other-image-path"
```
