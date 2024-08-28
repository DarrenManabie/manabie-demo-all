import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-pro')

# Hardcoded question
HARDCODED_QUESTION = """
                    # この問題集に含まれる問題を、"Section番号, Section名, 問題セクション名, 大問番号, 大問問題文, 中問番号, 中問問題文, 小問番号, 小問問題文, 回答形式, 回答オプション(選択式の場合), 図" のCSVフォーマットで全問題抜け漏れなく忠実に書き出して
                    # 該当するデータがない場合は"null"を表記して
                    # 全ての数字・数式をLaTex codeで表記して。例：\sqrt{4}
                    # 問題文の中にカンマが含まれる場合は、"、"で出力して（", "で出力しないで）
                    # 問題に図が含まれる場合はそれを「図」の列にI-Yes、ない場合はI-Noと明記して
                    # アウトプット例に忠実に出力して
                    ## Section16, 平方根の意味と混合, Practice, STEP1, null, (1), 次の数の平方根を求めなさい。, ①, 4, FIB, null, I-No
                    ## Section16, 平方根の意味と混合, Practice, STEP1, null, (1), 次の数の平方根を求めなさい。, ②, 16, FIB, null, I-No
                    ## Section17, 平方根の大小, Practice, STEP2, 次の各組の数の大小を、不等号を使って表しなさい。，(1), \sqrt{7}、\sqrt{6}, FIB, null, I-No
                    #「回答形式」は「FIB, MCQ, MAQ」の3種類のみです。"FIB"は空欄補充形式、"MCQ"は単一回答の選択式（正答が1つのみ）、"MAQ"は複数回答の選択式（正答が2つ以上）です
                    #「回答オプション」は、FIBの問題には必ず"null"を表記して。MCQ or MAQの問題には、全ての選択肢の内容をカンマで区切って表記して。
                    """

def process_pdf(uploaded_file):
    # Save the uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Upload the file to Google's API
    sample_file = genai.upload_file(path="temp.pdf", display_name="Uploaded PDF")
    
    # Generate content using the model with the hardcoded question
    response = model.generate_content([sample_file, HARDCODED_QUESTION], stream=True)
    
    # Remove the temporary file
    os.remove("temp.pdf")
    
    return response

# Streamlit app
st.title("教科書からの問題抽出デモ (All)")

# Get user input (optional)
user_input = st.text_area("追加の情報を入力してください（オプション）:")

if st.button("Save"):
    st.session_state['saved_input'] = user_input
    st.success("Input saved successfully!")

# Retrieve saved input if available
saved_input = st.session_state.get('saved_input', '')

# Concatenate user input to the hardcoded question if provided
if user_input:
    HARDCODED_QUESTION += "\n" + user_input

# File uploader
uploaded_file = st.file_uploader("", type="pdf")

if uploaded_file is not None:
    if st.button("Execute Process"):
        with st.spinner("Processing..."):
            response = process_pdf(uploaded_file)
            
            # Create a placeholder for the streaming output
            output_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # Use st.code to standardize font
                    output_placeholder.code(full_response)
            
            st.write("処理が完了しました。")
else:
    st.write("PDFファイルをアップロードしてください。")
