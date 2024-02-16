# MyTeam Alertmanager Bot

- [MyTeam Bot API](https://myteam.mail.ru/botapi/tutorial/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)

This is a bot that can be integrated with [VKTeams Messenger](https://teams.vk.com/) and [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/)

### How to install

1. First of all, you have to create a bot in MyTeam (VK Teams) messenger via Metabot. Metabot is a father of the all bots like the @BotFather in the Telegram messenger.
- Type "Metabot" in the search bar and choose a chat
- Press "start"
- Type `/newbot` to create a new bot
- Enter an unique bot nick. It must end with a "bot"
- Save an api token

2. Secondly, you have to allow bot to join chats.
- Choose "Metabot" chat
- Type `/setjoingroups` and enter botId or nick name of bot

3. Also, you must define some environment variables in your myteam-alertmanager-bot installation.
- Define `API_URL_BASE` variable
- Define `BOT_NAME` variable
- Define default `default_chat_id` variable , if chat ID is not installed then use default (chatid to set query params to sent service ) examples:

- Define `CHECK_ALERTMANAGER` variable , check alertmanager , in default set false. If you set true , Alertmanager send to route /heartbeat
- Define `ALERTMANAGER_NAME` variable , set you name ALERTMANAGE in cluster
- Define `time_interval_check_alert`  variable ,  time interval check last send alertmanager message , default 30 seconds
- Define `time_how_long_not_to_send`  variable ,  time interval check how long not to send alert , default 300 seconds

```
http://localhost:8080/api/v1/push?chat_id=YOU_CHAT_ID
```  
  
- Define `API_TOKEN` variable

4. Quick start and test:

```bash
export API_URL_BASE="https://api.vkteams.example.com/bot/v1/"
export BOT_NAME="<bot_name>"
export API_TOKEN="<bot_token>"
export default_chat_id="<default_chat_id>"

cd app/
python3 manager.py &

curl -X POST -H "Content-Type: application/json" -d '{
  "status": "firing",
  "receiver": "example_receiver",
  "commonLabels": {
    "severity": "critical"
  },
  "commonAnnotations": {
    "summary": "Test alert",
    "description": "This is a test alert",
    "runbook": "Just do it, thats why manual", 
    "dashboard": "https://dashboard_you"
  },
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "severity": "critical"
      },
      "annotations": {
        "summary": "Instance 1",
        "instance": "Server 1",
        "value": "100"
      }
    },
    {
      "status": "firing",
      "labels": {
        "severity": "warning"
      },
      "annotations": {
        "summary": "Instance 2",
        "instance": "Server 2",
        "value": "50",
        "runbook": "Just do it, thats why manual",
        "dashboard": "https://dashboard_you"
      }
    }
  ]
}' "http://localhost:8080/api/v1/push?chat_id=$CHAT_ID"
```
5. To make it all works using alertmanager, you have to define a `webhook_config` in your alertmanager installation.
```yaml
# alertmanager example config
global:
  resolve_timeout: 5m
  http_config:
    follow_redirects: true
    enable_http2: true
  smtp_hello: localhost
  smtp_require_tls: true
  pagerduty_url: https://events.pagerduty.com/v2/enqueue
  opsgenie_api_url: https://api.opsgenie.com/
  wechat_api_url: https://qyapi.weixin.qq.com/cgi-bin/
  victorops_api_url: https://alert.victorops.com/integrations/generic/20131114/alert/
  telegram_api_url: https://api.telegram.org
  webex_api_url: https://webexapis.com/v1/messages
route:
  receiver: vkteams-foo-alerts
  continue: false
  routes:
    - receiver: vkteams-foo-alerts
      group_by:
        - alertname
        - group
      matchers:
        - team="FOO"
      continue: true
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
    - receiver: vkteams-bar-alerts
      group_by:
        - alertname
        - group
      matchers:
        - team="BAR"
      continue: true
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
receivers:
  - name: vkteams-foo-alerts
    webhook_configs:
      - send_resolved: true
        http_config:
          follow_redirects: true
          enable_http2: true
        url: http://myteam-alertmanager-bot.example.com:8080/api/v1/push?chat_id=$CHAT_ID
        max_alerts: 0
  - name: vkteams-bar-alerts
    webhook_configs:
      - send_resolved: true
        http_config:
          follow_redirects: true
          enable_http2: true
        url: http://myteam-alertmanager-bot.example.com:8080/api/v1/push?chat_id=$CHAT_ID
        max_alerts: 0
templates:
  - /etc/vm/configs/**/*.tmpl
```

if you want check sent alertmanager. to alert rule:

```yaml
- name: heartbeat
  rules:
    - alert: heartbeat
      expr: vector(1)
      labels:
        severity: none
      annotations:
        description: This is heartbeat alert
        summary: Alerting Dead mens  
        dashboard: "ToDo"
        runbook: "https://blog.ediri.io/how-to-set-up-a-dead-mans-switch-in-prometheus"
```

add config alertmanager this example :
```yaml
routes:
  - receiver: 'heartbeat'
    match:
      alertname: 'heartbeat'
    group_wait: 10s
    group_interval: 1m
    repeat_interval: 2m  
receivers:
- name: 'heartbeat'
  webhook_configs:
  - url: 'http://myteam-alertmanager-bot.example.com.monitoring.svc.cluster.local:8080/heartbeat'    
```