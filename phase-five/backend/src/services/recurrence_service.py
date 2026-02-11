"""Recurrence service for calculating next task occurrences.

Handles all recurrence logic including daily, weekly, monthly frequencies
and respects end dates.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RecurrenceService:
    """Service for calculating task recurrence."""

    @staticmethod
    def calculate_next_occurrence(
        recurrence_rule: Dict[str, Any],
        current_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Calculate next task occurrence based on recurrence rule.

        Args:
            recurrence_rule: Dict with 'frequency' and optional 'end_date'
                           Format: {'frequency': 'daily|weekly|monthly', 'end_date': 'YYYY-MM-DD'}
            current_date: Reference date (defaults to now)

        Returns:
            Next occurrence datetime or None if recurrence ended or invalid
        """
        if not recurrence_rule or "frequency" not in recurrence_rule:
            logger.debug("No recurrence rule provided")
            return None

        current_date = current_date or datetime.utcnow()
        frequency = recurrence_rule.get("frequency", "").lower()
        end_date_str = recurrence_rule.get("end_date")

        # Calculate next occurrence
        try:
            if frequency == "daily":
                next_occurrence = current_date + timedelta(days=1)
            elif frequency == "weekly":
                next_occurrence = current_date + timedelta(weeks=1)
            elif frequency == "monthly":
                next_occurrence = RecurrenceService._add_months(current_date, 1)
            else:
                logger.warning(f"Unknown recurrence frequency: {frequency}")
                return None

            # Check end date constraint
            if end_date_str:
                try:
                    # Parse end_date (could be ISO format or just date)
                    if "T" in end_date_str:
                        end_date = datetime.fromisoformat(end_date_str)
                    else:
                        end_date = datetime.fromisoformat(f"{end_date_str}T23:59:59")

                    if next_occurrence > end_date:
                        logger.info(f"Next occurrence {next_occurrence} exceeds end date {end_date}")
                        return None

                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing end_date '{end_date_str}': {e}")
                    return None

            logger.debug(f"Calculated next occurrence: {next_occurrence} (frequency: {frequency})")
            return next_occurrence

        except Exception as e:
            logger.error(f"Error calculating next occurrence: {e}", exc_info=True)
            return None

    @staticmethod
    def _add_months(date: datetime, months: int) -> datetime:
        """Add months to a datetime, handling edge cases like Feb 31st.

        Args:
            date: Starting date
            months: Number of months to add (can be negative)

        Returns:
            New datetime with months added
        """
        month = date.month + months
        year = date.year

        # Handle year overflow/underflow
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1

        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(date.day, max_day)

        return date.replace(year=year, month=month, day=day)

    @staticmethod
    def is_recurring(recurrence_rule: Optional[Dict[str, Any]]) -> bool:
        """Check if recurrence rule is valid and non-empty."""
        return bool(recurrence_rule and recurrence_rule.get("frequency"))

    @staticmethod
    def validate_recurrence_rule(recurrence_rule: Dict[str, Any]) -> tuple[bool, str]:
        """Validate recurrence rule format.

        Args:
            recurrence_rule: Rule to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not recurrence_rule:
            return True, ""  # None/empty is valid

        frequency = recurrence_rule.get("frequency", "").lower()

        if frequency not in ["daily", "weekly", "monthly"]:
            return False, f"Invalid frequency: {frequency}. Must be daily, weekly, or monthly."

        end_date_str = recurrence_rule.get("end_date")
        if end_date_str:
            try:
                if "T" in end_date_str:
                    datetime.fromisoformat(end_date_str)
                else:
                    datetime.fromisoformat(f"{end_date_str}T00:00:00")
            except (ValueError, TypeError):
                return False, f"Invalid end_date format: {end_date_str}. Use ISO format (YYYY-MM-DD or ISO-8601)."

        return True, ""


# Module-level functions for convenience
def calculate_next_occurrence(
    recurrence_rule: Dict[str, Any],
    current_date: Optional[datetime] = None
) -> Optional[datetime]:
    """Module-level function for calculating next occurrence."""
    return RecurrenceService.calculate_next_occurrence(recurrence_rule, current_date)


def is_recurring(recurrence_rule: Optional[Dict[str, Any]]) -> bool:
    """Module-level function to check if recurring."""
    return RecurrenceService.is_recurring(recurrence_rule)


def validate_recurrence_rule(recurrence_rule: Dict[str, Any]) -> tuple[bool, str]:
    """Module-level function for validation."""
    return RecurrenceService.validate_recurrence_rule(recurrence_rule)
