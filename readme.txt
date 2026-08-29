========================================================================
 EMAIL MANAGEMENT AND RESPONSE AGENT
 Free Build Guide (B.Tech Project - I, 7th Semester)
========================================================================

PROJECT TYPE
------------
This is a WEB APP, not a mobile app.
- Frontend: React.js dashboard, opened in a browser (desktop or phone browser)
- Backend: Python Flask (or Node.js) server, handles all the logic
- No app-store install needed; works as a responsive website

You can add a mobile app later using React Native or Flutter with the
same backend, but that is out of scope for this synopsis.


========================================================================
1. FREE TECH STACK
========================================================================

Email Integration
  - Gmail API (free, generous quota for personal/dev use)
  - Google Cloud project + OAuth consent screen kept in "Testing" mode
  - Add yourself as a test user -> no app verification needed

Preprocessing
  - NLTK or spaCy (free, open-source) for cleaning, tokenizing,
    language detection

Classification (urgent / informational / promotional)
  - scikit-learn (TF-IDF + Logistic Regression or SVM) - free
  - Optional upgrade: a pretrained Hugging Face transformer model

Spam Detection
  - Do NOT rebuild this from scratch.
  - Use Gmail's own SPAM label via the Gmail API - it is already
    trained on billions of emails and is free to query.

Response Generation (LLM)
  - Google Gemini API free tier - no credit card required, best
    free option for this project (roughly 1,000+ requests/day on
    Flash models)
  - Alternative: Ollama running a local open model (Llama 3.1,
    Mistral) - 100% free, runs on your own laptop, no API limits
  - Note: Anthropic Claude API and OpenAI API are PAID. If your
    synopsis lists them, mention them as "evaluated options" in your
    report and note that Gemini was used for the free prototype.

Backend
  - Python Flask (or Node.js) - free

Frontend
  - React.js (Vite) - free

Database
  - SQLite for local dev - free, zero setup
  - or MongoDB Atlas free tier (512MB, free forever) if cloud-hosted

Notifications (agent alerting you)
  - Telegram bot (via BotFather) - free, real-time, easiest "wow
    factor" for a demo
  - Alternatives: daily/hourly email digest via Gmail API, or
    dashboard-only (no push needed)

Hosting (for your demo)
  - Backend: Render or Railway free tier
  - Frontend: Vercel or Netlify free tier

Version Control
  - GitHub (free) - also useful to show progress to your supervisor


========================================================================
2. BUILD STEPS (IN ORDER)
========================================================================

1. Set up Gmail API access
   Create a free Google Cloud project, enable the Gmail API, set up
   an OAuth consent screen in Testing mode, add yourself as a test
   user. Use google-api-python-client to fetch emails.

2. Build the preprocessing pipeline
   Pull emails, strip HTML/signatures, tokenize with NLTK/spaCy,
   detect language. Output clean text for classification.

3. Train or plug in the classifier
   Label 100-300 of your own emails (urgent / informational /
   promotional). Train TF-IDF + Logistic Regression/SVM in
   scikit-learn. Optionally swap in a Hugging Face model later.

4. Add priority scoring
   Combine classifier output with rule-based signals:
     - sender importance (known contact vs first-time sender)
     - keyword signals ("urgent", "deadline", "action required")
     - deadline detection (regex or spaCy date-entity recognition)
   Example formula:
     priority = 0.6*classifier_confidence + 0.2*sender_score
                + 0.2*keyword_score

5. Wire up response generation
   Send classified email content to the Gemini API (or local Ollama
   model) with a prompt asking for a short, professional, editable
   draft reply.

6. Build the Flask backend
   Expose REST endpoints: fetch emails, get classification/priority,
   get draft reply, approve/edit/send reply, archive.

7. Build the React dashboard
   Inbox list sorted by priority/category, email detail view, and an
   editable draft-reply panel with Approve & Send / Discard buttons.

8. Add notifications
   Simplest: dashboard-only. Best demo value: Telegram bot alert on
   high-priority emails (a few lines using requests.post() to the
   Telegram Bot API).

9. Test and deploy for the demo
   Test classification accuracy and the end-to-end flow with a real
   inbox. Deploy backend on Render (free) and frontend on Vercel
   (free) so your supervisor can open it via a real URL.


========================================================================
3. IMPORTANT DESIGN NOTE
========================================================================

Never let the agent auto-send emails. Every AI-drafted reply should
sit in the dashboard for you to review, edit, and approve before it
sends. This matches your synopsis objective #5 and is also the safer,
more defensible design choice for your project report.


========================================================================
4. HOW TO FRAME THIS IN YOUR REPORT
========================================================================

"Spam filtering leverages Gmail's existing model; the project's
contribution is the importance/priority layer, which combines an
ML text classifier with rule-based signals (sender, keywords,
deadlines), plus an LLM-based draft-response module with human
review before sending."

This is an honest, examiner-friendly framing: it's clear about what
is reused (Gmail spam detection) versus what you actually built
(priority scoring + response generation + review workflow).


========================================================================
END OF FILE
========================================================================