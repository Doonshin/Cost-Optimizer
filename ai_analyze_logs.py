import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from glob import glob

# Load environment and initialize OpenAI client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# File to analyze
file_path = "/Users/shinjikato/Desktop/ cost opt/input_usage_log/lambda_logs.json"
print(f"\nAnalyzing {file_path} ...")

# Load JSON
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# System prompt
prompt = """
You are an AWS FinOps cost optimization expert with deep knowledge of EC2, S3, Lambda, and DynamoDB workloads.

Analyze each workload entry in the input JSON. The JSON may include CloudWatch Logs, CloudWatch Metrics, and AWS Cost Explorer billing data.


Return the output **as JSON** with the following fields:

1) Analyze these raw Lambda usage records and identify resource inefficiencies and configuration problems. Provide specific optimization fixes, including recommended memory/timeout changes.

2) Estimate potential monthly savings if each function is right-sized based on observed max memory usage and execution duration.

3) Provide a remediation plan for each function including: root cause analysis, configuration changes, expected performance improvement, and estimated cost reduction.

"""

# Send to model
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(data, indent=2)},
    ],
)

# Extract AI result
result = response.choices[0].message.content.strip()

# Output file
output_file = file_path.replace(".json", "_analysis.json")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ Analysis complete → {output_file}")
print("\nAll analyses completed successfully.")
