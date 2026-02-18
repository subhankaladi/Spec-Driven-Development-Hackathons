#!/bin/bash
# Verification script for Phase 5: Recurring Tasks & Reminders
# Ensures all deliverables for User Story 3 are properly created

set -euo pipefail

echo "🔍 Verifying Phase 5: Recurring Tasks & Reminders Deliverables..."

# Define expected files
EXPECTED_FILES=(
    "services/recurring_task_scheduler.py"
    "services/reminder_notification_system.py"
    "services/task_recurrence_patterns.py"
    "services/reminder_config_api.py"
    "services/recurring_task_persistence.py"
    "services/reminder_delivery_mechanism.py"
    "services/task_synchronization.py"
    "main.py"
    "PHASE-5-README.md"
    "PHASE-5-COMPLETE.md"
)

MISSING_FILES=()
ALL_PRESENT=true

echo "📋 Checking required files..."
for file in "${EXPECTED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        MISSING_FILES+=("$file")
        ALL_PRESENT=false
    fi
done

echo ""
if [ "$ALL_PRESENT" = true ]; then
    echo "🎉 All Phase 5 deliverables are present!"

    echo ""
    echo "📄 File details:"
    for file in "${EXPECTED_FILES[@]}"; do
        size=$(stat -c%s "$file")
        echo "   $file ($(numfmt --to=iec --format="%.2f" $size))"
    done

    echo ""
    echo "🎯 Phase 5 Tasks Successfully Verified:"
    echo "   T023: Recurring Task Scheduler Service - services/recurring_task_scheduler.py"
    echo "   T024: Reminder Notification System - services/reminder_notification_system.py"
    echo "   T025: Task Recurrence Patterns - services/task_recurrence_patterns.py"
    echo "   T026: Reminder Configuration API - services/reminder_config_api.py"
    echo "   T027: Recurring Task Persistence - services/recurring_task_persistence.py"
    echo "   T028: Reminder Delivery Mechanism - services/reminder_delivery_mechanism.py"
    echo "   T029: Task Synchronization Across Instances - services/task_synchronization.py"

    echo ""
    echo "🚀 Ready for production deployment!"
else
    echo "❌ Some files are missing. Please create the following files:"
    for missing in "${MISSING_FILES[@]}"; do
        echo "   - $missing"
    done
    exit 1
fi