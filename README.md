# Certificate Number Generator

A tool to generate and validate unique certificate identification numbers based on CSV data. This application creates secure, verifiable certificate IDs that can be later validated against the source data.

## Features

- Generate unique certificate numbers from CSV data
- Validate certificate numbers against source data
- Export certificate data to CSV file
- Secure encoding based on SHA-256 hash algorithm

## Installation

Simply download the script and ensure you have Python 3.6+ installed.

**Required Python libraries**:

- Standard libraries (csv, base64, hashlib, argparse, os)

## Usage

### 1. Generate Certificate Numbers

```bash
python certnum-generator.py --generate --csv <input_csv_file>
```

This will read data from the input CSV, generate certificate numbers, and save the results to a new CSV file with the suffix `_certificates`.

**Options**:

- `--output <filename>`: Specify a custom output filename
- `--verbose`: Show detailed debugging information

**Example**:

```bash
python certnum-generator.py --generate --csv data.csv
python certnum-generator.py --generate --csv data.csv --output custom_output.csv
```

### 2. Validate Certificate Numbers

```bash
python certnum-generator.py --validate <certificate_number> --csv <data_csv_file>
```

This will check if the certificate number is valid and display information about the certificate.

**Example**:

```bash
python certnum-generator.py --validate CI-WEB-250427-QFTGQA --csv data.csv
```

**Output**:

```
Certificate Validation Result:
============================================================
Status: VALID
Organization: CI
Program: WEB
Date: 27/4/2025
Recipient: Salman Wiharja
```

For detailed debugging information, add the `--verbose` flag:

```bash
python certnum-generator.py --validate CI-WEB-250427-QFTGQA --csv data.csv --verbose
```

## Input CSV Format

The input CSV file must contain the following columns:

- `organization`: Organization code
- `program_code`: Program/course code
- `year`: Year of certificate issuance (4-digit format)
- `month`: Month of certificate issuance
- `date`: Date of certificate issuance
- `name`: Recipient's name

**Example**:

```csv
organization,program_code,year,month,date,name
CI,WEB,2025,4,27,Salman Wiharja
CI,WEB,2025,4,27,John Doe
CI,WEB,2025,4,27,Master
```

## Certificate Number Format

The generated certificate numbers follow this format:

```
ORG-PROG-YYMMDD-CODE
```

**Where**:

- `ORG`: Organization code
- `PROG`: Program code
- `YYMMDD`: Year (last 2 digits) and Month (2 digits) and Date (2 digits)
- `CODE`: Unique 6-character alphanumeric code derived from the certificate data

**Example**: `CI-WEB-250427-QFTGQA`

## Output CSV Format

The output CSV will contain all columns from the input CSV plus an additional column:

- `certificate_number`: The generated certificate number

## Security Notes

- The unique certificate code is generated using SHA-256 hash algorithm
- Each certificate number can be validated against the original data
- The system can detect any alterations to certificate information
