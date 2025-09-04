"""Datetime tools: time calculation, formatting, timezone conversion. PEP8 compliant."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import holidays
import pytz
from dateutil.relativedelta import relativedelta
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from zhdate import ZhDate

from .base import ToolResult


class TimeUnit(str, Enum):
    """Time calculation units."""

    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"


class DateFormat(str, Enum):
    """Date output formats."""

    ISO_DATE = "iso_date"  # YYYY-MM-DD
    ISO_DATETIME = "iso_datetime"  # YYYY-MM-DD HH:MM:SS
    US_DATE = "us_date"  # MM/DD/YYYY
    EU_DATE = "eu_date"  # DD/MM/YYYY
    COMPACT = "compact"  # YYYYMMDD
    READABLE = "readable"  # March 15, 2024


class TimezoneConversionInput(BaseModel):
    datetime_string: str = Field(description="Datetime string to convert.")
    target_timezone: str = Field(description="Target timezone.")
    source_timezone: Optional[str] = Field(default=None, description="Source timezone (optional).")


class DateFormatInput(BaseModel):
    date_string: str = Field(description="Date string to format.")
    target_formats: Optional[List[DateFormat]] = Field(default=None, description="List of target formats.")


class AddTimeDeltaInput(BaseModel):
    base_datetime: str = Field(description="Base datetime string.")
    years: int = Field(default=0, description="Years to add/subtract.")
    months: int = Field(default=0, description="Months to add/subtract.")
    days: int = Field(default=0, description="Days to add/subtract.")
    hours: int = Field(default=0, description="Hours to add/subtract.")
    minutes: int = Field(default=0, description="Minutes to add/subtract.")
    seconds: int = Field(default=0, description="Seconds to add/subtract.")
    input_format: Optional[str] = Field(default=None, description="Input format (optional).")
    output_format: Optional[str] = Field(default=None, description="Output format (optional).")


class DateInfoInput(BaseModel):
    datetime: Optional[str] = Field(default=None, description="Datetime string (optional, None for now)")
    timezone: Optional[str] = Field(default="UTC", description="Timezone (default UTC)")
    countries_of_holidays_interested: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="List of dicts with 'country' (ISO 3166-1 alpha-2, e.g., 'US', 'CN') and optional 'subdivision' "
        "(ISO 3166-2, e.g., 'CA' for California, 'SH' for Shanghai) for holidays.",
    )
    days_window_for_holiday_info: Optional[Tuple[int, int]] = Field(
        default=None,
        description="Tuple of (before_days, after_days) to check for holidays. Defaults to (7, 7) if not specified.",
    )
    format_type: DateFormat = Field(default=DateFormat.ISO_DATETIME, description="Output format type")


def parse_datetime_string(
    date_string: str, input_format: Optional[str] = None
) -> Tuple[Optional[datetime], Optional[str]]:
    """Parse a datetime string using known formats or provided format. Returns (datetime, format) or (None, None)."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y%m%d",
        "%Y-%m-%d %H:%M:%S.%f",
    ]
    if input_format:
        try:
            return datetime.strptime(date_string, input_format), input_format
        except ValueError:
            return None, None
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt), fmt
        except ValueError:
            continue
    return None, None


def format_datetime_by_type(dt: datetime, format_type: DateFormat) -> str:
    """Format datetime according to format type."""
    if format_type == DateFormat.ISO_DATE:
        return dt.strftime("%Y-%m-%d")
    if format_type == DateFormat.ISO_DATETIME:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    if format_type == DateFormat.US_DATE:
        return dt.strftime("%m/%d/%Y")
    if format_type == DateFormat.EU_DATE:
        return dt.strftime("%d/%m/%Y")
    if format_type == DateFormat.COMPACT:
        return dt.strftime("%Y%m%d")
    if format_type == DateFormat.READABLE:
        return dt.strftime("%B %d, %Y")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@tool("local::datetime.add_time_delta", args_schema=AddTimeDeltaInput)
def add_time_delta(
    base_datetime: str,
    years: int = 0,
    months: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    input_format: Optional[str] = None,
    output_format: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add or subtract time periods to a base datetime string.

    Returns:
        Dictionary containing time delta calculation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'new_datetime': (string) The calculated datetime after delta operation
          - 'base_datetime': (string) Original input datetime string
          - 'delta': (dict) Applied time delta with keys: years, months, days, hours, minutes, seconds
          - 'input_format': (string) Format used to parse input datetime
          - 'output_format': (string) Format used for output datetime
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        dt, used_format = parse_datetime_string(base_datetime, input_format)
        if dt is None:
            return ToolResult.failure(f"Failed to parse base_datetime: {base_datetime}").model_dump()
        delta = relativedelta(
            years=years,
            months=months,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        new_dt = dt + delta
        fmt = output_format or used_format or "%Y-%m-%d %H:%M:%S"
        formatted = new_dt.strftime(fmt)
        return ToolResult.success(
            {
                "new_datetime": formatted,
                "base_datetime": base_datetime,
                "delta": {
                    "years": years,
                    "months": months,
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                },
                "input_format": used_format,
                "output_format": fmt,
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Time delta operation failed: {str(e)}").model_dump()


@tool("local::datetime.get_date_info", args_schema=DateInfoInput)
def get_date_info(
    datetime: Optional[str] = None,
    timezone: Optional[str] = "UTC",
    countries_of_holidays_interested: Optional[List[Dict[str, str]]] = None,
    days_window_for_holiday_info: Optional[Tuple[int, int]] = None,
    format_type: DateFormat = DateFormat.ISO_DATETIME,
) -> Dict[str, Any]:
    """
    Get date information for a datetime string, or current time if not provided.

    Returns:
        Dictionary containing date information:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'date': (string) Formatted datetime string
          - 'timezone': (string) Timezone information
          - 'timestamp': (float) Unix timestamp
          - 'iso_format': (string) ISO format datetime string
          - 'day_of_week': (string) Full day name (e.g., 'Monday')
          - 'weekday_number': (integer) Weekday number (0=Monday, 6=Sunday)
          - 'short_day_name': (string) Abbreviated day name (e.g., 'Mon')
          - 'is_weekend': (boolean) Whether it's Saturday or Sunday
          - 'format_used': (string) Format used to parse input or output
          - 'holidays': (list, optional) List of holidays if countries_of_holidays_interested provided
          - 'lunar_date': (string, optional) Lunar date if 'CN' is in countries_of_holidays_interested
        - 'error': (string, optional) Error message if operation failed

    Examples:
        # Example 1: Get current date info without countries (no holidays or lunar date)
        get_date_info()

        # Example 2: Get date info with countries, including US and CN with subdivision XJ
        get_date_info(
            countries_of_holidays_interested=[
                {'country': 'US'},
                {'country': 'CN', 'subdivision': 'XJ'}
            ],
            days_window_for_holiday_info=(3, 10)
        )
    """
    try:
        if datetime is None:
            tz = pytz.timezone(timezone) if timezone else pytz.UTC
            dt = __import__("datetime").datetime.now(tz)
            format_used = None
        else:
            dt, format_used = parse_datetime_string(datetime)
            if dt is None:
                return ToolResult.failure(f"Failed to parse datetime: {datetime}").model_dump()
            if timezone is not None:
                tz = pytz.timezone(str(timezone))
                if dt.tzinfo is None:
                    dt = tz.localize(dt)
                else:
                    dt = dt.astimezone(tz)
        formatted_time = format_datetime_by_type(dt, format_type)
        day_of_week = dt.strftime("%A")
        weekday_number = dt.weekday()
        short_day_name = dt.strftime("%a")
        is_weekend = weekday_number >= 5

        # Handle holidays and lunar date
        holidays_list = []
        lunar_date = None
        if countries_of_holidays_interested:
            window = days_window_for_holiday_info or (7, 7)
            before_days, after_days = window
            start_date = dt.date() - relativedelta(days=before_days)
            end_date = dt.date() + relativedelta(days=after_days)
            for country_info in countries_of_holidays_interested:
                country = country_info.get("country")
                subdivision = country_info.get("subdivision")
                if country:
                    if holidays is None:
                        continue
                    try:
                        if subdivision:
                            holiday_obj = holidays.country_holidays(country, subdiv=subdivision, years=dt.year)
                        else:
                            holiday_obj = holidays.country_holidays(country, years=dt.year)
                        for date, name in holiday_obj.items():
                            if start_date <= date <= end_date:
                                holidays_list.append(
                                    {
                                        "date": date.isoformat(),
                                        "name": name,
                                        "country": country,
                                        "subdivision": subdivision,
                                    }
                                )
                    except Exception:
                        # Skip invalid country/subdivision
                        continue
                if country == "CN":
                    try:
                        # ZhDate requires naive datetime
                        dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
                        lunar = ZhDate.from_datetime(dt_naive)
                        lunar_date = str(lunar)
                    except Exception:
                        lunar_date = None

        return ToolResult.success(
            {
                "date": formatted_time,
                "timezone": str(dt.tzinfo) if dt.tzinfo else (timezone or "naive"),
                "timestamp": dt.timestamp(),
                "iso_format": dt.isoformat(),
                "day_of_week": day_of_week,
                "weekday_number": weekday_number,
                "short_day_name": short_day_name,
                "is_weekend": is_weekend,
                "format_used": format_used or str(format_type.value),
                "holidays": holidays_list if holidays_list else None,
                "lunar_date": lunar_date,
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to get date info: {str(e)}").model_dump()


@tool("local::datetime.convert_timezone", args_schema=TimezoneConversionInput)
def convert_timezone(
    datetime_string: str,
    target_timezone: str,
    source_timezone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a datetime string from one timezone to another.

    Returns:
        Dictionary containing timezone conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'converted_datetime': (string) Datetime string in target timezone
          - 'original_datetime': (string) Original input datetime string
          - 'source_timezone': (string) Source timezone used
          - 'target_timezone': (string) Target timezone
          - 'time_difference': (float) Time difference in hours between timezones
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        dt, _ = parse_datetime_string(datetime_string)
        if dt is None:
            return ToolResult.failure(f"Could not parse datetime: {datetime_string}").model_dump()
        if source_timezone:
            source_tz = pytz.timezone(source_timezone)
            if dt.tzinfo is None:
                localized_dt = source_tz.localize(dt)
            else:
                localized_dt = dt.astimezone(source_tz)
        else:
            if dt.tzinfo is None:
                localized_dt = pytz.UTC.localize(dt)
                source_timezone = "UTC"
            else:
                localized_dt = dt
                source_timezone = str(dt.tzinfo)
        target_tz = pytz.timezone(target_timezone)
        converted_dt = localized_dt.astimezone(target_tz)
        source_offset = localized_dt.utcoffset()
        target_offset = converted_dt.utcoffset()
        time_difference = None
        if source_offset is not None and target_offset is not None:
            time_difference = (target_offset.total_seconds() - source_offset.total_seconds()) / 3600
        return ToolResult.success(
            {
                "converted_datetime": converted_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "original_datetime": datetime_string,
                "source_timezone": source_timezone,
                "target_timezone": target_timezone,
                "time_difference": time_difference,
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to convert timezone: {str(e)}").model_dump()


@tool("local::datetime.get_available_timezones")
def get_available_timezones() -> Dict[str, Any]:
    """
    Get list of all available timezone names supported by the system.

    Returns:
        Dictionary containing timezone information:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'timezones': (list) List of all available timezone names (e.g., 'UTC', 'America/New_York')
          - 'total_count': (integer) Total number of available timezones
          - 'common_timezones': (list) List of commonly used timezone names
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        all_timezones = pytz.all_timezones
        common_timezones = pytz.common_timezones
        return ToolResult.success(
            {
                "timezones": all_timezones,
                "total_count": len(all_timezones),
                "common_timezones": common_timezones,
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to get available timezones: {str(e)}").model_dump()
