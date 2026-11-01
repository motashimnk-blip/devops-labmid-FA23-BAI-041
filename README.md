# Assignment Submission Portal - DevOps Lab Mid

- **Name:** Mohtashim Nawaz Khan
- **Reg No:** FA23-BAI-041
- **Program:** BS Artificial Intelligence
- **Course:** CSC418 DevOps for Cloud Computing
- **Instructor:** Mr. Babar Shazad

A simple portal where students enter their name, registration number, assignment
title and submission URL. Every push to GitHub runs the automated tests in GitHub
Actions, builds a JSON test report and sends it to a receiver running on my own
computer, which saves it as `test-report.json`.

## Project structure

```
assignment-portal/
├── app.py                     # starts the Flask app
├── portal/
│   ├── __init__.py            # routes (form, submit, list)
│   ├── validation.py          # required fields + URL check
│   └── storage.py             # SQLite database (submissions.db)
├── templates/index.html       # form + saved submissions table
├── tests/test_portal.py       # 3 automated test cases (pytest)
├── ci/
│   ├── build_report.py        # pytest XML -> test-report.json
│   ├── send_report.py         # POST report to the local receiver
│   └── send_email.py          # bonus: email the report
├── receiver/
│   ├── receiver.py            # local HTTP receiver (saves test-report.json)
│   ├── tunnel.py              # ngrok tunnel so GitHub can reach localhost
│   └── requirements.txt
├── site/                      # bonus: static demo for GitHub Pages
├── .github/workflows/ci.yml   # CI pipeline
├── start-receiver.bat
└── start-tunnel.bat
```

## 1. Run the application

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in the browser.

## 2. Run the tests

```bash
pytest -v
```

| Test | Expected result |
|------|-----------------|
| `test_valid_submission_is_saved_and_listed` | Submission is saved and shown in the list |
| `test_missing_registration_number_is_rejected` | Rejected with "Registration number is required." |
| `test_invalid_url_is_rejected_and_not_saved` | Rejected and nothing is saved |

## 3. Start the local receiver

```bash
python receiver/receiver.py
```

It listens on http://localhost:8080 and saves every report it gets on
`POST /report` to `test-report.json` in the project folder (plus a copy of each run
in `reports/`). You can also double click `start-receiver.bat`.

## 4. Open the tunnel (so GitHub can reach my computer)

A GitHub runner's `localhost` is the runner itself, so I use ngrok.

1. Make a free account on https://dashboard.ngrok.com and copy the authtoken.
2. Install the tunnel package and start it (or put the token in `start-tunnel.bat`):

```bash
pip install -r receiver/requirements.txt
set NGROK_AUTHTOKEN=your_token_here
python receiver/tunnel.py
```

3. It prints a URL like `https://xxxx.ngrok-free.app`. Keep the receiver and the
   tunnel windows open during the demo.

## 5. GitHub secrets

Repository -> Settings -> Secrets and variables -> Actions -> New repository secret

| Secret | Value |
|--------|-------|
| `RECEIVER_URL` | `https://xxxx.ngrok-free.app/report` |
| `RECEIVER_TOKEN` | optional, same token set in `RECEIVER_TOKEN` when starting the receiver |
| `SMTP_USERNAME` | (bonus) Gmail address that sends the email |
| `SMTP_PASSWORD` | (bonus) Gmail App Password |
| `REPORT_EMAIL_TO` | (bonus) email address that receives the report |
| `SMTP_SERVER` / `SMTP_PORT` | optional, default `smtp.gmail.com` / `587` |

## 6. CI pipeline (`.github/workflows/ci.yml`)

On every push:

1. Checkout the pushed commit and install Python 3.12 + requirements.
2. Run `pytest -v --junitxml=results.xml`. If any test fails, this step fails and
   the job is marked failed.
3. Build `test-report.json` (repo, branch, commit SHA, run id, timestamp, every test
   result with failure message, total / passed / failed, overall status).
4. Send the report to the local receiver. Runs with `if: always()` so it is sent for
   passing **and** failing runs.
5. Email the report (bonus), also for pass and fail.
6. **deploy-pages** job (bonus): only on `main` and only when the test job passed.
   A failing run skips it, so the old Pages site stays unchanged.

For Pages: Repository -> Settings -> Pages -> Source = **GitHub Actions**.
Deployed URL: `https://<github-username>.github.io/<repo-name>/`

## 7. Demo steps (pass -> fail -> fix)

1. Push the project. All 3 tests pass, `test-report.json` shows `"overall_status": "PASSED"`.
2. Add a defect, e.g. in `portal/validation.py` make the URL check always pass:
   ```python
   def is_valid_url(url):
       return True   # DEFECT
   ```
   Push. `test_invalid_url_is_rejected_and_not_saved` fails, the pipeline is red and
   `test-report.json` is updated with `"overall_status": "FAILED"` and the failure message.
3. Undo the defect and push again. Pipeline is green and the JSON file shows PASSED.
