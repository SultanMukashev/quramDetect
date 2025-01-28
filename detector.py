import ast
import base64
import datetime
import os
import re
import openai
from bson import ObjectId
from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
from pymongo import MongoClient

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_INITDB_DATABASE")
collection_name = os.getenv("MONGO_INITDB_COLLECTION")


client = MongoClient(mongo_uri)
db = client[str(db_name)]
collection = db[str(collection_name)]
app = Flask(__name__)

@app.route('/process-images', methods=['POST'])
def process_images():
    try:
        # Ensure files are sent in the request
        if 'images' not in request.files:
            return jsonify({"error": "No images provided"}), 400

        images = request.files.getlist('images')
        extracted_texts = []

        # Process each image with OpenAI GPT-4 Vision
        
        for image_file in images:
            try:
                # Convert image file to base64 string
                img_type = image_file.content_type  # e.g., 'image/jpeg'
                img_b64_str = base64.b64encode(image_file.read()).decode('utf-8')

                # Send the image to OpenAI for processing
                response = openai.chat.completions.create(
                    model="gpt-4o",  # Ensure this model supports image inputs
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": """Ты OCR-ассистент, твоя задача – извлекать состав продукта из текста на изображении. Неважно, на каком языке состав указан. Твоя цель:  
  
1. Извлечь все ингредиенты и добавки (например: "вода", "сок манго", "кислота", "сукралоза", "E102", "E110").  
2. Если видишь элементы вида "E100", "E121" и любые другие добавки с префиксом E, выделяй их отдельно как индивидуальные элементы.  
3. Всегда возвращай результат в строго формате Python-списка (list), например:   
   ["вода", "сок манго", "кислота", "сукралоза", "пищевые красители", "E102", "E110"] 
4. Никакой другой формы ответа, только список. Без лишнего текста, пояснений или форматов."""},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"}
                                }
                            ]
                        }
                    ],
                    temperature=0
                )

                # Extract response text from OpenAI API
                text = response.choices[0].message.content
                result = []
                result += ast.literal_eval(text)
            except Exception as e:
                return jsonify({"error": f"Error processing image {image_file.filename}: {str(e)}"}), 500

        # Save the merged text to a file
        output_file_path = "output_texts.txt"
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(", ".join(result))

        return jsonify({
            "result": result,
            "file_saved": output_file_path
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/check', methods=['POST'])
def check():
    try:
        all_kumandi = ["Глицерин", "Желатин", "Эфиры глицерина и смоляных кислот", "Жирных кислотсоли калия, кальция, натрия", 
    "Моно- и диглицериды жирных кислот", "Различные эфиры моно- и диглицеридов жирных кислот", "Эфиры глицерина, диацетилвинной и жирных кислот", 
    "Эфиры и жирных кислот", "глицериды", "Эфиры полиглицеридов и жирных кислот", "Полиглицерин, полирицинолеаты", "Пропан-1,2-диоловые эфиры жирных кислот", 
    "Эфиры лактилированных жирных кислот глицерина и пропиленгликоля", "Термически окисленное соевое и бобовое масло с моно- и диглицеридами жирных кислот", " Стеароил-2-лактилат натрия", 
    "Стеароил-2-лактилат кальция", "Стеарилтартрат", "Сорбитан моностеарат", "Сорбитан тристеарат", "Сорбитан монолаурат", "Сорбитан моноолеат", 
    "Сорбитан монопальмитат", "Костный фосфат", "Стеариновая кислота", "Стеарат магния", "Инозиновая кислота", "Инозинат натрия двузамещенный", 
    "Инозинат калия двузамещенный", "5-инозинат кальция", "5-рибонуклеотиды кальция", "5-рибонуклеотиды натрия двузамещенные", "Глицин и его натриевые соли", 
    "Шеллак", "L-цистеин", "Искусственные красители", "Искусственные ароматизаторы", "Бета-каротин", "Бутилоксианизол или бутилгидрокситолуол", 
    "Липолизированный молочный жир", "Сухие кисломолочные продукты", "Стеарат кальция", "Стеароил-лактилат кальция",'E107', 'E133', 'E154', 'E495', 'E920', 'E100', 'E101', 'E102', 'E104', 'E110', 'E122', 'E123', 'E124', 'E127', 'E128', 'E131', 'E132', 'E140', 'E141', 'E142', 'E151', 'E153', 'E160c', 'E160f', 'E161c', 'E161f', 'E163', 'E160a', 'E160d', 'E161a', 'E161d', 'E161g', 'E170', 'E160e', 'E161b', 'E161e', 'E162', 'E180', 'E213', 'E214', 'E215', 'E216', 'E217', 'E218', 'E219', 'E227', 'E230', 'E231', 'E232', 'E233', 'E270', 'E282', 'E304', 'E306', 'E308', 'E309', 'E302', 'E307', 'E311', 'E312', 'E320', 'E321', 'E325', 'E326', 'E327', 'E333', 'E334', 'E335', 'E336', 'E337', 'E341', 'E322', 'E422', 'E470', 'E471', 'E472', 'E473', 'E474', 'E475', 'E476', 'E477', 'E478', 'E481', 'E482', 'E483', 'E491', 'E492', 'E493', 'E494', 'E542', 'E544', 'E556', 'E620', 'E621', 'E622', 'E623', 'E627', 'E631', 'E635', 'E904']

        all_haram = ["Кошениль/карминовая кислота", "Тартрат кальция", "Экстракт Квиллайи", "Аденозин 5'-монофосфат", 
    "Алкоголь как растворитель для придания аромата", "Алкоголь в сухой форме в качестве ингредиента", 
    "Бекон", "Кусочки бекона", "Бальзамический уксус", "Пиво", "Ароматизатор пива", "Экстракт пивных дрожжей", 
    "Пивные дрожжи", 'E120', 'E103', 'E121', 'E125', 'E129', 'E182', 'E240', 'E313', 'E314', 'E324', 'E388', 'E389', 'E390', 'E391', 'E399h', 'E425', 'E479', 'E480', 'E484', 'E485', 'E486', 'E487', 'E488', 'E489', 'E496', 'E505', 'E537', 'E538', 'E557', 'E626', 'E700', 'E701', 'E710', 'E711', 'E712', 'E713', 'E714', 'E715', 'E716', 'E717', 'E906', 'E918', 'E919', 'E922', 'E923', 'E929', 'E940', 'E946', 'E904', 'E1000', 'E1001', 'E1510']
        # Threshold for fuzzysearch
        threshold=95

        # Retrieve the JSON payload
        data = request.json
        if not data or 'checklist' not in data:
            return jsonify({"error": "No checklist provided"}), 400
        
        # Parse the checklist
        to_check = data['checklist']
    
        is_kumandi = False  
        is_haram = False 
        response = ""
        result = []

        def matches(element, reference_list): 
            """Проверяет, есть ли элемент в списке с учетом вариаций написания.""" 
            element_lower = element.lower() 
            for ref in reference_list: 
                ref_lower = ref.lower() 
                # Точное совпадение 
                if ref_lower in element_lower or element_lower in ref_lower: 
                    return True 
                # Регулярное совпадение 
                if re.search(rf"\b{re.escape(ref_lower)}\b", element_lower): 
                    return True 
                # Нечеткое сравнение 
                if fuzz.partial_ratio(element_lower, ref_lower) >= threshold: 
                    return True 
            return False 
    
        for element in to_check: 
            if matches(element, all_kumandi): 
                result.append({"name": element, "result": "kymandy"})
                is_kumandi = True 
            elif matches(element, all_haram): 
                result.append({"name": element, "result": "haram"})
                is_haram = True 
            else:
                result.append({"name": element, "result": "taza"})
        
        # if is_haram: 
        #     response+="\nТауар адал емес" 
        # elif is_kumandi: 
        #     response+="\nТауардың құрамында күмәнді қоспалар бар" 
        # else: 
        #     response+="\nТауардың құрамы таза"

        print(response)
        return jsonify({
            "result": result
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

@app.route('/approve', methods=['POST'])
def approve():
    try:
        # Получаем данные из запроса
        data = request.json
        barcode = data.get('barcode')
        image = data.get('image')  # Ожидается base64 строка
        category = data.get('category')
        ingredients = data.get('ingredients')  # Состав продукта
        halal = data.get('halal')  # Халяльность состава (True/False)

        if not barcode or not image or not category or not ingredients or halal is None:
            return jsonify({"error": "Все поля обязательны"}), 400

        image_data = base64.b64decode(image)

        product = {
            "_id": barcode,
            "image": image_data,  
            "category": category,
            "ingredients": ingredients,
            "halal": halal,
            "created_at": datetime.datetime.utcnow()
        }

        collection.insert_one(product)

        return jsonify({"message": "Продукт успешно добавлен"}), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500


@app.route('/product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Получить продукт по ID."""
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({"error": f"Invalid product ID format: {product_id}"}), 400

        product = collection.find_one({"_id": ObjectId(product_id)})

        if not product:
            return jsonify({"error": f"Product with ID {product_id} not found"}), 404

        product['_id'] = str(product['_id'])
        return jsonify(product), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/products', methods=['GET'])
def get_all_products():
    """Получить все продукты."""
    try:
        products = list(collection.find())

        for product in products:
            product['_id'] = str(product['_id'])

        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
