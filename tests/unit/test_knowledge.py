from sih.domain.knowledge.service import KnowledgePlatform
from sih.domain.knowledge.models import KnowledgeSourceType

def test_knowledge_document_indexing_and_search():
    kp = KnowledgePlatform()
    doc = kp.index_document(
        title="Project Q3 Meeting Notes",
        content="We discussed the roadmap, pending tasks, and budget allocations for Q3.",
        source_type=KnowledgeSourceType.USER_PROVIDED,
        workspace_id="ws-101"
    )
    assert doc.title == "Project Q3 Meeting Notes"

    results = kp.search_knowledge("roadmap", workspace_id="ws-101")
    assert len(results) == 1
    assert results[0].id == doc.id

def test_knowledge_entity_graph():
    kp = KnowledgePlatform()
    person = kp.register_entity("Alice Smith", "Person")
    project = kp.register_entity("Project Alpha", "Project")
    
    kp.link_entities(person.id, project.id, "LEADS")

    relations = kp.get_entity_relations(person.id)
    assert len(relations) == 1
    assert relations[0]["relation"] == "LEADS"
    assert relations[0]["target"] == "Project Alpha"
