from typing import Dict, Type, Optional, Any
from flask import Request
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.types import Integer as IntegerType, String as StringType, Float as FloatType


class MyForm:
    def __init__(self, model: Type[DeclarativeMeta]):
        """
        Initializes the form with a model and creates attributes based on the model’s columns.
        :param model: SQLAlchemy model class
        """
        self.model = model
        self._create_attributes_from_model()

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
        return {column.name: column.type for column in self.model.__table__.columns}

    def post(self, request: Request, instance: DeclarativeMeta):
        """
        Updates the model instance based on form data from the request.
        :param request: Flask request object
        :param instance: SQLAlchemy model instance to be updated
        """
        for column_name, column_type in self.get_columns().items():
            if column_name == "id":
                if request.form.get("record_id"):
                    setattr(instance, "id", request.form.get("record_id"))
                continue

            value = request.form.get(column_name)
            if isinstance(column_type, FloatType):
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
            if isinstance(column_type, FloatType):
                setattr(self, column_name, float(value) if value else None)
            elif isinstance(column_type, IntegerType):
                setattr(self, column_name, int(value) if value else None)
            elif isinstance(column_type, StringType):
                setattr(self, column_name, value)
            else:
                setattr(self, column_name, value)

        return self

    def html_tag(self) -> Dict[str, str]:
        """
        Generates HTML tags for each form attribute.
        :return: Dictionary where keys are column names and values are HTML tag strings
        """
        tags = {}
        columns = self.get_columns()
        for column_name, column_type in columns.items():
            value = getattr(self, column_name)
            tag = self._generate_tag(column_name, column_type, value)
            tags[column_name] = tag
        
        # Special handling for 'id' if needed
        tags['id'] = self._generate_tag('record_id', IntegerType, getattr(self, "id", ""))
        
        return tags
    
    def _generate_tag(self, name: str, column_type: Type, value: Any, **attributes: Optional[Any]) -> str:
        """
        Generates an HTML tag with optional additional attributes.
        :param name: Name of the form field
        :param column_type: SQLAlchemy column type to determine the input type
        :param value: Value to be placed in the input field
        :param attributes: Additional attributes like css_class, autofocus, etc.
        :return: HTML tag string
        """
        tag_type = 'text'
        if isinstance(column_type, IntegerType):
            tag_type = 'number'
        elif isinstance(column_type, FloatType):
            tag_type = 'number'
        
        # Convert css_class to class
        if 'css_class' in attributes:
            attributes['class'] = attributes.pop('css_class')
        
        attrs = ' '.join([f'{key}="{value}"' for key, value in attributes.items() if value is not None])
        return f'<input type="{tag_type}" name="{name}" value="{value}" {attrs}>'