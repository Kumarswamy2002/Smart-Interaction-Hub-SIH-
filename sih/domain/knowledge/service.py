from typing import Optional
from sih.domain.knowledge.models import Document, KnowledgeItem, Entity, EntityRelationship, KnowledgeSourceType

class KnowledgePlatform:
    """Knowledge Platform handling documents, semantic items, entities, relationships & provenance."""
    def __init__(self):
        self._documents: dict[str, Document] = {}
        self._items: dict[str, KnowledgeItem] = {}
        self._entities: dict[str, Entity] = {}
        self._relationships: list[EntityRelationship] = []

    def index_document(
        self,
        title: str,
        content: str,
        source_type: KnowledgeSourceType = KnowledgeSourceType.USER_PROVIDED,
        user_id: str | None = None,
        workspace_id: str | None = None,
        metadata: dict | None = None
    ) -> Document:
        doc = Document(
            title=title,
            content=content,
            source_type=source_type,
            user_id=user_id,
            workspace_id=workspace_id,
            metadata=metadata or {}
        )
        self._documents[doc.id] = doc

        # Create snippet KnowledgeItem
        snippet = content[:300] + ("..." if len(content) > 300 else "")
        item = KnowledgeItem(
            document_id=doc.id,
            title=title,
            content_snippet=snippet,
            tags=list(metadata.keys()) if metadata else [],
            source_type=source_type
        )
        self._items[item.id] = item
        return doc

    def register_entity(self, name: str, entity_type: str, properties: dict | None = None) -> Entity:
        entity = Entity(name=name, entity_type=entity_type, properties=properties or {})
        self._entities[entity.id] = entity
        return entity

    def link_entities(self, source_id: str, target_id: str, relation: str) -> EntityRelationship:
        rel = EntityRelationship(source_entity_id=source_id, target_entity_id=target_id, relation_type=relation)
        self._relationships.append(rel)
        return rel

    def search_knowledge(
        self,
        query: str,
        workspace_id: str | None = None,
        source_type: KnowledgeSourceType | None = None
    ) -> list[Document]:
        query_lower = query.lower()
        results = []
        for doc in self._documents.values():
            if workspace_id and doc.workspace_id and doc.workspace_id != workspace_id:
                continue
            if source_type and doc.source_type != source_type:
                continue

            if query_lower in doc.title.lower() or query_lower in doc.content.lower():
                results.append(doc)
        return results

    def get_entity_relations(self, entity_id: str) -> list[dict]:
        output = []
        for rel in self._relationships:
            if rel.source_entity_id == entity_id:
                target = self._entities.get(rel.target_entity_id)
                output.append({"relation": rel.relation_type, "target": target.name if target else rel.target_entity_id})
        return output

knowledge_platform = KnowledgePlatform()
