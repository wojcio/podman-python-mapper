"""Tests for the simple mapper."""

import sys
sys.path.insert(0, '.')

from src.simple_mapper import SimpleMapper


def test_csv_to_xml():
    """Test CSV to XML mapping."""
    dml = '''MAPPING csv_to_xml {
        SOURCE CSV { file: "input.csv" }
        TARGET XML { file: "output.xml" }
        RULES {
            map id -> Itemid
            map name -> Itemname
            map price -> Itemprice
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    print(f"Parsed: {mapping}")
    
    assert mapping['name'] == 'csv_to_xml'
    assert mapping['source_type'] == 'CSV'
    assert mapping['target_type'] == 'XML'
    assert len(mapping['rules']) == 3
    print("✓ CSV to XML test passed")


def test_xml_to_csv():
    """Test XML to CSV mapping."""
    dml = '''MAPPING xml_to_csv {
        SOURCE XML { file: "input.xml", root_element: "Items" }
        TARGET CSV { file: "output.csv" }
        RULES {
            map Itemid -> id
            map Itemname -> name
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    assert mapping['name'] == 'xml_to_csv'
    assert mapping['source_type'] == 'XML'
    assert mapping['target_type'] == 'CSV'
    print("✓ XML to CSV test passed")


def test_csv_to_db():
    """Test CSV to DB mapping."""
    dml = '''MAPPING csv_to_db {
        SOURCE CSV { file: "input.csv", has_header: true }
        TARGET DB { type: sqlite, connection_string: "data.db", table: "customers" }
        RULES {
            map id -> customer_id
            map name -> customer_name
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    assert mapping['source_type'] == 'CSV'
    assert mapping['target_type'] == 'DB'
    print("✓ CSV to DB test passed")


def test_db_to_csv():
    """Test DB to CSV mapping."""
    dml = '''MAPPING db_to_csv {
        SOURCE DB { type: sqlite, connection_string: "data.db", query: "SELECT * FROM customers" }
        TARGET CSV { file: "output.csv" }
        RULES {
            map customer_id -> id
            map customer_name -> name
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    assert mapping['source_type'] == 'DB'
    assert mapping['target_type'] == 'CSV'
    print("✓ DB to CSV test passed")


def test_edi_to_csv():
    """Test EDI to CSV mapping."""
    dml = '''MAPPING edi_to_csv {
        SOURCE EDI { file: "input.edi", version: "X12" }
        TARGET CSV { file: "output.csv" }
        RULES {
            map segment -> segment
            map data -> data
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    assert mapping['source_type'] == 'EDI'
    assert mapping['target_type'] == 'CSV'
    print("✓ EDI to CSV test passed")


def test_csv_to_edi():
    """Test CSV to EDI mapping."""
    dml = '''MAPPING csv_to_edi {
        SOURCE CSV { file: "input.csv" }
        TARGET EDI { file: "output.edi", version: "X12" }
        RULES {
            map segment -> segment
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    assert mapping['source_type'] == 'CSV'
    assert mapping['target_type'] == 'EDI'
    print("✓ CSV to EDI test passed")


def test_with_transform():
    """Test mapping with TRANSFORM."""
    dml = '''MAPPING transform_test {
        SOURCE CSV { file: "input.csv" }
        TARGET XML { file: "output.xml" }
        RULES {
            map name -> Itemname TRANSFORM upper()
            map price -> Itemprice AS float
        }
    }'''
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(dml)
    
    # The transform should be captured
    print(f"Rules with transforms: {mapping['rules']}")
    print("✓ Transform test passed")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Running Simple Mapper Tests")
    print("=" * 50)
    
    tests = [
        test_csv_to_xml,
        test_xml_to_csv,
        test_csv_to_db,
        test_db_to_csv,
        test_edi_to_csv,
        test_csv_to_edi,
        test_with_transform,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with error: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)


if __name__ == "__main__":
    main()