import os
import tempfile
import shutil
from django.test import TestCase
import pandas as pd
from documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber)
from openpyxl import Workbook
from pandas.testing import assert_frame_equal

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
        cls.processing_extract = ExtractNIKandPassportNumber()
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
                'Yayasan Abdi Mulia Sentosa',
            ],
            'Terduga': [
                'Orang',
                'Orang',
                'Korporasi'
            ]
        })

        # Processing input DataFrame to separate names and aliases
        processed_df = self.processing.extract_and_split_names(
            input_df)

        # Constructing the expected DataFrame
        expected_data = {
            'Nama': [
                'John Doe Alias Don John Alias John Krew',
                'Jane Elizabeth Smith Alias Yan Hitms',
                'Yayasan Abdi Mulia Sentosa'],
            'Terduga': [
                'Orang',
                'Orang',
                'Korporasi'],
            'first_name': [
                'John',
                'Jane',
                'Yayasan'],
            'middle_name': ['', 'Elizabeth', 'Abdi Mulia'],
            'last_name': ['Doe', 'Smith', 'Sentosa'],
            # Assuming 'extract_aliases_from_names'
            # dynamically adds 'Alias_name_1'
            'Alias_name_1': ['Don John', 'Yan Hitms', ''],
            'first_name_alias_1': ['Don', 'Yan', ''],
            'middle_name_alias_1': ['', '', ''],
            'last_name_alias_1': ['John', 'Hitms', ''],
            'Alias_name_2': ['John Krew', '', ''],
            'first_name_alias_2': ['John', '', ''],
            'middle_name_alias_2': ['', '', ''],
            'last_name_alias_2': ['Krew', '', ''],
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(
            processed_df,
            expected_df,
            check_like=True,
            check_dtype=False)

    def test_extract_idNumber_and_Paspor_fromDeskripsi_column(self):
        """Test extracting id_number from deskripsi name of column
        that has value `Orang` on `Terduga` column"""  # noqa
        # Given input DataFrame with 'Nama' column
        input_df = pd.DataFrame({
            "Terduga": [
                "Orang",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
            ],
            "Deskripsi": [
                """
                '- NIK nomor: 1234567898765432
                '- paspor A0987654
                '- pekerjaan: Karyawan Swasta
                """,
                """
                '- NIK 1232546589765954;
                '- paspor PA6574873
                '- diduga berada di Amerika
                '- relawan The SintoSintoBule
                """,
                """
                - NIK 9087654536287512;
                '- paspor 7865473 (dikeluarkan oleh madagascar);
                - pekerjaan Pegawai Negeri Sipil;
                """,
                """
                - didirikan pada tahun 1940 oleh Indriyana Nurhayati;
                - beberapa anggota terbutki secara sah melakukan penipuan
                '- kegiatan amal (Charity)
                """,
                """
                1. NIK 7765484598234123;
                2. no. paspor A 4876576
                3. saat ini berada di madagascar
                """,
                """
                - NIK 6654786328764102
                - Pendidikan SLTA/Sederajat
                - Yang bersangkutan tercatat dimana saja boleh
                - paspor B 5438675;
                """,
            ]
        })

        # Function to be tested
        processed_df = self.processing_extract.extract_nik_and_passport_number(
            input_df)

        # Expected output DataFrame
        expected_data = {
                'Terduga': [
                    'Orang',
                    'Orang',
                    'Orang',
                    'Korporasi',
                    'Orang',
                    'Orang'],
                "Deskripsi": ["""'- NIK nomor:
                '- paspor
                '- pekerjaan: Karyawan Swasta""", """'- NIK ;
                '- paspor
                '- diduga berada di Amerika
                '- relawan The SintoSintoBule""", """- NIK ;
                '- paspor  (dikeluarkan oleh madagascar);
                - pekerjaan Pegawai Negeri Sipil;""", """
                - didirikan pada tahun 1940 oleh Indriyana Nurhayati;
                - beberapa anggota terbutki secara sah melakukan penipuan
                - kegiatan amal (Charity)
                """, """1. NIK ;
                2. no. paspor
                3. saat ini berada di madagascar""", """- NIK
                - Pendidikan SLTA/Sederajat
                - Yang bersangkutan tercatat dimana saja boleh
                - paspor ;"""
            ],  # noqa
                'idNumber': [
                    '1234567898765432',
                    '1232546589765954',
                    '9087654536287512',
                    '',
                    '7765484598234123',
                    '6654786328764102'],
                'passport_number': [
                    'A0987654',
                    'PA6574873',
                    '7865473',
                    '',
                    'A 4876576',
                    'B 5438675',
                ]
            }
        expected_df = pd.DataFrame(expected_data)
        # Custom comparison logic for "Deskripsi" column
        similarities = []
        for processed_text, expected_text in zip(
                processed_df['Deskripsi'],
                expected_df['Deskripsi']):
            similarity = self.processing_extract.calculate_similarity(
                processed_text,
                expected_text)
            similarities.append(similarity)

        # Check if average similarity is above a threshold (e.g., 0.9 for 90% similarity)  # noqa
        average_similarity = sum(similarities) / len(similarities)
        print(f"Average similarity: {average_similarity}")
        self.assertTrue(
            average_similarity >= 0.95, "Average text similarity is below 95%")

        # For other columns where exact matches are expected,
        for column in ['Terduga', 'idNumber', 'passport_number']:
            assert_frame_equal(
                processed_df[[column]],
                expected_df[[column]],
                check_like=True,
                check_dtype=False)
