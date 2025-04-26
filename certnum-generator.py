import csv
import base64
import hashlib
import sys
import argparse
import os
from datetime import datetime

def read_csv(file_path):
    """Read data from CSV file"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def write_csv_with_certificates(data, output_file):
    """Write data with certificate numbers back to CSV"""
    try:
        if not data:
            return False
            
        # Get the original fieldnames without duplicating certificate_number
        fieldnames = []
        for field in data[0].keys():
            # Hanya tambahkan field yang belum ada atau bukan certificate_number duplikat
            if field not in fieldnames:
                fieldnames.append(field)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        return True
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return False

def generate_unique_code(data_row):
    """Generate a unique 6-character code based on the data row"""
    # Create a string with all data fields
    data_str = ''.join([str(val) for val in data_row.values()])
    
    # Generate a hash of the data
    hash_obj = hashlib.sha256(data_str.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert hash to a 6-character alphanumeric string
    # Use first 9 bytes of hash for encoding to ensure enough characters
    code = base64.b32encode(hash_bytes[:9]).decode('utf-8')[:6]
    return code

def generate_cert_number(row):
    """Generate certificate number in format: ORG-PROG-YYMM-CODE"""
    org = row['organization']
    prog = row['program_code']
    year = row['year'][2:4]  # Get last 2 digits of year
    month = row['month'].zfill(2)  # Ensure month has 2 digits
    date = row['date'].zfill(2)  # Ensure date has 2 digits
    
    # Generate unique code for this certificate
    code = generate_unique_code(row)
    
    return f"{org}-{prog}-{year}{month}{date}-{code}"

def decode_cert_number(cert_number, csv_path, verbose=False):
    """Attempt to verify a certificate number against the CSV data"""
    try:
        if verbose:
            print(f"Decoding certificate: {cert_number}")
        
        # Parse certificate number
        parts = cert_number.split('-')
        if len(parts) != 4:
            return False, "Invalid certificate format"
        
        org = parts[0]
        prog = parts[1]
        year_month_date = parts[2]
        code = parts[3]
        
        if verbose:
            print(f"Parsed: org={org}, prog={prog}, year_month_date={year_month_date}, code={code}")
        
        # Extract year and month
        if len(year_month_date) != 6:
            return False, "Invalid year/month format"
        year = "20" + year_month_date[:2]
        month = year_month_date[2:4]
        date = year_month_date[4:6]

        # Convert to int to strip leading zeros for comparison
        month_int = str(int(month))  # This converts '04' -> '4'
        date_int = str(int(date))    # This converts '07' -> '7'
        
        if verbose:
            print(f"Looking for: year={year}, month={month_int}, date={date_int}")
        
        # Read data from CSV to find a match
        data = read_csv(csv_path)
        if verbose:
            print(f"Found {len(data)} records in CSV file")
        
        for idx, row in enumerate(data):
            if verbose:
                print(f"\nChecking row {idx+1}:")
                print(f"  CSV row: {row}")
            
            # Check if basic criteria match
            if (row['organization'] == org and 
                row['program_code'] == prog and
                row['year'] == year and
                row['month'] == month_int and
                row['date'] == date_int):  # Use the month without leading zeros
                
                if verbose:
                    print(f"  Basic criteria match: org, prog, year, month, date")
                
                # Generate code for this row to see if it matches
                generated_code = generate_unique_code(row)
                if verbose:
                    print(f"  Generated code: {generated_code}, Looking for: {code}")
                
                if generated_code == code:
                    if verbose:
                        print(f"  Code match found!")
                    return True, row
                elif verbose:
                    print(f"  Code does not match")
            elif verbose:
                print(f"  Basic criteria don't match")
                if row['organization'] != org:
                    print(f"    org mismatch: '{row['organization']}' vs '{org}'")
                if row['program_code'] != prog:
                    print(f"    prog mismatch: '{row['program_code']}' vs '{prog}'")
                if row['year'] != year:
                    print(f"    year mismatch: '{row['year']}' vs '{year}'")
                if row['month'] != month_int:
                    print(f"    month mismatch: '{row['month']}' vs '{month_int}'")
                if row['date'] != date_int:
                    print(f"    date mismatch: '{row['date']}' vs '{date_int}'")
        
        return False, "Certificate not found in database"
    except Exception as e:
        if verbose:
            print(f"Error during decoding: {e}")
        return False, f"Error decoding certificate: {e}"

def main():
    parser = argparse.ArgumentParser(description='Certificate Number Generator and Validator')
    parser.add_argument('--generate', action='store_true', help='Generate certificate numbers from CSV')
    parser.add_argument('--validate', type=str, help='Validate a certificate number')
    parser.add_argument('--csv', type=str, default='data.csv', help='Path to the CSV file')
    parser.add_argument('--output', type=str, help='Output CSV file path (default: same as input with _certificates suffix)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed debug information')
    
    args = parser.parse_args()
    
    if args.generate:
        # Generate certificate numbers
        data = read_csv(args.csv)
        if not data:
            print("No data found or error reading CSV file")
            return
        
        # Generate certificate numbers and add to data
        print("Generating certificate numbers...")
        print("=" * 60)
        print(f"{'Name':<30} {'Certificate Number':<30}")
        print("=" * 60)
        
        for row in data:
            cert_number = generate_cert_number(row)
            row['certificate_number'] = cert_number
            print(f"{row['name']:<30} {cert_number:<30}")
        
        # Determine output filename
        output_file = args.output
        if not output_file:
            # Create output filename based on input filename
            base_name = os.path.splitext(args.csv)[0]
            output_file = f"{base_name}_certificates.csv"
        
        # Write to CSV
        success = write_csv_with_certificates(data, output_file)
        if success:
            print(f"\nCertificate numbers saved to: {output_file}")
        else:
            print("\nFailed to save certificate numbers to CSV")
        
    elif args.validate:
        # Validate a certificate number
        valid, result = decode_cert_number(args.validate, args.csv, args.verbose)
        print("Certificate Validation Result:")
        print("=" * 60)
        if valid:
            print(f"Status: VALID")
            print(f"Organization: {result['organization']}")
            print(f"Program: {result['program_code']}")
            print(f"Date: {result['date']}/{result['month']}/{result['year']}")
            print(f"Recipient: {result['name']}")
        else:
            print(f"Status: INVALID")
            print(f"Reason: {result}")
    else:
        print("Please specify either --generate or --validate option.")
        print("Example: python certnum-generator.py --generate --csv data.csv")
        print("Example: python certnum-generator.py --validate CI-WEB-2504-QFTGQA --csv data.csv")

if __name__ == "__main__":
    main()