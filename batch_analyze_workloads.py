import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------
# Load API key
# ---------------------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("ERROR: OPENAI_API_KEY is not set in your environment.")

client = OpenAI(api_key=api_key)

# ---------------------------------------------------------
# SYSTEM PROMPT (ENUM + FORMAT CONTROL)
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are an AWS FinOps optimization expert.
Your job is to analyze cloud workloads (Lambda or EC2) and output STRICT JSON.

You MUST obey ALL rules below. Violating ANY rule is not allowed.

-----------------------------------------------------
### 1. STRICT CATEGORY ENUM (NO OTHER VALUES ALLOWED)

If the resource_type == "lambda_function":
    issue_detected MUST be one of:
    [
      "over_provisioned_memory",
      "under_provisioned_memory",
      "timeout_failure",
      "cold_start_issue",
      "throttling",
      "healthy"
    ]

If the resource_type == "ec2_instance":
    issue_detected MUST be one of:
    [
      "over_provisioned_compute",
      "under_provisioned_compute",
      "idle_instance",
      "storage_cost_inefficiency",
      "deprecated_os_security_risk",
      "healthy_utilization"
    ]


### REQUIRED ENUM for recommended_action (ABSOLUTELY NO NATURAL LANGUAGE)

If the resource_type == "lambda_function":
    recommended_action MUST be one of:
    [
      "reduce_memory",
      "increase_memory",
      "increase_timeout",
      "mitigate_cold_starts",
      "resolve_throttling",
      "none"
    ]

If the resource_type == "ec2_instance":
    recommended_action MUST be one of:
    [
      "downsizing_instance",
      "scale_up_instance",
      "stop_or_terminate",
      "migrate_to_gp3_or_reduce_storage",
      "no_change",
      "upgrade_or_rebuild_instance"
    ]

DO NOT output any other values.
DO NOT alter spelling.
DO NOT create new enums.
DO NOT output natural language.


-----------------------------------------------------
### 2. JSON OUTPUT FORMAT (ABSOLUTELY STRICT)

For Lambda output:
{
  "<function_id>": {
    "issue_detected": "ENUM_VALUE",
    "recommended_action": "ENUM_VALUE"
    }
  }
}

For EC2 output:
{
  "<instance_id>": {
    "issue_detected": "ENUM_VALUE",
    "recommended_action": "ENUM_VALUE"
  }
}


-----------------------------------------------------
### 3. OUTPUT RULES

- Output ONLY valid JSON.
- DO NOT output any natural language.
- DO NOT wrap JSON in code fences (no ```json).
- DO NOT include comments.
- Keys MUST match the input function_id or instance_id exactly.
- All required keys MUST appear even if values are null.

-----------------------------------------------------

Analyze the input workloads and return ONLY the JSON prediction output.

"""


# ---------------------------------------------------------
# LLM CALL
# ---------------------------------------------------------
def analyze_with_llm(input_payload):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(input_payload, indent=2)}
        ],
        temperature=0,
    )

    text = response.choices[0].message.content.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("\n❌ ERROR: LLM returned invalid JSON:\n")
        print(text)
        return {}


# ---------------------------------------------------------
# EVALUATION ( STRICT )
# ---------------------------------------------------------
def evaluate(pred, ground_truth_list):
    results = []
    correct = 0
    total = 0

    for entry in ground_truth_list:
        input_block = entry.get("input", entry)
        truth = entry["ground_truth"]

        # Determine ID
        if "instance_id" in input_block:
            rid = input_block["instance_id"]
        elif "function_id" in input_block:
            rid = input_block["function_id"]
        else:
            continue

        pred_block = pred.get(rid, {})

        # STRICT COMPARISON
        issue_correct = pred_block.get("issue_detected") == truth.get("issue_detected")
        action_correct = pred_block.get("recommended_action") == truth.get("recommended_action")

        results.append({
            rid: {
                "issue_detected_correct": issue_correct,
                "recommended_action_correct": action_correct
            }
        })

        correct += int(issue_correct) + int(action_correct) 
        total += 2

    accuracy = correct / total if total > 0 else 0
    return results, accuracy


# ---------------------------------------------------------
# BATCH PROCESSING
# ---------------------------------------------------------
def batch_process(folder="workloads"):
    output_dir = "output_results"
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(folder, fname)
        print(f"\n🚀 Processing file: {fname}")

        with open(path, "r") as f:
            data = json.load(f)

        # Convert list → dict input for LLM
        formatted = {}
        for entry in data:
            inp = entry.get("input", entry)

            if "resource_type" in inp and inp["resource_type"] == "lambda_function":
                key = inp["function_id"]
            else:
                key = inp.get("instance_id")

            formatted[key] = inp

        # LLM prediction
        pred = analyze_with_llm(formatted)

        # Evaluate
        eval_result, acc = evaluate(pred, data)

        out = {
            "predictions": pred,
            "evaluation": eval_result,
            "overall_accuracy": acc
        }

        # Save
        out_path = os.path.join(output_dir, fname.replace(".json", "_output.json"))
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)

        print(f"✅ Saved → {out_path}")


# ---------------------------------------------------------
# Run Script
# ---------------------------------------------------------
if __name__ == "__main__":
    batch_process("workloads")
