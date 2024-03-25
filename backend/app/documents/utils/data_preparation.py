import pandas as pd
import re


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
