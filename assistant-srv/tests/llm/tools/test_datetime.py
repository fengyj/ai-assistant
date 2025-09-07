"""
Unit tests for datetime tools module.

This module contains tests for:
- add_time_delta function
- get_date_info function
- convert_timezone function
- get_country_timezones function
"""

from assistant.llm.tools.datetime import (
    add_time_delta,
    convert_timezone,
    get_country_timezones,
    get_date_info,
    get_holiday_info,
)


class TestAddTimeDelta:
    """Test cases for add_time_delta function."""

    def test_add_days(self) -> None:
        """Test adding days to a datetime."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01 12:00:00", "days": 5})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2023-01-06T12:00:00"

    def test_subtract_hours(self) -> None:
        """Test subtracting hours from a datetime."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01 12:00:00", "hours": -2})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2023-01-01T10:00:00"

    def test_add_years_and_months(self) -> None:
        """Test adding years and months."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01", "years": 1, "months": 2})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2024-03-01T00:00:00"

    def test_invalid_datetime(self) -> None:
        """Test with invalid datetime string."""
        result = add_time_delta.invoke({"base_datetime": "invalid-date"})
        assert result["status"] == "error"


class TestGetDateInfo:
    """Test cases for get_date_info function."""

    def test_current_datetime(self) -> None:
        """Test getting current datetime info."""
        result = get_date_info.invoke({})
        assert result["status"] == "success"
        assert "date" in result["data"]
        assert "timestamp" in result["data"]

    def test_specific_datetime(self) -> None:
        """Test getting info for a specific datetime."""
        result = get_date_info.invoke({"datetime_str": "2023-01-01 12:00:00"})
        assert result["status"] == "success"
        assert result["data"]["day_of_week"] == "Sunday"
        assert result["data"]["weekday_number"] == 6

    def test_invalid_datetime(self) -> None:
        """Test with invalid datetime string."""
        result = get_date_info.invoke({"datetime_str": "invalid-date"})
        assert result["status"] == "error"

    def test_with_china_lunar_date_today(self) -> None:
        """Test getting date info with China for lunar date using today's date."""
        result = get_date_info.invoke({"datetime_str": "2025-09-04"})  # Today's date
        assert result["status"] == "success"
        assert "chinese_lunar_date" in result["data"]
        # Expected lunar date: 农历2025年7月13日
        assert "农历2025年7月13日" in result["data"]["chinese_lunar_date"]


class TestConvertTimezone:
    """Test cases for convert_timezone function."""

    def test_timezone_conversion(self) -> None:
        """Test converting between timezones."""
        result = convert_timezone.invoke(
            {"datetime_string": "2023-01-01 12:00:00", "target_timezone": "America/New_York", "source_timezone": "UTC"}
        )
        assert result["status"] == "success"
        assert "converted_datetime" in result["data"]
        assert result["data"]["source_timezone"] == "UTC"
        assert result["data"]["target_timezone"] == "America/New_York"

    def test_naive_datetime_conversion(self) -> None:
        """Test converting naive datetime (assumes UTC)."""
        result = convert_timezone.invoke(
            {"datetime_string": "2023-01-01 12:00:00", "source_timezone": "UTC", "target_timezone": "America/New_York"}
        )
        assert result["status"] == "success"
        assert result["data"]["source_timezone"] == "UTC"
        assert result["data"]["target_timezone"] == "America/New_York"
        assert "converted_datetime" in result["data"]
        assert result["data"]["converted_datetime"] == "2022-12-31T23:00:00-05:00"

    def test_invalid_timezone(self) -> None:
        """Test with invalid timezone."""
        result = convert_timezone.invoke(
            {
                "datetime_string": "2023-01-01T12:00:00",
                "source_timezone": "unknown",
                "target_timezone": "Invalid/Timezone",
            }
        )
        assert result["status"] == "error"


class TestGetCountryTimezones:
    """Test cases for get_country_timezones function."""

    def test_get_timezones(self) -> None:
        """Test getting list of available timezones."""
        result = get_country_timezones.invoke({"country": "US"})
        assert result["status"] == "success"
        assert "timezones" in result["data"]
        assert "total_count" in result["data"]
        assert len(result["data"]["timezones"]) > 0
        assert "America/New_York" in result["data"]["timezones"]


class TestGetHolidayInfo:
    """Test cases for get_holiday_info function."""

    def test_basic_holiday_query(self) -> None:
        """Test querying holidays for US and CN in a short range."""
        result = get_holiday_info.invoke(
            {
                "start_date": "2025-01-01",
                "end_date": "2025-01-10",
                "countries": ["US", "CN"],
                "include_subdivisions": False,
            }
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        assert "start_date" in result["data"]
        assert "end_date" in result["data"]
        # 至少有一个国家有节日
        assert isinstance(result["data"]["holidays"], list)

    def test_holiday_with_subdivisions(self) -> None:
        """Test querying holidays with subdivisions included."""
        result = get_holiday_info.invoke(
            {"start_date": "2025-07-01", "end_date": "2025-07-10", "countries": ["US"], "include_subdivisions": True}
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        # 检查是否有 regional 级别的节日
        has_regional = any(h.get("level") == "regional" for h in result["data"]["holidays"])
        assert has_regional or len(result["data"]["holidays"]) == 0  # 允许无 regional

    def test_invalid_country(self) -> None:
        """Test with invalid country code."""
        result = get_holiday_info.invoke(
            {"start_date": "2025-01-01", "end_date": "2025-01-10", "countries": ["XX"], "include_subdivisions": False}
        )
        assert result["status"] == "success"
        assert isinstance(result["data"]["holidays"], list)
        # XX不是合法国家，应该没有节日
        assert len(result["data"]["holidays"]) == 0

    def test_invalid_date(self) -> None:
        """Test with invalid date format."""
        result = get_holiday_info.invoke(
            {"start_date": "invalid-date", "end_date": "2025-01-10", "countries": ["US"], "include_subdivisions": False}
        )
        assert result["status"] == "error"
