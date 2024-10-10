#!/bin/bash

BOT_TOKEN=$TELEGRAM_BOT_TOKEN
CHAT_ID=$TELEGRAM_CHAT_ID

send_telegram_message() {
    local message="$1"
    curl -s -X POST https://api.telegram.org/bot"$BOT_TOKEN"/sendMessage \
        -d chat_id="$CHAT_ID" \
        -d text="$message" \
        -d parse_mode="HTML"
}

process_log_line() {
    local line="$1"
	local timestamp
	local error_msg
    if echo "$line" | grep -q "ERROR"; then
		timestamp=$(echo "$line" | grep -oP 'time="\K[^"]+')
		error_msg=$(echo "$line" | grep -oP 'msg="\K[^"]+')

		local message="<b>Error Alert</b>
		<b>Time:</b> $timestamp
		<b>Message:</b> $error_msg"

		send_telegram_message "$message"
    fi
}

docker compose logs -f web | while read -r line; do
    process_log_line "$line"
done
