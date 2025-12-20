"""
Custom Filters for client management
"""

from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import make_aware
from django.db.models import Q


class BaseCustomFilter:
    """
    Base class for custom filters with common functionality.
    """

    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        self.query_params = request.query_params

    def get_filter_value(self, param_name):
        """Get a single parameter value from query params."""
        return self.query_params.get(param_name)

    def get_list_filter_value(self, param_name):
        """Get a list of values from comma-separated or repeated query params."""
        values = self.request.query_params.getlist(param_name)
        return [v.strip() for v in values if v.strip()] if values else []

    def parse_datetime_value(self, value, field_name):
        """Parse datetime string to datetime object with validation."""
        if not value:
            return None

        parsed_dt = parse_datetime(value)
        if parsed_dt is None:
            # If not a full datetime, try parsing as a date and assume start/end of day
            parsed_date = parse_date(value)
            if parsed_date is None:
                raise ValidationError(
                    {
                        "detail": f"Invalid datetime format for {field_name}."
                        f"Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)."
                    }
                )
            return make_aware(datetime.combine(parsed_date, datetime.min.time()))

        return make_aware(parsed_dt)

    def parse_date_value(self, value, field_name):
        """Parse date string to date object with validation."""
        if not value:
            return None
        parsed_date = parse_date(value)
        if parsed_date is None:
            raise ValidationError(
                {"detail": f"Invalid date format for {field_name}. Use YYYY-MM-DD."}
            )
        return parsed_date


class ClientDetailsCustomFilter(BaseCustomFilter):
    """
    Custom filter for ClientDetails model.
    """

    ALLOWED_FILTERS = {
        "status": "list",  # This filter_type is meant for the _apply_list_filter method
        "user_fk": "list_fk",
        "project_fk": "list_fk",
        "start_date": "project_date_filter_start",
        "end_date": "project_date_filter_end",
        "from_created_at": "datetime_range_start",
        "to_created_at": "datetime_range_end",
    }

    IGNORED_FIELDS = {"search", "page", "page_size", "ordering"}

    def __init__(self, queryset, request):
        super().__init__(queryset, request)
        self.validate_filter_fields()

    def validate_filter_fields(self):
        """
        Method to filter fileds
        """
        request_fields = set(self.request.query_params.keys())
        valid_filters_keys = set(self.ALLOWED_FILTERS.keys())
        invalid_fields = request_fields - valid_filters_keys - self.IGNORED_FIELDS

        if invalid_fields:
            raise ValidationError(
                f"Invalid filter fields provided: {', '.join(invalid_fields)}"
            )

    def apply_filters(self):
        """
        Method to apply filters
        """
        filtered_queryset = self.queryset

        # Handle Project Date Range Filters (from frontend 'start_date' and 'end_date' params)
        start_date_param = self.get_filter_value("start_date")
        if start_date_param:
            date_obj = self.parse_date_value(start_date_param, "start_date")
            if date_obj:
                filtered_queryset = filtered_queryset.filter(start_date__gte=date_obj)

        end_date_param = self.get_filter_value("end_date")
        if end_date_param:
            date_obj = self.parse_date_value(end_date_param, "end_date")
            if date_obj:
                filtered_queryset = filtered_queryset.filter(start_date__lte=date_obj)

        # Handle Other Filters defined in ALLOWED_FILTERS
        for field_name, filter_type in self.ALLOWED_FILTERS.items():
            if field_name in ["start_date", "end_date"]:
                continue

            if filter_type == "list":
                filtered_queryset = self._apply_list_filter(
                    filtered_queryset, field_name
                )
            elif filter_type == "list_fk":
                filtered_queryset = self._apply_foreign_key_list_filter(
                    filtered_queryset, field_name
                )
            elif filter_type == "datetime_range_start":
                param_value = self.request.query_params.get(field_name)
                if param_value:
                    from_dt = self.parse_datetime_value(param_value, field_name)
                    if from_dt:
                        filtered_queryset = filtered_queryset.filter(
                            created_at__gte=from_dt
                        )
            elif filter_type == "datetime_range_end":
                param_value = self.request.query_params.get(field_name)
                if param_value:
                    to_dt = self.parse_datetime_value(param_value, field_name)
                    if to_dt:
                        to_dt = to_dt.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        filtered_queryset = filtered_queryset.filter(
                            created_at__lte=to_dt
                        )

        return filtered_queryset

    def _apply_list_filter(self, queryset, field_name):
        """
        Method to apply list filter
        """
        values = self.get_list_filter_value(field_name)
        if values:
            # Check if the list contains a single item which is a comma-separated string
            if len(values) == 1 and "," in values[0]:
                # If so, split that string into a proper list of values
                values = values[0].split(",")
            lowercase_values = [v.strip().lower() for v in values if v.strip()]
            queries = [Q(**{f"{field_name}__iexact": v}) for v in lowercase_values]
            if queries:
                combined_query = queries.pop()
                for item in queries:
                    combined_query |= item
                return queryset.filter(combined_query)
        return queryset

    def _apply_foreign_key_list_filter(self, queryset, field_name):
        """
        Method to apply foreign key list filters
        """
        values = self.get_list_filter_value(field_name)
        if values:
            try:
                pk_values = [int(v) for v in values]
                return queryset.filter(**{f"{field_name}__in": pk_values})
            except (ValueError, TypeError) as exc:
                raise ValidationError(
                    f"Invalid format for '{field_name}'. Expected a list of integers."
                ) from exc
        return queryset
