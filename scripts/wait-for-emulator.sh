#!/bin/bash
# Wait for emulator via adb (on port 5555)
ADB_TARGET=${1:-localhost:5555}
set -euo pipefail

adb kill-server || true
adb start-server

echo "Connecting to ${ADB_TARGET}..."
n=0
until adb connect ${ADB_TARGET} || [ $n -gt 60 ]; do
  n=$((n+1))
  sleep 1
done

n=0
until [ "$(adb -s ${ADB_TARGET} shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ] || [ $n -gt 120 ]; do
  echo "Waiting for emulator to complete boot..."
  sleep 2
  n=$((n+1))
done

if [ "$(adb -s ${ADB_TARGET} shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; then
  echo "Emulator didn't boot in time"
  adb -s ${ADB_TARGET} logcat -d | sed -n '1,500p' > emulator-boot-logcat.txt || true
  exit 1
fi
echo "Emulator booted and ready"