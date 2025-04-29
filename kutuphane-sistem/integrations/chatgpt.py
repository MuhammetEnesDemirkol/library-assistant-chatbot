from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize LangChain with OpenAI
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

# GÜNCELLENMİŞ PROMPT (Sadece Türkçe yanıta zorlar)
prompt = ChatPromptTemplate.from_template(
"""
Sen bir üniversite kütüphane asistanısın. Kullanıcıların araştırma konularına göre ilgili akademik kaynakları bulup yardımcı oluyorsun. 
Eğer birden fazla kaynak bulursan, cevaplarını şu şekilde sıralamalısın:

Başlık: ...
Yazar: ...
Tarih: ...

Her maddeyi Türkçe ve düzenli formatta sırala. 
Kullanıcı ek bir şey söylemese bile bu formatı uygula.


Kullanıcının araştırmak istediği konu:

{query}

Eğer bu konuda özel bir bilgin yoksa, genel bir yönlendirme yap.

"""
)

# Create a chain
chain = LLMChain(llm=llm, prompt=prompt)

def ask_gpt(query: str) -> str:
    try:
        response = chain.invoke({"query": query})
        return response["text"]
    except Exception as e:
        return f"İsteğiniz işlenirken bir hata oluştu: {str(e)}"
