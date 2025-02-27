#!/usr/bin/env python3
"""
OEIS Parser main script.
Command-line interface for fetching and storing OEIS sequence data.
"""

import argparse
import sys
import json
from typing import List, Dict, Any

from db import OEISDatabase
from oeis_parser import OEISParser


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='OEIS Sequence Parser')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch sequence data')
    fetch_parser.add_argument('a_number', help='A-number of the sequence (e.g., A000032)')
    
    # Fetch range command
    range_parser = subparsers.add_parser('fetch-range', help='Fetch a range of sequences')
    range_parser.add_argument('start', type=int, help='Starting sequence number')
    range_parser.add_argument('end', type=int, help='Ending sequence number (inclusive)')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get sequence data from database')
    get_parser.add_argument('a_number', help='A-number of the sequence (e.g., A000032)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all sequences in the database')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search sequences by name or description')
    search_parser.add_argument('query', help='Search query')
    
    # Common options for all commands
    for subparser in [fetch_parser, range_parser, get_parser, list_parser, search_parser]:
        # Database path option
        subparser.add_argument('--db', default='oeis.db', help='Path to SQLite database file')
        
        # Output format option
        subparser.add_argument('--format', choices=['text', 'json'], default='text',
                              help='Output format (text or json)')
        
        # Verbose output option
        subparser.add_argument('--verbose', '-v', action='store_true',
                              help='Display detailed information')
    
    return parser.parse_args()


def format_sequence(sequence: Dict[str, Any], output_format: str, verbose: bool = False) -> str:
    """Format sequence data for output.
    
    Args:
        sequence: Sequence data dictionary
        output_format: Output format ('text' or 'json')
        verbose: Whether to include detailed information
        
    Returns:
        Formatted sequence data as a string
    """
    if output_format == 'json':
        return json.dumps(sequence, indent=2)
    
    # Text format
    lines = []
    lines.append(f"A-Number: {sequence['a_number']}")
    lines.append(f"Name: {sequence['name']}")
    
    # Terms
    if sequence.get('terms'):
        terms_count = len(sequence['terms'])
        terms_str = ', '.join(str(t) for t in sequence['terms'][:10])
        if terms_count > 10:
            terms_str += ', ...'
        lines.append(f"Terms ({terms_count} values): {terms_str}")
    
    # Formula
    if sequence.get('formula'):
        formula_lines = sequence['formula'].count('\n') + 1
        lines.append(f"Formula ({formula_lines} lines): {sequence['formula'][:200]}")
        if len(sequence['formula']) > 200:
            lines.append("  ...")
    
    # Comments
    if sequence.get('comments'):
        comments_lines = sequence['comments'].count('\n') + 1
        comments_length = len(sequence['comments'])
        lines.append(f"Comments ({comments_lines} lines, {comments_length} chars):")
        if verbose:
            lines.append(sequence['comments'])
        else:
            lines.append(f"  {sequence['comments'][:200]}...")
    
    # Examples
    if sequence.get('example'):
        example_lines = sequence['example'].count('\n') + 1
        lines.append(f"Examples ({example_lines} lines):")
        if verbose:
            lines.append(sequence['example'])
        else:
            lines.append(f"  {sequence['example'][:200]}...")
            if len(sequence['example']) > 200:
                lines.append("  ...")
    
    # Implementations
    if sequence.get('implementations'):
        impl_count = len(sequence['implementations'])
        languages = [impl['language'] for impl in sequence['implementations']]
        lines.append(f"Implementations ({impl_count} total):")
        lines.append(f"  Languages: {', '.join(languages)}")
        
        if verbose:
            for impl in sequence['implementations']:
                lines.append(f"  {impl['language']}:")
                code_lines = impl['code'].split('\n')
                for line in code_lines:
                    lines.append(f"    {line}")
                lines.append("")
        else:
            for impl in sequence['implementations'][:2]:
                lines.append(f"  {impl['language']}:")
                code_lines = impl['code'].split('\n')
                for i, line in enumerate(code_lines[:3]):
                    lines.append(f"    {line}")
                if len(code_lines) > 3:
                    lines.append("    ...")
                lines.append("")
            if impl_count > 2:
                lines.append(f"  ... and {impl_count - 2} more implementations")
    
    # Cross References
    if sequence.get('cross_references'):
        ref_count = len(sequence['cross_references'])
        ref_types = set(ref['reference_type'] for ref in sequence['cross_references'])
        lines.append(f"Cross References ({ref_count} total, types: {', '.join(ref_types)}):")
        
        if verbose or ref_count <= 10:
            for ref in sequence['cross_references']:
                lines.append(f"  {ref['target_a_number']} ({ref['reference_type']})")
        else:
            for ref in sequence['cross_references'][:10]:
                lines.append(f"  {ref['target_a_number']} ({ref['reference_type']})")
            lines.append(f"  ... and {ref_count - 10} more references")
    
    # Data summary
    data_size = len(json.dumps(sequence['data']))
    lines.append(f"Raw data size: {data_size} bytes")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize database and parser
    db = OEISDatabase(args.db)
    parser = OEISParser()
    
    try:
        if args.command == 'fetch':
            # Fetch a single sequence
            print(f"Fetching sequence {args.a_number}...")
            sequence_data = parser.fetch_sequence(args.a_number)
            db.insert_sequence(sequence_data)
            print(f"Sequence {args.a_number} stored in database.")
            
            # Display sequence data
            if args.format:
                print("\nSequence data:")
                print(format_sequence(sequence_data, args.format, args.verbose))
        
        elif args.command == 'fetch-range':
            # Fetch a range of sequences
            print(f"Fetching sequences {args.start} to {args.end}...")
            
            # We'll modify the fetch_sequence_range method to fetch one by one
            # so we can show progress
            sequence_count = 0
            sequence_stats = []
            
            for n in range(args.start, args.end + 1):
                a_number = f"A{n:06d}"
                print(f"Fetching {a_number}...", end="", flush=True)
                
                try:
                    # Fetch the sequence
                    sequence_data = parser.fetch_sequence(a_number)
                    
                    # Store in database
                    db.insert_sequence(sequence_data)
                    sequence_count += 1
                    
                    # Collect stats for this sequence
                    stats = {
                        'a_number': sequence_data['a_number'],
                        'name': sequence_data['name'],
                        'terms_count': len(sequence_data.get('terms', [])),
                        'implementations': [impl['language'] for impl in sequence_data.get('implementations', [])],
                        'cross_refs_count': len(sequence_data.get('cross_references', [])),
                        'data_size': len(json.dumps(sequence_data.get('data', {})))
                    }
                    sequence_stats.append(stats)
                    
                    # Print immediate information
                    print(" Done")
                    if args.verbose:
                        print(f"  Name: {sequence_data['name']}")
                        print(f"  Terms: {len(sequence_data.get('terms', []))} values")
                        if sequence_data.get('implementations'):
                            print(f"  Implementations: {', '.join([impl['language'] for impl in sequence_data.get('implementations', [])])}")
                        print(f"  Cross references: {len(sequence_data.get('cross_references', []))}")
                        print(f"  Data size: {len(json.dumps(sequence_data.get('data', {})))} bytes")
                        print()
                
                except Exception as e:
                    print(f" Error: {e}")
            
            print(f"Fetched and stored {sequence_count} sequences.")
        
        elif args.command == 'get':
            # Get sequence from database
            sequence = db.get_sequence(args.a_number)
            if sequence:
                print(format_sequence(sequence, args.format, args.verbose))
            else:
                print(f"Sequence {args.a_number} not found in database.")
                return 1
        
        elif args.command == 'list':
            # List all sequences in database
            a_numbers = db.get_all_sequences()
            if a_numbers:
                if args.format == 'json':
                    print(json.dumps(a_numbers, indent=2))
                else:
                    print(f"Found {len(a_numbers)} sequences in database:")
                    
                    if args.verbose:
                        # Get detailed information for each sequence
                        for a_number in a_numbers:
                            sequence = db.get_sequence(a_number)
                            if sequence:
                                print(f"\n  {a_number}: {sequence['name']}")
                                
                                # Terms
                                if sequence.get('terms'):
                                    terms_count = len(sequence['terms'])
                                    terms_str = ', '.join(str(t) for t in sequence['terms'][:5])
                                    if terms_count > 5:
                                        terms_str += ', ...'
                                    print(f"    Terms ({terms_count} values): {terms_str}")
                                
                                # Implementations
                                if sequence.get('implementations'):
                                    impl_count = len(sequence['implementations'])
                                    languages = [impl['language'] for impl in sequence['implementations']]
                                    print(f"    Implementations: {', '.join(languages)}")
                                
                                # Cross References
                                if sequence.get('cross_references'):
                                    ref_count = len(sequence['cross_references'])
                                    print(f"    Cross references: {ref_count}")
                    else:
                        # Just list the A-numbers
                        for a_number in a_numbers:
                            print(f"  {a_number}")
            else:
                print("No sequences found in database.")
        
        elif args.command == 'search':
            # Search sequences
            results = db.search_sequences(args.query)
            if results:
                if args.format == 'json':
                    print(json.dumps(results, indent=2))
                else:
                    print(f"Found {len(results)} matching sequences:")
                    
                    if args.verbose:
                        # Get detailed information for each matching sequence
                        for result in results:
                            a_number = result['a_number']
                            sequence = db.get_sequence(a_number)
                            if sequence:
                                print(f"\n  {a_number}: {sequence['name']}")
                                
                                # Show why this sequence matched
                                match_reason = []
                                if args.query.lower() in sequence['name'].lower():
                                    match_reason.append("name")
                                if sequence.get('description') and args.query.lower() in sequence['description'].lower():
                                    match_reason.append("description")
                                if match_reason:
                                    print(f"    Matched in: {', '.join(match_reason)}")
                                
                                # Terms
                                if sequence.get('terms'):
                                    terms_count = len(sequence['terms'])
                                    terms_str = ', '.join(str(t) for t in sequence['terms'][:5])
                                    if terms_count > 5:
                                        terms_str += ', ...'
                                    print(f"    Terms ({terms_count} values): {terms_str}")
                                
                                # Implementations
                                if sequence.get('implementations'):
                                    impl_count = len(sequence['implementations'])
                                    languages = [impl['language'] for impl in sequence['implementations']]
                                    print(f"    Implementations: {', '.join(languages)}")
                                
                                # Cross References
                                if sequence.get('cross_references'):
                                    ref_count = len(sequence['cross_references'])
                                    print(f"    Cross references: {ref_count}")
                    else:
                        # Just list the matching sequences
                        for seq in results:
                            print(f"  {seq['a_number']}: {seq['name']}")
            else:
                print(f"No sequences matching '{args.query}' found in database.")
        
        else:
            # No command specified
            print("No command specified. Use --help for usage information.")
            return 1
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    finally:
        # Close database connection
        db.close()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
