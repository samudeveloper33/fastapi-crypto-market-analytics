1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and configure your settings:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/cryptoanalytics
COINGECKO_API_KEY=your_api_key_here
INGEST_INTERVAL_MINUTES=5
LOG_LEVEL=INFO
```


## Running the Application

Start the API server:
```bash
uvicorn app.main:app --reload
```
