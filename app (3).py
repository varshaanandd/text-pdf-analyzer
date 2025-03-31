import os
import gradio as gr
import google.generativeai as genai
import chardet  # Auto-detect file encoding

# ✅ Load API Key securely from Hugging Face Secrets
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("⚠ Error: Google API Key is missing. Set it in Hugging Face Secrets.")

# ✅ Configure Google Generative AI (Gemini)
genai.configure(api_key=GOOGLE_API_KEY)

# ✅ Load the Gemini Model
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# 🔹 Function to read a file with auto-detected encoding
def read_file_with_encoding(file_path):
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()

        # Detect file encoding
        encoding = chardet.detect(raw_data)["encoding"]
        if encoding is None:
            encoding = "utf-8"  # Default to UTF-8 if detection fails

        # Read file with detected encoding
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"⚠ Error reading file: {str(e)}"

# 🔹 Function to analyze text or file content
def analyze_input(text, file):
    try:
        if file is not None:
            text = read_file_with_encoding(file)  # ✅ Auto-detect encoding
        elif not text.strip():
            return "⚠ Error: Please enter text or upload a file.", ""

        text = text[:2000]  # Limit input text size
        prompt = f"Analyze and summarize this document:\n\n{text}"
        response = model.generate_content([prompt], stream=True)  # ✅ Fix applied

        # Collect streamed response
        result = "".join([chunk.text for chunk in response])
        word_count = len(text.split())

        return result, f"📊 Word Count: {word_count}"
    except Exception as e:
        return f"⚠ Error: {str(e)}", ""

# 🔹 Function to clear inputs and outputs
def clear_inputs():
    return "", None, "", "", None  

# 🔹 Function to generate a downloadable text file
def generate_downloadable_file(text):
    if text.strip():
        file_path = "analysis_result.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        return file_path
    else:
        return None  

# ✅ Create Gradio UI
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("""
    # 📄 *AI-Powered Text & File Analyzer*
    🚀 Upload a .txt file or enter text manually to get an AI-generated analysis and summary.
    """)

    with gr.Row():
        text_input = gr.Textbox(label="✍ Enter Text", placeholder="Type or paste your text here...", lines=6)
        file_input = gr.File(label="📂 Upload Text File (.txt)", type="filepath")  

    output_text = gr.Textbox(label="📝 Analysis Result", lines=10, interactive=False)
    word_count_display = gr.Textbox(label="📊 Word Count", interactive=False)

    with gr.Row():
        analyze_button = gr.Button("🔍 Analyze", variant="primary")
        clear_button = gr.Button("🗑 Clear", variant="secondary")

    with gr.Column():
        gr.Markdown("### 📥 Download Analysis Result")
        with gr.Row():
            download_button = gr.Button("⬇ Download Result", variant="success", size="sm")
            download_file = gr.File(label="📄 Click to Download", interactive=False)

    # ✅ Button functionalities
    analyze_button.click(analyze_input, inputs=[text_input, file_input], outputs=[output_text, word_count_display])
    clear_button.click(clear_inputs, inputs=[], outputs=[text_input, file_input, output_text, word_count_display, download_file])
    download_button.click(generate_downloadable_file, inputs=output_text, outputs=download_file)

# ✅ Launch the Gradio app
demo.launch()
