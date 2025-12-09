# personal-notes-manager-291545-291584

This workspace contains the FastAPI backend for a personal notes app.

- Backend service directory: notes_backend
- To run locally:
  1. cd notes_backend
  2. pip install -r requirements.txt
  3. uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
- Open API docs at: http://localhost:3001/docs

For more details, see notes_backend/README.md.