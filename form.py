from typing import Dict, Type, Optional, Any
from flask import Request
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.types import Integer as IntegerType, String as StringType, Float as FloatType, Date as DateType
from sqlalchemy import ForeignKey
from datetime import datetime, date

class MyForm:
    def __init__(self, model: Type[DeclarativeMeta]):
        """
        Initializes the form with a model and creates attributes based on the model’s columns.
        :param model: SQLAlchemy model class
        """
        self.model = model
        self._create_attributes_from_model()
        self.errors = {}  # Used in validate_on_submit method in child class form

    def _create_attributes_from_model(self):
        """
        Initializes attributes on the form object based on the model’s columns.
        """
        columns = self.get_columns()
        for column_name, column_type in columns.items():
            value = "" if isinstance(column_type, StringType) else 0
            setattr(self, column_name, value)

    def get_columns(self) -> Dict[str, Type]:
        """
        Returns a dictionary of column names and their types.
        :return: Dictionary where keys are column names and values are SQLAlchemy types
        """
        columns = {}
        for column in self.model.__table__.columns:
            if column.foreign_keys:
                columns[column.name] = 'ForeignKey'
            else:
                columns[column.name] = column.type
        return columns

    def post(self, request: Request, instance: DeclarativeMeta, i: int = -1):
        """
        Updates the model instance based on form data from the request.
        :param request: Flask request object
        :param instance: SQLAlchemy model instance to be updated
        """
        for column_name, column_type in self.get_columns().items():
            if column_name == "id":
                if request.form.get("record_id"):
                    html_name = f"record_id-{i}" if i > -1 else "record_id"
                    setattr(self, "id", request.form.get(html_name))
                continue

            html_name = f"{column_name}-{i}" if i > -1 else column_name
            value = request.form.get(html_name)

            if column_type == 'ForeignKey':
                setattr(instance, column_name, int(value) if value else None)
                setattr(self, column_name, int(value) if value else None)
            elif isinstance(column_type, DateType):
                if isinstance(value, str):
                    setattr(instance, column_name, datetime.strptime(value, '%Y-%m-%d').date() if value else None)
                    setattr(self, column_name, datetime.strptime(value, '%Y-%m-%d').date() if value else None)
                else:
                    setattr(instance, column_name, value)
                    setattr(self, column_name, value)
            elif isinstance(column_type, FloatType):
                setattr(instance, column_name, float(value) if value else None)
                setattr(self, column_name, float(value) if value else None)
            elif isinstance(column_type, IntegerType):
                setattr(instance, column_name, int(value) if value else None)
                setattr(self, column_name, int(value) if value else None)
            elif isinstance(column_type, StringType):
                setattr(instance, column_name, value)
                setattr(self, column_name, value)
            else:
                setattr(instance, column_name, value)
                setattr(self, column_name, value)

    def get(self, instance: DeclarativeMeta) -> 'MyForm':
        """
        Update form attributes based on the instance.
        :param instance: SQLAlchemy model instance to read values from
        :return: Updated MyForm instance
        """
        for column_name, column_type in self.get_columns().items():
            value = getattr(instance, column_name)
            if column_type == 'ForeignKey':
                setattr(self, column_name, int(value) if value else None)
            elif isinstance(column_type, DateType):
                if isinstance(value, date):
                    setattr(self, column_name, value)
                else:
                    setattr(self, column_name, datetime.strptime(value, '%Y-%m-%d').date() if value else None)
            elif isinstance(column_type, FloatType):
                setattr(self, column_name, float(value) if value else None)
            elif isinstance(column_type, IntegerType):
                setattr(self, column_name, int(value) if value else None)
            elif isinstance(column_type, StringType):
                setattr(self, column_name, value)
            else:
                setattr(self, column_name, value)

        return self

    @property
    def html_tag(self):
        """
        Property that returns a function to generate HTML tags for form attributes.
        """
        def generate_tag(name: str, **attributes: Optional[Any]) -> str:
            """
            Generates an HTML tag with optional additional attributes.
            :param name: Name of the form field
            :param attributes: Additional attributes like css_class, autofocus, etc.
            :return: HTML tag string
            """
            column_type = self.get_columns()[name]
            value = getattr(self, name)

            tag_type = 'text'
            if isinstance(column_type, DateType):
                tag_type = 'date'
            elif isinstance(column_type, IntegerType) and column_type != 'ForeignKey':
                tag_type = 'number'
            elif isinstance(column_type, FloatType):
                tag_type = 'number'
            elif column_type == 'ForeignKey':
                tag_type = 'select'

            # Convert css_class to class
            if 'css_class' in attributes:
                attributes['class'] = attributes.pop('css_class')

            # Handle boolean attributes
            for key, val in attributes.items():
                if isinstance(val, bool) and val:
                    attributes[key] = key
                elif key == 'autocomplete' and val is False:
                    attributes[key] = 'off'
                elif key == 'autocomplete' and val is True:
                    attributes[key] = 'on'

            # Handle special case for 'id' attribute
            field_name = 'record_id' if name == 'id' else name

            if 'i' in attributes: 
                field_name = f"{field_name}-{attributes['i']}"
                attributes.pop('i')

            attrs = ' '.join([f'{key}="{value}"' for key, value in attributes.items() if value is not None])

            if tag_type == 'select':
                options = [(0, "")] + attributes.pop('options', [])
                options_html = ''.join([
                    f'<option value="{opt[0]}" {"selected" if opt[0] == value else ""}>{opt[1]}</option>' 
                    for opt in options
                ])
                return f'<select name="{field_name}" {attrs}>{options_html}</select>'
            else:
                return f'<input type="{tag_type}" name="{field_name}" value="{value}" {attrs}>'

        return generate_tag
    
    def __str__(self):
        """
        Returns a string representation of the form’s attributes in dictionary format.
        :return: String representation of the form’s attributes
        """
        columns = self.get_columns()
        attributes = {column_name: getattr(self, column_name) for column_name in columns.keys()}
        return str(attributes)
