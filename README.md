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

To send photos use `/process-images`. 

```
 curl -X POST http://127.0.0.1:5000/process-images -H "Content-Type: multipart/form-data" -F "images=@image3.jpg" -F "images=@other-image-path"
```

It will return result in format 

```json
{
    "result": ["list","of","results"],
    "file_saved": output_file_path
}
```

Then, all dobavki are checked by another route `/check`

```
curl -X POST http://127.0.0.1:5000/check \
-H "Content-Type: application/json" \
--data-binary @- <<EOF
{
  "checklist": ["вода", "сок манго", "сахар", "лимонная кислота", "аскорбиновая кислота", "сукралоза", "пищевые красители", "E102", "E110"]
}
EOF

```
or 

Save result in some payload.json file and pass it
```
curl -X POST http://127.0.0.1:5000/check -H "Content-Type: application/json" -d @payload.json

```

and get result like:

```json
{
    "response": "E102 - күмәнді
                E110 - күмәнді
                Тауардың құрамында күмәнді қоспалар бар"
}
```