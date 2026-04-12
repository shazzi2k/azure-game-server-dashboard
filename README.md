# ☁️ Azure Game Server Dashboard

A cloud-based dashboard for managing virtual machines using Microsoft Azure APIs.

---

## 🚀 Overview

This project is a Flask-based web application deployed on Azure App Service that allows users to:

* Monitor system metrics
* Authenticate securely
* Control Azure Virtual Machines (start/stop)
* Interact with cloud resources via REST APIs

---

## 🧱 Architecture

User → Web App (Flask) → Azure REST API → Virtual Machines

---

## 🔐 Security

* Uses Microsoft Entra ID (Azure AD) App Registration
* OAuth2 Client Credentials flow
* Role-Based Access Control (RBAC)
* Secrets stored securely in App Service environment variables

---

## ⚙️ Tech Stack

* Python (Flask)
* Azure App Service
* Azure Virtual Machines
* GitHub Actions (CI/CD)
* REST APIs

---

## 📦 Features

* User authentication (session-based)
* System monitoring endpoints
* Cloud-ready API structure
* CI/CD deployment from GitHub
* Scalable architecture for VM control

---

## 🛠️ Deployment

This application is deployed using Azure App Service and connected to GitHub for automatic deployments.

---

## 📌 Future Improvements

* VM start/stop integration (in progress)
* Role-based user access
* Dashboard UI enhancements
* Auto-scaling logic
* Cost optimisation features

---

## 📷 Screenshots

*(Add screenshots of your dashboard here once complete)*

---

## 👤 Author

Aaron Schorah
