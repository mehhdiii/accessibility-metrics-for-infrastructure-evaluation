```
docker run -d --name datadog-agent \
  -e DD_API_KEY=2b7d5744ca522e867da8845d01c66df4 \
  -e DD_SITE=us5.datadoghq.com \
  -e DD_LOGS_ENABLED=true \
  -v /home/ozanpali/Documents/mehdi-khorasani/accessibility-metrics-for-infrastructure-evaluation/logging/ros2_logs:/ros2_logs:ro \
  -v /home/ozanpali/Documents/mehdi-khorasani/accessibility-metrics-for-infrastructure-evaluation/logging/datadog.yaml:/etc/datadog-agent/conf.d/ros2_logs.d/conf.yaml:ro \
  -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  gcr.io/datadoghq/agent:latest

```