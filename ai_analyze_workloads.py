import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from glob import glob

# Load enviroment and initialize OpenAI client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")
client = OpenAI(api_key=api_key)

# Gather all demo JSON files
json_files = glob("/Users/shinjikato/Desktop/ cost opt/input_usage_log")
# if not json_files:
#     raise FileNotFoundError("No demo_*.json files found in this directory")


# Define the system prompt
prompt = """
You are an AWS FinOps cost optimization expert with deep knowledge of EC2, S3, Lambda, and DynamoDB workloads.

Analyze each workload entry in the input JSON. The JSON may include CloudWatch Logs, CloudWatch Metrics, and AWS Cost Explorer billing data.

For each workload item, provide detailed optimization guidance. Use specific AWS terminology, metrics, and actionable suggestions.

Return the output **as JSON** with the following fields:

1) Workload_Description:
   A concise natural-language summary of what the workload appears to do based on logs, metrics, and events.

2) Cost_Efficiency_Opportunities:
   Identify wasted spend, overprovisioning, cost anomalies, pricing model improvements 
   (e.g., ARM migration, instance rightsizing, Spot, Savings Plans, S3 storage class changes).

3) Performance_Reliability_Risks:
   Include timeouts, throttles, memory pressure, concurrency issues, API retries, cold starts, or database hot partitions.

4) Rightsizing_Recommendations:
   Provide memory/CPU/timeout suggestions (for Lambda: memory_mb and timeout_seconds).
   Include estimated headroom and percent over/under-provisioning when possible.

5) Monthly_Savings_Estimate_USD:
   Estimate potential monthly savings with realistic ranges. If insufficient data, say "insufficient data".

Be practical and precise. Reference Lambda duration, GB-seconds, DynamoDB RCU/WCU, S3 storage size, or EC2 instance class when helpful. Avoid generic advice.
"""


# # Analyze each JSON file
# for file_path in json_files:
#     print(f"\n Analyzing {file_path} ...")

#     # Load input data
#     with open(file_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     # Send to model
#     response = client.chat.completions.create(
#         model="gpt-5",
#         messages=[
#             {"role": "system", "content": prompt},
#             {"role": "user", "content": json.dumps(data, indent=2,)},
#         ],
#     )

#     # Extract AI result
#     result = response.choices[0].message.content.strip()

#     # Save output
#     output_file = file_path.replace(".json", "_analysis.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(result)

#     print(f"✅ Analysis complete → {output_file}")

# print("\n All analyses completed successfully.")

print(f"\n Analyzing {"/Users/shinjikato/Desktop/ cost opt/input_usage_log/lambda_logs.json"} ...")

# Load input data
with open("/Users/shinjikato/Desktop/ cost opt/input_usage_log/lambda_logs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Send to model
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(data, indent=2,)},
    ],
)

# Extract AI result
result = response.choices[0].message.content.strip()
file_path = "/Users/shinjikato/Desktop/ cost opt/input_usage_log"

# Save output
output_file = file_path.replace(".json", "_analysis.json")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ Analysis complete → {output_file}")

print("\n All analyses completed successfully.")