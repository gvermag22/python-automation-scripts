import sys
import argparse
import re

def format_phone_number(phone_number):
    """Formats the phone number by keeping only digits and ensuring uniform format."""
    cleaned_number = re.sub(r'\D', '', phone_number)  # Remove non-digit characters
    if cleaned_number.startswith("1") and len(cleaned_number) == 11:
        cleaned_number = cleaned_number[1:]  # Remove leading '1' for US numbers
    return cleaned_number

def remove_entries(input_file_path, remove_file_path, output_file_path):
    """
    Remove entries from the input file based on phone numbers in the remove file.
    
    Args:
    input_file_path (str): Path to the input file (source file)
    remove_file_path (str): Path to the file containing phone numbers to remove
    output_file_path (str): Path to the output file
    
    Returns:
    tuple: (input_count, remove_count, output_count, removed_entries, not_removed_from_exclusion)
    """
    try:
        # Read and normalize phone numbers from the remove file
        with open(remove_file_path, 'r') as remove_file:
            numbers_to_remove = {format_phone_number(line.strip()) for line in remove_file}
        remove_count = len(numbers_to_remove)

        # Overwrite remove file with cleaned numbers
        with open(remove_file_path, 'w') as remove_file:
            for number in numbers_to_remove:
                remove_file.write(number + '\n')

        # Process the input file and write to output file
        input_count = 0
        output_count = 0
        removed_entries = []
        not_removed_entries = []  # To store entries that are not removed
        not_found_in_input = set(numbers_to_remove)  # Track numbers not found in input

        with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
            for line in input_file:
                input_count += 1
                phone_number = format_phone_number(line.split(',')[0].strip())

                # Check if phone number is in the removal list
                if phone_number not in numbers_to_remove:
                    output_file.write(line)
                    output_count += 1
                    not_removed_entries.append(line.strip())  # Store the entry that is not removed
                else:
                    removed_entries.append(line.strip())
                    not_found_in_input.discard(phone_number)  # Remove from not found set

        print(f"Entries processed. Result saved in {output_file_path}")
        return input_count, remove_count, output_count, removed_entries, not_found_in_input

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
    except PermissionError:
        print("Error: Permission denied. Check file permissions.")
    except IndexError:
        print("Error: Invalid file format. Ensure each line contains 'phone number, name'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return 0, 0, 0, [], set()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove entries from an input file based on phone numbers in a remove file.\n"
                    "File format should be: 'phone number, name' on each line.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", help="Path to the input file (source file)")
    parser.add_argument("remove_file", help="Path to the file containing phone numbers to remove")
    parser.add_argument("output_file", help="Path to the output file")
    
    args = parser.parse_args()

    input_count, remove_count, output_count, removed_entries, not_found_in_input = remove_entries(args.input_file, args.remove_file, args.output_file)

    print("\nSummary:")
    print(f"Input file records: {input_count}")
    print(f"Remove file records: {remove_count}")
    print(f"Output file records: {output_count}")
    print(f"Number of entries removed: {len(removed_entries)}")

    if removed_entries:
        print("\nRemoved entries:")
        for entry in removed_entries:
            print(entry)

    # Print numbers from the exclusion file that were not found in the input file
    if not_found_in_input:
        print("\nNumbers from the exclusion file not found in the input file:")
        for number in not_found_in_input:
            print(number)
