"""Datetime tools: time calculation, formatting, timezone conversion. PEP8 compliant."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import convertdate
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
    datetime_string: str = Field(description="Datetime to convert, in ISO format")
    source_timezone: str = Field(description="Source timezone.")
    target_timezone: str = Field(description="Target timezone.")


class AddTimeDeltaInput(BaseModel):
    base_datetime: str = Field(description="Base datetime, in ISO format")
    years: int = Field(default=0, description="Years to add/subtract.")
    months: int = Field(default=0, description="Months to add/subtract.")
    days: int = Field(default=0, description="Days to add/subtract.")
    hours: int = Field(default=0, description="Hours to add/subtract.")
    minutes: int = Field(default=0, description="Minutes to add/subtract.")
    seconds: int = Field(default=0, description="Seconds to add/subtract.")
    input_format: Optional[str] = Field(default=None, description="Input format (optional).")
    output_format: Optional[str] = Field(default=None, description="Output format (optional).")


class DateInfoInput(BaseModel):
    datetime_str: Optional[str] = Field(default=None, description="Date/time in ISO format (optional, None for now)")
    timezone: Optional[str] = Field(
        default="UTC",
        description="Timezone for parsing datetime_str or current time."
        "Uses IANA names (e.g., 'UTC', 'US/Eastern', 'Asia/Shanghai').",
    )


class HolidayInfoInput(BaseModel):
    start_date: str = Field(description="Start date (inclusive), in ISO format.")
    end_date: str = Field(description="End date (inclusive), in ISO format.")
    countries: List[str] = Field(description="List of countries (ISO 3166-1 alpha-2, e.g., 'US', 'CN') for holidays.")
    include_subdivisions: bool = Field(
        default=False,
        description="Whether to include subdivisions (like states/provinces) if available.",
    )


class DateDiffInput(BaseModel):
    start_datetime: str = Field(description="Start date/time, in ISO format.")
    end_datetime: str = Field(description="End date/time, in ISO format.")


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


# --- 伊斯兰历格式化函数 ---
def format_islamic_date(date_tuple: Tuple[int, int, int]) -> str:
    """
    Formats a 3-tuple (year, month, day) from convertdate.islamic into a human-readable Islamic/Hijri date string.

    Args:
        date_tuple: A tuple containing (year, month_number, day).

    Returns:
        A formatted string, e.g., "1446 Safar 18".
    """
    try:
        year, month_num, day = date_tuple
        # 月份列表是0-indexed, 月份数字是1-indexed
        month_name = convertdate.islamic.MONTHS[month_num - 1]
        return f"{year} {month_name} {day}"
    except (IndexError, TypeError, ValueError):
        # 如果元组格式错误或月份数字无效，则返回原始表示
        return str(date_tuple)


# --- 希伯来历格式化函数 ---
def format_hebrew_date(date_tuple: Tuple[int, int, int]) -> str:
    """
    Formats a 3-tuple (year, month, day) from convertdate.hebrew into a human-readable Hebrew date string.

    Args:
        date_tuple: A tuple containing (year, month_number, day).

    Returns:
        A formatted string, e.g., "5785 Tishrei 18".
    """
    try:
        year, month_num, day = date_tuple
        month_name = convertdate.hebrew.MONTHS[month_num - 1]
        return f"{year} {month_name} {day}"
    except (IndexError, TypeError, ValueError):
        return str(date_tuple)


# --- 波斯历格式化函数 ---
def format_persian_date(date_tuple: Tuple[int, int, int]) -> str:
    """
    Formats a 3-tuple (year, month, day) from convertdate.persian into a human-readable Persian date string.

    Args:
        date_tuple: A tuple containing (year, month_number, day).

    Returns:
        A formatted string, e.g., "1403 Shahrivar 31".
    """
    try:
        year, month_num, day = date_tuple
        month_name = convertdate.persian.MONTHS[month_num - 1]
        return f"{year} {month_name} {day}"
    except (IndexError, TypeError, ValueError):
        return str(date_tuple)


@tool("add_time_delta", args_schema=AddTimeDeltaInput)
def add_time_delta(
    base_datetime: str,
    years: int = 0,
    months: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> Dict[str, Any]:
    """
    Use it to add or subtract time periods to a base datetime.

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
        dt, _ = parse_datetime_string(base_datetime)
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

        return ToolResult.success(
            {
                "new_datetime": new_dt.isoformat(),
                "base_datetime": dt.isoformat(),
                "delta": {
                    "years": years,
                    "months": months,
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                },
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Time delta operation failed: {str(e)}").model_dump()


@tool(name_or_callable="get_date_info", args_schema=DateInfoInput)
def get_date_info(
    datetime_str: Optional[str] = None,
    timezone: Optional[str] = "UTC",
) -> Dict[str, Any]:
    """
    Use it to get basic information about current or a specific date/time.
    - Get current time by specifying parameter datetime_str to None.
    - Get day of week, weekday number, short day name, is_weekend.
    - Get the date in other calendars
      - Chinese Lunar date (农历).
      - Hebrew date (לוח עברי).
      - Islamic date (التقويم الهجري).
      - Persian date (تقویم جلالی).
      - Julian date (JD).

    If the user doesn't provide a date, this tool will use the current time in the specified timezone.
    If the user doesn't provide a timezone, this tool will use UTC as the timezone.
    When parsing a datetime string, if it's timezone-naive, it will be interpreted in the specified timezone.
    If it's timezone-aware, it will be converted to the specified timezone.

    Returns:
        Dictionary containing date information:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'datetime': (string) datetime in ISO format
          - 'timestamp': (float) Unix timestamp
          - 'timezone': (string, optional) Timezone
          - 'datetime_utc': (string) datetime in UTC in ISO format
          - 'day_of_week': (string) Full day name (e.g., 'Monday')
          - 'weekday_number': (integer) Weekday number (0=Monday, 6=Sunday)
          - 'short_day_name': (string) Abbreviated day name (e.g., 'Mon')
          - 'is_weekend': (boolean) Whether it's Saturday or Sunday
          - 'format_used': (string) Format used to parse input
          - 'chinese_lunar_date': (string, optional) Chinese Lunar date
          - 'hebrew_date': (string, optional) Hebrew date
          - 'islamic_date': (string, optional) Islamic date
          - 'persian_date': (string, optional) Persian date
        - 'error': (string, optional) Error message if operation failed

    Examples:
        # User asks: "What day is it today in New York?"
        # LLM calls: get_date_info(datetime_str=None, timezone="America/New_York")

        # User asks: "What is the lunar date for 2025-01-01 in Beijing time?"
        # LLM calls: get_date_info(datetime_str="2025-01-01", timezone="Asia/Shanghai")
    """
    try:
        # Parse and validate timezone
        tz_name = timezone or "UTC"
        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            return ToolResult.failure(f"Unknown timezone: {tz_name}").model_dump()

        if datetime_str is None:
            # Get current time in specified timezone
            dt = datetime.now(tz)
            format_used = None
        else:
            # Parse the datetime string
            t, format_used = parse_datetime_string(datetime_str)
            if t is None:
                return ToolResult.failure(f"Failed to parse datetime: {datetime_str}").model_dump()

            # If parsed datetime is naive, localize it to the specified timezone
            if t.tzinfo is None:
                dt = tz.localize(t)
            else:
                # If parsed datetime is timezone-aware, convert to specified timezone
                dt = t.astimezone(tz)
        day_of_week = dt.strftime("%A")
        weekday_number = dt.weekday()
        short_day_name = dt.strftime("%a")
        is_weekend = weekday_number >= 5
        try:
            # ZhDate requires naive datetime
            dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
            lunar = ZhDate.from_datetime(dt_naive)
            chinese_lunar_date = str(lunar)
        except Exception:
            chinese_lunar_date = None

        return ToolResult.success(
            {
                "datetime": dt.isoformat(),
                "timestamp": dt.timestamp(),
                "timezone": tz.zone,
                "datetime_utc": dt.astimezone(pytz.utc).isoformat(),
                "day_of_week": day_of_week,
                "weekday_number": weekday_number,
                "short_day_name": short_day_name,
                "is_weekend": is_weekend,
                "format_used": format_used,
                "chinese_lunar_date": chinese_lunar_date,
                "hebrew_date": format_hebrew_date(convertdate.hebrew.from_gregorian(dt.year, dt.month, dt.day)),
                "islamic_date": format_islamic_date(convertdate.islamic.from_gregorian(dt.year, dt.month, dt.day)),
                "persian_date": format_persian_date(convertdate.persian.from_gregorian(dt.year, dt.month, dt.day)),
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to get date info: {str(e)}").model_dump()


@tool(name_or_callable="get_holiday_info", args_schema=HolidayInfoInput)
def get_holiday_info(
    start_date: str,
    end_date: str,
    countries: List[str],
    include_subdivisions: bool = False,
) -> Dict[str, Any]:
    """
    Use it to query holidays between start_date and end_date (inclusive) for one or more countries.

    Set parameter include_subdivisions to True to include holidays of subdivisions (like states/provinces) if available.

    Returns:
        Dictionary containing holiday information:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'holidays': (list) List of holidays within the range. Each item contains:
              - 'date': (string) Holiday date in ISO format
              - 'name': (string) Holiday name
              - 'country': (string) Country code (ISO 3166-1 alpha-2)
              - 'subdivision': (string, optional) Subdivision if regional level (ISO 3166-2 code, e.g., 'US-CA')
              - 'level': (string, optional) national level or regional level holiday
          - 'start_date': (string) Start date in ISO format
          - 'end_date': (string) End date in ISO format
        - 'error': (string, optional) Error message if operation failed

    Examples:
        # User asks: "What holidays are in US and CN from 2025-01-01 to 2025-01-10?"
        # LLM calls: get_holiday_info(start_date="2025-01-01", end_date="2025-01-10", countries=["US", "CN"])
    """
    try:
        start_dt, _ = parse_datetime_string(start_date)
        end_dt, _ = parse_datetime_string(end_date)
        if start_dt is None or end_dt is None:
            return ToolResult.failure(f"Failed to parse start_date or end_date: {start_date}, {end_date}").model_dump()

        years = list(range(start_dt.year, end_dt.year + 1))

        holidays_list = []
        for country_code in countries:
            if not country_code:
                continue

            try:
                national_holidays = holidays.country_holidays(country_code, years=years)
                for date, name in national_holidays.items():
                    if start_dt.date() <= date <= end_dt.date():
                        holidays_list.append(
                            {
                                "date": date.isoformat(),
                                "name": name,
                                "country": country_code,
                                "subdivision": None,
                                "level": "national",
                            }
                        )

                if include_subdivisions:
                    all_subdivisions = holidays.list_supported_countries().get(country_code, [])
                    for subdivision in all_subdivisions:
                        subdiv_holidays = holidays.country_holidays(country_code, subdiv=subdivision, years=years)
                        for date, name in subdiv_holidays.items():
                            if start_dt.date() <= date <= end_dt.date():
                                holidays_list.append(
                                    {
                                        "date": date.isoformat(),
                                        "name": name,
                                        "countrye": country_code,
                                        "subdivision": f"{country_code}-{subdivision}",
                                        "level": "regional",
                                    }
                                )
            except Exception:
                # Skip invalid country/subdivision
                continue
        return ToolResult.success(
            {
                "holidays": holidays_list,
                "start_date": start_dt.date().isoformat(),
                "end_date": end_dt.date().isoformat(),
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to get holiday info: {str(e)}").model_dump()


@tool("convert_timezone", args_schema=TimezoneConversionInput)
def convert_timezone(
    datetime_string: str,
    source_timezone: str,
    target_timezone: str,
) -> Dict[str, Any]:
    """
    Use it to convert a datetime from one timezone to another.

    Returns:
        Dictionary containing timezone conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'converted_datetime': (string) Datetime string in target timezone in ISO format
          - 'original_datetime': (string) Original input datetime string
          - 'source_timezone': (string) Source timezone in ISO format
          - 'target_timezone': (string) Target timezone in ISO format
          - 'time_difference': (float) Time difference in hours between timezones
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        dt, _ = parse_datetime_string(datetime_string)
        if dt is None:
            return ToolResult.failure(f"Could not parse datetime: {datetime_string}").model_dump()

        source_tz = pytz.timezone(source_timezone)
        if dt.tzinfo is None:
            localized_dt = source_tz.localize(dt)
        else:
            localized_dt = dt.astimezone(source_tz)

        target_tz = pytz.timezone(target_timezone)
        converted_dt = localized_dt.astimezone(target_tz)

        source_offset = localized_dt.utcoffset()
        target_offset = converted_dt.utcoffset()
        time_difference = None
        if source_offset is not None and target_offset is not None:
            time_difference = (target_offset.total_seconds() - source_offset.total_seconds()) / 3600

        return ToolResult.success(
            {
                "converted_datetime": converted_dt.isoformat(),
                "original_datetime": dt.isoformat(),
                "source_timezone": source_timezone,
                "target_timezone": target_timezone,
                "time_difference": time_difference,
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to convert timezone: {str(e)}").model_dump()


@tool("get_country_timezones")
def get_country_timezones(country: str) -> Dict[str, Any]:
    """
    Use it to get list of all available timezone names of the given country can be used by the convert_timezone tool.

    The input of the country code must be ISO 3166-1 alpha-2 format, e.g., 'US', 'CN'.

    Returns:
        Dictionary containing timezone information:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'timezones': (list) List of all available timezone names (e.g., 'UTC', 'America/New_York')
          - 'total_count': (integer) Total number of available timezones
        - 'error': (string, optional) Error message if operation failed
    """
    try:
        all_timezones = pytz.country_timezones.get(country.upper(), [])
        return ToolResult.success(
            {
                "timezones": all_timezones,
                "total_count": len(all_timezones),
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Failed to get available timezones of {country}: {str(e)}").model_dump()


@tool("date_diff", args_schema=DateDiffInput)
def date_diff(
    start_datetime: str,
    end_datetime: str,
) -> Dict[str, Any]:
    """
    Use it to calculate the absolute difference and relative order between two date/time.

    Returns:
        - total_seconds (int): Absolute difference in seconds
        - total_minutes (int): Absolute difference in minutes
        - total_hours (int): Absolute difference in hours
        - total_days (int): Absolute difference in days
        - days (int): Day part of the difference
        - hours (int): Hour part of the difference
        - minutes (int): Minute part of the difference
        - seconds (int): Second part of the difference
        - start_datetime (str): The input start datetime in ISO format
        - end_datetime (str): The input end datetime in ISO format
        - compare_result (str): Relative order, one of 'less' (start < end), 'greater' (start > end), 'equal'
    """
    try:
        dt1, _ = parse_datetime_string(start_datetime)
        dt2, _ = parse_datetime_string(end_datetime)
        if dt1 is None or dt2 is None:
            return ToolResult.failure(f"Cannot parse the date: {start_datetime}, {end_datetime}").model_dump()
        delta = abs(dt2 - dt1)
        total_seconds = delta.total_seconds() // 1
        total_minutes = total_seconds // 60
        total_hours = total_seconds // 3600
        total_days = total_seconds // 86400

        days = delta.days
        seconds_left = delta.seconds
        hours = seconds_left // 3600
        minutes = (seconds_left % 3600) // 60
        seconds = seconds_left % 60

        return ToolResult.success(
            {
                "total_seconds": total_seconds,
                "total_minutes": total_minutes,
                "total_hours": total_hours,
                "total_days": total_days,
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "start_datetime": dt1.isoformat(),
                "end_datetime": dt2.isoformat(),
                "compare_result": "less" if dt1 < dt2 else ("greater" if dt1 > dt2 else "equal"),
            }
        ).model_dump()
    except Exception as e:
        return ToolResult.failure(f"Calculate the diff failed: {str(e)}").model_dump()
