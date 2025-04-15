from __future__ import annotations

import logging
from pathlib import Path
from typing import (
    Any,
)

import pandas as pd  #type: ignore # noqa: PGH003
from django.core.files.base import ContentFile  #type: ignore # noqa: PGH003
from django.utils.timezone import now  #type: ignore # noqa: PGH003
from docx import Document  #type: ignore # noqa: PGH003

from app.dttotDocReport.models import dttotDocReport  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


def load_template(
        template_path: str | Path,
) -> Document | None:
    """Load a Word document template.

    Args:
    ----
        template_path (Union[str, Path]): The path to the Word document template.

    Returns:
    -------
        Optional[Document]: The loaded Word document template, or None if the template could not be loaded.

    """
    try:
        # Convert template path to string if it is a pathlib.Path object
        if isinstance(template_path, Path):
            template_path = str(template_path)

        logger.info("Loading template: %s", template_path)

        # Check if the file is a .docx file
        if not template_path.endswith(".docx"):
            msg = "Template file must be a .docx file"
            raise ValueError(msg)  # noqa: TRY301

        # Load the template file using python-docx
        doc = Document(template_path)
        logger.info("Template loaded successfully")

        return doc  # noqa: TRY300

    except Exception as e:
        logger.exception("Error loading template: %s", e)  # noqa: TRY401
        return None

def replace_variable_in_template(  # noqa: C901
        template_path: str,
        output_dir: Path,
        variable_values: dict[str, Any],
) -> bool:
    """To replace variables in Word document template with actual values, dynamically generating rows if needed.

    Args:
    ----
        template_path (str): The path to the Word document template.
        output_dir (Path): The directory where the generated Word document will be saved.
        variable_values (Dict[str, Any]): A dictionary containing variable names and their corresponding values.

    Returns:
    -------
        bool: True if the template was successfully replaced, False otherwise.

    """
    import copy

    def format_number(value: Any) -> str:
        """Format a number value into a string.

        Args:
        ----
            value (Any): The value to be formatted.

        Returns:
        -------
            str: The formatted string representation of the number value.

        """
        if isinstance(value, float):
            # Convert to float to percentage if the value is less than 1
            return f"{value * 100:.0f}%" if value < 1 else f"{value:,}"
        elif isinstance(value, int):  # noqa: RET505
            # Format integers with commas
            return f"{value:,}"
        else:
            # Default to converting other types to string
            return str(value)

    def replace_text_in_element(
        element: Any,
        variables: dict[str, Any],
    ) -> None:
        """Replace placeholders in a Word document element with actual values.

        Args:
        ----
            element (OxmlElement): The element to be processed.
            variables (dict[str, Any]): A dictionary containing variable names and their corresponding values.

        Returns:
        -------
            None

        """
        for variable, value in variables.items():
            placeholder = f"${{{variable}}}"
            if placeholder in element.text:
                element.text = element.text.replace(placeholder, str(value))

    def copy_cell_properties(source_cell: Any, dest_cell: Any) -> None:
        """Copy properties from a source cell to a destination cell.

        Args:
        ----
            source_cell (Any): The source cell to copy properties from.
            dest_cell (Any): The destination cell to copy properties to.

        Returns:
        -------
            None

        """
        cell_properties = source_cell._tc_get_or_add_tcPr()  # noqa: SLF001
        dest_cell._tc.remove(dest_cell._tc.get_or_add_tcPr())  # noqa: SLF001
        cell_properties = copy.deepcopy(cell_properties)
        dest_cell._tc.append(cell_properties)  # noqa: SLF001

    try:
        # Ensure the variable_values is a dictionary
        if not isinstance(variable_values, dict):
            logger.error("variable_values must be a dictionary")
            return False

        # Load the Word document template
        document = load_template(template_path)
        if document is None:
            logger.error("Failed to load template")
            return False

        # Format the numerical values
        formatted_variables = {k: format_number(v) for k, v in variable_values.items()}

        # Replace variables in paragraphs
        for paragraph in document.paragraphs:
            replace_text_in_element(paragraph, formatted_variables)

        # Save the updated document
        attachment_created_date = now.strftime("%d%m%Y")
        attachemnt_file_name = f"DTTOTDOCREPORT_{attachment_created_date}.docx"
        final_output_path = output_dir / attachemnt_file_name
        document.save(final_output_path)
        logger.info(f"Template replaced successfully to {final_output_path}")  # noqa: G004

        return True  # noqa: TRY300

    except Exception as e:
        logger.exception("Error replacing template: %s", e)  # noqa: TRY401
        return False
