from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
import croniter
import pytz
from enum import Enum
from pydantic import BaseModel
import calendar

class RecurrencePatternType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"
    CRON = "cron"

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class MonthlyPatternType(str, Enum):
    FIXED_DAY = "fixed_day"
    WEEKDAY_OF_MONTH = "weekday_of_month"
    LAST_WEEKDAY = "last_weekday"

class YearlyPatternType(str, Enum):
    FIXED_DATE = "fixed_date"
    WEEKDAY_OF_MONTH = "weekday_of_month"

class RecurrenceRule(BaseModel):
    """
    Defines a recurrence rule similar to RFC 5545 RRULE

    Attributes:
        freq: Frequency of recurrence (DAILY, WEEKLY, MONTHLY, YEARLY)
        interval: Interval between occurrences (every n units)
        count: Number of occurrences to generate
        until: End date for recurrence
        bysecond: Seconds for time (0-59)
        byminute: Minutes for time (0-59)
        byhour: Hours for time (0-23)
        byday: Days of week (MO, TU, WE, TH, FR, SA, SU)
        bymonthday: Days of month (1-31)
        byyearday: Days of year (1-366)
        byweekno: Week numbers of year (1-53)
        bymonth: Months of year (1-12)
        bysetpos: Position within set (-1 for last, 1 for first, etc.)
        wkst: Week start day (default MO)
    """
    freq: RecurrencePatternType
    interval: int = 1
    count: Optional[int] = None
    until: Optional[datetime] = None
    bysecond: Optional[List[int]] = None
    byminute: Optional[List[int]] = None
    byhour: Optional[List[int]] = None
    byday: Optional[List[str]] = None  # MO, TU, WE, TH, FR, SA, SU
    bymonthday: Optional[List[int]] = None
    byyearday: Optional[List[int]] = None
    byweekno: Optional[List[int]] = None
    bymonth: Optional[List[int]] = None
    bysetpos: Optional[List[int]] = None
    wkst: str = "MO"

class AdvancedRecurrenceRule(BaseModel):
    """
    Advanced recurrence patterns with more complex scheduling options
    """
    pattern_type: RecurrencePatternType
    custom_cron_expression: Optional[str] = None  # For CUSTOM and CRON patterns
    daily_interval: Optional[int] = 1
    weekly_days: Optional[List[str]] = None  # Days of week for weekly patterns
    weekly_interval: Optional[int] = 1
    monthly_pattern: Optional[MonthlyPatternType] = None
    monthly_day: Optional[int] = None  # Day of month for FIXED_DAY
    monthly_weekday: Optional[str] = None  # Day of week for WEEKDAY_OF_MONTH
    monthly_week_number: Optional[int] = None  # Which week (1-5) for WEEKDAY_OF_MONTH
    yearly_pattern: Optional[YearlyPatternType] = None
    yearly_month: Optional[int] = None
    yearly_day: Optional[int] = None  # Day of month for FIXED_DATE
    yearly_weekday: Optional[str] = None  # Day of week for WEEKDAY_OF_MONTH
    yearly_week_number: Optional[int] = None  # Which week for WEEKDAY_OF_MONTH
    timezone: str = "UTC"

class RecurrencePatternCalculator:
    """
    Calculates occurrence dates based on various recurrence patterns
    """

    def __init__(self, timezone: str = "UTC"):
        self.timezone = pytz.timezone(timezone) if timezone else pytz.UTC

    def calculate_next_occurrence(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence based on the recurrence rule
        """
        if from_date is None:
            from_date = start_date

        # Adjust to timezone if needed
        if start_date.tzinfo is None:
            start_date = self.timezone.localize(start_date)

        if from_date.tzinfo is None:
            from_date = self.timezone.localize(from_date)

        if rule.freq == RecurrencePatternType.DAILY:
            return self._calculate_daily_next(start_date, rule, from_date)
        elif rule.freq == RecurrencePatternType.WEEKLY:
            return self._calculate_weekly_next(start_date, rule, from_date)
        elif rule.freq == RecurrencePatternType.MONTHLY:
            return self._calculate_monthly_next(start_date, rule, from_date)
        elif rule.freq == RecurrencePatternType.YEARLY:
            return self._calculate_yearly_next(start_date, rule, from_date)
        elif rule.freq == RecurrencePatternType.CRON:
            return self._calculate_cron_next(start_date, rule, from_date)
        elif rule.freq == RecurrencePatternType.CUSTOM:
            return self._calculate_custom_next(start_date, rule, from_date)

        return None

    def calculate_occurrences(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        max_count: int = 100
    ) -> List[datetime]:
        """
        Calculate multiple occurrences based on the recurrence rule
        """
        occurrences = []
        current_date = start_date

        count = 0
        while count < max_count:
            if rule.count and len(occurrences) >= rule.count:
                break

            if rule.until and current_date > rule.until:
                break

            next_occurrence = self.calculate_next_occurrence(start_date, rule, current_date)

            if next_occurrence is None or (rule.until and next_occurrence > rule.until):
                break

            occurrences.append(next_occurrence)
            current_date = next_occurrence
            count += 1

        return occurrences

    def _calculate_daily_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next daily occurrence"""
        # Use the interval to determine the next occurrence
        next_date = from_date + timedelta(days=rule.interval)

        # Apply time constraints if specified
        if rule.byhour:
            next_date = next_date.replace(hour=min(rule.byhour))
        if rule.byminute:
            next_date = next_date.replace(minute=min(rule.byminute))
        if rule.bysecond:
            next_date = next_date.replace(second=min(rule.bysecond))

        return next_date

    def _calculate_weekly_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next weekly occurrence"""
        if not rule.byday:
            # If no specific days specified, repeat on the same weekday as start
            target_weekday = start_date.weekday()
            current_weekday = from_date.weekday()

            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # Target day has passed this week
                days_ahead += 7 * rule.interval

            next_date = from_date + timedelta(days=days_ahead)
        else:
            # Find next occurrence among specified days
            weekdays_map = {
                'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3,
                'FR': 4, 'SA': 5, 'SU': 6
            }

            target_weekdays = [weekdays_map[day] for day in rule.byday if day in weekdays_map]
            current_weekday = from_date.weekday()

            # Find the next occurrence
            next_date = None
            for weekday in sorted(target_weekdays):
                days_diff = (weekday - current_weekday) % 7
                if days_diff == 0 and from_date.time() >= start_date.time():
                    # Same day but time has passed, move to next week
                    days_diff = 7

                candidate_date = from_date + timedelta(days=days_diff)

                if next_date is None or candidate_date < next_date:
                    next_date = candidate_date

        # Apply time constraints if specified
        if rule.byhour:
            next_date = next_date.replace(hour=min(rule.byhour))
        if rule.byminute:
            next_date = next_date.replace(minute=min(rule.byminute))
        if rule.bysecond:
            next_date = next_date.replace(second=min(rule.bysecond))

        return next_date

    def _calculate_monthly_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next monthly occurrence"""
        if rule.bymonthday:
            # Occur on specific day(s) of the month
            target_days = sorted(rule.bymonthday)
            current_day = from_date.day

            # Find next occurrence in current month
            for day in target_days:
                if day > current_day:
                    try:
                        next_date = from_date.replace(day=day)
                        break
                    except ValueError:
                        # Day doesn't exist in this month (e.g., Feb 30), continue to next month
                        continue
            else:
                # No suitable day in current month, go to next month
                if from_date.month == 12:
                    next_month = 1
                    next_year = from_date.year + 1
                else:
                    next_month = from_date.month + 1
                    next_year = from_date.year

                # Find first suitable day in next month
                for day in target_days:
                    try:
                        next_date = from_date.replace(year=next_year, month=next_month, day=day)
                        break
                    except ValueError:
                        continue
                else:
                    # No suitable day found, skip to next month
                    next_month = next_month + rule.interval
                    while next_month > 12:
                        next_month -= 12
                        next_year += 1

                    for day in target_days:
                        try:
                            next_date = from_date.replace(year=next_year, month=next_month, day=day)
                            break
                        except ValueError:
                            continue
        else:
            # Occur on same day as start date
            target_day = start_date.day
            current_month = from_date.month
            current_year = from_date.year

            # Try same month first
            try:
                next_date = from_date.replace(day=target_day)
                if next_date <= from_date:
                    # If the day has passed, go to next interval
                    next_month = current_month + rule.interval
                    while next_month > 12:
                        next_month -= 12
                        current_year += 1
                    next_date = from_date.replace(year=current_year, month=next_month, day=target_day)
            except ValueError:
                # Day doesn't exist in this month (e.g., Feb 30), go to next month
                next_month = current_month + rule.interval
                while next_month > 12:
                    next_month -= 12
                    current_year += 1
                # Find the last day of the month
                last_day = calendar.monthrange(current_year, next_month)[1]
                next_date = from_date.replace(year=current_year, month=next_month, day=last_day)

        # Apply time constraints if specified
        if rule.byhour:
            next_date = next_date.replace(hour=min(rule.byhour))
        if rule.byminute:
            next_date = next_date.replace(minute=min(rule.byminute))
        if rule.bysecond:
            next_date = next_date.replace(second=min(rule.bysecond))

        return next_date

    def _calculate_yearly_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next yearly occurrence"""
        if rule.bymonth and rule.bymonthday:
            # Occur on specific month and day
            target_month = rule.bymonth[0]  # Take first specified month
            target_day = rule.bymonthday[0]  # Take first specified day

            if from_date.month > target_month or (
                from_date.month == target_month and from_date.day >= start_date.day
            ):
                # Need to go to next year
                target_year = from_date.year + rule.interval
            else:
                target_year = from_date.year

            try:
                next_date = from_date.replace(year=target_year, month=target_month, day=target_day)
            except ValueError:
                # Day doesn't exist (e.g., Feb 29 on non-leap year)
                # Use last day of month instead
                last_day = calendar.monthrange(target_year, target_month)[1]
                next_date = from_date.replace(year=target_year, month=target_month, day=last_day)
        else:
            # Occur on same month/day as start date
            target_month = start_date.month
            target_day = start_date.day

            if (from_date.month > target_month or
                (from_date.month == target_month and from_date.day >= start_date.day)):
                # Need to go to next year
                target_year = from_date.year + rule.interval
            else:
                target_year = from_date.year

            try:
                next_date = from_date.replace(year=target_year, month=target_month, day=target_day)
            except ValueError:
                # Day doesn't exist (e.g., Feb 29 on non-leap year)
                last_day = calendar.monthrange(target_year, target_month)[1]
                next_date = from_date.replace(year=target_year, month=target_month, day=last_day)

        # Apply time constraints if specified
        if rule.byhour:
            next_date = next_date.replace(hour=min(rule.byhour))
        if rule.byminute:
            next_date = next_date.replace(minute=min(rule.byminute))
        if rule.bysecond:
            next_date = next_date.replace(second=min(rule.bysecond))

        return next_date

    def _calculate_cron_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next occurrence using cron expression"""
        # This would typically use croniter library
        # For now, we'll simulate it with a placeholder
        if hasattr(rule, 'custom_cron'):
            try:
                cron_iter = croniter.croniter(rule.custom_cron, from_date)
                next_date = cron_iter.get_next(datetime)
                return next_date
            except:
                # Fallback to daily if cron is invalid
                return from_date + timedelta(days=rule.interval)
        else:
            # Fallback to daily interval
            return from_date + timedelta(days=rule.interval)

    def _calculate_custom_next(
        self,
        start_date: datetime,
        rule: RecurrenceRule,
        from_date: datetime
    ) -> Optional[datetime]:
        """Calculate next occurrence for custom patterns"""
        # For custom patterns, we'll use interval-based calculation
        # In a real implementation, this would support more complex custom logic
        return from_date + timedelta(days=rule.interval)

class AdvancedRecurrenceCalculator:
    """
    Advanced calculator for complex recurrence patterns
    """

    def __init__(self, timezone: str = "UTC"):
        self.timezone = pytz.timezone(timezone) if timezone else pytz.UTC

    def calculate_advanced_occurrence(
        self,
        start_date: datetime,
        advanced_rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """
        Calculate occurrences based on advanced recurrence rules
        """
        if advanced_rule.pattern_type == RecurrencePatternType.CUSTOM and advanced_rule.custom_cron_expression:
            return self._calculate_cron_occurrences(start_date, advanced_rule)
        elif advanced_rule.pattern_type == RecurrencePatternType.DAILY:
            return self._calculate_daily_occurrences(start_date, advanced_rule)
        elif advanced_rule.pattern_type == RecurrencePatternType.WEEKLY:
            return self._calculate_weekly_occurrences(start_date, advanced_rule)
        elif advanced_rule.pattern_type == RecurrencePatternType.MONTHLY:
            return self._calculate_monthly_occurrences(start_date, advanced_rule)
        elif advanced_rule.pattern_type == RecurrencePatternType.YEARLY:
            return self._calculate_yearly_occurrences(start_date, advanced_rule)

        return []

    def _calculate_cron_occurrences(
        self,
        start_date: datetime,
        rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """Calculate occurrences using cron expression"""
        if not rule.custom_cron_expression:
            return []

        try:
            cron_iter = croniter.croniter(rule.custom_cron_expression, start_date)
            occurrences = []

            # Generate next 10 occurrences as example
            for _ in range(10):
                next_date = cron_iter.get_next(datetime)
                occurrences.append(next_date)

            return occurrences
        except:
            return []

    def _calculate_daily_occurrences(
        self,
        start_date: datetime,
        rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """Calculate daily occurrences"""
        occurrences = []
        current_date = start_date

        # Generate next 10 occurrences
        for i in range(10):
            occurrences.append(current_date)
            current_date += timedelta(days=rule.daily_interval or 1)

        return occurrences

    def _calculate_weekly_occurrences(
        self,
        start_date: datetime,
        rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """Calculate weekly occurrences"""
        occurrences = []
        current_date = start_date

        # Map day names to numbers
        day_mapping = {
            'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3,
            'FR': 4, 'SA': 5, 'SU': 6,
            'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3,
            'FRI': 4, 'SAT': 5, 'SUN': 6
        }

        if rule.weekly_days:
            target_days = [day_mapping[day.upper()] for day in rule.weekly_days if day.upper() in day_mapping]
        else:
            target_days = [start_date.weekday()]

        count = 0
        while count < 10:  # Generate up to 10 occurrences
            current_weekday = current_date.weekday()

            # Find next occurrence among target days
            next_date = None
            for day in sorted(target_days):
                days_diff = (day - current_weekday) % 7
                if days_diff == 0 and current_date.time() >= start_date.time():
                    # Same day but time has passed, move to next week
                    days_diff = 7

                candidate_date = current_date + timedelta(days=days_diff)

                if next_date is None or candidate_date < next_date:
                    next_date = candidate_date

            if next_date:
                occurrences.append(next_date)
                count += 1
                current_date = next_date + timedelta(weeks=rule.weekly_interval or 1)
            else:
                break

        return occurrences

    def _calculate_monthly_occurrences(
        self,
        start_date: datetime,
        rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """Calculate monthly occurrences"""
        occurrences = []
        current_date = start_date

        if rule.monthly_pattern == MonthlyPatternType.FIXED_DAY:
            # Occur on fixed day of each month
            target_day = rule.monthly_day or start_date.day

            for i in range(10):
                try:
                    occurrence = current_date.replace(day=target_day)
                    occurrences.append(occurrence)

                    # Move to next month
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                except ValueError:
                    # Day doesn't exist in this month (e.g., Feb 31)
                    # Use last day of month instead
                    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                    occurrence = current_date.replace(day=last_day)
                    occurrences.append(occurrence)

                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)

        elif rule.monthly_pattern == MonthlyPatternType.WEEKDAY_OF_MONTH:
            # Occur on specific weekday of specific week of month
            target_weekday = self._get_weekday_number(rule.monthly_weekday or start_date.strftime('%a').upper())
            week_number = rule.monthly_week_number or 1

            for i in range(10):
                occurrence = self._nth_weekday_of_month(
                    current_date.year, current_date.month, week_number, target_weekday
                )
                occurrences.append(occurrence)

                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

        elif rule.monthly_pattern == MonthlyPatternType.LAST_WEEKDAY:
            # Occur on last occurrence of specific weekday in month
            target_weekday = self._get_weekday_number(rule.monthly_weekday or start_date.strftime('%a').upper())

            for i in range(10):
                occurrence = self._last_weekday_of_month(
                    current_date.year, current_date.month, target_weekday
                )
                occurrences.append(occurrence)

                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

        else:
            # Default: same day as start date
            target_day = start_date.day

            for i in range(10):
                try:
                    occurrence = current_date.replace(day=target_day)
                    occurrences.append(occurrence)

                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                except ValueError:
                    # Day doesn't exist, use last day of month
                    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                    occurrence = current_date.replace(day=last_day)
                    occurrences.append(occurrence)

                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)

        return occurrences

    def _calculate_yearly_occurrences(
        self,
        start_date: datetime,
        rule: AdvancedRecurrenceRule
    ) -> List[datetime]:
        """Calculate yearly occurrences"""
        occurrences = []
        current_date = start_date

        if rule.yearly_pattern == YearlyPatternType.FIXED_DATE:
            # Occur on fixed month and day each year
            target_month = rule.yearly_month or start_date.month
            target_day = rule.yearly_day or start_date.day

            for i in range(10):
                try:
                    occurrence = current_date.replace(month=target_month, day=target_day)
                    occurrences.append(occurrence)

                    current_date = current_date.replace(year=current_date.year + 1)
                except ValueError:
                    # Day doesn't exist (e.g., Feb 29 on non-leap year)
                    last_day = calendar.monthrange(current_date.year, target_month)[1]
                    occurrence = current_date.replace(month=target_month, day=last_day)
                    occurrences.append(occurrence)

                    current_date = current_date.replace(year=current_date.year + 1)

        elif rule.yearly_pattern == YearlyPatternType.WEEKDAY_OF_MONTH:
            # Occur on specific weekday of specific week of specific month each year
            target_month = rule.yearly_month or start_date.month
            target_weekday = self._get_weekday_number(rule.yearly_weekday or start_date.strftime('%a').upper())
            week_number = rule.yearly_week_number or 1

            for i in range(10):
                occurrence = self._nth_weekday_of_month(
                    current_date.year, target_month, week_number, target_weekday
                )
                occurrences.append(occurrence)

                current_date = current_date.replace(year=current_date.year + 1)

        else:
            # Default: same date each year
            for i in range(10):
                try:
                    occurrence = current_date.replace(
                        month=start_date.month,
                        day=start_date.day
                    )
                    occurrences.append(occurrence)

                    current_date = current_date.replace(year=current_date.year + 1)
                except ValueError:
                    # Day doesn't exist (Feb 29 on non-leap year)
                    last_day = calendar.monthrange(current_date.year, start_date.month)[1]
                    occurrence = current_date.replace(
                        month=start_date.month,
                        day=last_day
                    )
                    occurrences.append(occurrence)

                    current_date = current_date.replace(year=current_date.year + 1)

        return occurrences

    def _get_weekday_number(self, weekday_str: str) -> int:
        """Convert weekday string to number (0=Monday, 6=Sunday)"""
        mapping = {
            'MO': 0, 'MON': 0, 'MONDAY': 0,
            'TU': 1, 'TUE': 1, 'TUESDAY': 1,
            'WE': 2, 'WED': 2, 'WEDNESDAY': 2,
            'TH': 3, 'THU': 3, 'THURSDAY': 3,
            'FR': 4, 'FRI': 4, 'FRIDAY': 4,
            'SA': 5, 'SAT': 5, 'SATURDAY': 5,
            'SU': 6, 'SUN': 6, 'SUNDAY': 6
        }
        return mapping.get(weekday_str.upper(), 0)

    def _nth_weekday_of_month(self, year: int, month: int, n: int, weekday: int) -> datetime:
        """Get the nth occurrence of a weekday in a month."""
        import calendar
        cal = calendar.monthcalendar(year, month)

        occurrence_count = 0
        for week in cal:
            if week[weekday] != 0:  # 0 means the day is in the previous/next month
                occurrence_count += 1
                if occurrence_count == n:
                    return datetime(year, month, week[weekday])

        # If nth occurrence doesn't exist, return the last occurrence of that weekday
        for week in reversed(cal):
            if week[weekday] != 0:
                return datetime(year, month, week[weekday])

        raise ValueError(f"Could not find {n}th {weekday} of {month}/{year}")

    def _last_weekday_of_month(self, year: int, month: int, weekday: int) -> datetime:
        """Get the last occurrence of a weekday in a month."""
        import calendar
        cal = calendar.monthcalendar(year, month)

        # Look for the weekday in reverse order
        for week in reversed(cal):
            if week[weekday] != 0:  # 0 means the day is in the previous/next month
                return datetime(year, month, week[weekday])

        raise ValueError(f"Could not find last {weekday} of {month}/{year}")

# Example usage and testing
if __name__ == "__main__":
    # Example: Create a daily recurring task
    calc = RecurrencePatternCalculator()

    start_date = datetime(2023, 1, 1, 9, 0)  # Jan 1, 2023 at 9 AM

    # Daily every 2 days
    daily_rule = RecurrenceRule(freq=RecurrencePatternType.DAILY, interval=2)
    daily_occurrences = calc.calculate_occurrences(start_date, daily_rule, 5)
    print("Daily occurrences:", daily_occurrences)

    # Weekly on Mondays and Wednesdays
    weekly_rule = RecurrenceRule(
        freq=RecurrencePatternType.WEEKLY,
        interval=1,
        byday=['MO', 'WE']
    )
    weekly_occurrences = calc.calculate_occurrences(start_date, weekly_rule, 5)
    print("Weekly occurrences:", weekly_occurrences)

    # Monthly on the 15th
    monthly_rule = RecurrenceRule(
        freq=RecurrencePatternType.MONTHLY,
        interval=1,
        bymonthday=[15]
    )
    monthly_occurrences = calc.calculate_occurrences(start_date, monthly_rule, 5)
    print("Monthly occurrences:", monthly_occurrences)

    # Advanced calculator example
    advanced_calc = AdvancedRecurrenceCalculator()

    # Monthly on the first Monday
    advanced_rule = AdvancedRecurrenceRule(
        pattern_type=RecurrencePatternType.MONTHLY,
        monthly_pattern=MonthlyPatternType.WEEKDAY_OF_MONTH,
        monthly_weekday="MO",
        monthly_week_number=1
    )
    advanced_occurrences = advanced_calc.calculate_advanced_occurrence(start_date, advanced_rule)
    print("Advanced monthly occurrences:", advanced_occurrences)