import os
import tempfile
import shutil
from django.test import TestCase
import pandas as pd
from app.config.documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    CleaningSeparatingDeskripsi,
    FormattingColumn)
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
            df, 'Nama')

        # Define the expected DataFrame after alias extraction
        expected_df = pd.DataFrame({
            'Nama': [
                'John Doe Alias Don Manuel John Alias John Krew',
                'Jane Maria Smith Alias Yan Miths'],
            'full_name': [
                'John Doe',
                'Jane Maria Smith'
            ],
            'aliases': [
                ['Don Manuel John', 'John Krew'],
                ['Yan Miths']
            ],
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
    """
    A set of unit tests designed to verify the functionality of document processing
    related to XLS files within the DTTOT document processing framework. This class
    focuses on testing the ability to import XLS documents, as well as the extraction
    of specific data from those documents, such as alias information from names and
    organization types from descriptions.

    The tests ensure that XLS documents are correctly imported, and that data extraction
    follows expected patterns and yields accurate results.

    Attributes:
        temp_dir (str): A directory created to temporarily store test files.
        processing_extract (ExtractNIKandPassportNumber): An instance of the class used to extract NIK and passport numbers.
        processing (DTTOTDocumentProcessing): An instance of the class under test that processes documents.
        xls_file_path (str): The file path to the test XLS document created for testing.
    """  # noqa
    @classmethod
    def setUp(cls):
        """
        Set up the test environment before running each test in the class. This method
        creates a temporary directory to hold test XLS files and initializes instances
        of the document processing classes. It also creates a sample XLS file to be used
        in the tests.
        """  # noqa
        # Create a temporary directory to hold the test files
        cls.temp_dir = tempfile.mkdtemp()
        cls.processing_extract = ExtractNIKandPassportNumber()
        cls.processing = DTTOTDocumentProcessing()
        cls.processing_separating = CleaningSeparatingDeskripsi()
        cls.processing_formatting = FormattingColumn()
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
        """
        Tear down the test environment after each test in the class has run. This method
        removes the temporary directory and all its contents, cleaning up the test environment.
        """  # noqa
        # Remove the temporary directory and all its contents after the tests
        shutil.rmtree(cls.temp_dir)

    def test_import_document_xls(self):
        """
        Test the functionality of importing a document uploaded as an XLS file. This test
        verifies that the imported document has the expected columns and is not empty.
        """  # noqa
        df = self.processing.import_document(self.xls_file_path, 'XLSX')
        expected_columns = ['Nama', 'Deskripsi', 'Terduga']
        self.assertEqual(list(df.columns), expected_columns)
        self.assertTrue(not df.empty)

    def test_extract_aliases_from_names(self):
        """
        Test the extraction of aliases from full names within the imported document. This test
        checks whether the extraction and separation of names and aliases are performed accurately,
        comparing the processed DataFrame against an expected structure.
        """  # noqa
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
            input_df, 'Nama')

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
            'full_name': [
                'John Doe',
                'Jane Elizabeth Smith',
                'Yayasan Abdi Mulia Sentosa'
            ],
            'aliases': [
                ['Don John', 'John Krew'],
                ['Yan Hitms'],
                []
            ],
            'first_name': [
                'John',
                'Jane',
                'Yayasan'],
            'middle_name': ['', 'Elizabeth', 'Abdi Mulia'],
            'last_name': ['Doe', 'Smith', 'Sentosa'],
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
        """Test extracting id_number and passport_number from separated description columns
        where 'Terduga' has the value 'Orang'."""  # noqa
        # Given input DataFrame with separated description columns
        input_df = pd.DataFrame({
            "Terduga": [
                "Orang", "Orang", "Orang", "Korporasi", "Orang", "Orang",
            ],
            "description_1": [
                "- NIK nomor: 1234567898765432",
                "- NIK 1232546589765954;",
                "- NIK 9087654536287512;",
                "- didirikan pada tahun 1940 oleh Indriyana Nurhayati;",
                "1. NIK 7765484598234123;",
                "- NIK 6654786328764102"
            ],
            "description_2": [
                "- paspor A0987654",
                "- paspor PA6574873",
                "- paspor 7865473 (dikeluarkan oleh madagascar);",
                "beberapa anggota terbutki secara sah melakukan penipuan",
                "no. paspor A 4876576",
                "Pendidikan SLTA/Sederajat"
            ],
            "description_3": [
                "- pekerjaan: Karyawan Swasta",
                "- diduga berada di Amerika",
                "pekerjaan Pegawai Negeri Sipil;",
                "- kegiatan amal (Charity)",
                "saat ini berada di madagascar",
                "Yang bersangkutan tercatat dimana saja boleh"
            ],
            "description_4": [
                "",
                "- relawan The SintoSintoBule",
                "",
                "",
                "",
                "- paspor B 5438675;"
            ]
        })

        # Function to be tested
        processed_df = self.processing_extract.extract_nik_and_passport_number(input_df)  # noqa

        # Expected output DataFrame
        expected_data = {
            'Terduga': ["Orang", "Orang", "Orang", "Korporasi", "Orang", "Orang"],  # noqa
            "description_1": ["- NIK nomor:", "- NIK ;", "- NIK ;", "- didirikan pada tahun 1940 oleh Indriyana Nurhayati;", "1. NIK ;", "- NIK"],  # noqa
            "description_2": ["- paspor", "- paspor", "- paspor (dikeluarkan oleh madagascar);", "beberapa anggota terbutki secara sah melakukan penipuan", "no. paspor", "Pendidikan SLTA/Sederajat"],  # noqa
            "description_3": ["- pekerjaan: Karyawan Swasta", "- diduga berada di Amerika", "pekerjaan Pegawai Negeri Sipil;", "- kegiatan amal (Charity)", "saat ini berada di madagascar", "Yang bersangkutan tercatat dimana saja boleh"],  # noqa
            "description_4": ["", "- relawan The SintoSintoBule", "", "", "", "- paspor ;"],  # noqa
            'idNumber': ['1234567898765432', '1232546589765954', '9087654536287512', '', '7765484598234123', '6654786328764102'],  # noqa
            'passport_number': ['A0987654', 'PA6574873', ' 7865473', '', 'A 4876576', 'B 5438675']  # noqa
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert equality between processed_df and expected_df for relevant columns  # noqa
        pd.testing.assert_frame_equal(
            processed_df[
                [
                    'Terduga',
                    'description_1',
                    'description_2',
                    'description_3',
                    'description_4',
                    'idNumber',
                    'passport_number']
                ],
            expected_df,
            check_like=True,
            check_dtype=False
        )

    def test_separating_description(self):
        """
        Test separating per bulletpoint in `Deskripsi` column to sequennce of
        description column (description_{number of sequence})
        """
        input_df = pd.DataFrame(
            {
                "Kode_ID": [
                    "EDD-013", "IDD-015", "ILQ-O54", "EDD-033", "ILQ-022", "IDD-021", "EDD-011"  # noqa
                ],
                "Terduga": [
                    "Orang", "Orang", "Orang", "Korporasi", "Orang", "Orang", "Orang"  # noqa
                ],
                "Deskripsi": [
                    """'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta""",  # noqa
                    """'- NIK 1232546589765954;\n'- paspor PA6574873\n'- diduga berada di Amerika\n'- relawan The SintoSintoBule""",  # noqa
                    """- NIK 9087654536287512;\n'- paspor 7865473 (dikeluarkan oleh madagascar);\n- pekerjaan Pegawai Negeri Sipil;""",  # noqa
                    """- didirikan pada tahun 1940 oleh Indriyana Nurhayati;\n- beberapa anggota terbutki secara sah melakukan penipuan\n'- kegiatan amal (Charity)""",  # noqa
                    """1. NIK 7765484598234123;\n2. no. paspor A 4876576\n3. saat ini berada di madagascar""",  # noqa
                    """- NIK 6654786328764102\n- Pendidikan SLTA/Sederajat\n- Yang bersangkutan tercatat dimana saja boleh\n- paspor B 5438675;""",  # noqa
                    """'- Terafiliasi dengan madagascar;\n'- NIK 2234574598760954;\n'- Badut banget sih;"""  # noqa
                    ]
            }
        )

        max_descriptions = self.processing_separating._find_max_descriptions(input_df['Deskripsi']) # noqa

        # Function to be tested
        processed_df = self.processing_separating.separating_cleaning_deskripsi(input_df)  # noqa

        # Check if description columns exist and correspond
        # to the maximum bullet points in any 'Deskripsi' entry
        description_columns = [
            f'description_{i+1}' for i in range(max_descriptions)]
        self.assertTrue(
            all(
                column in processed_df.columns for column in description_columns  # noqa
            ), "Missing description columns")

        # Expected output DataFrame
        expected_data = {
            "Kode_ID": [
                "EDD-013", "IDD-015", "ILQ-O54", "EDD-033", "ILQ-022", "IDQ-021", "EDD-011"  # noqa
            ],
            'Terduga': [
                'Orang', 'Orang', 'Orang', 'Korporasi', 'Orang', 'Orang', "Orang"  # noqa
            ],
            "description_1": [
                "'- NIK nomor: 1234567898765432", "'- NIK 1232546589765954;", "- NIK 9087654536287512;", "- didirikan pada tahun 1940 oleh Indriyana Nurhayati;", "1. NIK 7765484598234123;", "- NIK 6654786328764102", "'- Terafiliasi dengan madagascar;"  # noqa
            ],
            "description_2": [
                "'- paspor nomor: A0987654", "'- paspor PA6574873", "'- paspor 7865473 (dikeluarkan oleh madagascar);", "beberapa anggota terbutki secara sah melakukan penipuan", "2. no. paspor A 4876576", "Pendidikan SLTA/Sederajat", "'- NIK 2234574598760954;"  # noqa
            ],
            "description_3": [
                "'- pekerjaan: Karyawan Swasta", "'- diduga berada di Amerika", "pekerjaan Pegawai Negeri Sipil;", "'- kegiatan amal (Charity)", "saat ini berada di madagascar", "Yang bersangkutan tercatat dimana saja boleh", "'- Badut banget sih;"  # noqa
            ],
            "description_4": [
                "", "'- relawan The SintoSintoBule", "", "", "", "- paspor B 5438675;", ""  # noqa
            ]
        }

        expected_df = pd.DataFrame(expected_data)

        # Assert that the structure of processed_df is as expected
        self.assertTrue(
            all(
                processed_df[column].equals(
                    input_df[column]
                ) for column in ["Kode_ID", "Terduga"]))

        # Assert the equality of each description_{i+1} column
        for column in description_columns:
            pd.testing.assert_series_equal(
                processed_df[column],
                expected_df[column],
                check_names=False,
                check_dtype=False,
                check_exact=False,
            )

        # Assert no unexpected columns are present
        expected_columns = set(["Kode_ID", "Terduga"] + description_columns)
        self.assertEqual(
            set(
                processed_df.columns
            ),
            expected_columns, "Unexpected columns in processed DataFrame")

        # Verify 'Terduga' column remains unchanged
        pd.testing.assert_series_equal(
            processed_df['Terduga'],
            expected_df['Terduga'],
            check_names=False
        )

        # Verify the correctness of description columns
        for i in range(1, max_descriptions + 1):
            column_name = f'description_{i}'
            self.assertIn(
                column_name,
                processed_df.columns,
                f"{column_name} is missing in the processed DataFrame"
            )

            # Content check - ensuring column is not empty
            if 'Deskripsi' in input_df.columns:
                non_empty_deskripsi_rows = input_df['Deskripsi'].apply(
                    lambda x: x.strip()
                ) != ''
                expected_non_empty = non_empty_deskripsi_rows.sum()
                processed_non_empty = processed_df[column_name].dropna().apply(
                    lambda x: x.strip() != '').sum()
                self.assertTrue(processed_non_empty <= expected_non_empty,
                                f"Column {column_name} has more non-empty entries than expected.")  # noqa

    def test_birth_date_formatting(self):
        """
        Test formatting value from `Tgl lahir` column thas has different formatting style for each row
        """  # noqa
        # Given input DataFrame with different formatting style in `Tgl lahir` column  # noqa
        input_df = pd.DataFrame({
            "Terduga": [
                "Orang",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang"
            ],
            "Tgl Lahir": [
                "4 Januari 1973/4 November 1974/4 November 1973",
                "03-Apr-78",
                "29 Juli 1983",
                "22 Oktober 1978;",
                "01-Apr-61",
                "5 Oktober 1991;",
                "",
                "1 Oktober 1983 atau 15 Maret 1983 atau 1 Januari 1980",
                "26/06/1978",
                "",
                "05/10/1976 atau 01/10/1976",
                "00/00/0000"
            ]
        })

        processed_df = self.processing_formatting.format_birth_date(input_df)  # noqa

        # Expected output DataFrame
        expected_data = {
            "Terduga": [
                "Orang",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang"
            ],
            "birth_date_1": [
                "1973/01/04",
                "1978/04/03",
                "1983/07/29",
                "1978/10/22",
                "1961/04/01",
                "1991/10/05",
                "",
                "1983/10/01",
                "1978/06/26",
                "",
                "1976/10/05",
                "",
            ],
            "birth_date_2": [
                "1974/11/04",
                "",
                "",
                "",
                "",
                "",
                "",
                "1983/03/15",
                "",
                "",
                "1976/10/01",
                ""
            ],
            "birth_date_3": [
                "1973/11/04",
                "",
                "",
                "",
                "",
                "",
                "",
                "1980/01/01",
                "",
                "",
                "",
                ""
            ]
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert equality between processed_df and expected_df for relevant columns  # noqa
        pd.testing.assert_frame_equal(
            processed_df[
                [
                    'Terduga',
                    'birth_date_1',
                    'birth_date_2',
                    'birth_date_3'
                    ]
                ],
            expected_df,
            check_like=True,
            check_dtype=False
        )

    def test_formatting_nationality(self):
        """Test style of formatting WN columns"""
        # Given input dataframe with different formatting style in `WN` column
        input_df = pd.DataFrame(
            {
                "Terduga": [
                    "Orang",
                    "Orang",
                    "Orang",
                    "Korporasi",
                    "Orang",
                    "Orang",
                    "Korporasi",
                    "Orang",
                    "Orang",
                    "Korporasi",
                    "Orang",
                    "Orang",
                    "Orang",
                ],
                "WN": [
                    "Indonesia,Yaman",
                    "Pakistan,Republik Arab Syria",
                    "Trinidad and Tobago;",
                    "",
                    "Republik Arab Suriah",
                    "Bosnia Herzegonia",
                    "",
                    "Palestina,Suriah",
                    "Tanzania; officially the United Republic of Tanzania",
                    "",
                    "Mali,Mauritania",
                    "Amerika Serikat,Yaman",
                    "Etiopia,banglades"
                ]
            }
        )

        processed_df = self.processing_formatting.format_nationality(input_df)  # noqa

        # Expected output DataFrame
        expected_data = {
            "Terduga": [
                "Orang",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Korporasi",
                "Orang",
                "Orang",
                "Orang"
            ],
            "WN_1": [
                "Indonesia",
                "Pakistan",
                "Trinidad and Tobago",
                "",
                "Syria",
                "Bosnia and Herzegovina",
                "",
                "Palestine",
                "Tanzania",
                "",
                "Mali",
                "United States of America",
                "Ethiopia",
            ],
            "WN_2": [
                "Yemen",
                "Syria",
                "",
                "",
                "",
                "",
                "",
                "Syria",
                "officially the United Republic of Tanzania",
                "",
                "Mauritania",
                "Yemen",
                "Bangladesh"
            ]
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert equality between processed_df and expected_df for relevant columns  # noqa
        pd.testing.assert_frame_equal(
            processed_df[
                [
                    'Terduga',
                    'WN_1',
                    'WN_2'
                    ]
                ],
            expected_df,
            check_like=True,
            check_dtype=False
        )
