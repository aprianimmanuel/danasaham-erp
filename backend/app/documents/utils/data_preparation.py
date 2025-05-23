from __future__ import annotations

import re
from typing import Any, Literal
from zipfile import BadZipFile

import pandas as pd  #type: ignore # noqa: PGH003


class DTTOTDocumentProcessing:
    def import_document(self, file_path: str, document_format: str) -> pd.DataFrame:
        """To import a document based on its format and returns a pandas DataFrame.

        Args:
        ----
            file_path (str): The path to the document file.
            document_format (str): The format of the document.
                Currently supported formats are 'CSV', 'XLS', and 'XLSX'.

        Returns:
        -------
            pd.DataFrame: The imported document as a pandas DataFrame.

        Raises:
        ------
            ValueError: If the document format is unsupported or the file is not a zip file.

        """
        try:
            # Check the document format and import the document accordingly
            if document_format == "CSV":
                return pd.read_csv(file_path)  # Import CSV file
            elif document_format == "XLS":  # noqa: RET505
                return pd.read_excel(file_path, engine="xlrd")  # Import XLS file
            elif document_format == "XLSX":
                return pd.read_excel(file_path, engine="openpyxl")  # Import XLSX file
            else:
                msg = f"Unsupported document format: {document_format}"
                raise ValueError(msg)
        except BadZipFile as e:
            # Raise an exception if the file is not a zip file
            msg = "File is not a zip file"
            raise ValueError(msg) from e

    def retrieve_data_as_dataframe(
            self,
            file_path: str,
            document_format: str,
        ) -> pd.DataFrame:
        """To Wrap the function to retrieve all data from a document into a pandas DataFrame.

        Args:
        ----
            file_path (str): The path to the document file.
            document_format (str): The format of the document ('CSV', 'XLS', or 'XLSX').

        Returns:
        -------
            DataFrame: The document data as a pandas DataFrame.

        """
        return self.import_document(file_path, document_format)

    def extract_and_split_names(
            self,
            df: pd.DataFrame,
            name_column: str,
            case_insensitive: Literal[False],
        ) -> pd.DataFrame:
        """To Extracts full names and aliases from a specified column in a DataFrame.

        then splits these names into first, middle, and last names.
        Adds new columns for each component of the name and its aliases.

        Args:
        ----
            df (DataFrame): The DataFrame containing the names.
            name_column (str): The column containing the names from which to extract aliases.
            case_insensitive (bool): Whether to process names in a case-insensitive manner.

        Returns:
        -------
            DataFrame: The DataFrame with additional columns for name components.

        """
        def split_name(
                name: str,
            ) -> tuple[str, str, str]:
            """To splits a name into first, middle, and last components.

            Args:
            ----
                name (str): The name to split.

            Returns:
            -------
                tuple: A tuple containing the first, middle, and last components of the name.

            """
            # Check if the name is a string
            if not isinstance(name, str):
                return "", "", ""
            parts = name.strip().split()
            if len(parts) >= 3:  # noqa: PLR2004
                return parts[0], " ".join(parts[1:-1]), parts[-1]
            elif len(parts) == 2:  # noqa: PLR2004, RET505
                return parts[0], "", parts[1]
            elif len(parts) == 1:
                return parts[0], "", ""
            return "", "", ""

        def split_aliases(
                name: str,
            ) -> list[str]:
            """To splits a name into aliases.

            Args:
            ----
                name (str): The name to split.

            Returns:
            -------
                list: A list containing the aliases of the name.

            """
            # Check if the name is a string
            if case_insensitive:
                name = name.lower()
                return name.split(" alias ")[1:] if " alias " in name else []
            else:  # noqa: RET505
                parts = name.split(" Alias ")
                aliases = parts[1:] if len(parts) > 1 else []
                if not aliases:
                    parts = name.split(" alias ")
                    aliases = parts[1:] if len(parts) > 1 else []
                return aliases

        # Initialize the full name column
        df["full_name"] = df[name_column].apply(
           lambda x: re.split(r"(?i)\s*alias\s*", x, 1)[0] if isinstance(x, str) else "",  # noqa: B034
        )

        # Extract first, middle, and last names from the full_name
        df[["first_name", "middle_name", "last_name"]] = (
            df["full_name"].apply(split_name).tolist()
        )

        # Extract all aliases from the name column
        df["aliases"] = df[name_column].apply(split_aliases)

        # Find the maximum number of aliases in any row to determine the number of fields
        max_aliases = df["aliases"].str.len().max()

        # Process each alias and split into name components
        for i in range(max_aliases):
            alias_col = f"Alias_name_{i+1}"
            df[alias_col] = df["aliases"].apply(
                lambda aliases: aliases[i] if len(aliases) > i else "",  # noqa: B023
            )
            df[
                [
                    f"first_name_alias_{i+1}",
                    f"middle_name_alias_{i+1}",
                    f"last_name_alias_{i+1}",
                ]
            ] = df[alias_col].apply(split_name).tolist()

        return df


class ExtractNIKandPassportNumber:
    """To accurately identify and extract numerical and alphanumeric sequences.

    Post-extraction, the original text from which these numbers are extracted is cleaned by removing the identified numbers, enhancing the clarity and utility of the dataset.

    Attributes
    ----------
        nik_regex (list of str): Contains regex patterns designed to match NIK numbers,
                                  which typically consist of a 16-digit sequence.
        passport_regex (list of str): Contains regex patterns aimed at identifying
                                       passport numbers, which may include up to two
                                       letters followed by six or more digits, with an
                                       optional space between letters and digits.

    """

    def __init__(self) -> None:
        """To initializes the ExtractNIKandPassportNumber class with specific regex patterns for identifying NIK and passport numbers within text.

        Returns
        -------
            None

        """
        self.nik_regex = re.compile(
            r"(\b\d{16}\b)",
        )  # Pattern for NIK numbers with a capture group
        self.passport_regex = re.compile(
            r"(\b[A-Z]{0,2}\s*\d{6,}\b)",
        )  # Pattern for passport numbers with a capture group

    def extract_nik_and_passport_number(
            self,
            df: pd.DataFrame,
        ) -> pd.DataFrame:
        """To extract NIK and passport numbers from the specified description columns in a DataFrame and updates the DataFrame directly with extracted values and cleaned descriptions.

        Args:
        ----
            df (pd.DataFrame): The input DataFrame containing description columns.

        Returns:
        -------
            pd.DataFrame: The modified DataFrame with NIK and passport numbers extracted
                          and description texts cleaned.


        """
        # Ensure all description columns
        # are strings and fill NaN with empty strings
        description_columns = self._detect_description_columns(df)
        if not description_columns:
            return df  # Return early if no description columns are found

        # Initialize columns to hold extracted NIK and passport numbers
        df["idNumber"] = ""
        df["passport_number"] = ""

        # Apply regex to all description columns at once
        for column in description_columns:
            df["idNumber"] = (
                df[column]
                .str.extract(self.nik_regex, expand=False)
                .fillna(df["idNumber"])
            )
            df["passport_number"] = (
                df[column]
                .str.extract(self.passport_regex, expand=False)
                .fillna(df["passport_number"])
            )

            # Clean the description text
            df[column] = (
                df[column]
                .str.replace(self.nik_regex, "", regex=True)
                .str.replace(self.passport_regex, "", regex=True)
                .str.strip()
            )

        return df

    def _detect_description_columns(
            self,
            df: pd.DataFrame,
        ) -> list[str]:
        """To identify columns within the DataFrame that likely contain descriptive texts for extracting NIK and passport numbers.

        Args:
        ----
            df (pd.DataFrame): The input DataFrame.

        Returns:
        -------
            list[str]: A list of column names that contain descriptive texts.

        """
        return [col for col in df.columns if "description" in col.lower()]

    def _clean_description(
            self,
            text: str,
        ) -> str:
        """To clean the description text by removing detected NIK and passport numbers.

        Args:
        ----
            text (str): The input text to be cleaned.

        Returns:
        -------
            str: The cleaned text.

        """
        text = self.nik_regex.sub("", text)
        text = self.passport_regex.sub("", text)
        return text.strip()


class CleaningSeparatingDeskripsi:
    """To separate the 'Deskripsi' column of a DataFrame into multiple 'description_{seqNumber}' columns based on the content of bullet points or numbered items.

    Attributes
    ----------
        split_regex (str): A regular expression pattern used to split the 'Deskripsi' column into multiple 'description_{seqNumber}' columns.

    Methods
    -------
        separating_cleaning_deskripsi(df)

    """

    def __init__(self) -> None:
        """To initialize the CleaningSeparatingDeskripsi instance."""
        self.split_regex = r"\n\s*(?:-\s+|\d+\.\s+|\*\s+)?(?=[^;\.,]*[;\.,]?\s*(?:-\s+|\d+\.\s+|\*\s+|$))"

    def separating_cleaning_deskripsi(
            self,
            df: pd.DataFrame,
        ) -> pd.DataFrame:
        """To separate bullet points or numbered items in the 'Deskripsi' column into individual 'description_{seqNumber}' columns based on the maximum count of items found in the column and to remove the original 'Deskripsi' column afterward.

        Args:
        ----
            df (pd.DataFrame): The input DataFrame with a 'Deskripsi' column.

        Returns:
        -------
            pd.DataFrame: The processed DataFrame
            with separated description columns.

        """
        df["Deskripsi"] = df["Deskripsi"].fillna("").astype(str)
        max_items = self._find_max_descriptions(df["Deskripsi"])

        description_cols = [f"description_{i+1}" for i in range(max_items)]
        for col in description_cols:
            df[col] = None

        for index, row in df.iterrows():
            descriptions = self._extract_descriptions(row["Deskripsi"])
            for i, desc in enumerate(descriptions):
                if i < max_items:
                    df.at[index, f"description_{i+1}"] = desc  # noqa: PD008

        return df.drop(columns=["Deskripsi"])

    def _find_max_descriptions(
            self,
            descriptions: pd.Series,
        ) -> int:
        """To find the maximum number of bullet points or numbered items in the 'Deskripsi' column.

        Args:
        ----
            descriptions (pd.Series): The 'Deskripsi' column of the DataFrame.

        Returns:
        -------
            int: The maximum count of descriptions found in any single row.

        """
        counts = descriptions.apply(
            lambda text: len(re.split(self.split_regex, text.strip())) - 1,
        )
        return counts.max()

    def _extract_descriptions(
            self,
            text: str,
        ) -> list[str]:
        """To extract individual descriptions from the given text based on bullet points or numbering.

        Args:
        ----
            text (str): The text containing descriptions to extract.

        Returns:
        -------
            list: A list of extracted descriptions.

        """
        descriptions = re.split(self.split_regex, text.strip())
        return [desc.strip() for desc in descriptions if desc.strip()]


class FormattingColumn:
    """To format birth dates from various formats to a standardized DD/MM/YYYY format.

    The class handles various date formats found in a 'Tgl Lahir' column of a DataFrame,
    converting them to a consistent format. It also skips any date entries marked as '00/00/0000',
    treating them as invalid or placeholder values.

    Attributes
    ----------
        months_dict (dict): A dictionary mapping month names and abbreviations to their
                            numerical representations.
        date_pattern (re.Pattern): A compiled regular expression pattern used to identify
                                   and extract date components from text.

    """

    def __init__(self) -> None:
        """To initialize the FormattingColumn instance, setting up the month dictionary and to compiling the date pattern regular expression."""
        self.months_dict = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
            "januari": "01",
            "februari": "02",
            "maret": "03",
            "april": "04",
            "mei": "05",
            "juni": "06",
            "juli": "07",
            "agustus": "08",
            "september": "09",
            "oktober": "10",
            "november": "11",
            "desember": "12",
        }

        self.date_pattern = re.compile(
            r"""
            (?P<day>\d{1,2})
            [\s/-]
            (?P<month>[a-zA-Z]+|\d{1,2})
            [\s/-]
            (?P<year>\d{4}|\d{2})
            | # Alternative pattern
            (?P<day2>\d{1,2})\s+
            (?P<month2>[a-zA-Z]+)\s+
            (?P<year2>\d{4})
        """,
            re.VERBOSE | re.IGNORECASE,
        )

        self.country_dict = {
            "Afghanistan": "Afghanistan",
            "Albania": "Albania",
            "Algeria": "Algeria",
            "Aljazair": "Algeria",
            "Andorra": "Andorra",
            "Angola": "Angola",
            "Antigua dan Barbuda": "Antigua and Barbuda",
            "Argentina": "Argentina",
            "Armenia": "Armenia",
            "Austria": "Austria",
            "Australia": "Australia",
            "Azerbaijan": "Azerbaijan",
            "Amerika Serikat": "United States of America",
            "Bahrain": "Bahrain",
            "Bangladesh": "Bangladesh",
            "Barbados": "Barbados",
            "Belarus": "Belarus",
            "Belgium": "Belgium",
            "Belize": "Belize",
            "Benin": "Benin",
            "Bhutan": "Bhutan",
            "Bolivia": "Bolivia",
            "Bosnia dan Herzegovina": "Bosnia and Herzegovina",
            "Botswana": "Botswana",
            "Brazil": "Brazil",
            "Brunei": "Brunei",
            "Bulgaria": "Bulgaria",
            "Burkina Faso": "Burkina Faso",
            "Burundi": "Burundi",
            "Bosnia Herzegonia": "Bosnia and Herzegovina",
            "Cabo Verde": "Cabo Verde",
            "Kamboja": "Cambodia",
            "Kamerun": "Cameroon",
            "Kanada": "Canada",
            "Republik Afrika Tengah": "Central African Republic",
            "Chad": "Chad",
            "Channel Islands": "Channel Islands",
            "Cile": "Chile",
            "Cina": "China",
            "Kolombia": "Colombia",
            "Comoros": "Comoros",
            "Congo": "Congo",
            "Costa Rica": "Costa Rica",
            "Côte d'Ivoire": "Côte d'Ivoire",
            "Kroasia": "Croatia",
            "Kuba": "Cuba",
            "Siprus": "Cyprus",
            "Czech Republic": "Czech Republic",
            "Denmark": "Denmark",
            "Djibouti": "Djibouti",
            "Dominica": "Dominica",
            "Republik Dominika": "Dominican Republic",
            "Republik Congo": "Democratic Republic of the Congo",
            "Ekuador": "Ecuador",
            "Mesir": "Egypt",
            "El Salvador": "El Salvador",
            "Equatorial Guinea": "Equatorial Guinea",
            "Eritrea": "Eritrea",
            "Estonia": "Estonia",
            "Eswatini": "Eswatini",
            "Ethiopia": "Ethiopia",
            "Faeroe Islands": "Faeroe Islands",
            "Finlandia": "Finland",
            "Perancis": "France",
            "French Guiana": "French Guiana",
            "Fiji": "Fiji",
            "Gabon": "Gabon",
            "Gambia": "Gambia",
            "Georgia": "Georgia",
            "Jerman": "Germany",
            "Ghana": "Ghana",
            "Gibraltar": "Gibraltar",
            "Yunani": "Greece",
            "Grenada": "Grenada",
            "Guatemala": "Guatemala",
            "Guinea": "Guinea",
            "Guinea-Bissau": "Guinea-Bissau",
            "Guyana": "Guyana",
            "Haiti": "Haiti",
            "Holy See": "Holy See",
            "Honduras": "Honduras",
            "Hong Kong": "Hong Kong",
            "Hungaria": "Hungary",
            "Islandia": "Iceland",
            "India": "India",
            "Indonesia": "Indonesia",
            "Iran": "Iran",
            "Irak": "Iraq",
            "Irlandia": "Ireland",
            "Isle of Man": "Isle of Man",
            "Israel": "Israel",
            "Italia": "Italy",
            "Jamaika": "Jamaica",
            "Jepang": "Japan",
            "Yordania": "Jordan",
            "Laos": "Laos",
            "Latvia": "Latvia",
            "Lebanon": "Lebanon",
            "Lesotho": "Lesotho",
            "Liberia": "Liberia",
            "Libya": "Libya",
            "Liechtenstein": "Liechtenstein",
            "Lithuania": "Lithuania",
            "Luxembourg": "Luxembourg",
            "Macao": "Macao",
            "Madagaskar": "Madagascar",
            "Malawi": "Malawi",
            "Malaysia": "Malaysia",
            "Maldives": "Maldives",
            "Mali": "Mali",
            "Malta": "Malta",
            "Mauritania": "Mauritania",
            "Mauritius": "Mauritius",
            "Mayotte": "Mayotte",
            "Mexico": "Mexico",
            "Moldova": "Moldova",
            "Monaco": "Monaco",
            "Mongolia": "Mongolia",
            "Montenegro": "Montenegro",
            "Maroko": "Morocco",
            "Mozambique": "Mozambique",
            "Myanmar": "Myanmar",
            "Namibia": "Namibia",
            "Nepal": "Nepal",
            "Netherlands": "Netherlands",
            "Nikaragua": "Nicaragua",
            "Niger": "Niger",
            "Nigeria": "Nigeria",
            "Korea Utara": "North Korea",
            "North Macedonia": "North Macedonia",
            "Nauru": "Nauru",
            "Norwegia": "Norway",
            "New Zealand": "New Zealand",
            "Oman": "Oman",
            "Palestina": "Palestine",
            "Pakistan": "Pakistan",
            "Panama": "Panama",
            "Paraguay": "Paraguay",
            "Peru": "Peru",
            "Filipina": "Philippines",
            "Polandia": "Poland",
            "Portugal": "Portugal",
            "Palau": "Palau",
            "Papua Nugini": "Papua New Guinea",
            "Qatar": "Qatar",
            "Republik Arab Suriah": "Syria",
            "Réunion": "Réunion",
            "Rumania": "Romania",
            "Rusia": "Russia",
            "Rwanda": "Rwanda",
            "Saint Helena": "Saint Helena",
            "Saint Kitts and Nevis": "Saint Kitts and Nevis",
            "Saint Lucia": "Saint Lucia",
            "Saint Vincent and the Grenadines": "Saint Vincent and the Grenadines",
            "San Marino": "San Marino",
            "Sao Tome & Principe": "Sao Tome & Principe",
            "Pulau Solomon": "Solomon Islands",
            "Arab Saudi": "Saudi Arabia",
            "Senegal": "Senegal",
            "Serbia": "Serbia",
            "Seychelles": "Seychelles",
            "Sierra Leone": "Sierra Leone",
            "Singapura": "Singapore",
            "Slovakia": "Slovakia",
            "Slovenia": "Slovenia",
            "Somalia": "Somalia",
            "Afrika Selatan": "South Africa",
            "Korea Selatan": "South Korea",
            "South Sudan": "South Sudan",
            "Spanyol": "Spain",
            "Sri Lanka": "Sri Lanka",
            "Sudan": "Sudan",
            "Suriname": "Suriname",
            "Swedia": "Sweden",
            "Swiss": "Switzerland",
            "Suriah": "Syria",
            "Taiwan": "Taiwan",
            "Tajikistan": "Tajikistan",
            "Tanzania": "Tanzania",
            "Thailand": "Thailand",
            "Bahamas": "The Bahamas",
            "Timor-Leste": "Timor-Leste",
            "Togo": "Togo",
            "Trinidad dan Tobago": "Trinidad and Tobago",
            "Tunisia": "Tunisia",
            "Turki": "Turkey",
            "Turkmenistan": "Turkmenistan",
            "Uganda": "Uganda",
            "Ukraina": "Ukraine",
            "Uni Emirat Arab": "United Arab Emirates",
            "United Kingdom": "United Kingdom",
            "Uzbekistan": "Uzbekistan",
            "Uruguay": "Uruguay",
            "Venezuela": "Venezuela",
            "Vietnam": "Vietnam",
            "Western Sahara": "Western Sahara",
            "Yaman": "Yemen",
            "Zambia": "Zambia",
            "Zimbabwe": "Zimbabwe",
        }

    @staticmethod
    def _calculate_similarity(
        str1: str,
        str2: str,
    ) -> float:
        """To calculate the similarity percentage between two strings using Levenshtein distance.

        Args:
        ----
            str1 (str): First string for comparison.
            str2 (str): Second string for comparison.

        Returns:
        -------
            float: The similarity percentage between the two strings.

        """
        len_str1, len_str2 = len(str1), len(str2)
        max_len = max(len_str1, len_str2)
        if max_len == 0:
            return 100.0  # Both strings are empty, considered 100% similar

        # Create a matrix to calculate distances
        matrix = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

        # Initialize the matrix
        for i in range(len_str1 + 1):
            matrix[i][0] = i
        for j in range(len_str2 + 1):
            matrix[0][j] = j

        # Calculate distances
        for i in range(1, len_str1 + 1):
            for j in range(1, len_str2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # Deletion
                    matrix[i][j - 1] + 1,  # Insertion
                    matrix[i - 1][j - 1] + cost,
                )  # Substitution

        distance = matrix[len_str1][len_str2]
        return ((max_len - distance) / max_len) * 100

    def format_birth_date(
            self,
            df: pd.DataFrame,
        ) -> pd.DataFrame:
        """To format birth dates from the 'Tgl lahir' column of the input DataFrame.

        Args:
        ----
            df (pd.DataFrame): The input DataFrame containing a 'Tgl lahir' column.

        Returns:
        -------
            pd.DataFrame: The DataFrame with additional columns for formatted birth dates.

        """
        for i in range(1, 4):
            df[f"birth_date_{i}"] = ""

        for index, row in df.iterrows():
            # Skip formatting if 'Tgl lahir' is "00/00/0000"
            if row["Tgl Lahir"] == "00/00/0000":
                continue
            dates = self.extract_dates(row["Tgl Lahir"])
            for i, date_str in enumerate(dates):
                if i >= 3:  # noqa: PLR2004
                    break
                df.at[index, f"birth_date_{i+1}"] = date_str  # noqa: PD008

        return df

    def extract_dates(
            self,
            text: str,
        ) -> list:
        """To extract and format dates from a text string containing one or more dates.

        Args:
        ----
            text (str): The input text from which to extract and format dates.

        Returns:
        -------
            list: A list of formatted dates as strings.

        """
        if not isinstance(text, str) or text == "00/00/0000":
            return []
        matches = self.date_pattern.finditer(text)
        return [self._format_match(match) for match in matches]

    def _format_match(
            self,
            match: re.Match,
        ) -> str:
        """To format a single date match into YYYY/MM/DD format."""
        day = match.group("day") or match.group("day2")
        month = match.group("month") or match.group("month2")
        year = match.group("year") or match.group("year2")

        month_number = month.zfill(2) if month.isdigit() else self._month_to_number(month)

        year = self._adjust_year(year)
        return f"{year}/{month_number}/{day.zfill(2)}"

    def _month_to_number(
            self,
            month: str,
        ) -> str:
        """To convert a month name or abbreviation to its numeric representation.

        Args:
        ----
            month (str): The month name or abbreviation.

        Returns:
        -------
            str: The numeric representation of the month, zero-padded to two digits.

        """
        return self.months_dict.get(month.lower(), month.zfill(2))

    def _adjust_year(
            self,
            year: str,
        ) -> str:
        """To adjust a two-digit year to a four-digit year based on a cutoff.

        Args:
        ----
            year (str): The year component of a date.

        Returns:
        -------
            str: The adjusted four-digit year.

        """
        if len(year) == 2:  # noqa: PLR2004
            return f"19{year}" if int(year) > 22 else f"20{year}"  # noqa: PLR2004
        return year

    def format_nationality(
            self,
            df: pd.DataFrame,
        ) -> pd.DataFrame:
        """To process and format the 'WN' column of the input DataFrame, standardizing nationality information and splitting into multiple columns if necessary.

        Args:
        ----
            df (pd.DataFrame): The input DataFrame containing a 'WN' column.

        Returns:
        -------
            pd.DataFrame: The DataFrame with formatted and possibly split nationality information.

        """
        # Initialize new columns for the potentially split nationalities
        df["WN_1"], df["WN_2"] = "", ""

        for index, row in df.iterrows():
            nationalities = self._clean_and_split_nationality(row["WN"])
            if len(nationalities) > 0:
                df.at[index, "WN_1"] = self._standardize_country_name(  # noqa: PD008
                    nationalities[0],
                )
            if len(nationalities) > 1:
                df.at[index, "WN_2"] = self._standardize_country_name(  # noqa: PD008
                    nationalities[1],
                )

        return df

    def _clean_and_split_nationality(
            self,
            nationality_str: str,
        ) -> list:
        """To clean, split, and standardize the nationality string into a list of standardized nationalities, based on the `country_dict`. If there are differences between the raw nationality and the dictionary entries, those are cleaned and standardized.

        Args:
        ----
            nationality_str (str): The raw nationality string from the 'WN' column.

        Returns:
        -------
            list: A list of cleaned, split, and potentially standardized nationalities.


        """
        # If the input is not a string, return an empty list
        if not isinstance(nationality_str, str):
            return []

        # Remove known extraneous phrases and split by commas or semicolons
        cleaned_str = re.sub(r"(;|,|/)", "-", nationality_str)
        split_nationalities = [
            nat.strip() for nat in cleaned_str.split("-") if nat.strip()
        ]

        # Standardize each nationality
        standardized_nationalities = []
        for nationality in split_nationalities:
            standardized = self._standardize_country_name(nationality)
            if standardized:
                standardized_nationalities.append(standardized)
            else:
                # If no standardization is found, keep the original
                standardized_nationalities.append(nationality)

        return standardized_nationalities

    def _standardize_country_name(
            self,
            country_name: str,
        ) -> Any:
        """To standardize a country name based on known variations and similarity comparison, choosing the closest match from `country_dict` based on the highest similarity score.

        Args:
        ----
            country_name (str): The raw country name to standardize.

        Returns:
        -------
            str: The standardized country name if a similar name is found in the dictionary with the highest similarity
                score; otherwise, the input name.

        """
        best_score: float = 0
        best_match = None
        for key, standardized_name in self.country_dict.items():
            score = self._calculate_similarity(country_name.lower(), key.lower())
            if score > best_score:
                best_score = score
                best_match = standardized_name

        if best_score >= 85:  # noqa: PLR2004
            return best_match
        return country_name


def process_data(
        file_path: str,
        document_format: str,
    ) -> pd.DataFrame:
    processor = DTTOTDocumentProcessing()
    df = processor.retrieve_data_as_dataframe(file_path, document_format)  # noqa: PD901

    df = processor.extract_and_split_names(  # noqa: PD901
        df,
        "Nama",
        False,
    )

    extractor = ExtractNIKandPassportNumber()
    df = extractor.extract_nik_and_passport_number(df)  # noqa: PD901

    cleaner = CleaningSeparatingDeskripsi()
    df = cleaner.separating_cleaning_deskripsi(df)  # noqa: PD901

    formatter = FormattingColumn()
    df = formatter.format_birth_date(df)  # noqa: PD901
    return formatter.format_nationality(df)
