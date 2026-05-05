# Hermes Audit to File Plugin

This is a [Hermes Hook Plugin](https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks#plugin-hooks) that logs tool calls and LLM API calls as an audit trail.

It registers two hooks:

- `post_tool_call` — logs the tool name, arguments (truncated to 200 chars), duration, and whether the call returned an error.
- `post_api_request` — logs the session, provider/model, API call count, duration, token usage, and assistant tool call count.

## Requirements

- Hermes Agent > 0.12.0

## Installation

- Clone or download this repository
- Copy the folder `audit_to_file` to `$HERMES_HOME/plugins`
- If you use profiles, copy `audit_to_file` to the `plugins` folder of each profile home
- Restart Hermes

## Enable the plugin

- Check if the plugin is detected:

```bash
hermes plugins list
```

- Enable the plugin

```bash
hermes plugins enable audit_to_file
```

- Or you can update the `config.yaml`:

```yaml
plugins:
  disabled: []
  enabled:
  - audit_to_file
```

## Log file

Each profile writes its own log to `$HERMES_HOME/logs/audit.log`.

```
2026-05-03 15:12:12,118 INFO LLM_CALL  => session=20260503_151207_61f3a268, model=openai-codex/gpt-5.5, api_calls=1, api_duration=4.0575408935546875 (s), tool_calls=1, usage={'input_tokens': 14439, 'output_tokens': 40, 'cache_read_tokens': 0, 'cache_write_tokens': 0, 'reasoning_tokens': 19, 'request_count': 1, 'prompt_tokens': 14439, 'total_tokens': 14479}, chars=0, rest={'platform': 'telegram', 'message_count': 2, 'response_model': 'gpt-5.5'}
2026-05-03 15:12:12,131 INFO TOOL_CALL => session=20260503_151207_61f3a268, tool=skill_view, error=False, duration=12 (ms): args={"name": "amazon-books"}
...
```

The log file rotates daily and keeps 30 days of backups.
