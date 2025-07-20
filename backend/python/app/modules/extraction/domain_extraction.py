import json
import uuid
from typing import List, Literal, Optional
from enum import Enum

import aiohttp
import jwt
import numpy as np
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.config.configuration_service import (
    DefaultEndpoints,
    Routes,
    TokenScopes,
    config_node_constants,
)
from app.config.utils.named_constants.arangodb_constants import (
    CollectionNames,
    DepartmentNames,
)
from app.config.utils.named_constants.http_status_code_constants import HttpStatusCode
from app.modules.extraction.prompt_template import prompt, aviation_prompt
from app.modules.extraction.confidence_utils import route_document_by_confidence, quality_monitor
from app.utils.llm import get_llm
from app.utils.time_conversion import get_epoch_timestamp_in_ms
from app.utils.token_counter import count_tokens
import tiktoken

# Prompt / completion token limits
MAX_PROMPT = 32_000          # hard prompt limit
MAX_OUT    = 512             # response budget

# Confidence-based processing thresholds
class ConfidenceBand(Enum):
    HIGH = "HIGH"      # >= 0.85
    MEDIUM = "MEDIUM"  # 0.6 - 0.84
    LOW = "LOW"        # < 0.6

class ConfidenceThresholds:
    AUTO_APPROVE = 0.85
    HUMAN_REVIEW = 0.6
    AUTO_REJECT = 0.3
    SAFETY_CRITICAL_MIN = 0.8  # Aviation safety documents need higher confidence

# Confidence-based cache TTL (in seconds)
CONFIDENCE_CACHE_CONFIG = {
    ConfidenceBand.HIGH: 86400,    # 24 hours for high confidence
    ConfidenceBand.MEDIUM: 43200,  # 12 hours for medium confidence  
    ConfidenceBand.LOW: 3600       # 1 hour for low confidence
}

# Update the Literal types
SentimentType = Literal["Positive", "Neutral", "Negative"]

# Aviation-specific types
AviationSentimentType = Literal[
    "Safety Critical",
    "Advisory", 
    "Routine",
    "Positive",
    "Negative",
    "Regulatory"
]

FlightPhaseType = Literal[
    "preflight",
    "pushback",
    "taxi",
    "takeoff",
    "initial_climb",
    "climb",
    "cruise",
    "descent",
    "approach",
    "landing",
    "taxi_in",
    "shutdown",
    "turnaround"
]

ProcedureType = Literal["Normal", "Non-Normal", "Emergency"]

MaintenanceType = Literal[
    "Scheduled",
    "Unscheduled",
    "MEL",
    "SB",
    "AD",
    "Modification"
]


class SubCategories(BaseModel):
    level1: str = Field(description="Level 1 subcategory")
    level2: str = Field(description="Level 2 subcategory")
    level3: str = Field(description="Level 3 subcategory")


class DocumentClassification(BaseModel):
    departments: List[str] = Field(
        description="The list of departments this document belongs to", max_items=3
    )
    categories: str = Field(description="Main category this document belongs to")
    subcategories: SubCategories = Field(
        description="Nested subcategories for the document"
    )
    languages: List[str] = Field(
        description="List of languages detected in the document"
    )
    sentiment: SentimentType = Field(description="Overall sentiment of the document")
    confidence_score: float = Field(
        description="Confidence score of the classification", ge=0, le=1
    )
    topics: List[str] = Field(
        description="List of key topics/themes extracted from the document"
    )
    summary: str = Field(description="Summary of the document")
    confidence_band: Optional[str] = Field(default=None, description="Confidence band: HIGH/MEDIUM/LOW")
    requires_review: Optional[bool] = Field(default=None, description="Whether document requires human review")
    cache_ttl: Optional[int] = Field(default=None, description="Cache TTL based on confidence")


# Aviation-specific models
class FlightOperationsMetadata(BaseModel):
    flight_phase: Optional[List[FlightPhaseType]] = Field(
        default=None,
        description="Flight phases covered in the document"
    )
    procedure_type: Optional[ProcedureType] = Field(
        default=None,
        description="Type of procedure: Normal, Non-Normal, or Emergency"
    )
    checklist_section: Optional[str] = Field(
        default=None,
        description="Specific checklist name or section"
    )
    systems_affected: Optional[List[str]] = Field(
        default=None,
        description="Aircraft systems affected or discussed"
    )


class MaintenanceMetadata(BaseModel):
    aircraft_type: Optional[str] = Field(
        default=None,
        description="ICAO aircraft type code (e.g., B737, A320)"
    )
    ata_chapter: Optional[str] = Field(
        default=None,
        description="ATA chapter number for the system/component"
    )
    maintenance_type: Optional[MaintenanceType] = Field(
        default=None,
        description="Type of maintenance activity"
    )
    regulatory_references: Optional[List[str]] = Field(
        default=None,
        description="Applicable ADs, SBs, or other regulatory references"
    )
    components_involved: Optional[List[str]] = Field(
        default=None,
        description="Specific components or parts involved"
    )
    tools_required: Optional[List[str]] = Field(
        default=None,
        description="Special tools or equipment required"
    )


class AviationDocumentClassification(BaseModel):
    departments: List[str] = Field(
        description="List of aviation departments (1-3)",
        max_items=3,
        min_items=1
    )
    category: str = Field(
        description="Either 'Flight Operations' or 'Aircraft Maintenance'"
    )
    subcategories: SubCategories = Field(
        description="Hierarchical aviation subcategories"
    )
    languages: List[str] = Field(
        description="Languages detected in the document"
    )
    sentiment: AviationSentimentType = Field(
        description="Aviation-specific sentiment classification"
    )
    confidence_score: float = Field(
        description="Confidence score of the classification",
        ge=0.0,
        le=1.0
    )
    topics: List[str] = Field(
        description="3-6 aviation-specific topics",
        min_items=3,
        max_items=6
    )
    summary: str = Field(
        description="Summary focusing on safety and operational impact"
    )
    flight_operations_metadata: Optional[FlightOperationsMetadata] = Field(
        default=None,
        description="Metadata specific to flight operations documents"
    )
    maintenance_metadata: Optional[MaintenanceMetadata] = Field(
        default=None,
        description="Metadata specific to maintenance documents"
    )
    confidence_band: Optional[str] = Field(default=None, description="Confidence band: HIGH/MEDIUM/LOW")
    requires_review: Optional[bool] = Field(default=None, description="Whether document requires human review")
    cache_ttl: Optional[int] = Field(default=None, description="Cache TTL based on confidence")
    safety_critical_low_confidence: Optional[bool] = Field(default=None, description="Safety doc with low confidence")


class DomainExtractor:
    def __init__(self, logger, base_arango_service, config_service) -> None:
        self.logger = logger
        self.arango_service = base_arango_service
        self.config_service = config_service
        self.logger.info("🚀 self.arango_service: %s", self.arango_service)
        self.logger.info("🚀 self.arango_service.db: %s", self.arango_service.db)

        self.parser = PydanticOutputParser(pydantic_object=DocumentClassification)
        self.aviation_parser = PydanticOutputParser(pydantic_object=AviationDocumentClassification)

        # Initialize topics storage
        self.topics_store = set()  # Store all accepted topics

        # Initialize TF-IDF vectorizer for topic similarity
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.similarity_threshold = 0.65  # Adjusted for TF-IDF similarity

        # Initialize LDA model as backup
        self.lda = LatentDirichletAllocation(
            n_components=10, random_state=42  # Adjust based on your needs
        )

        # Configure retry parameters
        self.max_retries = 3
        self.min_wait = 1  # seconds
        self.max_wait = 10  # seconds

    def _calculate_confidence_band(self, confidence_score: float) -> ConfidenceBand:
        """Calculate confidence band from confidence score"""
        if confidence_score >= ConfidenceThresholds.AUTO_APPROVE:
            return ConfidenceBand.HIGH
        elif confidence_score >= ConfidenceThresholds.HUMAN_REVIEW:
            return ConfidenceBand.MEDIUM
        else:
            return ConfidenceBand.LOW

    def _should_require_review(self, confidence_score: float, is_safety_critical: bool = False) -> bool:
        """Determine if document requires human review based on confidence"""
        if is_safety_critical:
            return confidence_score < ConfidenceThresholds.SAFETY_CRITICAL_MIN
        return ConfidenceThresholds.HUMAN_REVIEW <= confidence_score < ConfidenceThresholds.AUTO_APPROVE

    def _get_cache_ttl(self, confidence_band: ConfidenceBand) -> int:
        """Get cache TTL based on confidence band"""
        return CONFIDENCE_CACHE_CONFIG.get(confidence_band, 3600)  # Default to 1 hour

    def _is_safety_critical_content(self, metadata) -> bool:
        """Check if content is safety critical based on metadata"""
        if hasattr(metadata, 'sentiment'):
            return metadata.sentiment == "Safety Critical"
        return False

    def _enhance_with_confidence_data(self, metadata, is_aviation: bool = False):
        """Enhance metadata with confidence-based processing data"""
        confidence_band = self._calculate_confidence_band(metadata.confidence_score)
        is_safety_critical = self._is_safety_critical_content(metadata)
        
        # Set confidence band
        metadata.confidence_band = confidence_band.value
        
        # Set review requirement
        metadata.requires_review = self._should_require_review(
            metadata.confidence_score, 
            is_safety_critical
        )
        
        # Set cache TTL
        metadata.cache_ttl = self._get_cache_ttl(confidence_band)
        
        # Aviation-specific: flag safety critical docs with low confidence
        if is_aviation and hasattr(metadata, 'safety_critical_low_confidence'):
            metadata.safety_critical_low_confidence = (
                is_safety_critical and confidence_band == ConfidenceBand.LOW
            )
        
        return metadata

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: retry_state.args[0].logger.warning(
            f"Retrying LLM call after error. Attempt {retry_state.attempt_number}"
        ),
    )
    async def _call_llm(self, messages) -> dict | None:
        """Wrapper for LLM calls with retry logic"""
        return await self.llm.ainvoke(messages)

    async def find_similar_topics(self, new_topic: str) -> str:
        """
        Find if a similar topic already exists in the topics store using TF-IDF similarity.
        Returns the existing topic if a match is found, otherwise returns the new topic.
        """
        # First check exact matches
        if new_topic in self.topics_store:
            return new_topic

        # If no topics exist yet, return the new topic
        if not self.topics_store:
            return new_topic

        try:
            # Convert topics to TF-IDF vectors
            all_topics = list(self.topics_store) + [new_topic]
            tfidf_matrix = self.vectorizer.fit_transform(all_topics)

            # Calculate cosine similarity between new topic and existing topics
            # Get the last row (new topic)
            new_topic_vector = tfidf_matrix[-1:]
            # Get all but the last row
            existing_topics_matrix = tfidf_matrix[:-1]

            similarities = cosine_similarity(new_topic_vector, existing_topics_matrix)[
                0
            ]

            # Find the most similar topic
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]

            if max_similarity >= self.similarity_threshold:
                return list(self.topics_store)[max_similarity_idx]

            # If TF-IDF similarity is low, try LDA as backup
            if max_similarity < self.similarity_threshold:
                try:
                    # Fit LDA on all topics
                    dtm = self.vectorizer.fit_transform(all_topics)
                    topic_distributions = self.lda.fit_transform(dtm)

                    # Compare topic distributions
                    new_topic_dist = topic_distributions[-1]
                    existing_topics_dist = topic_distributions[:-1]

                    # Calculate Jensen-Shannon divergence or cosine similarity
                    lda_similarities = cosine_similarity(
                        [new_topic_dist], existing_topics_dist
                    )[0]
                    max_lda_sim_idx = np.argmax(lda_similarities)
                    max_lda_similarity = lda_similarities[max_lda_sim_idx]

                    if max_lda_similarity >= self.similarity_threshold:
                        return list(self.topics_store)[max_lda_sim_idx]

                except Exception as e:
                    self.logger.error(f"❌ Error in LDA similarity check: {str(e)}")

        except Exception as e:
            self.logger.error(f"❌ Error in topic similarity check: {str(e)}")

        return new_topic

    async def process_new_topics(self, new_topics: List[str]) -> List[str]:
        """
        Process new topics against existing topics store.
        Returns list of topics, using existing ones where matches are found.
        """
        processed_topics = []
        for topic in new_topics:
            matched_topic = await self.find_similar_topics(topic)
            processed_topics.append(matched_topic)
            # Only add to topics_store if it's a new topic
            if matched_topic == topic:  # This means no match was found
                self.topics_store.add(topic)

        return list(set(processed_topics))

    async def extract_metadata(
        self, content: str, org_id: str
    ) -> DocumentClassification:
        """
        Extract metadata from document content using Azure OpenAI.
        Includes reflection logic to attempt recovery from parsing failures.
        """
        self.logger.info("🎯 Extracting domain metadata - CHUNKING VERSION ACTIVE")
        # Initialise LLM with explicit token limits
        self.llm = await get_llm(
            self.logger,
            self.config_service,
            max_tokens=MAX_OUT,
        )

        try:
            self.logger.info(f"🎯 Extracting departments for org_id: {org_id}")
            departments = await self.arango_service.get_departments(org_id)
            if not departments:
                departments = [dept.value for dept in DepartmentNames]

            # Format department list for the prompt
            department_list = "\n".join(f'     - "{dept}"' for dept in departments)

            # Format sentiment list for the prompt
            sentiment_list = "\n".join(
                f'     - "{sentiment}"' for sentiment in SentimentType.__args__
            )

            filled_prompt = prompt.replace(
                "{department_list}", department_list
            ).replace("{sentiment_list}", sentiment_list)
            self.prompt_template = PromptTemplate.from_template(filled_prompt)
            
            self.logger.info("🎯 Prompt formatted successfully")
            
            # Calculate token overhead from template with error handling
            try:
                self.logger.info("🔧 About to initialize tiktoken encoder...")
                enc = tiktoken.encoding_for_model(self.llm.model_name)
                self.logger.info(f"🔧 Tiktoken encoder initialized for model: {self.llm.model_name}")
                
                self.logger.info("🔧 About to get template...")
                TEMPLATE = self.prompt_template.template
                self.logger.info(f"🔧 Template retrieved, length: {len(TEMPLATE)}")
                
                self.logger.info("🔧 About to count tokens...")
                OVERHEAD = count_tokens(TEMPLATE.format(content=""), self.llm.model_name)
                self.logger.info(f"🔧 Token overhead calculated: {OVERHEAD}")
                
                self.logger.info("🔧 About to calculate STEP...")
                STEP = MAX_PROMPT - MAX_OUT - OVERHEAD  # safe room per chunk
                self.logger.info(f"🔧 STEP calculated: {STEP}")
                
            except Exception as e:
                self.logger.error(f"❌ Error in token overhead calculation: {str(e)}")
                self.logger.error(f"❌ Model name: {getattr(self.llm, 'model_name', 'UNKNOWN')}")
                self.logger.error(f"❌ Template type: {type(self.prompt_template)}")
                # Fallback to safe defaults
                self.logger.error("❌ Using fallback values - will send entire content as single chunk")
                enc = None
                OVERHEAD = 1000  # Conservative estimate
                STEP = MAX_PROMPT - MAX_OUT - OVERHEAD
            
            try:
                self.logger.info("🔧 About to log template overhead...")
                self.logger.info(f"🔧 Template overhead: {OVERHEAD} tokens, Step size: {STEP} tokens")
                self.logger.info("🔧 Template overhead logged successfully")
            except Exception as e:
                self.logger.error(f"❌ Error logging template overhead: {str(e)}")
                try:
                    self.logger.error(f"OVERHEAD type: {type(OVERHEAD)}, value: {OVERHEAD}")
                    self.logger.error(f"STEP type: {type(STEP)}, value: {STEP}")
                except:
                    self.logger.error("❌ Cannot even log OVERHEAD/STEP values")

            try:
                self.logger.info("📊 About to encode content...")
                # Chunk content to respect token limits
                toks = enc.encode(content)
                content_tokens = len(toks)
                self.logger.info(f"📊 Content has {content_tokens} tokens, will create {(content_tokens + STEP - 1) // STEP} chunks")
                
                self.logger.info("📦 About to create blocks...")
                blocks = [
                    enc.decode(toks[i : i + STEP]) for i in range(0, len(toks), STEP)
                ]
                
                self.logger.info(f"📦 Created {len(blocks)} chunks for processing")
            except Exception as e:
                self.logger.error(f"❌ Error in chunking logic: {str(e)}")
                # Fallback to original behavior - send entire content
                self.logger.error("❌ Falling back to single chunk processing")
                blocks = [content]

            results = []
            for idx, block in enumerate(blocks, 1):
                formatted_prompt = self.prompt_template.format(content=block)
                
                # Log actual token counts for debugging
                chunk_tokens = len(enc.encode(block))
                full_prompt_tokens = len(enc.encode(formatted_prompt))
                self.logger.info(f"🔍 Chunk {idx} debug: chunk_tokens={chunk_tokens}, full_prompt_tokens={full_prompt_tokens}, STEP={STEP}, OVERHEAD={OVERHEAD}")
                
                if full_prompt_tokens > MAX_PROMPT:
                    self.logger.error(f"❌ Chunk {idx} exceeds MAX_PROMPT! full_prompt_tokens={full_prompt_tokens} > MAX_PROMPT={MAX_PROMPT}")
                
                messages = [HumanMessage(content=formatted_prompt)]
                try:
                    resp = await self._call_llm(messages)
                    results.append(self._parse(resp))
                except Exception as e:
                    self.logger.warning("LLM call failed on chunk %d: %s", idx, e)
                    self.logger.error(f"❌ Failed chunk {idx} had {full_prompt_tokens} tokens (MAX_PROMPT={MAX_PROMPT})")

            final_result = self._merge_chunks(results)
            
            # Enhance with confidence-based data
            final_result = self._enhance_with_confidence_data(final_result, is_aviation=False)
            
            # Log confidence-based routing decision
            self.logger.info(f"📊 Extraction confidence: {final_result.confidence_score:.3f} ({final_result.confidence_band})")
            if final_result.requires_review:
                self.logger.info("🔍 Document flagged for human review")
                
            return final_result

        except Exception as e:
            self.logger.error(f"❌ Error during metadata extraction: {str(e)}")
            raise

    def _parse(self, response) -> DocumentClassification:
        """Parse LLM response into DocumentClassification object"""
        # Clean the response content
        response_text = response.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        try:
            # Parse the response using the Pydantic parser
            parsed_response = self.parser.parse(response_text)
            return parsed_response
        except Exception as parse_error:
            self.logger.error(f"❌ Failed to parse response: {str(parse_error)}")
            self.logger.error(f"Response content: {response_text}")
            # Return a default DocumentClassification on parse failure
            return DocumentClassification(
                departments=[],
                categories="Unknown",
                subcategories=SubCategories(level1="Unknown", level2="Unknown", level3="Unknown"),
                languages=["Unknown"],
                sentiment="Neutral",
                confidence_score=0.0,
                topics=[],
                summary=""
            )

    def _merge_chunks(self, parts: list[DocumentClassification]) -> DocumentClassification:
        """Union sets and concatenate summary; simple majority for category."""
        if not parts:
            return DocumentClassification(
                departments=[],
                categories="Unknown", 
                subcategories=SubCategories(level1="Unknown", level2="Unknown", level3="Unknown"),
                languages=["Unknown"],
                sentiment="Neutral",
                confidence_score=0.0,
                topics=[],
                summary=""
            )
        
        base = parts[0]
        base.departments = sorted({d for p in parts for d in p.departments})
        base.languages = sorted({l for p in parts for l in p.languages})
        base.topics = sorted({t for p in parts for t in p.topics})[:20]
        base.summary = " ".join(p.summary for p in parts if p.summary)
        return base

    async def extract_aviation_metadata(
        self, content: str, org_id: str
    ) -> AviationDocumentClassification:
        """
        Extract aviation-specific metadata from document content using Azure OpenAI.
        """
        self.logger.info("✈️ Extracting aviation domain metadata")
        
        # Initialize LLM with explicit token limits
        self.llm = await get_llm(
            self.logger,
            self.config_service,
            max_tokens=MAX_OUT,
        )
        
        try:
            # Aviation departments list
            aviation_departments = [
                "Flight Operations",
                "Aircraft Maintenance",
                "Air Traffic Control",
                "Safety & Quality Assurance",
                "Regulatory Compliance",
                "Training & Certification",
                "Ground Operations",
                "Engineering & Technical Publications",
                "Flight Dispatch",
                "Emergency Response"
            ]
            
            # Use aviation prompt template
            self.prompt_template = PromptTemplate.from_template(aviation_prompt)
            
            # Calculate token overhead
            try:
                enc = tiktoken.encoding_for_model(self.llm.model_name)
                TEMPLATE = self.prompt_template.template
                OVERHEAD = count_tokens(TEMPLATE.format(content=""), self.llm.model_name)
                STEP = MAX_PROMPT - MAX_OUT - OVERHEAD
                
            except Exception as e:
                self.logger.warning(f"⚠️ Token counting failed: {str(e)}, using fallback")
                STEP = 25000  # Conservative fallback
            
            # Chunk the content if needed
            chunks = []
            if len(content) > STEP:
                self.logger.info(f"📄 Content exceeds token limit, chunking required")
                for i in range(0, len(content), STEP):
                    chunks.append(content[i:i + STEP])
            else:
                chunks = [content]
            
            # Process each chunk
            all_results = []
            for i, chunk in enumerate(chunks):
                self.logger.info(f"🔄 Processing chunk {i+1} of {len(chunks)}")
                
                messages = [
                    HumanMessage(content=self.prompt_template.format(content=chunk))
                ]
                
                try:
                    response = await self._call_llm(messages)
                    if response:
                        parsed = await self._parse_aviation_response(response.content)
                        if parsed:
                            all_results.append(parsed)
                except Exception as e:
                    self.logger.error(f"❌ Error processing chunk {i+1}: {str(e)}")
                    continue
            
            # Merge results if multiple chunks
            if len(all_results) > 1:
                final_result = self._merge_aviation_chunks(all_results)
            elif all_results:
                final_result = all_results[0]
            else:
                # Return default aviation classification
                final_result = AviationDocumentClassification(
                    departments=["Flight Operations"],
                    category="Flight Operations",
                    subcategories=SubCategories(level1="Unknown", level2="Unknown", level3=""),
                    languages=["English"],
                    sentiment="Routine",
                    confidence_score=0.0,
                    topics=["aviation", "operations", "safety"],
                    summary="Unable to extract metadata",
                    flight_operations_metadata=None,
                    maintenance_metadata=None
                )
            
            # Enhance with confidence-based data (aviation-specific)
            final_result = self._enhance_with_confidence_data(final_result, is_aviation=True)
            
            # Log aviation-specific confidence routing
            self.logger.info(f"✈️ Aviation extraction confidence: {final_result.confidence_score:.3f} ({final_result.confidence_band})")
            if final_result.requires_review:
                self.logger.info("🔍 Aviation document flagged for review")
            if hasattr(final_result, 'safety_critical_low_confidence') and final_result.safety_critical_low_confidence:
                self.logger.warning("⚠️ SAFETY CRITICAL document with LOW confidence - immediate review required!")
                
            return final_result
                
        except Exception as e:
            self.logger.error(f"❌ Aviation metadata extraction failed: {str(e)}")
            raise
    
    async def _parse_aviation_response(self, response_text: str) -> AviationDocumentClassification:
        """Parse LLM response for aviation metadata"""
        try:
            # Clean response
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Handle optional metadata fields
            flight_ops_metadata = None
            if "flight_operations_metadata" in data and data["flight_operations_metadata"]:
                flight_ops_metadata = FlightOperationsMetadata(**data["flight_operations_metadata"])
            
            maintenance_metadata = None  
            if "maintenance_metadata" in data and data["maintenance_metadata"]:
                maintenance_metadata = MaintenanceMetadata(**data["maintenance_metadata"])
            
            # Create classification object
            return AviationDocumentClassification(
                departments=data["departments"],
                category=data["category"],
                subcategories=SubCategories(**data["subcategories"]),
                languages=data["languages"],
                sentiment=data["sentiment"],
                confidence_score=data["confidence_score"],
                topics=data["topics"],
                summary=data["summary"],
                flight_operations_metadata=flight_ops_metadata,
                maintenance_metadata=maintenance_metadata
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse aviation response: {str(e)}")
            raise
    
    def _merge_aviation_chunks(self, parts: list[AviationDocumentClassification]) -> AviationDocumentClassification:
        """Merge multiple aviation document classifications"""
        if not parts:
            return None
            
        base = parts[0]
        base.departments = sorted({d for p in parts for d in p.departments})[:3]
        base.languages = sorted({l for p in parts for l in p.languages})
        base.topics = sorted({t for p in parts for t in p.topics})[:6]
        base.summary = " ".join(p.summary for p in parts if p.summary)
        
        # Merge flight ops metadata if present
        if any(p.flight_operations_metadata for p in parts):
            flight_phases = []
            systems = []
            for p in parts:
                if p.flight_operations_metadata:
                    if p.flight_operations_metadata.flight_phase:
                        flight_phases.extend(p.flight_operations_metadata.flight_phase)
                    if p.flight_operations_metadata.systems_affected:
                        systems.extend(p.flight_operations_metadata.systems_affected)
            
            if flight_phases or systems:
                base.flight_operations_metadata = FlightOperationsMetadata(
                    flight_phase=list(set(flight_phases)) if flight_phases else None,
                    systems_affected=list(set(systems)) if systems else None,
                    procedure_type=base.flight_operations_metadata.procedure_type if base.flight_operations_metadata else None,
                    checklist_section=base.flight_operations_metadata.checklist_section if base.flight_operations_metadata else None
                )
        
        # Merge maintenance metadata if present  
        if any(p.maintenance_metadata for p in parts):
            refs = []
            components = []
            tools = []
            for p in parts:
                if p.maintenance_metadata:
                    if p.maintenance_metadata.regulatory_references:
                        refs.extend(p.maintenance_metadata.regulatory_references)
                    if p.maintenance_metadata.components_involved:
                        components.extend(p.maintenance_metadata.components_involved)
                    if p.maintenance_metadata.tools_required:
                        tools.extend(p.maintenance_metadata.tools_required)
            
            if refs or components or tools:
                base.maintenance_metadata = MaintenanceMetadata(
                    aircraft_type=base.maintenance_metadata.aircraft_type if base.maintenance_metadata else None,
                    ata_chapter=base.maintenance_metadata.ata_chapter if base.maintenance_metadata else None,
                    maintenance_type=base.maintenance_metadata.maintenance_type if base.maintenance_metadata else None,
                    regulatory_references=list(set(refs)) if refs else None,
                    components_involved=list(set(components)) if components else None,
                    tools_required=list(set(tools)) if tools else None
                )
        
        return base

    async def save_metadata_to_db(
        self, org_id: str, record_id: str, metadata: DocumentClassification, virtual_record_id: str
    ) -> dict | None:
        """
        Extract metadata from a document in ArangoDB and create department relationships
        """
        self.logger.info("🚀 Saving metadata to ArangoDB")

        try:
            # Route document based on confidence score
            metadata_dict = metadata.dict() if hasattr(metadata, 'dict') else metadata.__dict__
            metadata_dict['document_id'] = record_id
            metadata_dict['org_id'] = org_id
            
            routing_decision = await route_document_by_confidence(record_id, metadata_dict)
            self.logger.info(f"📊 Confidence routing: {routing_decision['processing_path']}")
            
            # Add routing information to document
            doc_updates = {
                'confidence_score': metadata.confidence_score,
                'confidence_band': metadata.confidence_band,
                'requires_review': metadata.requires_review,
                'processing_path': routing_decision['processing_path'],
                'cache_ttl': metadata.cache_ttl
            }
            # Retrieve the document content from ArangoDB
            record = await self.arango_service.get_document(
                record_id, CollectionNames.RECORDS.value
            )
            doc = dict(record)
            # Create relationships with departments
            for department in metadata.departments:
                try:
                    dept_query = f"FOR d IN {CollectionNames.DEPARTMENTS.value} FILTER d.departmentName == @department RETURN d"
                    cursor = self.arango_service.db.aql.execute(
                        dept_query, bind_vars={"department": department}
                    )
                    dept_doc = cursor.next()
                    self.logger.info(f"🚀 Department: {dept_doc}")

                    if dept_doc:
                        edge = {
                            "_from": f"{CollectionNames.RECORDS.value}/{record_id}",
                            "_to": f"{CollectionNames.DEPARTMENTS.value}/{dept_doc['_key']}",
                            "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                        }
                        await self.arango_service.batch_create_edges(
                            [edge], CollectionNames.BELONGS_TO_DEPARTMENT.value
                        )
                        self.logger.info(
                            f"🔗 Created relationship between document {record_id} and department {department}"
                        )

                except StopIteration:
                    self.logger.warning(f"⚠️ No department found for: {department}")
                    continue
                except Exception as e:
                    self.logger.error(
                        f"❌ Error creating relationship with department {department}: {str(e)}"
                    )
                    continue

            # Handle single category
            category_query = f"FOR c IN {CollectionNames.CATEGORIES.value} FILTER c.name == @name RETURN c"
            cursor = self.arango_service.db.aql.execute(
                category_query, bind_vars={"name": metadata.categories}
            )
            try:
                category_doc = cursor.next()
                if category_doc is None:
                    raise KeyError("No category found")
                category_key = category_doc["_key"]
            except (StopIteration, KeyError, TypeError):
                category_key = str(uuid.uuid4())
                self.arango_service.db.collection(
                    CollectionNames.CATEGORIES.value
                ).insert(
                    {
                        "_key": category_key,
                        "name": metadata.categories,
                    }
                )

            # Create category relationship if it doesn't exist
            edge_query = f"""
            FOR e IN {CollectionNames.BELONGS_TO_CATEGORY.value}
            FILTER e._from == @from AND e._to == @to
            RETURN e
            """
            cursor = self.arango_service.db.aql.execute(
                edge_query,
                bind_vars={
                    "from": f"records/{record_id}",
                    "to": f"categories/{category_key}",
                },
            )
            if not cursor.count():
                self.arango_service.db.collection(
                    CollectionNames.BELONGS_TO_CATEGORY.value
                ).insert(
                    {
                        "_from": f"{CollectionNames.RECORDS.value}/{record_id}",
                        "_to": f"{CollectionNames.CATEGORIES.value}/{category_key}",
                        "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                    }
                )

            # Handle subcategories with similar pattern
            def handle_subcategory(name, level, parent_key, parent_collection) -> str:
                collection_name = getattr(
                    CollectionNames, f"SUBCATEGORIES{level}"
                ).value
                query = f"FOR s IN {collection_name} FILTER s.name == @name RETURN s"
                cursor = self.arango_service.db.aql.execute(
                    query, bind_vars={"name": name}
                )
                try:
                    doc = cursor.next()
                    if doc is None:
                        raise KeyError("No subcategory found")
                    key = doc["_key"]
                except (StopIteration, KeyError, TypeError):
                    key = str(uuid.uuid4())
                    self.arango_service.db.collection(collection_name).insert(
                        {
                            "_key": key,
                            "name": name,
                        }
                    )

                # Create belongs_to relationship
                edge_query = f"""
                FOR e IN {CollectionNames.BELONGS_TO_CATEGORY.value}
                FILTER e._from == @from AND e._to == @to
                RETURN e
                """
                cursor = self.arango_service.db.aql.execute(
                    edge_query,
                    bind_vars={
                        "from": f"{CollectionNames.RECORDS.value}/{record_id}",
                        "to": f"{collection_name}/{key}",
                    },
                )
                if not cursor.count():
                    self.arango_service.db.collection(
                        CollectionNames.BELONGS_TO_CATEGORY.value
                    ).insert(
                        {
                            "_from": f"{CollectionNames.RECORDS.value}/{record_id}",
                            "_to": f"{collection_name}/{key}",
                            "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                        }
                    )

                # Create hierarchy relationship
                if parent_key:
                    edge_query = f"""
                    FOR e IN {CollectionNames.INTER_CATEGORY_RELATIONS.value}
                    FILTER e._from == @from AND e._to == @to
                    RETURN e
                    """
                    cursor = self.arango_service.db.aql.execute(
                        edge_query,
                        bind_vars={
                            "from": f"{collection_name}/{key}",
                            "to": f"{parent_collection}/{parent_key}",
                        },
                    )
                    if not cursor.count():
                        self.arango_service.db.collection(
                            CollectionNames.INTER_CATEGORY_RELATIONS.value
                        ).insert(
                            {
                                "_from": f"{collection_name}/{key}",
                                "_to": f"{parent_collection}/{parent_key}",
                                "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                            }
                        )
                return key

            # Process subcategories
            sub1_key = handle_subcategory(
                metadata.subcategories.level1, "1", category_key, "categories"
            )
            sub2_key = handle_subcategory(
                metadata.subcategories.level2, "2", sub1_key, "subcategories1"
            )
            handle_subcategory(
                metadata.subcategories.level3, "3", sub2_key, "subcategories2"
            )

            # Handle languages
            for language in metadata.languages:
                query = f"FOR l IN {CollectionNames.LANGUAGES.value} FILTER l.name == @name RETURN l"
                cursor = self.arango_service.db.aql.execute(
                    query, bind_vars={"name": language}
                )
                try:
                    lang_doc = cursor.next()
                    if lang_doc is None:
                        raise KeyError("No language found")
                    lang_key = lang_doc["_key"]
                except (StopIteration, KeyError, TypeError):
                    lang_key = str(uuid.uuid4())
                    self.arango_service.db.collection(
                        CollectionNames.LANGUAGES.value
                    ).insert(
                        {
                            "_key": lang_key,
                            "name": language,
                        }
                    )

                # Create relationship if it doesn't exist
                edge_query = f"""
                FOR e IN {CollectionNames.BELONGS_TO_LANGUAGE.value}
                FILTER e._from == @from AND e._to == @to
                RETURN e
                """
                cursor = self.arango_service.db.aql.execute(
                    edge_query,
                    bind_vars={
                        "from": f"records/{record_id}",
                        "to": f"languages/{lang_key}",
                    },
                )
                if not cursor.count():
                    self.arango_service.db.collection(
                        CollectionNames.BELONGS_TO_LANGUAGE.value
                    ).insert(
                        {
                            "_from": f"{CollectionNames.RECORDS.value}/{record_id}",
                            "_to": f"{CollectionNames.LANGUAGES.value}/{lang_key}",
                            "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                        }
                    )

            # Handle topics
            for topic in metadata.topics:
                query = f"FOR t IN {CollectionNames.TOPICS.value} FILTER t.name == @name RETURN t"
                cursor = self.arango_service.db.aql.execute(
                    query, bind_vars={"name": topic}
                )
                try:
                    topic_doc = cursor.next()
                    if topic_doc is None:
                        raise KeyError("No topic found")
                    topic_key = topic_doc["_key"]
                except (StopIteration, KeyError, TypeError):
                    topic_key = str(uuid.uuid4())
                    self.arango_service.db.collection(
                        CollectionNames.TOPICS.value
                    ).insert(
                        {
                            "_key": topic_key,
                            "name": topic,
                        }
                    )

                # Create relationship if it doesn't exist
                edge_query = f"""
                FOR e IN {CollectionNames.BELONGS_TO_TOPIC.value}
                FILTER e._from == @from AND e._to == @to
                RETURN e
                """
                cursor = self.arango_service.db.aql.execute(
                    edge_query,
                    bind_vars={
                        "from": f"records/{record_id}",
                        "to": f"topics/{topic_key}",
                    },
                )
                if not cursor.count():
                    self.arango_service.db.collection(
                        CollectionNames.BELONGS_TO_TOPIC.value
                    ).insert(
                        {
                            "_from": f"{CollectionNames.RECORDS.value}/{record_id}",
                            "_to": f"{CollectionNames.TOPICS.value}/{topic_key}",
                            "createdAtTimestamp": get_epoch_timestamp_in_ms(),
                        }
                    )

            # Handle summary document
            if metadata.summary:
                document_id = await self.save_summary_to_storage(org_id, record_id,virtual_record_id, metadata.summary)
                if document_id is None:
                    self.logger.error("❌ Failed to save summary to storage")


            self.logger.info(
                f"🚀 Metadata saved successfully for document: {document_id}"
            )

            doc.update(
                {
                    "summaryDocumentId": document_id,
                    "extractionStatus": "COMPLETED",
                    "lastExtractionTimestamp": get_epoch_timestamp_in_ms(),
                }
            )
            docs = [doc]

            self.logger.info(
                f"🎯 Upserting domain metadata for document: {document_id}"
            )
            await self.arango_service.batch_upsert_nodes(
                docs, CollectionNames.RECORDS.value
            )

            doc.update(
                {
                    "departments": [dept for dept in metadata.departments],
                    "categories": metadata.categories,
                    "subcategoryLevel1": metadata.subcategories.level1,
                    "subcategoryLevel2": metadata.subcategories.level2,
                    "subcategoryLevel3": metadata.subcategories.level3,
                    "topics": metadata.topics,
                    "languages": metadata.languages,
                    "summary": metadata.summary,
                }
            )

            return doc

        except Exception as e:
            self.logger.error(f"❌ Error saving metadata to ArangoDB: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: retry_state.args[0].logger.warning(
            f"Retrying API call after error. Attempt {retry_state.attempt_number}"
        ),
    )
    async def _create_placeholder(self, session, url, data, headers) -> dict | None:
        """Helper method to create placeholder with retry logic"""
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != HttpStatusCode.SUCCESS.value:
                    try:
                        error_response = await response.json()
                        self.logger.error("❌ Failed to create placeholder. Status: %d, Error: %s",
                                        response.status, error_response)
                    except aiohttp.ContentTypeError:
                        error_text = await response.text()
                        self.logger.error("❌ Failed to create placeholder. Status: %d, Response: %s",
                                        response.status, error_text[:200])
                    raise aiohttp.ClientError(f"Failed with status {response.status}")

                response_data = await response.json()
                self.logger.debug("✅ Successfully created placeholder")
                return response_data
        except aiohttp.ClientError as e:
            self.logger.error("❌ Network error creating placeholder: %s", str(e))
            raise
        except Exception as e:
            self.logger.error("❌ Unexpected error creating placeholder: %s", str(e))
            raise aiohttp.ClientError(f"Unexpected error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: retry_state.args[0].logger.warning(
            f"Retrying API call after error. Attempt {retry_state.attempt_number}"
        ),
    )
    async def _get_signed_url(self, session, url, data, headers) -> dict | None:
        """Helper method to get signed URL with retry logic"""
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != HttpStatusCode.SUCCESS.value:
                    try:
                        error_response = await response.json()
                        self.logger.error("❌ Failed to get signed URL. Status: %d, Error: %s",
                                        response.status, error_response)
                    except aiohttp.ContentTypeError:
                        error_text = await response.text()
                        self.logger.error("❌ Failed to get signed URL. Status: %d, Response: %s",
                                        response.status, error_text[:200])
                    raise aiohttp.ClientError(f"Failed with status {response.status}")

                response_data = await response.json()
                self.logger.debug("✅ Successfully retrieved signed URL")
                return response_data
        except aiohttp.ClientError as e:
            self.logger.error("❌ Network error getting signed URL: %s", str(e))
            raise
        except Exception as e:
            self.logger.error("❌ Unexpected error getting signed URL: %s", str(e))
            raise aiohttp.ClientError(f"Unexpected error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: retry_state.args[0].logger.warning(
            f"Retrying API call after error. Attempt {retry_state.attempt_number}"
        ),
    )
    async def _upload_to_signed_url(self, session, signed_url, data) -> int | None:
        """Helper method to upload to signed URL with retry logic"""
        try:
            async with session.put(
                signed_url,
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != HttpStatusCode.SUCCESS.value:
                    try:
                        error_response = await response.json()
                        self.logger.error("❌ Failed to upload to signed URL. Status: %d, Error: %s",
                                        response.status, error_response)
                    except aiohttp.ContentTypeError:
                        error_text = await response.text()
                        self.logger.error("❌ Failed to upload to signed URL. Status: %d, Response: %s",
                                        response.status, error_text[:200])
                    raise aiohttp.ClientError(f"Failed to upload with status {response.status}")

                self.logger.debug("✅ Successfully uploaded to signed URL")
                return response.status
        except aiohttp.ClientError as e:
            self.logger.error("❌ Network error uploading to signed URL: %s", str(e))
            raise
        except Exception as e:
            self.logger.error("❌ Unexpected error uploading to signed URL: %s", str(e))
            raise aiohttp.ClientError(f"Unexpected error: {str(e)}")


    async def save_summary_to_storage(self, org_id: str, record_id: str, virtual_record_id: str, summary_doc: dict) -> str | None:
        """
        Save summary document to storage using FormData upload
        Returns:
            str | None: document_id if successful, None if failed
        """
        try:
            self.logger.info("🚀 Starting summary storage process for record: %s", record_id)

            # Generate JWT token
            try:
                payload = {
                    "orgId": org_id,
                    "scopes": [TokenScopes.STORAGE_TOKEN.value],
                }
                secret_keys = await self.config_service.get_config(
                    config_node_constants.SECRET_KEYS.value
                )
                scoped_jwt_secret = secret_keys.get("scopedJwtSecret")
                if not scoped_jwt_secret:
                    raise ValueError("Missing scoped JWT secret")

                jwt_token = jwt.encode(payload, scoped_jwt_secret, algorithm="HS256")
                headers = {
                    "Authorization": f"Bearer {jwt_token}"
                }
            except Exception as e:
                self.logger.error("❌ Failed to generate JWT token: %s", str(e))
                return None

            # Get endpoint configuration
            try:
                endpoints = await self.config_service.get_config(
                    config_node_constants.ENDPOINTS.value
                )
                nodejs_endpoint = endpoints.get("cm", {}).get("endpoint", DefaultEndpoints.NODEJS_ENDPOINT.value)
                if not nodejs_endpoint:
                    raise ValueError("Missing CM endpoint configuration")

                storage = await self.config_service.get_config(
                    config_node_constants.STORAGE.value
                )
                storage_type = storage.get("storageType")
                if not storage_type:
                    raise ValueError("Missing storage type configuration")
                self.logger.info("🚀 Storage type: %s", storage_type)
            except Exception as e:
                self.logger.error("❌ Failed to get endpoint configuration: %s", str(e))
                return None

            if storage_type == "local":
                try:
                    async with aiohttp.ClientSession() as session:
                        # Convert summary_doc to JSON string and then to bytes
                        upload_data = {
                            "summary": summary_doc,
                            "virtualRecordId": virtual_record_id
                        }
                        json_data = json.dumps(upload_data).encode('utf-8')

                        # Create form data
                        form_data = aiohttp.FormData()
                        form_data.add_field('file',
                                        json_data,
                                        filename=f'summary_{record_id}.json',
                                        content_type='application/json')
                        form_data.add_field('documentName', f'summary_{record_id}')
                        form_data.add_field('documentPath', 'summaries')
                        form_data.add_field('isVersionedFile', 'true')
                        form_data.add_field('extension', 'json')
                        form_data.add_field('recordId', record_id)

                        # Make upload request
                        upload_url = f"{nodejs_endpoint}{Routes.STORAGE_UPLOAD.value}"
                        self.logger.info("📤 Uploading summary to storage for record: %s", record_id)

                        async with session.post(upload_url,
                                            data=form_data,
                                            headers=headers) as response:
                            if response.status != HttpStatusCode.SUCCESS.value:
                                try:
                                    error_response = await response.json()
                                    self.logger.error("❌ Failed to upload summary. Status: %d, Error: %s",
                                                    response.status, error_response)
                                except aiohttp.ContentTypeError:
                                    error_text = await response.text()
                                    self.logger.error("❌ Failed to upload summary. Status: %d, Response: %s",
                                                    response.status, error_text[:200])
                                return None

                            response_data = await response.json()
                            document_id = response_data.get('_id')

                            if not document_id:
                                self.logger.error("❌ No document ID in upload response")
                                return None

                            self.logger.info("✅ Successfully uploaded summary for document: %s", document_id)
                            return document_id

                except aiohttp.ClientError as e:
                    self.logger.error("❌ Network error during upload process: %s", str(e))
                    return None
                except Exception as e:
                    self.logger.error("❌ Unexpected error during upload process: %s", str(e))
                    self.logger.exception("Detailed error trace:")
                    return None

            else:
                placeholder_data = {
                    "documentName": f"summary_{record_id}",
                    "documentPath": "summaries",
                    "extension": "json"
                }

                try:
                    async with aiohttp.ClientSession() as session:
                        # Step 1: Create placeholder
                        self.logger.info("📝 Creating placeholder for record: %s", record_id)
                        placeholder_url = f"{nodejs_endpoint}{Routes.STORAGE_PLACEHOLDER.value}"
                        document = await self._create_placeholder(session, placeholder_url, placeholder_data, headers)

                        document_id = document.get("_id")
                        if not document_id:
                            self.logger.error("❌ No document ID in placeholder response")
                            return None

                        self.logger.info("📄 Created placeholder with ID: %s", document_id)

                        # Step 2: Get signed URL
                        self.logger.info("🔑 Getting signed URL for document: %s", document_id)
                        upload_data = {
                            "summary": summary_doc,
                            "virtualRecordId": virtual_record_id
                        }

                        upload_url = f"{nodejs_endpoint}{Routes.STORAGE_DIRECT_UPLOAD.value.format(documentId=document_id)}"
                        upload_result = await self._get_signed_url(session, upload_url, upload_data, headers)

                        signed_url = upload_result.get('signedUrl')
                        if not signed_url:
                            self.logger.error("❌ No signed URL in response for document: %s", document_id)
                            return None

                        # Step 3: Upload to signed URL
                        self.logger.info("📤 Uploading summary to storage for document: %s", document_id)
                        await self._upload_to_signed_url(session, signed_url, upload_data)

                        self.logger.info("✅ Successfully completed summary storage process for document: %s", document_id)
                        return document_id

                except aiohttp.ClientError as e:
                    self.logger.error("❌ Network error during storage process: %s", str(e))
                    return None
                except Exception as e:
                    self.logger.error("❌ Unexpected error during storage process: %s", str(e))
                    self.logger.exception("Detailed error trace:")
                    return None

        except Exception as e:
            self.logger.error("❌ Critical error in saving summary to storage: %s", str(e))
            self.logger.exception("Detailed error trace:")
            return None
