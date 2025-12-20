from django.db.models import Q
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import make_aware
from rest_framework.exceptions import ValidationError
from datetime import datetime


class BaseCustomFilter:
    """
    Base class for custom filters with common functionality.
    """
    
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        self.query_params = request.query_params
        
    def get_filter_value(self, param_name):
        """Get parameter value from query params."""
        return self.query_params.get(param_name)
    
    def get_list_filter_value(self, param_name):
        """Get comma-separated values as a list."""
        value = self.get_filter_value(param_name)
        if value:
            return [v.strip() for v in value.split(',') if v.strip()]
        return []
    
    def parse_datetime_value(self, value):
        """Parse datetime string to datetime object."""
        if not value:
            return None
        
        # Try parsing as datetime first
        parsed_dt = parse_datetime(value)
        if parsed_dt:
            return parsed_dt
        
        # Try parsing as date
        parsed_date = parse_date(value)
        if parsed_date:
            # For to_date, set to end of day; for from_date, set to start of day
            return datetime.combine(parsed_date, datetime.min.time())
        
        return None
    
    def validate_datetime_format(self, value, field_name):
        """Validate datetime format and raise ValidationError if invalid."""
        if not value:
            return None
        
        parsed_dt = self.parse_datetime_value(value)
        if parsed_dt is None:
            raise ValidationError({
                'detail': f"Invalid datetime format for {field_name}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            })
        return parsed_dt

class CustomerLeadCustomFilter(BaseCustomFilter):
    """
    Custom filter for CustomerLead model with validation and filtering logic.
    """
    
    # Define allowed filter fields and their types
    ALLOWED_FILTERS = {
        'status': 'list',
        'city': 'list', 
        'assigned_to_fk': 'list',
        'service_type': 'json_list', # <--- CHANGE THIS LINE
        'from_date': 'datetime',
        'to_date': 'datetime',
        'client_name': 'string',
        'email': 'string',
        'phone': 'string',
        'source': 'string',
    }
    
    # Fields to ignore during validation
    IGNORED_FIELDS = {'search', 'page', 'page_size', 'ordering'}
    
    def __init__(self, queryset, request):
        super().__init__(queryset, request)
        self.validate_filter_fields()
    
    def validate_filter_fields(self):
        """Validate that only allowed filter fields are used."""
        if not self.query_params:
            return
        
        provided_fields = set(self.query_params.keys())
        allowed_fields = set(self.ALLOWED_FILTERS.keys())
        
        invalid_fields = provided_fields - allowed_fields - self.IGNORED_FIELDS
        
        if invalid_fields:
            raise ValidationError({
                'detail': f"Invalid filter field(s): {', '.join(invalid_fields)}. "
                         f"Allowed fields: {', '.join(allowed_fields)}"
            })
    
    def apply_filters(self):
        """Apply all filters to the queryset."""
        filtered_queryset = self.queryset
        
        # Apply each filter
        for field_name, filter_type in self.ALLOWED_FILTERS.items():
            if filter_type == 'list':
                filtered_queryset = self._apply_list_filter(filtered_queryset, field_name)
            elif filter_type == 'json_list':
                filtered_queryset = self._apply_json_list_filter(filtered_queryset, field_name)
            elif filter_type == 'datetime':
                filtered_queryset = self._apply_datetime_filter(filtered_queryset, field_name)
            elif filter_type == 'string':
                filtered_queryset = self._apply_string_filter(filtered_queryset, field_name)
        
        return filtered_queryset
    
    def _apply_list_filter(self, queryset, field_name):
        values = self.get_list_filter_value(field_name)
        if values:
            lookup_field = field_name.replace('__in', '')
            return queryset.filter(**{f'{lookup_field}__in': values})
        return queryset

    def _apply_json_list_filter(self, queryset, field_name):
        """
        Apply filter for JSONField that is a list of objects.
        This uses `Q` objects to combine multiple OR conditions for the `service_name`.
        """
        values = self.get_list_filter_value(field_name)
        if values:
            q_objects = Q()
            for value in values:
                # Use the __contains lookup to check for a dictionary with a specific service_name
                q_objects |= Q(**{f'{field_name}__contains': [{'service_name': value}]})
            return queryset.filter(q_objects)
        return queryset
    
    def _apply_datetime_filter(self, queryset, field_name):
        """Apply datetime range filters."""
        value = self.get_filter_value(field_name)
        if value:
            validated_dt = make_aware(self.validate_datetime_format(value, field_name))
            if validated_dt:
                # Map user-friendly parameter names to actual field lookups
                if field_name == 'from_date':
                    # validated_dt = validated_dt.replace(hour=0, minute=0, second=0)
                    return queryset.filter(created_at__gte=validated_dt)
                elif field_name == 'to_date':
                    validated_dt = validated_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    return queryset.filter(created_at__lte=validated_dt)
        return queryset
    
    def _apply_string_filter(self, queryset, field_name):
        """Apply string-based filters with icontains lookup."""
        value = self.get_filter_value(field_name)
        if value:
            return queryset.filter(**{f'{field_name}__icontains': value})
        return queryset 


class CustomSearchFilter:
    """
    Custom search filter that works with multiple fields.
    """
    
    def __init__(self, queryset, request, search_fields=None):
        self.queryset = queryset
        self.request = request
        self.search_fields = search_fields or []
        self.search_param = 'search'
    
    def apply_search(self):
        """Apply search filter across multiple fields."""
        search_term = self.request.query_params.get(self.search_param)
        
        if not search_term or not self.search_fields:
            return self.queryset
        
        # Build Q objects for each search field
        search_queries = Q()
        for field in self.search_fields:
            search_queries |= Q(**{f'{field}__icontains': search_term})
        
        return self.queryset.filter(search_queries)

