import json, sqlite3
import pytest
from foodrugs_full import tuples, build
from index_foodrugs import index
import foodrugs_store as store

def test_literal_parser_preserves_escapes_nulls_and_numeric_types():
    rows=list(tuples("(1,'St. John\\'s wort',NULL,-1.2e-3),(2,'a\\n(b),c',0,2);",4))
    assert rows==[[1,"St. John's wort",None,-.0012],[2,'a\n(b),c',0,2]]
    with pytest.raises(ValueError):list(tuples("(1,load_file('/secret'));",2))
    with pytest.raises(ValueError):list(tuples("(1,2); DROP TABLE usuarios;",2))

@pytest.fixture
def source_db(tmp_path,monkeypatch):
    dump=tmp_path/'source.sql';db=tmp_path/'full.sqlite'
    dump.write_text('''CREATE TABLE `TM_interactions` (
  `TM_interactions_ID` int NOT NULL,
  `texts_ID` int NOT NULL,
  `start_index` int DEFAULT NULL,
  `end_index` int DEFAULT NULL,
  `food` varchar(150),
  `drug` varchar(150)
) ENGINE=InnoDB;
INSERT INTO `TM_interactions` VALUES (0,0,0,16,'Grapefruit','simvastatin'),(1,0,0,16,'grapefruit','Simvastatin'),(2,1,0,6,'milk','drug two'),(3,1,0,6,NULL,'drug two');
UNLOCK TABLES;
CREATE TABLE `texts` (
  `texts_ID` int,
  `document` text,
  `link` text,
  `citation` text
) ENGINE=InnoDB;
INSERT INTO `texts` VALUES (0,'Example document','https://pubmed.ncbi.nlm.nih.gov/123/','Example citation'),(1,'Second','https://example.org','Second citation');
UNLOCK TABLES;
CREATE TABLE `cmap_foodrugs` (
  `node_id` int,
  `cmap_node_id` int,
  `tau` float
) ENGINE=InnoDB;
INSERT INTO `cmap_foodrugs` VALUES (1,2,-99.1),(2,3,98.0);
UNLOCK TABLES;
CREATE TABLE `cmap` (
  `cmap_node_id` int,
  `compound` text,
  `pert_type` text,
  `cell_line` text
) ENGINE=InnoDB;
INSERT INTO `cmap` VALUES (2,'compound A','trt_cp','cell A'),(3,'gene B','trt_sh','cell B');
CREATE TABLE `nodes` (
  `node_id` int,
  `sample_id` int
) ENGINE=InnoDB;
INSERT INTO `nodes` VALUES (1,10),(2,11);
CREATE TABLE `sample` (
  `sample_id` int,
  `study_id` int,
  `treatment` text,
  `origin_name` text,
  `time_point` text,
  `concentration` text
) ENGINE=InnoDB;
INSERT INTO `sample` VALUES (10,100,'resveratrol','culture','1h','1uM'),(11,100,'tea','culture','2h','2uM');
CREATE TABLE `study` (
  `study_id` int,
  `title` text,
  `accession` int,
  `pubmed_id` text
) ENGINE=InnoDB;
INSERT INTO `study` VALUES (100,'Example study',123,'456');
UNLOCK TABLES;
-- Dump completed on 2023-07-28 11:48:01
''',encoding='utf-8')
    build(dump,db,verify=False);index(db);monkeypatch.setattr(store,'PATH',db)
    return db

def test_complete_storage_lookup_provenance_and_pagination(source_db):
    manifest=store.metadata()
    assert manifest['tables']['TM_interactions']['rows']==4
    assert manifest['tables']['cmap_foodrugs']['rows']==2
    assert manifest['validation']['unsearchable_text_records']==1
    assert store.coverage()['associations']==4
    drug=store.search('d','sinvastatina')[0];food=store.search('f','toranja')[0]
    result=store.evidence(drug['id'],food['id'],limit=1)
    assert result['found'] and result['evidence_total']==2 and len(result['evidence'])==1
    assert result['risk'] is None and not result['personalized']
    assert result['evidence'][0]['source_excerpt']=='Example document'
    assert result['evidence'][0]['reference_url']=='https://pubmed.ncbi.nlm.nih.gov/123/'
    page2=store.evidence(drug['id'],food['id'],offset=1,limit=1)
    assert page2['evidence'][0]['source_record_id']=='1'
    assert store.library('toranja')['total']==1
    assert len(store.library(limit=1)['items'])==1
    assert store.get_foods(drug['id'])['total']==1
    raw=store.table_rows('TM_interactions',record='3')
    assert raw['rows'][0]['food'] is None
    with pytest.raises(ValueError):store.table_rows('usuarios')
    with pytest.raises(ValueError):store.table_rows('texts; DROP TABLE texts')
    with pytest.raises(ValueError):store.evidence('fd:d:1 OR 1=1',food['id'])

def test_checksum_rejects_partial_download(tmp_path):
    p=tmp_path/'partial.sql';p.write_text('partial')
    with pytest.raises(ValueError,match='checksum'):build(p,tmp_path/'never-created.sqlite')
    assert not (tmp_path/'never-created.sqlite').exists()


def test_molecular_join_preserves_experimental_context(source_db):
    found=store.molecular('resveratrol')
    assert found['total']==1
    row=found['rows'][0]
    assert row['compound']=='compound A' and row['treatment']=='resveratrol'
    assert row['tau']==-99.1 and row['title']=='Example study'
    assert 'risk' not in row
    assert store.molecular('gene b')['rows'][0]['pert_type']=='trt_sh'
    assert store.molecular('does-not-exist')['total']==0
    assert store.molecular(offset=1,limit=1)['rows'][0]['compound']=='gene B'
