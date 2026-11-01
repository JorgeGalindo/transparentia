#!/bin/zsh
# uso: run_agent.sh <modelo: haiku|sonnet|opus> <fichero_prompt> <log>
# Lanza un claude -p headless con el token OAuth del llavero (solo para este proceso).
MODEL=$1; PROMPT=$2; LOG=$3
SP=$WORKDIR
cd "$SP"
CLAUDE_CODE_OAUTH_TOKEN=$(security find-generic-password -a "$USER" -s anthropic-api-key -w) \
  claude -p "$(cat "$PROMPT")" --model "$MODEL" \
  --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch" \
  --permission-mode acceptEdits --add-dir "$SP" --output-format text > "$LOG" 2>&1
echo "EXIT $? $(date)" >> "$LOG"
