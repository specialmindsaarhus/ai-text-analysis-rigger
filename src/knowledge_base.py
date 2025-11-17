"""
Knowledge Base for RAG (Retrieval-Augmented Generation)

This module provides semantic search over the style guide to inject
relevant writing guidelines into LLM prompts.

Design:
- Loads style_guide.md and chunks it into retrievable segments
- Uses sentence-transformers for embeddings
- Uses FAISS for efficient similarity search
- Monitors file changes and auto-rebuilds index
- Extracts most relevant sentences from retrieved chunks
- Formats output with XML tags for LLM consumption
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class KnowledgeBase:
    """
    RAG-based knowledge base for style guide retrieval.

    Implements hybrid chunking (sections + sub-items) and adaptive retrieval
    based on document length.
    """

    def __init__(self, style_guide_path: str, min_guidelines: int = 5, max_guidelines: int = 15):
        """
        Initialize knowledge base.

        Args:
            style_guide_path: Path to style_guide.md file
            min_guidelines: Minimum number of guidelines to retrieve
            max_guidelines: Maximum number of guidelines to retrieve
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "RAG dependencies not installed. "
                "Install with: pip install sentence-transformers faiss-cpu"
            )

        self.style_guide_path = Path(style_guide_path)
        self.min_guidelines = min_guidelines
        self.max_guidelines = max_guidelines

        # Embeddings model
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Storage for chunks and index
        self.chunks: List[Dict[str, str]] = []
        self.index: Optional[faiss.Index] = None
        self.embeddings: Optional[np.ndarray] = None

        # File modification tracking
        self.last_modified: Optional[float] = None

        # Initialize
        if self.style_guide_path.exists():
            self._build_index()
        else:
            print(f"Warning: Style guide not found at {self.style_guide_path}")

    def _build_index(self):
        """Build or rebuild the FAISS index from style guide."""
        print(f"Building knowledge base from {self.style_guide_path}...")

        # Load and chunk the style guide
        self.chunks = self._load_and_chunk()

        if not self.chunks:
            print("Warning: No chunks extracted from style guide")
            return

        # Create embeddings
        texts_to_embed = [chunk['content'] for chunk in self.chunks]
        self.embeddings = self.model.encode(texts_to_embed, show_progress_bar=False)

        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))

        # Update modification time
        self.last_modified = self.style_guide_path.stat().st_mtime

        print(f"Knowledge base built: {len(self.chunks)} chunks indexed")

    def _load_and_chunk(self) -> List[Dict[str, str]]:
        """
        Load style guide and split into retrievable chunks.

        Uses hybrid chunking: sections + sub-items for granular retrieval.

        Returns:
            List of chunk dictionaries with 'section', 'content', 'type'
        """
        with open(self.style_guide_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = []

        # Extract XML-tagged sections
        sections = self._extract_sections(content)

        for section_name, section_content in sections.items():
            # Each section becomes a chunk
            chunks.append({
                'section': section_name,
                'content': section_content.strip(),
                'type': 'section',
                'original': section_content.strip()
            })

            # Also chunk large sections into sub-items
            sub_chunks = self._chunk_section(section_name, section_content)
            chunks.extend(sub_chunks)

        return chunks

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract XML-tagged sections from style guide."""
        sections = {}

        # Pattern to match <tag>content</tag>
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, content, re.DOTALL)

        for tag, section_content in matches:
            sections[tag] = section_content

        return sections

    def _chunk_section(self, section_name: str, content: str) -> List[Dict[str, str]]:
        """
        Break large sections into smaller sub-chunks.

        Uses various strategies based on section structure:
        - Bullet points
        - Numbered lists
        - Paragraphs with headers
        """
        chunks = []

        # Strategy 1: Extract bullet points
        bullet_pattern = r'^[•\-\*]\s+(.+?)(?=^[•\-\*]|\Z)'
        bullets = re.findall(bullet_pattern, content, re.MULTILINE | re.DOTALL)
        for bullet in bullets:
            bullet_text = bullet.strip()
            if len(bullet_text) > 20:  # Skip very short bullets
                chunks.append({
                    'section': section_name,
                    'content': bullet_text,
                    'type': 'sub-item',
                    'original': bullet_text
                })

        # Strategy 2: Extract paragraphs with strong semantic content
        # Split by double newline
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            para = para.strip()
            # Skip very short paragraphs, code blocks, and headers
            if len(para) > 50 and not para.startswith('#') and not para.startswith('```'):
                # Only add if not already covered by bullet extraction
                if para not in [c['content'] for c in chunks]:
                    chunks.append({
                        'section': section_name,
                        'content': para,
                        'type': 'paragraph',
                        'original': para
                    })

        return chunks

    def _check_and_rebuild(self):
        """Check if style guide has been modified and rebuild if needed."""
        if not self.style_guide_path.exists():
            return

        current_mtime = self.style_guide_path.stat().st_mtime

        if self.last_modified is None or current_mtime > self.last_modified:
            print("Style guide updated, rebuilding index...")
            self._build_index()

    def get_relevant_guidelines(self, text: str, top_k: Optional[int] = None) -> str:
        """
        Retrieve and format relevant guidelines for the given text.

        Args:
            text: Input text to analyze
            top_k: Number of guidelines to retrieve (None = adaptive based on text length)

        Returns:
            XML-formatted string with relevant guidelines
        """
        # Check for updates
        self._check_and_rebuild()

        if not self.index or not self.chunks:
            return ""

        # Determine retrieval count
        if top_k is None:
            top_k = self._adaptive_retrieval_count(text)

        # Get query embedding
        query_embedding = self.model.encode([text], show_progress_bar=False)

        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)

        # Retrieve chunks
        retrieved_chunks = [self.chunks[idx] for idx in indices[0]]

        # Extract most relevant sentences from each chunk
        guidelines = []
        for chunk in retrieved_chunks:
            relevant_sentences = self._extract_relevant_sentences(
                chunk['content'],
                text,
                max_sentences=3
            )
            if relevant_sentences:
                guidelines.append({
                    'section': chunk['section'],
                    'content': relevant_sentences,
                    'type': chunk['type']
                })

        # Format as XML
        return self._format_as_xml(guidelines)

    def _adaptive_retrieval_count(self, text: str) -> int:
        """
        Determine how many guidelines to retrieve based on text length.

        Args:
            text: Input text

        Returns:
            Number of guidelines to retrieve (between min and max)
        """
        word_count = len(text.split())

        # Scale linearly based on word count
        if word_count < 100:
            return self.min_guidelines
        elif word_count > 500:
            return self.max_guidelines
        else:
            # Linear interpolation
            ratio = (word_count - 100) / 400
            count = self.min_guidelines + int(ratio * (self.max_guidelines - self.min_guidelines))
            return count

    def _extract_relevant_sentences(self, chunk_text: str, query_text: str, max_sentences: int = 3) -> str:
        """
        Extract the most relevant sentences from a chunk.

        Uses sentence-level similarity scoring.

        Args:
            chunk_text: Text chunk to extract from
            query_text: Query text for relevance scoring
            max_sentences: Maximum number of sentences to extract

        Returns:
            Extracted sentences joined together
        """
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', chunk_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if not sentences:
            return chunk_text[:200]  # Fallback to first 200 chars

        if len(sentences) <= max_sentences:
            return chunk_text  # Return whole chunk if small enough

        # Compute sentence embeddings
        sentence_embeddings = self.model.encode(sentences, show_progress_bar=False)
        query_embedding = self.model.encode([query_text], show_progress_bar=False)

        # Compute similarities
        similarities = np.dot(sentence_embeddings, query_embedding.T).flatten()

        # Get top sentences
        top_indices = np.argsort(similarities)[-max_sentences:]
        top_indices = sorted(top_indices)  # Maintain original order

        # Join selected sentences
        selected = [sentences[i] for i in top_indices]
        return '. '.join(selected) + '.'

    def _format_as_xml(self, guidelines: List[Dict[str, str]]) -> str:
        """
        Format retrieved guidelines as XML for LLM prompt injection.

        Uses structured tags similar to SKILL.md pattern.

        Args:
            guidelines: List of guideline dictionaries

        Returns:
            XML-formatted string
        """
        if not guidelines:
            return ""

        xml_parts = ["<style_guidelines>"]

        # Group by section
        sections_seen = set()

        for guideline in guidelines:
            section = guideline['section']
            content = guideline['content']

            # Add section header if new section
            if section not in sections_seen:
                xml_parts.append(f"\n<{section}>")
                sections_seen.add(section)

            # Add content
            xml_parts.append(content)

        # Close all open sections
        for section in sections_seen:
            xml_parts.append(f"</{section}>")

        xml_parts.append("\n</style_guidelines>")

        return '\n'.join(xml_parts)

    def get_stats(self) -> Dict[str, any]:
        """Get knowledge base statistics."""
        return {
            'chunks_indexed': len(self.chunks) if self.chunks else 0,
            'style_guide_exists': self.style_guide_path.exists(),
            'last_modified': datetime.fromtimestamp(self.last_modified) if self.last_modified else None,
            'min_guidelines': self.min_guidelines,
            'max_guidelines': self.max_guidelines
        }
