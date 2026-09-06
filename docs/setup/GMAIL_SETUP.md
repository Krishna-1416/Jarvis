# 📧 Setting Up Gmail with Project Jarvis

Jarvis uses the official **Google Gmail API (OAuth 2.0)** to securely check unread emails, search your inbox, summarize threads, and draft replies.

---

### ⚡ 3-Step Setup (Takes ~2 Minutes)

#### Step 1: Create Google Cloud OAuth Credentials
1. Go to the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Create a new project (or select an existing one) named **`Project Jarvis`**.
3. In the search bar at the top, search for **`Gmail API`** and click **Enable**.
4. Go to **APIs & Services > OAuth consent screen**:
   - Choose **External** (or Internal if using Google Workspace).
   - Fill in an App name (e.g. `Jarvis Assistant`) and your email address.
   - Under **Test Users**, add your personal Gmail address (`your_email@gmail.com`).
5. Go to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth client ID**.
   - Select Application Type: **Desktop app**.
   - Name it `Jarvis Client` and click **Create**.
6. Click **Download JSON** for your new Client ID.

---

#### Step 2: Save `credentials.json`
Rename the downloaded file to **`credentials.json`** and place it in:
```
c:\Users\Krishna\Jarvis\data\credentials\credentials.json
```

---

#### Step 3: Run the 1-Click Authenticator
In your terminal, run:
```powershell
python scripts/setup_gmail.py
```
A Google authorization tab will open in your browser. Click **Continue** and grant permissions. A local `token.json` will be saved securely.

---

### 🎙️ Try These Voice & Text Commands with Jarvis:
- *"Jarvis, check my unread emails"*
- *"Do I have any emails from GitHub?"*
- *"Search emails with subject invoice"*
- *"Summarize the latest email from Alice"*
- *"Draft an email to john@example.com with subject Meeting and body See you at 3 PM"*
