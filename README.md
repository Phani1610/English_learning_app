# English Learning App

A web-based English learning application with a Flask backend and HTML/CSS/JS frontend.

## Project Structure

```
english-learning-app/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## Setup & Installation

### Backend Setup
1. Navigate to the backend directory:
   
```
   cd backend
   
```

2. Create a virtual environment (optional but recommended):
   
```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
```

3. Install dependencies:
   
```
   pip install -r requirements.txt
   
```

4. Run the backend server:
   
```
   python app.py
   
```

### Frontend Setup
Simply open `frontend/index.html` in a web browser, or use a local server:
```
# Using Python
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```

## Features

- Interactive English learning interface
- User-friendly design
- Backend API for data handling

## License

MIT License
