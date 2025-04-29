# 🤖 Batman University Library Assistant

This project is an AI-powered assistant system developed for the Batman University Library. It helps users search library resources, access academic publications, and get information about library services.

> ⚠️ Disclaimer: This project is a generalized version of a freelance work delivered to a private client. No confidential information is shared.

---

## 🚀 Features

1. **Library Catalog Search**
   - Search books, journals, and other materials via Yordam API
   - Access detailed bibliographic information
   - Secure API access with a static token

2. **Academic Resource Search**
   - Access academic papers via OAI-PMH protocol
   - Search theses, articles, and proceedings
   - Retrieve metadata for academic documents

3. **Library Information**
   - Up-to-date announcements
   - Staff directory
   - Contact information
   - Working hours

4. **AI-Powered Support**
   - ChatGPT integration for smart responses
   - Full Turkish language support
   - Library-specific customized replies

---

## ⚙️ Installation

1. Install Python 3.8 or higher.
2. Clone the project:
   ```bash
   git clone https://github.com/yourusername/library-assistant-chatbot.git
   cd library-assistant-chatbot
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/MacOS
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file and configure required environment variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   LIBRARY_API_URL=your_library_api_url
   LIBRARY_API_USER=your_api_user
   LIBRARY_API_PASS=your_api_pass
   STATIC_YORDAM_TOKEN=your_static_token
   ```

---

## ▶️ Running the App

To start the development server:

```bash
uvicorn app:app --reload
```

The app will be accessible at: [http://localhost:8000](http://localhost:8000)

---

## 📡 API Endpoints

- `GET /` – Home page
- `POST /sorgula` – Handles user queries
- `GET /bilgiler` – Returns general library information

---

## 📁 Project Structure

```
library-assistant-chatbot/
├── app.py                # Main application
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── README.md             # Documentation
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates
├── integrations/         # API integrations
│   ├── library_api.py    # Yordam API integration
│   ├── oai_pmh.py        # OAI-PMH integration
│   └── query_service.py  # Core query processing
└── scrapers/             # Web scrapers (if any)
```

---

## 💻 Development Guidelines

1. Follow PEP 8 code standards.
2. Create a new branch for each feature.
3. Test all changes before committing.
4. Submit pull requests for review.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---


## 👨‍💼 Author
**Muhammet Enes DEMİRKOL** – Project Developer

---
