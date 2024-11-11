import csv
import re
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process Outlook contacts CSV file and format phone numbers.')
    parser.add_argument('input_file', help='Input CSV file containing Outlook contacts')
    parser.add_argument('output_file', help='Output CSV file for processed contacts')
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable verbose output')
    return parser.parse_args()

def format_phone(phone):
    """Format the phone number to ensure it starts with the correct country code."""
    phone = re.sub(r'\D', '', phone)
    
    # Default to +1 for US numbers if no country code given
    if len(phone) == 10:
        return f'+1{phone}'
    elif len(phone) == 11 and phone.startswith('1'):
        return f'+{phone}'
    elif len(phone) == 12 and phone.startswith('91'):
        return f'+{phone}'  # India code
    elif len(phone) >= 11:
        # Assuming it's an international number
        return f'+{phone}'
    return None

def clean_name(name):
    """Clean the name by removing any trailing commas and extra whitespace."""
    return name.strip().rstrip(',')

def process_contacts(input_file, output_file):
    contacts = []
    invalid_numbers = []
    duplicate_numbers = set()
    total_input_rows = 0
    skipped_rows = 0

    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            logger.debug(f"Available columns: {reader.fieldnames}")
            
            phone_fields = ['Primary Phone', 'Home Phone', 'Home Phone 2', 'Mobile Phone', 
                            'Business Phone', 'Business Phone 2', 'Other Phone']
            
            for row in reader:
                total_input_rows += 1
                valid_numbers_for_contact = 0

                try:
                    first_name = clean_name(row.get('First Name', row.get('FirstName', '')).split()[0].capitalize())
                except IndexError:
                    logger.warning(f"Unable to process name in row: {row}")
                    first_name = ''

                for field in phone_fields:
                    if row.get(field):
                        formatted_phone = format_phone(row[field])
                        if formatted_phone:
                            contacts.append((formatted_phone, first_name))
                            valid_numbers_for_contact += 1
                        else:
                            invalid_numbers.append(row[field])
                
                if valid_numbers_for_contact == 0:
                    skipped_rows += 1

                if len(set(contacts[-valid_numbers_for_contact:])) < valid_numbers_for_contact:
                    duplicate_numbers.update([c[0] for c in contacts[-valid_numbers_for_contact:]])

        contacts.sort(key=lambda x: x[0])
        unique_contacts = list(dict.fromkeys(contacts))  # Remove duplicates

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            for phone, name in unique_contacts:
                writer.writerow([phone, name])

        duplicate_count = len(contacts) - len(unique_contacts)
        invalid_count = len(invalid_numbers)

        logger.info(f"Total input rows: {total_input_rows}")
        logger.info(f"Skipped rows (no valid numbers): {skipped_rows}")
        logger.info(f"Total valid phone numbers found: {len(contacts)}")
        logger.info(f"Unique phone numbers in output: {len(unique_contacts)}")
        logger.info(f"Invalid phone numbers: {invalid_count}")
        logger.info(f"Duplicate phone numbers removed: {duplicate_count}")

        if invalid_numbers:
            logger.debug(f"Invalid numbers: {', '.join(invalid_numbers[:5])}{'...' if len(invalid_numbers) > 5 else ''}")
        if duplicate_numbers:
            logger.debug(f"Duplicate numbers: {', '.join(list(duplicate_numbers)[:5])}{'...' if len(duplicate_numbers) > 5 else ''}")

    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found.")
        sys.exit(1)
    except csv.Error as e:
        logger.error(f"CSV error in file '{input_file}': {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"I/O error: {e}")
        sys.exit(1)

    return unique_contacts, invalid_numbers, duplicate_count, invalid_count

def main():
    args = parse_arguments()
    if args.quiet:
        logger.setLevel(logging.INFO)

    logger.info(f"Processing contacts from {args.input_file}")
    contacts, invalid_numbers, duplicate_count, invalid_count = process_contacts(args.input_file, args.output_file)

    logger.info(f"Conversion complete. Output saved to {args.output_file}")
    logger.info(f"Summary: {duplicate_count} duplicates found, {invalid_count} invalid numbers")

if __name__ == "__main__":
    main()
