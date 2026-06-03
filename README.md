Hermes Detective Agent

AI-Powered Recruitment Fraud Investigation Assistant

Overview

Hermes Detective Agent is an AI-powered cybersecurity assistant designed to help students, job seekers, and early-career professionals identify suspicious internship and job opportunities before becoming victims of scams.

The platform investigates recruiter messages, onboarding workflows, screenshots, offer letters, PDFs, images, and suspicious domains using autonomous AI investigation agents and multimodal reasoning.

Instead of asking users to understand cybersecurity concepts, Hermes answers a simple question:

"Can I trust this opportunity?"

---

The Problem

Recruitment scams are rapidly increasing across:

- LinkedIn
- Telegram
- WhatsApp
- Fake HR portals
- Phishing onboarding websites

Common attack patterns include:

- Fake recruiters
- Refundable onboarding fees
- Telegram-only hiring processes
- Fake offer letters
- Impersonated company websites
- Phishing domains
- Identity theft attempts

Students often lack the technical expertise needed to investigate these opportunities.

---

The Solution

Hermes Detective Agent acts as an AI-powered recruitment fraud investigator.

Users can:

- Paste recruiter messages
- Upload screenshots
- Analyze suspicious domains
- Upload offer letters
- Investigate PDFs
- Submit onboarding instructions

The system investigates the evidence and produces:

- Risk Score
- Confidence Score
- Threat Indicators
- Explainable Verdict
- Recommended Actions

---

Features

Recruitment Scam Detection

Detects:

- Fake internships
- Fake job offers
- Payment coercion scams
- Telegram onboarding scams
- Recruiter impersonation
- Domain spoofing attacks
- Social engineering tactics

Multimodal Investigations

Supports:

- Text
- Images
- Screenshots
- PDFs
- Offer Letters
- Domains and URLs

Explainable AI

Provides:

- Risk assessment
- Investigation reasoning
- Confidence score
- Supporting evidence
- Recommended actions

Domain Intelligence

Identifies:

- Typo-squatting attacks
- Phishing domains
- Fake company portals
- Brand impersonation

---

Architecture

Frontend

- React.js
- Responsive conversational interface
- Evidence upload support
- Modern AI assistant experience

Mobile

- Flutter
- Cross-platform deployment
- Shared API integration

Backend

- FastAPI
- Python
- REST APIs
- Modular agent architecture

AI Models

NVIDIA NIM

Model:
"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"

Used for:

- Investigation reasoning
- Risk analysis
- Verdict generation
- Consensus evaluation

Pollinations AI

Used for:

- Image analysis
- Screenshot understanding
- Multimodal investigations

---

Investigation Agents

Behavior Analysis Agent

Detects:

- Urgency tactics
- Emotional manipulation
- Payment requests
- Suspicious onboarding behavior

OSINT Intelligence Agent

Verifies:

- Company legitimacy
- Recruiter claims
- Public trust indicators

Domain Intelligence Agent

Detects:

- Typo-squatting
- Fake company domains
- Phishing infrastructure
- Brand impersonation

Consensus Agent

Combines:

- Behavioral analysis
- OSINT intelligence
- Domain validation
- AI reasoning

to generate the final verdict.

---

Example Investigation

Input

Telegram recruiter requests a refundable onboarding payment and provides a link to:

onboard.googles.xyz

Investigation Findings

- Payment requested before onboarding
- Telegram-only communication
- Typo-squatted domain
- Brand impersonation detected

Verdict

Risk Level: Critical

Confidence: High

Recommendation:
Do not proceed. Verify through official company channels.

---

Technology Stack

Frontend:

- React.js

Mobile:

- Flutter

Backend:

- FastAPI
- Python

AI:

- NVIDIA NIM
- Pollinations AI

Infrastructure:

- Docker
- REST APIs
- JSON Workflows

---

Local Setup

Clone Repository

git clone <repository-url>
cd hermes-detective-agent

Install Dependencies

pip install -r requirements.txt

Configure Environment

Create ".env"

NVIDIA_API_KEY=your_key
POLLINATIONS_API_KEY=your_key

Run Backend

uvicorn main:app --reload

Run Frontend

npm install
npm run dev

Run Flutter App

flutter pub get
flutter run

---

Demo Scenarios

Safe Opportunity

Input:

Interview through careers.google.com with no onboarding payment.

Expected Result:

Low Risk

Suspicious Opportunity

Input:

Telegram onboarding with refundable UPI payment.

Expected Result:

High Risk

Impersonation Attack

Input:

onboard.googles.xyz

Expected Result:

Critical Risk

---

Future Roadmap

- Browser Extension
- LinkedIn Scam Detection
- Email Investigation
- Enterprise HR Verification
- Real-Time Threat Intelligence
- Mobile Store Deployment

---

Hackathon Submission

Project:
Hermes Detective Agent

Category:
AI Cybersecurity / Trust & Safety

Built During:
AI Builders Hackathon

Core Technologies:
React, Flutter, FastAPI, NVIDIA NIM, Pollinations AI, Python

---

Vision

Hermes Detective Agent aims to become the AI cybersecurity detective for the global hiring ecosystem.

Our mission is to help students and job seekers confidently evaluate opportunities before investing their time, money, or personal information.