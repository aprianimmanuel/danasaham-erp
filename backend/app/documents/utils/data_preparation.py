import re
import pandas as pd  # noqa
from sklearn.metrics.pairwise import cosine_similarity  # noqa
from sklearn.feature_extraction.text import CountVectorizer  # noqa
from collections import Counter
from dateutil.parser import parse


class DTTOTDocumentProcessing:
    def import_document(self, file_path, document_format):
        """
        Imports a document based on its format and returns a pandas DataFrame.

        Args:
            file_path (str): The path to the document file.
            document_format (str): The format of the document ('CSV' or 'XLS').

        Returns:
            DataFrame: The imported document as a pandas DataFrame.
        """
        if document_format == 'CSV':
            return pd.read_csv(file_path)
        elif document_format == 'XLS':
            return pd.read_excel(file_path)
        else:
            raise ValueError(
                "Unsupported document format: {}".format(document_format))

    def retrieve_data_as_dataframe(self, file_path, document_format):
        """
        Wrapper function to retrieve all data from a document into a pandas DataFrame.  # noqa

        Args:
            file_path (str): The path to the document file.
            document_format (str): The format of the document ('CSV' or 'XLS').

        Returns:
            DataFrame: The document data as a pandas DataFrame.
        """
        df = self.import_document(file_path, document_format)
        return df

    def extract_and_split_names(self, df, name_column='Nama'):
        """
        Extracts aliases from names in the specified column of a DataFrame,
        splits the names and aliases into first, middle, and last names, and
        adds them as new columns.

        Args:
            df (DataFrame): The DataFrame containing the names.
            name_column (str): The column containing the names from which to extract aliases.

        Returns:
            DataFrame: The modified DataFrame with aliases extracted and names split.
        """  # noqa
        def split_name(name):
            """Splits a name into first, middle, and last components."""
            if not isinstance(name, str):
                return '', '', ''
            parts = name.strip().split()
            if len(parts) >= 3:
                return parts[0], ' '.join(parts[1:-1]), parts[-1]
            elif len(parts) == 2:
                return parts[0], '', parts[1]
            return name, '', ''

        # Calculate the maximum number of aliases in any name
        # to standardize column creation
        max_aliases = df[
            name_column
        ].apply(
            lambda x: x.count(' Alias ') if isinstance(x, str) else 0
        ).max()

        # Initialize columns for the main name split
        df[
            [
                'first_name',
                'middle_name',
                'last_name']] = df.apply(
                    lambda row: pd.Series(
                        split_name(
                            row[
                                name_column
                            ].split(
                                ' Alias ', 1
                                )[0]
                            ) if isinstance(
                                row[
                                    name_column
                                ], str) else ('', '', '')), axis=1)

        # Initialize columns for aliases and their split names
        for i in range(1, max_aliases + 1):
            df[f'Alias_name_{i}'] = ''
            df[f'first_name_alias_{i}'] = ''
            df[f'middle_name_alias_{i}'] = ''
            df[f'last_name_alias_{i}'] = ''

        # Extract aliases and split names
        for index, row in df.iterrows():
            aliases = re.split(
                r' Alias ',
                row[name_column],
                flags=re.IGNORECASE)[1:] if isinstance(
                    row[name_column], str
                ) else []
            for i, alias in enumerate(aliases, start=1):
                f_name_alias, m_name_alias, l_name_alias = split_name(alias)
                df.at[index, f'Alias_name_{i}'] = alias
                df.at[index, f'first_name_alias_{i}'] = f_name_alias
                df.at[index, f'middle_name_alias_{i}'] = m_name_alias
                df.at[index, f'last_name_alias_{i}'] = l_name_alias

        return df


class ExtractNIKandPassportNumber:
    """
    A class designed to extract and clean National Identification Numbers (NIK)
    and passport numbers from specified description columns within a pandas DataFrame.
    Utilizes regular expressions (regex) to accurately identify and extract these
    numerical and alphanumeric sequences. Post-extraction, the original text from
    which these numbers are extracted is cleaned by removing the identified numbers,
    enhancing the clarity and utility of the dataset.

    Attributes:
        nik_regex (list of str): Contains regex patterns designed to match NIK numbers,
                                  which typically consist of a 16-digit sequence.
        passport_regex (list of str): Contains regex patterns aimed at identifying
                                       passport numbers, which may include up to two
                                       letters followed by six or more digits, with an
                                       optional space between letters and digits.
    """  # noqa
    def __init__(self):
        """
        Initializes the ExtractNIKandPassportNumber class with specific regex patterns
        for identifying NIK and passport numbers within text.
        """  # noqa
        self.nik_regex = [
            r"\b\d{16}\b",  # Pattern for NIK numbers
        ]

        self.passport_regex = [
            r"\b[A-Z]{0,2}\s*\d{6,}\b",  # Pattern for passport numbers
        ]

    def extract_nik_and_passport_number(self, df):
        """
        Iterates over each row within the DataFrame to extract NIK and passport numbers
        from dynamically identified description columns. Updates the DataFrame with
        extracted numbers and cleans the description text from which these numbers were
        extracted.

        Args:
            df (pd.DataFrame): The input DataFrame containing the description columns.

        Returns:
            pd.DataFrame: The modified DataFrame with NIK and passport numbers extracted
                          and original description texts cleaned.
        """  # noqa
        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Initialize or clear the idNumber and passport_number for the row
            df.at[index, 'idNumber'] = ''
            df.at[index, 'passport_number'] = ''

            # Iterate through each description column
            description_columns = self._detect_description_columns(df)
            for description_column in description_columns:
                text = row[description_column]
                nik_number, passport_number, cleaned_text = self._extract_from_description(text)  # noqa

                # Update the DataFrame with extracted data if not already set
                if not df.at[index, 'idNumber'] and nik_number:
                    df.at[index, 'idNumber'] = nik_number
                if not df.at[index, 'passport_number'] and passport_number:
                    df.at[index, 'passport_number'] = passport_number
                # Update the cleaned description back into the DataFrame
                df.at[index, description_column] = cleaned_text

        return df

    def _detect_description_columns(self, df):
        """
        Identifies columns within the DataFrame that are likely to contain descriptive
        texts from which NIK and passport numbers need to be extracted. This identification
        is based on a consistent naming pattern for these columns.

        Args:
            df (pd.DataFrame): The input DataFrame to analyze.

        Returns:
            list: A list of column names that match the expected pattern for description columns.
        """  # noqa
        return [col for col in df.columns if col.startswith('description_')]

    def _extract_from_description(self, text):
        """
        Extracts NIK and passport numbers from a given piece of text. Utilizes the
        class's regex patterns for identification and extraction. Also cleans the text
        by removing the extracted numbers.

        Args:
            text (str): The text from which to extract NIK and passport numbers.

        Returns:
            tuple: Contains the extracted NIK number, passport number, and the cleaned text.
        """  # noqa
        # Extract NIK and passport numbers from text, then clean the text
        id_number = ''
        passport_number = ''
        cleaned_text = text

        # Try each NIK pattern until a match is found
        for nik_regex in self.nik_regex:
            nik_match = re.search(nik_regex, cleaned_text)
            if nik_match:
                id_number = nik_match.group()
                cleaned_text = re.sub(nik_regex, '', cleaned_text, 1)
                break  # Stop after finding the first match

        # Try each passport pattern until a match is found
        for passport_regex in self.passport_regex:
            passport_match = re.search(passport_regex, cleaned_text)
            if passport_match:
                passport_number = passport_match.group()
                cleaned_text = re.sub(passport_regex, '', cleaned_text, 1)
                break  # Stop after finding the first match

        return id_number, passport_number, cleaned_text.strip()


class CleaningSeparatingDeskripsi:
    """
    Class for dynamically separating the 'Deskripsi' column of a DataFrame into multiple
    'description_{seqNumber}' columns based on the content of bullet points or numbered items.
    """  # noqa

    def __init__(self):
        """
        Initializes the CleaningSeparatingDeskripsi instance.
        """
        self.split_regex = r'\n\s*(?:-\s+|\d+\.\s+|\*\s+)?(?=[^;\.,]*[;\.,]?\s*(?:-\s+|\d+\.\s+|\*\s+|$))'  # noqa

    def separating_cleaning_deskripsi(self, df):
        """
        Separates bullet points or numbered items in the 'Deskripsi' column into
        individual 'description_{seqNumber}' columns based on the maximum count of items
        found in the column. Removes the original 'Deskripsi' column afterward.

        Args:
            df (pd.DataFrame): The input DataFrame with a 'Deskripsi' column.

        Returns:
            pd.DataFrame: The processed DataFrame with separated description columns.
        """  # noqa
        max_items = self._find_max_descriptions(df['Deskripsi'])

        # Initialize and clean description columns
        # based on the maximum count of bullet points or numbered items
        description_cols = [f'description_{i+1}' for i in range(max_items)]
        for col in description_cols:
            df[col] = None

        for index, row in df.iterrows():
            descriptions = self._extract_descriptions(row['Deskripsi'])

            for i, desc in enumerate(descriptions):
                if i < max_items:
                    df.at[index, f'description_{i+1}'] = desc

        # Optionally remove the original 'Deskripsi' column if no longer needed
        df.drop(columns=['Deskripsi'], inplace=True)

        return df

    def _find_max_descriptions(self, descriptions):
        """
        Finds the maximum number of bullet points or numbered items in the 'Deskripsi' column.

        Args:
            descriptions (pd.Series): The 'Deskripsi' column of the DataFrame.

        Returns:
            int: The maximum count of descriptions found in any single row.
        """  # noqa
        counts = descriptions.apply(
            lambda text: len(
                re.split(
                    self.split_regex, text.strip())) - 1)
        return max(counts, default=0)

    def _extract_descriptions(self, text):
        """
        Extracts individual descriptions from the given text based on bullet points or numbering.

        Args:
            text (str): The text containing descriptions to extract.

        Returns:
            list: A list of extracted descriptions.
        """  # noqa
        descriptions = re.split(self.split_regex, text.strip())
        return [desc.strip() for desc in descriptions if desc.strip()]


class FormattingBirthDate:
    """
    A class to format birth dates from various formats to a standardized DD/MM/YYYY format.

    The class handles various date formats found in a 'Tgl lahir' column of a DataFrame,
    converting them to a consistent format. It also skips any date entries marked as '00/00/0000',
    treating them as invalid or placeholder values.

    Attributes:
        months_dict (dict): A dictionary mapping month names and abbreviations to their
                            numerical representations.
        date_pattern (re.Pattern): A compiled regular expression pattern used to identify
                                   and extract date components from text.
    """  # noqa

    def __init__(self):
        """
        Initializes the FormattingBirthDate instance, setting up the month dictionary and
        compiling the date pattern regular expression.
        """  # noqa
        self.months_dict = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
            'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
            'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
            'september': '09', 'oktober': '10',
            'november': '11', 'desember': '12'
        }  # noqa
        self.date_pattern = re.compile(r"""
            (?P<day>\d{1,2})
            [\s/-]
            (?P<month>[a-zA-Z]+|\d{1,2})
            [\s/-]
            (?P<year>\d{4}|\d{2})
            (?=[\s/-]?|$)
        """, re.VERBOSE | re.IGNORECASE)

    def format_birth_date(self, df):
        """
        Formats birth dates from the 'Tgl lahir' column of the input DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame containing a 'Tgl lahir' column.

        Returns:
            pd.DataFrame: The DataFrame with additional columns for formatted birth dates.
        """  # noqa
        for i in range(1, 4):
            df[f'birth_date_{i}'] = ""

        for index, row in df.iterrows():
            # Skip formatting if 'Tgl lahir' is "00/00/0000"
            if row['Tgl lahir'] == "00/00/0000":
                continue
            dates = self.extract_dates(row['Tgl lahir'])
            for i, date_str in enumerate(dates):
                if i >= 3:
                    break
                df.at[index, f'birth_date_{i+1}'] = date_str

        return df

    def extract_dates(self, text):
        """
        Extracts and formats dates from a text string containing one or more dates.

        Args:
            text (str): The input text from which to extract and format dates.

        Returns:
            list: A list of formatted dates as strings.
        """  # noqa
        if not isinstance(text, str) or text == "00/00/0000":
            return []
        matches = self.date_pattern.finditer(text)
        dates = [self._format_match(match) for match in matches]
        return dates

    def _format_match(self, match):
        """
        Formats a single date match into DD/MM/YYYY format.

        Args:
            match (re.Match): A regex match object containing date components.

        Returns:
            str: The formatted date string.
        """  # noqa
        day, month, year = match.group('day'), match.group('month'), match.group('year')  # noqa
        month_number = self._month_to_number(month)
        year = self._adjust_year(year)
        return f"{day.zfill(2)}/{month_number}/{year}"

    def _month_to_number(self, month):
        """
        Converts a month name or abbreviation to its numeric representation.

        Args:
            month (str): The month name or abbreviation.

        Returns:
            str: The numeric representation of the month, zero-padded to two digits.
        """  # noqa
        return self.months_dict.get(month.lower(), month.zfill(2))

    def _adjust_year(self, year):
        """
        Adjusts a two-digit year to a four-digit year based on a cutoff.

        Args:
            year (str): The year component of a date.

        Returns:
            str: The adjusted four-digit year.
        """  # noqa
        if len(year) == 2:
            return f"19{year}" if int(year) > 22 else f"20{year}"
        return year
