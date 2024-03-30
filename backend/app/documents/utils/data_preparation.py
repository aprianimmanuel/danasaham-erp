import re
import pandas as pd  # noqa
from sklearn.metrics.pairwise import cosine_similarity  # noqa
from sklearn.feature_extraction.text import CountVectorizer  # noqa


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
    A class to extract and clean NIK (Nomor Induk Kependudukan) and
    passport numbers from a given DataFrame column. It utilizes regular
    expressions to identify and extract the relevant data, and then cleans
    the original text by removing the extracted parts. Additionally, it
    calculates the similarity between extracted patterns and original text
    using cosine similarity.

    Attributes:
        nik_patterns (list of str): A list of regex patterns for extracting NIK numbers.
        passport_patterns (list of str): A list of regex patterns for extracting passport numbers.
    """  # noqa
    def __init__(self):
        """Initialize the pattern lists for NIK and passport number extraction."""  # noqa
        self.nik_patterns = [
            r"\bNIK nomor:\s+(\d+)",
            r"\bNIK\s+(\d+)"
        ]

        self.passport_patterns = [
            r"(?:-?\s*\d*\.\s*)?-?\s*paspor\s+?\s*([A-Z0-9]+(?:\s?[A-Z0-9]+)*)\s*(?:\(dikeluarkan\s+oleh\s+[^\)]+\);?)?"  # noqa
        ]

    def vectorize_text(self, text1, text2):
        """
        Vectorize two strings for cosine similarity comparison.

        Args:
            text1 (str): The first text to be vectorized.
            text2 (str): The second text to be vectorized.

        Returns:
            numpy.ndarray: The array representation of vectorized texts.
        """
        vectorizer = CountVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return vectors

    def calculate_similarity(self, text1, text2):
        """
        Calculates the cosine similarity between two strings.

        Args:
            text1 (str): The first text to compare.
            text2 (str): The second text to compare.

        Returns:
            float: The cosine similarity score between the two texts.
        """
        vectors = self.vectorize_text(text1, text2)
        return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    def extract_with_highest_similarity(self, text, patterns):
        """
        Extracts data based on the highest similarity score between the text and regex pattern matches.
        Now simplified to only return the best match and the cleaned text.
        """  # noqa
        match_data = []  # Store tuples of (matched_text, similarity_score)

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = ''.join(match)
                if matched_text:
                    similarity = self.calculate_similarity(text, matched_text)
                    # Store matched text with its similarity score
                    match_data.append((matched_text, similarity))

        # Sort match_data by similarity score in descending order to pick the highest similarity  # noqa
        match_data.sort(key=lambda x: x[1], reverse=True)

        # Choose the match with the highest similarity that's less than 90%
        for matched_text, similarity in match_data:
            if similarity < 0.9:
                best_match = matched_text
                # Remove the best match from the text to clean it
                cleaned_text = re.sub(re.escape(best_match), '', text, flags=re.IGNORECASE).strip()  # noqa
                return best_match, cleaned_text

        # Fallback if no match or all matches are >= 90% similarity
        return "", text

    def extract_nik_and_passport_number(self, df):
        """
        Extracts NIK and passport numbers from the `Deskripsi` column of a dataframe,
        based on the highest similarity score, then cleans the text by removing the extracted information,
        and updates the dataframe with new columns for the extracted data.
        """  # noqa
        idNumbers, passportNumbers, cleanedDeskripsi = [], [], []

        for _, row in df.iterrows():
            if row['Terduga'] == 'Orang':
                nik_best_match, cleaned_text = self.extract_with_highest_similarity(row['Deskripsi'], self.nik_patterns)  # noqa
                passport_best_match, cleaned_text = self.extract_with_highest_similarity(cleaned_text, self.passport_patterns)  # noqa

                idNumbers.append(nik_best_match)
                passportNumbers.append(passport_best_match)
                cleanedDeskripsi.append(cleaned_text)
            else:
                idNumbers.append('')
                passportNumbers.append('')
                cleanedDeskripsi.append(row['Deskripsi'])

        df['idNumber'] = idNumbers
        df['passport_number'] = passportNumbers
        df['Deskripsi'] = cleanedDeskripsi

        return df
