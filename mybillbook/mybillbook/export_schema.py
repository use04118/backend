import sqlite3
import sqliteschema

def export_schema(db_path, output_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Extract schema using sqliteschema
    extractor = sqliteschema.SQLiteSchemaExtractor('E:/Mybillbook/mybillbook/mybillbook/db.sqlite3')
    schema = extractor.dumps(output_format='markdown')

    # Write schema to output file
    with open(output_file, 'w') as f:
        f.write(schema)

    print(f"Schema exported to {output_file}")

# Replace 'your_database.db' with the path to your SQLite database
export_schema('your_database.db', 'schema.md')
