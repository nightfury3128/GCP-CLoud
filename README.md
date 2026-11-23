# Bearcat Campus Assistant
Flask + Google App Engine + optional Vertex AI Gemini college inquiry chatbot.

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Open http://127.0.0.1:8080

## Deployment
1. Make a Google Cloud project and attach billing.
2. In the project, enable Cloud Build, App Engine, and Vertex AI APIs.
3. Run `gcloud auth login`, `gcloud config set project YOUR_PROJECT_ID`, `gcloud app create --region=us-central`.
4. Change creator values in app.yaml to your own name and school email.
5. Run `gcloud app deploy` and `gcloud app browse`.

## Gemini extra credit
Set ENABLE_GEMINI: "true" in app.yaml. Grant the App Engine runtime service account `roles/aiplatform.user` and redeploy.
Local AI use requires `gcloud auth application-default login` and setting `GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID` and `ENABLE_GEMINI=true`.

## Important
Only four required questions use fixed answers. Other questions are sent to Vertex AI when enabled. Gemini usage and hosting may incur charges. All predefined university details should be reviewed before production use. No account information is persisted by this app.
