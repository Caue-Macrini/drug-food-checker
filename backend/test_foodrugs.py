from foodrugs_import import normalized_rows, sql_string

def test_real_dump_structure_and_no_clinical_inference():
    line="INSERT INTO `TM_interactions` VALUES (0,0,0,116,'Grapefruit','abemaciclib'),(1,0,1943,2220,'carbohydrate','abemaciclib');"
    rows=list(normalized_rows([line],1))
    assert len(rows)==1
    assert rows[0]['source_record_id']=='0'
    assert rows[0]['food']=='Grapefruit'
    assert rows[0]['base_risk'] is None and rows[0]['reviewed'] is False

def test_sql_data_not_executed_and_escape_handling():
    assert list(normalized_rows(['DROP TABLE usuarios;'],10))==[]
    assert sql_string("'St. John\\'s wort'")=="St. John's wort"
    assert sql_string('NULL')==''
