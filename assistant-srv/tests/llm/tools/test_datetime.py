"""
Unit tests for datetime tools module.

This module contains tests for:
- add_time_delta function
- get_date_info function
- convert_timezone function
- get_available_timezones function
"""

from assistant.llm.tools.datetime import add_time_delta, convert_timezone, get_available_timezones, get_date_info


class TestAddTimeDelta:
    """Test cases for add_time_delta function."""

    def test_add_days(self) -> None:
        """Test adding days to a datetime."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01 12:00:00", "days": 5})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2023-01-06 12:00:00"

    def test_subtract_hours(self) -> None:
        """Test subtracting hours from a datetime."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01 12:00:00", "hours": -2})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2023-01-01 10:00:00"

    def test_add_years_and_months(self) -> None:
        """Test adding years and months."""
        result = add_time_delta.invoke({"base_datetime": "2023-01-01", "years": 1, "months": 2})
        assert result["status"] == "success"
        assert result["data"]["new_datetime"] == "2024-03-01"

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
        result = get_date_info.invoke({"datetime": "2023-01-01 12:00:00"})
        assert result["status"] == "success"
        assert result["data"]["day_of_week"] == "Sunday"
        assert result["data"]["weekday_number"] == 6

    def test_with_timezone(self) -> None:
        """Test getting datetime info with timezone."""
        result = get_date_info.invoke({"datetime": "2023-01-01 12:00:00", "timezone": "America/New_York"})
        assert result["status"] == "success"
        assert "timezone" in result["data"]

    def test_invalid_datetime(self) -> None:
        """Test with invalid datetime string."""
        result = get_date_info.invoke({"datetime": "invalid-date"})
        assert result["status"] == "error"

    def test_with_countries_holidays_us(self) -> None:
        """Test getting date info with US holidays using Independence Day."""
        result = get_date_info.invoke(
            {"datetime": "2023-07-04", "countries_of_holidays_interested": [{"country": "US"}]}  # Independence Day
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        assert len(result["data"]["holidays"]) > 0
        # Check if Independence Day is in the holidays
        holiday_names = [h["name"] for h in result["data"]["holidays"]]
        assert any("Independence" in name for name in holiday_names)

    def test_with_countries_holidays_canada(self) -> None:
        """Test getting date info with Canada holidays using Canada Day."""
        result = get_date_info.invoke(
            {"datetime": "2023-07-01", "countries_of_holidays_interested": [{"country": "CA"}]}  # Canada Day
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        assert len(result["data"]["holidays"]) > 0
        # Check if Canada Day is in the holidays
        holiday_names = [h["name"] for h in result["data"]["holidays"]]
        assert any("Canada" in name for name in holiday_names)

    def test_with_countries_and_subdivision_canada_nl(self) -> None:
        """Test getting date info with Canada Newfoundland subdivision."""
        result = get_date_info.invoke(
            {
                "datetime": "2023-07-01",  # Canada Day
                "countries_of_holidays_interested": [{"country": "CA", "subdivision": "NL"}],
            }
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        assert len(result["data"]["holidays"]) > 0
        # Check subdivision is recorded
        assert result["data"]["holidays"][0]["subdivision"] == "NL"

    def test_with_china_lunar_date_today(self) -> None:
        """Test getting date info with China for lunar date using today's date."""
        result = get_date_info.invoke(
            {"datetime": "2025-09-04", "countries_of_holidays_interested": [{"country": "CN"}]}  # Today's date
        )
        assert result["status"] == "success"
        assert "lunar_date" in result["data"]
        # Expected lunar date: 农历2025年7月13日
        assert "农历2025年7月13日" in result["data"]["lunar_date"]

    def test_with_days_window_us(self) -> None:
        """Test getting date info with custom days window for US holidays."""
        result = get_date_info.invoke(
            {
                "datetime": "2023-07-04",  # Independence Day
                "countries_of_holidays_interested": [{"country": "US"}],
                "days_window_for_holiday_info": (3, 5),
            }
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        # Should include holidays within the window
        holiday_dates = [h["date"] for h in result["data"]["holidays"]]
        assert "2023-07-04" in holiday_dates

    def test_multiple_countries_us_and_ca(self) -> None:
        """Test getting date info with multiple countries: US and CA."""
        result = get_date_info.invoke(
            {"datetime": "2023-07-01", "countries_of_holidays_interested": [{"country": "US"}, {"country": "CA"}]}
        )
        assert result["status"] == "success"
        assert "holidays" in result["data"]
        holiday_names = [h["name"] for h in result["data"]["holidays"]]
        # Should have both US and CA holidays
        assert any("Canada" in name for name in holiday_names) or any("Independence" in name for name in holiday_names)

    def test_without_countries(self) -> None:
        """Test getting date info without countries (no holidays or lunar date)."""
        result = get_date_info.invoke({"datetime": "2023-01-01"})
        assert result["status"] == "success"
        assert result["data"]["holidays"] is None
        assert result["data"]["lunar_date"] is None


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
            {"datetime_string": "2023-01-01 12:00:00", "target_timezone": "America/New_York"}
        )
        assert result["status"] == "success"
        assert result["data"]["source_timezone"] == "UTC"

    def test_invalid_timezone(self) -> None:
        """Test with invalid timezone."""
        result = convert_timezone.invoke(
            {"datetime_string": "2023-01-01 12:00:00", "target_timezone": "Invalid/Timezone"}
        )
        assert result["status"] == "error"


class TestGetAvailableTimezones:
    """Test cases for get_available_timezones function."""

    def test_get_timezones(self) -> None:
        """Test getting list of available timezones."""
        result = get_available_timezones.invoke({})
        assert result["status"] == "success"
        assert "timezones" in result["data"]
        assert "total_count" in result["data"]
        assert "common_timezones" in result["data"]
        assert len(result["data"]["timezones"]) > 0
        assert "UTC" in result["data"]["timezones"]
