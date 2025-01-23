import os
from dotenv import load_dotenv
import base64
from flask import Flask, request, jsonify
import openai
import ast

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
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
                result += ast.literal_eval(text)
            except Exception as e:
                return jsonify({"error": f"Error processing image {image_file.filename}: {str(e)}"}), 500

        # Save the merged text to a file
        output_file_path = "output_texts.txt"
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(result.join(", "))

        return jsonify({
            "result": result,
            "file_saved": output_file_path
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/check', methods=['POST'])
def check():
    try:
        all_kumandi = ['E107', 'E133', 'E154', 'E495', 'E920', 'E100', 'E101', 'E102', 'E104', 'E110', 'E122', 'E123', 'E124', 'E127', 'E128', 'E131', 'E132', 'E140', 'E141', 'E142', 'E151', 'E153', 'E160c', 'E160f', 'E161c', 'E161f', 'E163', 'E160a', 'E160d', 'E161a', 'E161d', 'E161g', 'E170', 'E160e', 'E161b', 'E161e', 'E162', 'E180', 'E213', 'E214', 'E215', 'E216', 'E217', 'E218', 'E219', 'E227', 'E230', 'E231', 'E232', 'E233', 'E270', 'E282', 'E304', 'E306', 'E308', 'E309', 'E302', 'E307', 'E311', 'E312', 'E320', 'E321', 'E325', 'E326', 'E327', 'E333', 'E334', 'E335', 'E336', 'E337', 'E341', 'E322', 'E422', 'E470', 'E471', 'E472', 'E473', 'E474', 'E475', 'E476', 'E477', 'E478', 'E481', 'E482', 'E483', 'E491', 'E492', 'E493', 'E494', 'E542', 'E544', 'E556', 'E620', 'E621', 'E622', 'E623', 'E627', 'E631', 'E635', 'E904']

        all_haram = ['E120', 'E103', 'E121', 'E125', 'E129', 'E182', 'E240', 'E313', 'E314', 'E324', 'E388', 'E389', 'E390', 'E391', 'E399h', 'E425', 'E479', 'E480', 'E484', 'E485', 'E486', 'E487', 'E488', 'E489', 'E496', 'E505', 'E537', 'E538', 'E557', 'E626', 'E700', 'E701', 'E710', 'E711', 'E712', 'E713', 'E714', 'E715', 'E716', 'E717', 'E906', 'E918', 'E919', 'E922', 'E923', 'E929', 'E940', 'E946', 'E904', 'E1000', 'E1001', 'E1510']

        # Retrieve the JSON payload
        data = request.json
        if not data or 'checklist' not in data:
            return jsonify({"error": "No checklist provided"}), 400
        
        # Parse the checklist
        to_check = data['checklist']
    
        is_kumandi = False  
        is_haram = False 
        response = ""
        for element in to_check: 
            if element in all_kumandi: 
                response+=f"\n{element} - күмәнді" 
                is_kumandi = True 
            elif element in all_haram: 
                response+=f"\n{element} - харам" 
                is_haram = True 
        
        if is_haram: 
            response+="\nТауар адал емес" 
        elif is_kumandi: 
            response+="\nТауардың құрамында күмәнді қоспалар бар" 
        else: 
            response+="\nТауардың құрамы таза"

        print(response)
        return jsonify({
            "result": response
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
