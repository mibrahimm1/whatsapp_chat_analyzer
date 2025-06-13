# 📊 WhatsApp Chat Analyzer with RAG (LangChain + Streamlit)

This is an intelligent WhatsApp chat analyzer built using **Python**, **Streamlit**, and **LangChain**. It allows users to upload WhatsApp chat exports and interactively explore them through visualizations and natural language queries using a **RAG (Retrieval-Augmented Generation)** pipeline powered by **LLMs**.

---

## 🚀 Features

- 📥 Upload and parse WhatsApp chat exports (`.txt` format)
- 📊 Chat statistics: top users, emoji usage, message timelines
- 🌩 Word clouds and Altair-based interactive graphs
- 🤖 Ask questions about your chat using **RAG** + LLMs
- 🧠 Embedding-powered retrieval using **FAISS**

---

## 🛠️ Technologies Used

### 🧠 AI & NLP
- [LangChain](https://www.langchain.com/)
  - `langchain_community.chat_models.ChatOpenAI` for LLM integration
  - `RetrievalQA` and `FAISS` for RAG implementation
- [HuggingFace Transformers](https://huggingface.co/) for sentence embeddings
- `sentence-transformers/all-MiniLM-L6-v2` as the embedding model

### 🧮 Data & Visuals
- `Pandas` for data analysis
- `Matplotlib` and `Altair` for data visualization
- `WordCloud` for generating word clouds

### 🌐 App Framework
- [Streamlit](https://streamlit.io/) for building the interactive web app

### 🔐 Security & Deployment
- `.env` with `python-dotenv` for local API key management
- `Streamlit Cloud` for hosting
- `streamlit secrets` for secure key injection in production

---

## 📂 Folder Structure

```
📦 WhatsApp_Chat_Analyzer
├── app.py                  # Main Streamlit app
├── helper.py               # Data statistics and visualization logic
├── preprocesser.py         # Chat cleaning and processing
├── rag.py                  # RAG chain and LLM integration
├── requirements.txt        # Dependencies
├── .env                    # API keys (excluded from GitHub)
├── .gitignore              # Ignored files
└── README.md               # You're here
```

---

## 🔑 .env Format

> ⚠️ Never push this file to GitHub!

```
OPENAI_API_KEY=your_openai_or_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

---

## 💻 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your `.env` file to the root folder

### 5. Run the Streamlit app
```bash
streamlit run app.py
```

---

## 🧠 How RAG Works in This App

1. **Text Splitting:** WhatsApp chat is chunked using `RecursiveCharacterTextSplitter`
2. **Embedding:** Each chunk is embedded using `HuggingFaceEmbeddings`
3. **Vector Store:** Chunks are stored in a `FAISS` index
4. **Retrieval:** On user query, top-k relevant chunks are retrieved
5. **Answer Generation:** An LLM (Meta Llama-4 Scout via Groq) answers using the retrieved context

---

## 📎 Dependencies

```txt
streamlit
pandas
matplotlib
altair
emoji
urlextract
wordcloud
langchain
langchain-community
faiss-cpu
openai
huggingface-hub
python-dotenv
```

---

## 📧 Contact

**Muhammad Ibrahim Shaikh**  
Bachelor of Software Engineering – NUST  
[LinkedIn Profile](https://www.linkedin.com/in/ibrahimshaikhh/) *(replace with your link)*

---

## 📜 License

This project is open-source and available under the MIT License.
