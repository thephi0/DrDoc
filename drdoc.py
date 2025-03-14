from flask import Flask, request, render_template
import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not set in environment variables!"

    result = ""  # Initialize result outside the try block

    if request.method == 'POST':
        input_type = request.form.get('input_type')  # "text", "image", or "pdf"
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            if input_type == 'text':
                text_input = request.form['text_input']
                prompt = f"""You are a medical AI assistant analyzing the following text report: {text_input}.

                Provide the following in your analysis:

                1. <b>Concise Summary:</b> A brief overview of the image's key findings (2-3 sentences).
2. <b>Facts:</b> A list of the anatomical structures shown in the image and any abnormalities detected.
3. <b>What to Do:</b> Based on the image, provide basic suggestions for next steps.
4. <b>Future Considerations:</b> What are the potential long-term implications or things to monitor.
5. <b>Diet Recommendation:</b> Based on the findings, provide general dietary advice.

                Always include a disclaimer: This analysis is solely for testing and demonstration, and it should not be used for medical advice.
                """
                response = model.generate_content(prompt)
                result = response.text

            elif input_type == 'image':
                image_file = request.files['image_input']
                if image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode("utf-8")
                    mime_type = image_file.mimetype
                    prompt = prompt = f"""You are a medical AI assistant analyzing this medical image. Describe what you see, and point out any specific anomalies.

Please provide your analysis in the following format:

1. <b>Concise Summary:</b> A brief overview of the image's key findings (2-3 sentences).
2. <b>Facts:</b> A list of the anatomical structures shown in the image and any abnormalities detected.
3. <b>What to Do:</b> Based on the image, provide basic suggestions for next steps.
4. <b>Future Considerations:</b> What are the potential long-term implications or things to monitor.
5. <b>Diet Recommendation:</b> Based on the findings, provide general dietary advice.

Always include a disclaimer: This analysis is solely for testing and demonstration, and it should not be used for medical advice.
"""
                    response = model.generate_content([prompt, {"mime_type": mime_type, "data": encoded_image}])
                    result = response.text.replace('\n', '<br>')
                else:
                    result = "No image uploaded."

            elif input_type == 'pdf':
                pdf_file = request.files['pdf_input']
                if pdf_file:
                    # Extract text from PDF
                    pdf_text = ""
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            pdf_text += page.extract_text()
                    except Exception as e:
                        result = f"Error reading PDF: {e}"
                    else:
                        prompt = f"""You are a medical AI assistant analyzing the following text extracted from a PDF medical report: {pdf_text}.

                        Provide the following in your analysis:

                       1. <b>Concise Summary:</b> A brief overview of the image's key findings (2-3 sentences).
2. <b>Facts:</b> A list of the anatomical structures shown in the image and any abnormalities detected.
3. <b>What to Do:</b> Based on the image, provide basic suggestions for next steps.
4. <b>Future Considerations:</b> What are the potential long-term implications or things to monitor.
5. <b>Diet Recommendation:</b> Based on the findings, provide general dietary advice.

                        Always include a disclaimer: This analysis is solely for testing and demonstration, and it should not be used for medical advice.
                        """
                        response = model.generate_content(prompt)
                        result = response.text
                else:
                    result = "No PDF file uploaded."

            else:
                result = "Invalid input type."

        except Exception as e:
            result = f"Error: {e}"

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)