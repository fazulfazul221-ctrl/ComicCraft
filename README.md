# ComicCraft 🎨📖

An AI-powered web application that turns story ideas into multi-panel comics with generated scripts, visuals, and downloadable layouts.

---

## 🚀 Features

- **Story & Script Generation:** Uses Google Gemini to generate story outlines, character dialogues, and visual scene prompts.
- **Panel Visual Generation:** Produces comic panel illustrations based on generated scene prompts.
- **Dynamic Layout Builder:** Assembles panels, dialogues, and captions into clean comic book page layouts.
- **Export Options:** Export final comics into PDF and image formats.
- **FastAPI Backend:** Lightweight and responsive modern Python backend.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn, Jinja2
- **AI Models:** Google Gemini (`google-generativeai`), Hugging Face / Diffusers
- **Image Processing & Export:** Pillow (PIL), `fpdf2`
- **Environment Management:** `python-dotenv`

---

## 📋 Prerequisites

- Python 3.10+
- A Google Gemini API Key
- A Hugging Face API Key (if using HF image endpoints)

---

## ⚙️ Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/ComicCraft.git
   cd ComicCraft
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   HF_API_KEY=your_huggingface_api_key_here
   ```

5. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Open your browser and navigate to `http://localhost:8000`.

---

## 📂 Project Structure

```
ComicCraft/
├── app/
│   ├── main.py              # Application entry point
│   ├── routes.py            # API & web routes
│   ├── gemini_flash.py      # Gemini Flash integration
│   ├── gemini_pro.py        # Gemini Pro integration
│   ├── image_generator.py   # AI panel image generation
│   ├── layout_builder.py    # Comic panel layout builder
│   └── exporters.py         # PDF and image export utilities
├── static/                  # CSS, JS, and generated assets
├── templates/               # Jinja2 HTML templates
├── .env.example             # Example environment configuration
├── .gitignore               # Ignored files (secrets & environments)
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 📜 License

This project is created for educational and academic submission purposes.
