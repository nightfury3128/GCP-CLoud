import os
import re
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

QUESTIONS = [
    {
        "id": "computer_science",
        "question": "Does UC offer a Computer Science major?",
        "answer": (
            "Yes. The University of Cincinnati offers a Bachelor of Science in Computer Science "
            "through its College of Engineering and Applied Science. The program covers computing "
            "fundamentals, software and systems, and offers opportunities for cooperative education "
            "(co-op), where students gain professional experience while studying. "
            "Program details: https://www.ceas.uc.edu/academics/departments/computer-science/degrees-programs/computer-science-bachelor-of-science.html"
        ),
        "keywords": ["computer science", "cs major", "computing major"],
    },
    {
        "id": "tuition",
        "question": "What is the in-state tuition at UC?",
        "answer": (
            "For the 2026–27 incoming undergraduate cohort at UC's Uptown campus, the published "
            "full-time Ohio-resident tuition and mandatory fees total $7,412 per semester "
            "($14,824 for two semesters). Rates depend on campus, academic cohort, program, and "
            "residency, and additional charges such as housing or program fees may apply. "
            "Verify your situation on the official tuition page: https://www.uc.edu/about/bursar/tuition-fees.html"
        ),
        "keywords": ["tuition", "in-state", "in state", "cost of attendance", "fees"],
    },
    {
        "id": "housing",
        "question": "Does UC provide on-campus housing?",
        "answer": (
            "Yes. The University of Cincinnati offers on-campus housing options for students, "
            "including residence halls and various room arrangements. Housing and meal-plan "
            "rates depend on the building, room type and student's tuition-guarantee cohort. "
            "Students can review housing options and current rates through UC Campus Life. "
            "Housing details: https://www.uc.edu/campus-life/housing/apply/rates.html"
        ),
        "keywords": ["housing", "dorm", "residence hall", "on-campus", "on campus"],
    },
    {
        "id": "football",
        "question": "Does UC have a football team?",
        "answer": (
            "Yes. The Cincinnati Bearcats have a university football team that competes in "
            "NCAA Division I's Football Bowl Subdivision and the Big 12 Conference. "
            "The team plays home games at Nippert Stadium on UC's campus. "
            "Learn about Bearcats athletics: https://www.uc.edu/big-12.html"
        ),
        "keywords": ["football", "bearcats team", "nippert"],
    },
]


def match_question(message):
    normalized = re.sub(r"[^a-z0-9 ]", "", message.lower()).strip()
    for question in QUESTIONS:
        if normalized == re.sub(r"[^a-z0-9 ]", "", question["question"].lower()).strip():
            return question
    for question in QUESTIONS:
        if any(keyword in message.lower() for keyword in question["keywords"]):
            return question
    return None


def gemini_answer(message):
    from google import genai
    from google.genai import types

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID")
    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    if not project:
        raise RuntimeError("Missing Google Cloud project ID")
    client = genai.Client(vertexai=True, project=project, location=location)
    response = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful student information assistant for the University of Cincinnati. "
                "Answer only university-related questions. Keep answers clear and concise. "
                "Do not invent tuition figures, deadlines, contact details, or university policies. "
                "For changing information, encourage checking the official University of Cincinnati "
                "website at https://www.uc.edu/. Do not request or reveal personal details."
            ),
            temperature=0.2,
            max_output_tokens=350,
        ),
    )
    return (response.text or "").strip()


@app.get("/")
def index():
    return render_template(
        "index.html",
        creator_first="Nipun",
        creator_last="Chandra",
        creator_email="chandrnu@mail.uc.edu",
    )


@app.get("/questions")
def questions():
    return jsonify([{"id": q["id"], "question": q["question"]} for q in QUESTIONS])


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()[:1000]
    if not message:
        return jsonify({"error": "Please enter a question."}), 400
    matched = match_question(message)
    if matched:
        return jsonify({"answer": matched["answer"], "source": "Verified predefined answer"})
    if os.environ.get("ENABLE_GEMINI", "false").lower() == "true":
        try:
            answer = gemini_answer(message)
            if answer:
                return jsonify({"answer": answer, "source": "Vertex AI Gemini"})
        except Exception:
            app.logger.exception("Gemini query failed")
            return jsonify({
                "answer": "The AI service is temporarily unavailable. You can still ask any of the four suggested questions.",
                "source": "Fallback",
            })
    return jsonify({
        "answer": "I can answer the four suggested UC questions. For other questions, enable Vertex AI Gemini in the cloud configuration.",
        "source": "Predefined mode",
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")), debug=True)
