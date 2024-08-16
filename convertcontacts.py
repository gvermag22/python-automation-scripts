import csv
import re
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process Outlook contacts CSV file and format phone numbers.')
    parser.add_argument('input_file', help='Input CSV file containing Outlook contacts')
    parser.add_argument('output_file', help='Output CSV file for processed contacts')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()

def format_phone(phone):
    """Format the phone number to ensure it starts with "+1" for US numbers."""
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 10:
        return f"+1{phone}"
    elif len(phone) == 11 and phone.startswith('1'):
        return f"+{phone}"
    elif len(phone) >= 11:
        return f"+{phone}"
    return None

def clean_name(name):
    """Clean the name by removing any trailing commas and extra whitespace."""
    return name.strip().rstrip(',')

def process_contacts(input_file, output_file):
    contacts = []
    invalid_numbers = []
    duplicate_numbers = set()

    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            phone_fields = ['Primary Phone', 'Home Phone', 'Home Phone 2', 'Mobile Phone', 
                            'Business Phone', 'Business Phone 2', 'Other Phone']
            
            for row in reader:
                first_name = clean_name(row['First Name'].split()[0].capitalize())
                
                contact_numbers = []
                for field in phone_fields:
                    if row[field]:
                        formatted_phone = format_phone(row[field])
                        if formatted_phone:
                            contact_numbers.append(formatted_phone)
                        else:
                            invalid_numbers.append(row[field])
                
                # Add each valid phone number as a separate entry
                for phone in contact_numbers:
                    contacts.append((phone, first_name))
                
                # Check for duplicates within this contact's numbers
                if len(contact_numbers) != len(set(contact_numbers)):
                    duplicate_numbers.update(contact_numbers)

        # Sort contacts by phone number to group duplicates together
        contacts.sort(key=lambda x: x[0])

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Phone', 'Name'])  # Write header
            for phone, name in contacts:
                writer.writerow([phone, name])

        logger.info(f"Processed {len(contacts)} contact entries.")
        if invalid_numbers:
            logger.warning(f"Found {len(invalid_numbers)} invalid phone numbers.")
        if duplicate_numbers:
            logger.warning(f"Found {len(duplicate_numbers)} duplicate phone numbers.")

    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found.")
        sys.exit(1)
    except csv.Error as e:
        logger.error(f"CSV error in file '{input_file}': {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"I/O error: {e}")
        sys.exit(1)

    return contacts, invalid_numbers, list(duplicate_numbers)

def main():
    args = parse_arguments()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Processing contacts from {args.input_file}")
    contacts, invalid_numbers, duplicate_numbers = process_contacts(args.input_file, args.output_file)

    logger.info(f"Conversion complete. Output saved to {args.output_file}")
    
    if args.verbose:
        if invalid_numbers:
            logger.debug(f"Invalid numbers: {', '.join(invalid_numbers[:5])}{'...' if len(invalid_numbers) > 5 else ''}")
        if duplicate_numbers:
            logger.debug(f"Duplicate numbers: {', '.join(duplicate_numbers[:5])}{'...' if len(duplicate_numbers) > 5 else ''}")

if __name__ == "__main__":
    main()
