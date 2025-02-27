# OEIS Parser

A Python tool for fetching and storing data from the [Online Encyclopedia of Integer Sequences (OEIS)](https://oeis.org/) in a structured SQLite database.

## Features

- Fetch sequence data from the OEIS API
- Store sequences in a SQLite database
- Extract sequence terms, descriptions, formulas, and examples
- Capture code implementations in various programming languages
- Track cross-references between sequences
- Search and retrieve sequences from the database

## Requirements

- Python 3.6+
- Required packages:
  - `requests`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/oeis-parser.git
   cd oeis-parser
   ```

2. Install dependencies:
   ```
   pip install requests
   ```

## Usage

The parser provides a command-line interface with several commands:

### Fetch a single sequence

```
python main.py fetch A000032
```

This fetches the sequence A000032 (Lucas numbers) from OEIS and stores it in the database.

### Fetch a range of sequences

```
python main.py fetch-range 1 100
```

This fetches sequences A000001 through A000100 and stores them in the database.

With the `--verbose` flag, it shows detailed progress information for each sequence as it's fetched:

```
python main.py fetch-range 1 10 --verbose
```

This displays real-time information about each sequence as it's being fetched, including:
- Sequence name
- Number of terms
- Available implementations
- Number of cross-references
- Data size

### Get a sequence from the database

```
python main.py get A000032
```

This retrieves and displays the sequence A000032 from the database.

### List all sequences in the database

```
python main.py list
```

This lists all sequences stored in the database.

### Search sequences

```
python main.py search "Fibonacci"
```

This searches for sequences with "Fibonacci" in their name or description.

### Output formats

You can specify the output format using the `--format` option:

```
python main.py get A000032 --format json
```

Supported formats:
- `text` (default): Human-readable text format
- `json`: JSON format for machine processing

### Verbose output

You can get more detailed information using the `--verbose` or `-v` option:

```
python main.py get A000032 --verbose
```

This will display:
- Complete comments and examples
- All implementations with full code
- All cross-references
- Detailed statistics about the sequence

The verbose option works with all commands:
- `fetch`: Shows complete sequence details
- `fetch-range`: Shows summary information for each fetched sequence
- `get`: Shows complete sequence details
- `list`: Shows summary information for each sequence in the database
- `search`: Shows detailed information for each matching sequence

### Custom database path

You can specify a custom database path using the `--db` option:

```
python main.py fetch A000032 --db /path/to/custom.db
```

## Database Schema

The parser uses a SQLite database with the following schema:

### Sequences Table

Stores the main sequence data:

- `a_number`: The A-number of the sequence (e.g., A000032)
- `name`: The name/title of the sequence
- `description`: Description of the sequence
- `terms`: The sequence terms as a JSON array
- `comments`: Additional comments about the sequence
- `formula`: Mathematical formula(s) for the sequence
- `example`: Examples of the sequence
- `data`: The complete raw JSON data from OEIS
- `fetched_at`: Timestamp when the sequence was fetched

### Implementations Table

Stores code implementations for sequences:

- `id`: Auto-incrementing ID
- `a_number`: The A-number of the sequence
- `language`: Programming language (e.g., Python, Mathematica)
- `code`: The implementation code

### Cross References Table

Stores relationships between sequences:

- `id`: Auto-incrementing ID
- `source_a_number`: The A-number of the source sequence
- `target_a_number`: The A-number of the referenced sequence
- `reference_type`: Type of reference (e.g., CROSSREF, KEYWORD)

## Rate Limiting

The parser respects OEIS rate limits by waiting at least 1 second between API requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
