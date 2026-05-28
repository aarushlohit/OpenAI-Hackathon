# Investigation Workflows - Hermes-X Custom Pipeline

## CLI Workflows

### Single Investigation

```bash
python scripts/custom_investigation.py --json << 'EOF'
Your suspicious message here
EOF
```

### Extract Verdict Only

```bash
python scripts/custom_investigation.py --json \
  | jq '.verdict | {score: .final_score, severity, confidence}'

# Output:
# {
#   "score": 78,
#   "severity": "HIGH",
#   "confidence": 0.84
# }
```

### Extract All Signals

```bash
python scripts/custom_investigation.py --json \
  | jq '.analysis_stages | to_entries[] | "\(.key): \(.value.signals // .value.indicators // .value.results)"'
```

### Batch Process Multiple Inputs

```bash
#!/bin/bash
mkdir -p reports
for input_file in test_cases/*.txt; do
  case_name=$(basename "$input_file" .txt)
  python scripts/custom_investigation.py --json < "$input_file" \
    > "reports/${case_name}_$(date +%s).json"
  echo "✓ Processed: $case_name"
done
```

### Filter by Severity Threshold

```bash
# Only HIGH and CRITICAL
python scripts/custom_investigation.py --json \
  | jq 'select(.verdict.severity == "HIGH" or .verdict.severity == "CRITICAL")'

# Only HIGH or above (score >= 60)
python scripts/custom_investigation.py --json \
  | jq 'select(.verdict.final_score >= 60)'
```

### Export for Analysis

```bash
# CSV format
python scripts/custom_investigation.py --json \
  | jq -r '[.investigation_id, .verdict.final_score, .verdict.severity, .verdict.confidence] | @csv' \
  >> investigation_log.csv

# Ndjson (newline-delimited JSON) for streaming
cat case1.txt | python scripts/custom_investigation.py --json >> results.ndjson
cat case2.txt | python scripts/custom_investigation.py --json >> results.ndjson
```

---

## Production Integration Patterns

### Docker Entrypoint (Standalone Container)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY scripts/custom_investigation.py .
COPY app/ app/

ENTRYPOINT ["python", "custom_investigation.py"]
```

Use:
```bash
docker run -i hermes-investigation < message.txt > report.json
```

### FastAPI Endpoint Wrapper

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess, json

app = FastAPI()

@app.post("/api/v1/investigate")
async def investigate(input_text: str):
    result = subprocess.run(
        ["python", "scripts/custom_investigation.py", "--json"],
        input=input_text.encode(),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    return json.loads(result.stdout)

# Use: POST /api/v1/investigate?input_text="Your message"
```

### Lambda Function (AWS)

```python
import subprocess, json, os

def lambda_handler(event, context):
    input_text = event.get('body', '')
    result = subprocess.run(
        ["python", "/opt/scripts/custom_investigation.py", "--json"],
        input=input_text.encode(),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': result.stderr})
        }
    
    return {
        'statusCode': 200,
        'body': result.stdout
    }
```

### Kubernetes Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: hermes-investigation
spec:
  template:
    spec:
      containers:
      - name: investigator
        image: hermes-investigation:latest
        stdin: true
        args: ["--json"]
        volumeMounts:
        - name: input
          mountPath: /input
      volumes:
      - name: input
        configMap:
          name: investigation-input
      restartPolicy: Never
  backoffLimit: 3
```

---

## Monitoring Integration

### Continuous Alert Scanning

```bash
#!/bin/bash
# Monitor Slack alerts for suspicious job postings

while true; do
  messages=$(curl -s https://api.slack.com/messages \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    | jq -r '.messages[].text')
  
  echo "$messages" | while read msg; do
    result=$(python scripts/custom_investigation.py --json << EOF
$msg
EOF
    )
    
    score=$(echo "$result" | jq '.verdict.final_score')
    if [ "$score" -gt 70 ]; then
      # Send alert to SOC
      curl -X POST https://soc.internal/api/alerts \
        -H "Content-Type: application/json" \
        -d "$result"
    fi
  done
  
  sleep 300  # Check every 5 minutes
done
```

### GitOps Investigation Pipeline

```yaml
# .github/workflows/investigate-pr.yml
name: Investigate Job Posting
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Custom Investigation
        run: |
          python scripts/custom_investigation.py --json \
            < job_posting.txt > report.json
      
      - name: Check Severity
        run: |
          severity=$(jq '.verdict.severity' report.json)
          if [ "$severity" == "CRITICAL" ]; then
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: investigation-report
          path: report.json
```

### Time-Series Analysis

```python
import json, sqlite3, datetime
from subprocess import run, PIPE

db = sqlite3.connect('investigations.db')
cursor = db.cursor()

# Create table
cursor.execute('''
  CREATE TABLE IF NOT EXISTS investigations (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    score INTEGER,
    severity TEXT,
    signals TEXT
  )
''')

# Log investigation
def log_investigation(input_text):
    result = run(
        ["python", "scripts/custom_investigation.py", "--json"],
        input=input_text.encode(),
        stdout=PIPE,
        text=True
    )
    
    data = json.loads(result.stdout)
    cursor.execute('''
      INSERT INTO investigations VALUES (?, ?, ?, ?, ?)
    ''', (
        data['investigation_id'],
        data['timestamp'],
        data['verdict']['final_score'],
        data['verdict']['severity'],
        json.dumps(data['analysis_stages'])
    ))
    db.commit()

# Analyze trends
def trend_report():
    cursor.execute('''
      SELECT 
        DATE(timestamp) as date,
        COUNT(*) as count,
        AVG(score) as avg_score,
        COUNT(CASE WHEN severity='CRITICAL' THEN 1 END) as critical_count
      FROM investigations
      GROUP BY DATE(timestamp)
      ORDER BY date DESC
      LIMIT 7
    ''')
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} investigations, avg score {row[2]:.1f}, {row[3]} critical")
```

---

## Testing Patterns

### Unit Testing Against Outcomes

```python
import subprocess, json

def run_investigation(input_text):
    result = subprocess.run(
        ["python", "scripts/custom_investigation.py", "--json"],
        input=input_text.encode(),
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def test_payment_scam_detection():
    input_text = "UPI payment required for onboarding"
    result = run_investigation(input_text)
    
    assert result['verdict']['final_score'] > 60, "Should detect payment scam"
    assert 'payment_extraction' in str(result['analysis_stages']['behavior'])

def test_legitimate_offer_passes():
    input_text = "Offer from careers@microsoft.com for Senior Software Engineer"
    result = run_investigation(input_text)
    
    assert result['verdict']['final_score'] < 40, "Should pass legitimate offer"
```

### Regression Testing

```bash
#!/bin/bash
# Run 5 test cases, compare output against baseline

for i in {1..5}; do
  case_file="tests/case_$i.txt"
  baseline_file="tests/case_$i.baseline.json"
  
  python scripts/custom_investigation.py --json < "$case_file" > output.json
  
  if diff -q <(jq '.verdict' output.json) <(jq '.verdict' "$baseline_file") > /dev/null; then
    echo "✓ Case $i: PASSED"
  else
    echo "✗ Case $i: FAILED"
    diff <(jq '.verdict' output.json) <(jq '.verdict' "$baseline_file")
  fi
done
```

### Performance Testing

```bash
#!/bin/bash
# Measure throughput and latency

echo "Testing 100 investigations..."
total_time=0

for i in {1..100}; do
  start=$(date +%s%N)
  
  python scripts/custom_investigation.py --json << EOF > /dev/null
Telegram message about job offer with payment ($i)
EOF
  
  end=$(date +%s%N)
  elapsed=$(( (end - start) / 1000000 ))  # Convert nanoseconds to ms
  total_time=$(( total_time + elapsed ))
  
  if [ $((i % 10)) -eq 0 ]; then
    echo "  Completed $i/100 investigations..."
  fi
done

avg_time=$(( total_time / 100 ))
throughput=$(( 100000 / total_time ))

echo "Average latency: ${avg_time}ms"
echo "Throughput: ${throughput} investigations/second"
```

---

## Integration Checklist

- [ ] Script tested with 5+ real scam scenarios
- [ ] JSON output validated against schema
- [ ] Performance baseline established (avg latency < 500ms)
- [ ] Batch processing tested (100+ investigations)
- [ ] CLI integration working (custom_investigation.py --json)
- [ ] Error handling verified (invalid input, provider failures)
- [ ] Logging configured (debug mode working)
- [ ] Deterministic validation all checks passing
- [ ] Cross-agent consensus reaching > 80% agreement
- [ ] Explainability output complete (signals + reasoning)

---

## Next Steps: Live Provider Integration

Replace mock reasoning patterns with real API calls:

```python
# Current (mock):
signals = extract_signals_by_keywords(text)

# Phase 2 (real NVIDIA):
signals = await behavior_analysis_agent.analyze(
    text=text,
    provider="nvidia",
    model="nvidia/nemotron-omni-30b"
)
```

See [LIVE_PROVIDER_SETUP.md](LIVE_PROVIDER_SETUP.md) for production API integration.

---

## Files Generated

- `INTERACTIVE_TESTING.md` — Complete testing reference (5 test cases, usage patterns)
- `scripts/custom_investigation.py` — Main investigation engine
- `CUSTOM_INVESTIGATION_GUIDE.md` — Usage guide + test cases
- `INVESTIGATION_WORKFLOWS.md` — This file (production patterns)

