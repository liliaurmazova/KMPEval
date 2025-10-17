#!/bin/bash
# Usage: install-and-verify.sh <adb_target> <apk_path> <app_package> <app_activity>
set -euo pipefail

ADB_TARGET=${1:-localhost:5555}
APK_PATH=${2:?apk path required}
APP_PACKAGE=${3:?app package required}
APP_ACTIVITY=${4:?app activity required}

echo "Installing ${APK_PATH} to ${ADB_TARGET}..."
adb -s ${ADB_TARGET} install -r "${APK_PATH}"

echo "Starting ${APP_PACKAGE}/${APP_ACTIVITY}..."
adb -s ${ADB_TARGET} shell am start -W -n ${APP_PACKAGE}/${APP_ACTIVITY} | tee am-start-output.txt || true

sleep 2

FOREGROUND=$(adb -s ${ADB_TARGET} shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp' || true)
echo "Foreground window: $FOREGROUND"

PID=$(adb -s ${ADB_TARGET} shell pidof ${APP_PACKAGE} || echo "")
echo "PID: $PID"

adb -s ${ADB_TARGET} logcat -d > logcat-after-start.txt || true

if [ -n "$PID" ]; then
  echo "App started (pid $PID). SUCCESS."
  exit 0
fi

if echo "$FOREGROUND" | grep -q "${APP_PACKAGE}"; then
  echo "App is in foreground. SUCCESS."
  exit 0
fi

echo "App did not start or did not come to foreground. Check logcat-after-start.txt"
exit 1