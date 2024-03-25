import os
import tempfile
import shutil
from django.test import TestCase
import pandas as pd
from documents.utils.data_preparation import DTTOTDocumentProcessing
from openpyxl import Workbook

# Ensure that openpyxl is used for handling Excel files
pd.ExcelWriter = pd.ExcelWriter
pd.read_excel = pd.read_excel


class DTTOTDocumentProcessingCSVTests(TestCase):
    @classmethod
    def setUp(self):
        # Set up a temporary directory to hold the test files
        self.temp_dir = tempfile.mkdtemp()
        self.processing = DTTOTDocumentProcessing()
        # Example CSV content
        self.csv_content = """Nama,Deskripsi,Terduga
John Doe,Pemimpin Senior,Orang
Jane Smith,Guru Honorer,Orang"""
        # Create a test CSV file
        self.csv_file_path = os.path.join(self.temp_dir, 'test.csv')
        with open(self.csv_file_path, 'w') as f:
            f.write(self.csv_content)

    @classmethod
    def tearDown(self):
        # Remove the temporary directory and all its contents after the tests
        shutil.rmtree(self.temp_dir)

    def test_import_document_csv(self):
        """Test processing a DTTOT document uploaded as a CSV file."""
        df = self.processing.import_document(self.csv_file_path, 'CSV')
        expected_columns = ['Nama', 'Deskripsi', 'Terduga']
        self.assertEqual(list(df.columns), expected_columns)

    def test_extract_aliases_from_names(self):
        """Test extracting aliases from names based on ' Alias ' keyword."""
        # Instantiate the processing class
        processing = DTTOTDocumentProcessing()

        # Define a DataFrame with the 'Nama' column
        # containing names and aliases
        df = pd.DataFrame(
            {
                'Nama': [
                    'John Doe Alias Don Manuel John Alias John Krew',
                    'Jane Maria Smith Alias Yan Miths'
                ]
            }
        )

        # Process the DataFrame to extract aliases
        processed_df = processing.extract_and_split_names(
            df,
            name_column='Nama')

        # Define the expected DataFrame after alias extraction
        expected_df = pd.DataFrame({
            'Nama': [
                'John Doe Alias Don Manuel John Alias John Krew',
                'Jane Maria Smith Alias Yan Miths'],
            'first_name': ['John', 'Jane'],
            'middle_name': ['', 'Maria'],
            'last_name': ['Doe', 'Smith'],
            'Alias_name_1': ['Don Manuel John', 'Yan Miths'],
            'first_name_alias_1': ['Don', 'Yan'],
            'middle_name_alias_1': ['Manuel', ''],
            'last_name_alias_1': ['John', 'Miths'],
            'Alias_name_2': ['John Krew', ''],
            'first_name_alias_2': ['John', ''],
            'middle_name_alias_2': ['', ''],
            'last_name_alias_2': ['Krew', ''],
        })  # Fill NA values for consistency in comparison

        try:
            # Using assert_frame_equal from pandas testing module
            pd.testing.assert_frame_equal(
                processed_df,
                expected_df,
                check_like=True)
        except AssertionError as e:
            print("AssertionError caught!")
            print("DataFrame resulting from the processing:")
            print(processed_df)
            print("Expected DataFrame:")
            print(expected_df)
            raise e


class DTTOTDocumentProcessingXLSTests(TestCase):
    @classmethod
    def setUp(cls):
        # Create a temporary directory to hold the test files
        cls.temp_dir = tempfile.mkdtemp()
        cls.processing = DTTOTDocumentProcessing()
        # Create a test XLS file using openpyxl
        cls.xls_file_path = os.path.join(cls.temp_dir, 'test.xlsx')
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Nama", "Deskripsi", "Terduga"])
        sheet.append(["Sultan Aziz", "Pemimpin Senior", "Orang"])
        sheet.append(
            [
                "Yayasan Amal Indonesia",
                "Kegiatan Amal (Charity)",
                "Organisasi",
            ]
        )
        workbook.save(cls.xls_file_path)

    @classmethod
    def tearDown(cls):
        # Remove the temporary directory and all its contents after the tests
        shutil.rmtree(cls.temp_dir)

    def test_import_document_xls(self):
        """Test importing a document uploaded as an XLS file."""
        df = self.processing.import_document(self.xls_file_path, 'XLS')
        expected_columns = ['Nama', 'Deskripsi', 'Terduga']
        self.assertEqual(list(df.columns), expected_columns)
        self.assertTrue(not df.empty)

    def test_extract_aliases_from_names(self):
        """Test separating full names into first, middle, and last names."""
        # Given input DataFrame with 'Nama' column
        input_df = pd.DataFrame({
            'Nama': [
                'John Doe Alias Don John Alias John Krew',
                'Jane Elizabeth Smith Alias Yan Hitms',
            ]
        })

        # Processing input DataFrame to separate names and aliases
        processed_df = self.processing.extract_and_split_names(input_df)

        # Constructing the expected DataFrame
        expected_data = {
            'Nama': [
                'John Doe Alias Don John Alias John Krew',
                'Jane Elizabeth Smith Alias Yan Hitms'],
            'first_name': ['John', 'Jane'],
            'middle_name': ['', 'Elizabeth'],
            'last_name': ['Doe', 'Smith'],
            # Assuming 'extract_aliases_from_names'
            # dynamically adds 'Alias_name_1'
            'Alias_name_1': ['Don John', 'Yan Hitms'],
            'first_name_alias_1': ['Don', 'Yan'],
            'middle_name_alias_1': ['', ''],
            'last_name_alias_1': ['John', 'Hitms'],
            'Alias_name_2': ['John Krew', ''],
            'first_name_alias_2': ['John', ''],
            'middle_name_alias_2': ['', ''],
            'last_name_alias_2': ['Krew', ''],
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(
            processed_df,
            expected_df,
            check_like=True,
            check_dtype=False)
