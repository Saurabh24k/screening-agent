# Autonomous AI Screening Agent - Complete Implementation
# This is a comprehensive implementation of the AI screening system

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from abc import ABC, abstractmethod

# Mock imports for demonstration (in real implementation, install these packages)
# pip install langchain openai redis psycopg2 spacy PyMuPDF rapidfuzz

try:
    import spacy
    import openai
    from langchain.agents import Agent
    from langchain.memory import ConversationBufferMemory
    import redis
    import psycopg2
    from rapidfuzz import fuzz
except ImportError:
    print("Note: Some packages are mocked for demonstration. Install required packages for production use.")

# =============================================================================
# MODELS AND DATA STRUCTURES
# =============================================================================

class CandidateTier(Enum):
    A = "auto-schedule"  # Top tier - auto schedule
    B = "optional"       # Good fit - optional review
    C = "reject"         # Poor fit - reject

class PipelineStatus(Enum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    VERIFIED = "verified"
    SCREENED = "screened"
    SCORED = "scored"
    SCHEDULED = "scheduled"
    INTERVIEWED = "interviewed"
    COMPLETED = "completed"
    REJECTED = "rejected"

@dataclass
class Candidate:
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: str = ""
    skills: List[str] = None
    experience: Dict[str, int] = None  # skill -> years
    education: str = ""
    certifications: List[str] = None
    languages: List[str] = None
    notice_period: Optional[str] = None
    resume_text: str = ""
    resume_hash: str = ""
    jd_similarity: float = 0.0  # Job description similarity score
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = {}
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []

@dataclass
class JobDescription:
    id: str
    title: str
    company: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_required: int
    location: str
    description: str
    salary_range: Optional[str] = None

@dataclass
class ScreeningResult:
    candidate_id: str
    current_org: str
    current_role: str
    validated_skills: Dict[str, bool]
    availability: str
    relocation_intent: bool
    enthusiasm_score: float
    red_flags: List[str]
    notes: str

@dataclass
class MatchScore:
    candidate_id: str
    relevance_score: float  # 0-100
    tier: CandidateTier
    reasoning: str
    red_flags: List[str]
    skill_match_percentage: float

@dataclass
class PipelineState:
    candidate_id: str
    job_id: str
    status: PipelineStatus
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]
    retries: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent(ABC):
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        pass
    
    def log_info(self, message: str, candidate_id: str = None):
        prefix = f"[{candidate_id}] " if candidate_id else ""
        self.logger.info(f"{prefix}{message}")
    
    def log_error(self, message: str, candidate_id: str = None):
        prefix = f"[{candidate_id}] " if candidate_id else ""
        self.logger.error(f"{prefix}{message}")

# =============================================================================
# STORAGE AND MEMORY
# =============================================================================

class MemoryStore:
    def __init__(self):
        # In production, this would be Redis/PostgreSQL
        self.pipeline_states = {}
        self.candidates = {}
        self.job_descriptions = {}
        self.screening_results = {}
        self.match_scores = {}
        
    async def save_pipeline_state(self, state: PipelineState):
        self.pipeline_states[f"{state.candidate_id}:{state.job_id}"] = state
        
    async def get_pipeline_state(self, candidate_id: str, job_id: str) -> Optional[PipelineState]:
        return self.pipeline_states.get(f"{candidate_id}:{job_id}")
        
    async def save_candidate(self, candidate: Candidate):
        self.candidates[candidate.id] = candidate
        
    async def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return self.candidates.get(candidate_id)
        
    async def save_job_description(self, jd: JobDescription):
        self.job_descriptions[jd.id] = jd
        
    async def get_job_description(self, job_id: str) -> Optional[JobDescription]:
        return self.job_descriptions.get(job_id)
        
    async def find_duplicate_candidates(self, candidate: Candidate) -> List[Candidate]:
        duplicates = []
        for existing in self.candidates.values():
            if (existing.email == candidate.email or 
                existing.phone == candidate.phone or
                existing.resume_hash == candidate.resume_hash):
                duplicates.append(existing)
        return duplicates

# =============================================================================
# PARSING AGENT
# =============================================================================

class ParsingAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ParsingAgent", config)
        # In production, load spaCy model: self.nlp = spacy.load("en_core_web_sm")
        
    async def process(self, input_data: Dict[str, Any]) -> Candidate:
        resume_text = input_data.get("resume_text", "")
        resume_file = input_data.get("resume_file")
        job_description = input_data.get("job_description", "")
        
        # Extract text from resume file if provided
        if resume_file:
            resume_text = await self._extract_text_from_file(resume_file)
            
        # Parse candidate information
        candidate_data = await self._parse_resume(resume_text)
        candidate_data["resume_text"] = resume_text
        candidate_data["resume_hash"] = hashlib.md5(resume_text.encode()).hexdigest()
        
        # Calculate similarity to job description
        similarity_score = await self._calculate_jd_similarity(resume_text, job_description)
        candidate_data["jd_similarity"] = similarity_score
        
        candidate = Candidate(**candidate_data)
        self.log_info(f"Parsed candidate: {candidate.name}", candidate.id)
        
        return candidate
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        # In production, use PyMuPDF or similar for PDF extraction
        # For now, return mock text
        return f"Mock resume text extracted from {file_path}"
    
    async def _parse_resume(self, resume_text: str) -> Dict[str, Any]:
        # Mock parsing - in production, use spaCy NER + regex patterns
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        email = emails[0] if emails else "candidate@example.com"
        
        # Extract phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, resume_text)
        phone = phones[0] if phones else None
        
        # Mock extraction of other fields
        return {
            "id": hashlib.md5(email.encode()).hexdigest()[:8],
            "name": "John Doe",  # Would extract from resume
            "email": email,
            "phone": phone,
            "location": "San Francisco, CA",
            "skills": ["Python", "Machine Learning", "SQL", "AWS"],
            "experience": {"Python": 5, "Machine Learning": 3, "SQL": 4, "AWS": 2},
            "education": "BS Computer Science, Stanford University",
            "certifications": ["AWS Solutions Architect"],
            "languages": ["English", "Spanish"],
            "notice_period": "2 weeks"
        }
    
    async def _calculate_jd_similarity(self, resume_text: str, job_description: str) -> float:
        # In production, use BERT embeddings or similar
        # Mock similarity calculation
        common_words = set(resume_text.lower().split()) & set(job_description.lower().split())
        total_words = len(set(job_description.lower().split()))
        return len(common_words) / max(total_words, 1) * 100

# =============================================================================
# UNIQUENESS VERIFIER AGENT
# =============================================================================

class UniquenessVerifier(BaseAgent):
    def __init__(self, memory_store: MemoryStore, config: Dict[str, Any] = None):
        super().__init__("UniquenessVerifier", config)
        self.memory_store = memory_store
        
    async def process(self, candidate: Candidate) -> Dict[str, Any]:
        duplicates = await self.memory_store.find_duplicate_candidates(candidate)
        
        if duplicates:
            self.log_info(f"Found {len(duplicates)} potential duplicates", candidate.id)
            return {
                "is_duplicate": True,
                "duplicates": [d.id for d in duplicates],
                "action": "skip_or_merge"
            }
        
        self.log_info("No duplicates found - candidate is unique", candidate.id)
        return {
            "is_duplicate": False,
            "duplicates": [],
            "action": "proceed"
        }

# =============================================================================
# CALLING/SCREENING AGENT
# =============================================================================

class CallingAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("CallingAgent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> ScreeningResult:
        candidate = input_data["candidate"]
        job_description = input_data["job_description"]
        screening_mode = input_data.get("mode", "chat")  # "voice" or "chat"
        
        self.log_info(f"Starting {screening_mode} screening", candidate.id)
        
        if screening_mode == "voice":
            result = await self._conduct_voice_screening(candidate, job_description)
        else:
            result = await self._conduct_chat_screening(candidate, job_description)
            
        self.log_info("Screening completed", candidate.id)
        return result
    
    async def _conduct_voice_screening(self, candidate: Candidate, jd: JobDescription) -> ScreeningResult:
        # Mock voice screening - in production, integrate with Twilio + ElevenLabs
        self.log_info("Conducting voice screening call", candidate.id)
        
        # Simulate AI conversation
        await asyncio.sleep(1)  # Simulate call duration
        
        return ScreeningResult(
            candidate_id=candidate.id,
            current_org="TechCorp Inc",
            current_role="Senior Software Engineer",
            validated_skills={"Python": True, "Machine Learning": True, "SQL": True},
            availability="Available in 2 weeks",
            relocation_intent=True,
            enthusiasm_score=8.5,
            red_flags=[],
            notes="Candidate sounds enthusiastic and knowledgeable"
        )
    
    async def _conduct_chat_screening(self, candidate: Candidate, jd: JobDescription) -> ScreeningResult:
        # Mock chat screening - in production, integrate with WhatsApp/Web chat
        self.log_info("Conducting chat screening", candidate.id)
        
        # Simulate chat conversation
        await asyncio.sleep(0.5)
        
        return ScreeningResult(
            candidate_id=candidate.id,
            current_org="DataCorp LLC",
            current_role="ML Engineer",
            validated_skills={"Python": True, "Machine Learning": True, "AWS": False},
            availability="Immediate",
            relocation_intent=False,
            enthusiasm_score=7.2,
            red_flags=["Concerns about salary expectations"],
            notes="Good technical background, some concerns about compensation"
        )

# =============================================================================
# MATCHING ENGINE AGENT
# =============================================================================

class MatchingEngine(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("MatchingEngine", config)
        
    async def process(self, input_data: Dict[str, Any]) -> MatchScore:
        candidate = input_data["candidate"]
        job_description = input_data["job_description"]
        screening_result = input_data["screening_result"]
        
        self.log_info("Calculating match score", candidate.id)
        
        # Calculate skill match
        skill_match = await self._calculate_skill_match(candidate, job_description)
        
        # Calculate experience match
        experience_match = await self._calculate_experience_match(candidate, job_description)
        
        # Factor in screening results
        screening_factor = await self._calculate_screening_factor(screening_result)
        
        # Calculate overall relevance score
        relevance_score = (skill_match * 0.4 + experience_match * 0.3 + screening_factor * 0.3)
        
        # Determine tier
        tier = self._determine_tier(relevance_score, screening_result.red_flags)
        
        # Generate reasoning
        reasoning = await self._generate_reasoning(candidate, job_description, screening_result, relevance_score)
        
        match_score = MatchScore(
            candidate_id=candidate.id,
            relevance_score=relevance_score,
            tier=tier,
            reasoning=reasoning,
            red_flags=screening_result.red_flags,
            skill_match_percentage=skill_match
        )
        
        self.log_info(f"Match score: {relevance_score:.1f}, Tier: {tier.value}", candidate.id)
        return match_score
    
    async def _calculate_skill_match(self, candidate: Candidate, jd: JobDescription) -> float:
        required_skills = set(skill.lower() for skill in jd.required_skills)
        candidate_skills = set(skill.lower() for skill in candidate.skills)
        
        if not required_skills:
            return 100.0
            
        matched_skills = required_skills & candidate_skills
        return (len(matched_skills) / len(required_skills)) * 100
    
    async def _calculate_experience_match(self, candidate: Candidate, jd: JobDescription) -> float:
        total_experience = sum(candidate.experience.values())
        if total_experience >= jd.experience_required:
            return 100.0
        else:
            return (total_experience / jd.experience_required) * 100
    
    async def _calculate_screening_factor(self, screening_result: ScreeningResult) -> float:
        base_score = screening_result.enthusiasm_score * 10  # Convert to 0-100 scale
        
        # Reduce score for red flags
        penalty = len(screening_result.red_flags) * 10
        
        return max(0, base_score - penalty)
    
    def _determine_tier(self, relevance_score: float, red_flags: List[str]) -> CandidateTier:
        if red_flags and len(red_flags) > 2:
            return CandidateTier.C
        elif relevance_score >= 80:
            return CandidateTier.A
        elif relevance_score >= 60:
            return CandidateTier.B
        else:
            return CandidateTier.C
    
    async def _generate_reasoning(self, candidate: Candidate, jd: JobDescription, 
                                screening_result: ScreeningResult, score: float) -> str:
        # In production, use LLM to generate detailed reasoning
        if score >= 80:
            return f"Excellent match with strong skills in {', '.join(candidate.skills[:3])} and {screening_result.enthusiasm_score}/10 enthusiasm"
        elif score >= 60:
            return f"Good candidate with relevant experience, some skill gaps to address"
        else:
            return f"Limited match due to skill/experience gaps and screening concerns"

# =============================================================================
# SCHEDULING AGENT
# =============================================================================

class SchedulingAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("SchedulingAgent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate = input_data["candidate"]
        match_score = input_data["match_score"]
        
        if match_score.tier == CandidateTier.C:
            self.log_info("Candidate rejected - no scheduling needed", candidate.id)
            return {"action": "reject", "scheduled": False}
        
        self.log_info("Scheduling interview", candidate.id)
        
        # Mock scheduling - in production, integrate with Google Calendar/Outlook
        available_slots = await self._get_available_slots()
        selected_slot = available_slots[0] if available_slots else None
        
        if selected_slot:
            await self._send_calendar_invite(candidate, selected_slot)
            await self._send_confirmation_message(candidate, selected_slot)
            
            return {
                "action": "scheduled",
                "scheduled": True,
                "interview_time": selected_slot,
                "calendar_invite_sent": True
            }
        else:
            return {
                "action": "no_slots_available",
                "scheduled": False,
                "message": "No available interview slots"
            }
    
    async def _get_available_slots(self) -> List[datetime]:
        # Mock availability - in production, check actual calendar
        now = datetime.now()
        return [
            now + timedelta(days=1, hours=10),
            now + timedelta(days=2, hours=14),
            now + timedelta(days=3, hours=11)
        ]
    
    async def _send_calendar_invite(self, candidate: Candidate, slot_time: datetime):
        # Mock calendar integration
        self.log_info(f"Calendar invite sent for {slot_time}", candidate.id)
    
    async def _send_confirmation_message(self, candidate: Candidate, slot_time: datetime):
        # Mock notification
        self.log_info(f"Confirmation message sent to {candidate.email}", candidate.id)

# =============================================================================
# FEEDBACK LOOP AGENT
# =============================================================================

class FeedbackLoopAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("FeedbackLoopAgent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate = input_data["candidate"]
        interviewer_feedback = input_data.get("interviewer_feedback", {})
        
        self.log_info("Processing interview feedback", candidate.id)
        
        # Analyze feedback
        final_score = await self._calculate_final_score(interviewer_feedback)
        recommendation = await self._generate_recommendation(final_score, interviewer_feedback)
        
        return {
            "candidate_id": candidate.id,
            "final_score": final_score,
            "recommendation": recommendation,
            "feedback_summary": await self._summarize_feedback(interviewer_feedback),
            "next_action": self._determine_next_action(recommendation)
        }
    
    async def _calculate_final_score(self, feedback: Dict[str, Any]) -> float:
        # Mock scoring based on feedback
        technical_score = feedback.get("technical_score", 7.0)
        communication_score = feedback.get("communication_score", 8.0)
        culture_fit = feedback.get("culture_fit", 7.5)
        
        return (technical_score * 0.5 + communication_score * 0.3 + culture_fit * 0.2)
    
    async def _generate_recommendation(self, score: float, feedback: Dict[str, Any]) -> str:
        if score >= 8.0:
            return "Hire"
        elif score >= 6.5:
            return "Hold"
        else:
            return "Drop"
    
    async def _summarize_feedback(self, feedback: Dict[str, Any]) -> str:
        # In production, use LLM for summarization
        return f"Technical: {feedback.get('technical_score', 'N/A')}/10, Communication: {feedback.get('communication_score', 'N/A')}/10"
    
    def _determine_next_action(self, recommendation: str) -> str:
        if recommendation == "Hire":
            return "generate_offer"
        elif recommendation == "Hold":
            return "schedule_final_round"
        else:
            return "send_rejection"

# =============================================================================
# ORCHESTRATOR AGENT
# =============================================================================

class OrchestratorAgent(BaseAgent):
    def __init__(self, memory_store: MemoryStore, config: Dict[str, Any] = None):
        super().__init__("OrchestratorAgent", config)
        self.memory_store = memory_store
        
        # Initialize all sub-agents
        self.parsing_agent = ParsingAgent()
        self.uniqueness_verifier = UniquenessVerifier(memory_store)
        self.calling_agent = CallingAgent()
        self.matching_engine = MatchingEngine()
        self.scheduling_agent = SchedulingAgent()
        self.feedback_agent = FeedbackLoopAgent()
    
    async def process(self, input_data: Any) -> Any:
        """Required abstract method implementation - delegates to process_candidate"""
        if isinstance(input_data, dict) and "resume_data" in input_data and "job_id" in input_data:
            return await self.process_candidate(input_data["resume_data"], input_data["job_id"])
        else:
            raise ValueError("Invalid input format for OrchestratorAgent")
        
    async def process_candidate(self, resume_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Main pipeline orchestration method"""
        
        candidate_id = None
        try:
            # Step 1: Parse Resume
            self.log_info("Starting candidate processing pipeline")
            candidate = await self.parsing_agent.process(resume_data)
            candidate_id = candidate.id
            
            # Initialize pipeline state
            state = PipelineState(
                candidate_id=candidate_id,
                job_id=job_id,
                status=PipelineStatus.PARSED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                data={}
            )
            await self.memory_store.save_pipeline_state(state)
            await self.memory_store.save_candidate(candidate)
            
            # Step 2: Check for duplicates
            await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.VERIFIED)
            uniqueness_result = await self.uniqueness_verifier.process(candidate)
            
            if uniqueness_result["is_duplicate"]:
                self.log_info("Duplicate candidate detected - skipping", candidate_id)
                await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.REJECTED)
                return {"status": "rejected", "reason": "duplicate_candidate"}
            
            # Step 3: Get job description
            job_description = await self.memory_store.get_job_description(job_id)
            if not job_description:
                raise Exception(f"Job description not found: {job_id}")
            
            # Step 4: Conduct screening
            await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.SCREENED)
            screening_input = {
                "candidate": candidate,
                "job_description": job_description,
                "mode": "chat"
            }
            screening_result = await self.calling_agent.process(screening_input)
            
            # Step 5: Calculate match score
            await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.SCORED)
            matching_input = {
                "candidate": candidate,
                "job_description": job_description,
                "screening_result": screening_result
            }
            match_score = await self.matching_engine.process(matching_input)
            
            # Step 6: Schedule if qualified
            if match_score.tier != CandidateTier.C:
                await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.SCHEDULED)
                scheduling_input = {
                    "candidate": candidate,
                    "match_score": match_score
                }
                scheduling_result = await self.scheduling_agent.process(scheduling_input)
                
                if scheduling_result["scheduled"]:
                    await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.SCHEDULED)
                else:
                    await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.REJECTED)
                    
                return {
                    "status": "success",
                    "candidate_id": candidate_id,
                    "match_score": match_score.relevance_score,
                    "tier": match_score.tier.value,
                    "scheduled": scheduling_result["scheduled"],
                    "reasoning": match_score.reasoning
                }
            else:
                await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.REJECTED)
                return {
                    "status": "rejected",
                    "candidate_id": candidate_id,
                    "reason": "low_match_score",
                    "score": match_score.relevance_score
                }
                
        except Exception as e:
            self.log_error(f"Pipeline error: {str(e)}", candidate_id)
            if candidate_id:
                await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.REJECTED)
            return {"status": "error", "message": str(e)}
    
    async def process_interview_feedback(self, candidate_id: str, job_id: str, 
                                       feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process feedback after interview"""
        
        candidate = await self.memory_store.get_candidate(candidate_id)
        if not candidate:
            return {"status": "error", "message": "Candidate not found"}
        
        feedback_input = {
            "candidate": candidate,
            "interviewer_feedback": feedback
        }
        
        result = await self.feedback_agent.process(feedback_input)
        await self._update_pipeline_status(candidate_id, job_id, PipelineStatus.COMPLETED)
        
        return result
    
    async def _update_pipeline_status(self, candidate_id: str, job_id: str, status: PipelineStatus):
        """Update pipeline status in memory store"""
        state = await self.memory_store.get_pipeline_state(candidate_id, job_id)
        if state:
            state.status = status
            state.updated_at = datetime.now()
            await self.memory_store.save_pipeline_state(state)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

class AIScreeningSystem:
    def __init__(self):
        self.memory_store = MemoryStore()
        self.orchestrator = OrchestratorAgent(self.memory_store)
        self.logger = logging.getLogger("ai_screening_system")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def add_job_description(self, job_data: Dict[str, Any]) -> str:
        """Add a new job description to the system"""
        jd = JobDescription(**job_data)
        await self.memory_store.save_job_description(jd)
        self.logger.info(f"Added job description: {jd.id} - {jd.title}")
        return jd.id
    
    async def process_resume(self, resume_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Process a new resume for a specific job"""
        return await self.orchestrator.process_candidate(resume_data, job_id)
    
    async def submit_interview_feedback(self, candidate_id: str, job_id: str, 
                                     feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Submit feedback after interview"""
        return await self.orchestrator.process_interview_feedback(candidate_id, job_id, feedback)
    
    async def get_pipeline_status(self, candidate_id: str, job_id: str) -> Optional[PipelineState]:
        """Get current pipeline status for a candidate"""
        return await self.memory_store.get_pipeline_state(candidate_id, job_id)

# =============================================================================
# DEMO USAGE
# =============================================================================

async def demo_usage():
    """Demonstrate the AI screening system"""
    
    # Initialize system
    system = AIScreeningSystem()
    
    print("🤖 AI Screening System Demo")
    print("=" * 50)
    
    # Step 1: Add job description
    job_data = {
        "id": "job001",
        "title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "preferred_skills": ["Machine Learning", "Docker", "Kubernetes"],
        "experience_required": 5,
        "location": "San Francisco, CA",
        "description": "We are seeking a senior Python developer...",
        "salary_range": "$120k - $160k"
    }
    
    job_id = await system.add_job_description(job_data)
    print(f"✅ Added job: {job_data['title']}")
    
    # Step 2: Process resume
    resume_data = {
        "resume_text": """
        John Doe
        Senior Software Engineer
        john.doe@email.com
        (555) 123-4567
        
        SKILLS: Python, Django, PostgreSQL, AWS, Machine Learning, Docker
        EXPERIENCE: 6 years in software development
        EDUCATION: BS Computer Science, MIT
        """,
        "job_description": job_data["description"]
    }
    
    print("\n📄 Processing resume...")
    result = await system.process_resume(resume_data, job_id)
    
    print(f"📊 Processing Result:")
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Match Score: {result['match_score']:.1f}/100")
        print(f"   Tier: {result['tier']}")
        print(f"   Scheduled: {result['scheduled']}")
        print(f"   Reasoning: {result['reasoning']}")
    
    # Step 3: Check pipeline status
    candidate_id = result.get('candidate_id')
    if candidate_id:
        print(f"\n📈 Pipeline Status:")
        status = await system.get_pipeline_status(candidate_id, job_id)
        if status:
            print(f"   Current Status: {status.status.value}")
            print(f"   Created: {status.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Updated: {status.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 4: Simulate interview feedback (if candidate was scheduled)
    if result.get('scheduled'):
        print(f"\n💬 Submitting Interview Feedback...")
        
        feedback = {
            "technical_score": 8.5,
            "communication_score": 9.0,
            "culture_fit": 8.0,
            "notes": "Strong technical skills, excellent communication, good culture fit",
            "recommendation": "hire"
        }
        
        feedback_result = await system.submit_interview_feedback(candidate_id, job_id, feedback)
        print(f"   Final Score: {feedback_result['final_score']:.1f}/10")
        print(f"   Recommendation: {feedback_result['recommendation']}")
        print(f"   Next Action: {feedback_result['next_action']}")
        print(f"   Summary: {feedback_result['feedback_summary']}")
    
    print(f"\n✨ Demo completed successfully!")

# =============================================================================
# ADDITIONAL UTILITY FUNCTIONS
# =============================================================================

def create_sample_job_descriptions():
    """Create sample job descriptions for testing"""
    return [
        {
            "id": "job001",
            "title": "Senior Python Developer",
            "company": "TechCorp Inc",
            "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
            "preferred_skills": ["Machine Learning", "Docker", "Kubernetes"],
            "experience_required": 5,
            "location": "San Francisco, CA",
            "description": "We are seeking a senior Python developer with strong backend experience.",
            "salary_range": "$120k - $160k"
        },
        {
            "id": "job002", 
            "title": "Machine Learning Engineer",
            "company": "AI Innovations LLC",
            "required_skills": ["Python", "TensorFlow", "PyTorch", "SQL"],
            "preferred_skills": ["MLOps", "Kubernetes", "GCP"],
            "experience_required": 4,
            "location": "Remote",
            "description": "Join our ML team to build next-generation AI products.",
            "salary_range": "$130k - $180k"
        },
        {
            "id": "job003",
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
            "preferred_skills": ["TypeScript", "GraphQL", "AWS"],
            "experience_required": 3,
            "location": "New York, NY",
            "description": "Build scalable web applications in a fast-paced startup environment.",
            "salary_range": "$90k - $130k"
        }
    ]

def create_sample_resumes():
    """Create sample resume data for testing"""
    return [
        {
            "resume_text": """
            John Doe
            Senior Software Engineer
            john.newdoe@email.com | (555) 123-4567 | LinkedIn: /in/johndoe
            San Francisco, CA
            
            EXPERIENCE:
            • Senior Python Developer at TechCorp (2019-2024) - 5 years
            • Built scalable web applications using Django and PostgreSQL
            • Deployed applications on AWS with Docker containers
            • Led team of 4 developers on ML integration project
            
            SKILLS: Python, Django, PostgreSQL, AWS, Machine Learning, Docker, REST APIs
            EDUCATION: BS Computer Science, Stanford University (2018)
            CERTIFICATIONS: AWS Solutions Architect Associate
            """,
            "job_description": "Senior Python developer position with Django and AWS experience"
        },
        {
            "resume_text": """
            Sarah Johnson
            Machine Learning Engineer
            sarah.j@example.com | (555) 987-6543
            Remote (Austin, TX)
            
            EXPERIENCE:
            • ML Engineer at DataCorp (2020-2024) - 4 years
            • Developed recommendation systems using TensorFlow and PyTorch
            • Built MLOps pipelines on GCP with Kubernetes
            • Published 3 research papers on deep learning
            
            SKILLS: Python, TensorFlow, PyTorch, Scikit-learn, SQL, GCP, Kubernetes, MLOps
            EDUCATION: MS Data Science, UT Austin (2020), BS Mathematics, Rice University (2018)
            """,
            "job_description": "Machine learning engineer with experience in deep learning frameworks"
        }
    ]

# =============================================================================
# ADVANCED FEATURES (Future Extensions)
# =============================================================================

class LearningRecommenderAgent(BaseAgent):
    """Optional agent to suggest learning paths for rejected candidates"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LearningRecommenderAgent", config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate = input_data["candidate"]
        job_description = input_data["job_description"]
        match_score = input_data["match_score"]
        
        # Identify skill gaps
        missing_skills = self._identify_skill_gaps(candidate, job_description)
        
        # Generate learning recommendations
        recommendations = await self._generate_learning_path(missing_skills)
        
        return {
            "candidate_id": candidate.id,
            "skill_gaps": missing_skills,
            "learning_recommendations": recommendations,
            "estimated_timeline": "3-6 months"
        }
    
    def _identify_skill_gaps(self, candidate: Candidate, jd: JobDescription) -> List[str]:
        candidate_skills = set(skill.lower() for skill in candidate.skills)
        required_skills = set(skill.lower() for skill in jd.required_skills)
        return list(required_skills - candidate_skills)
    
    async def _generate_learning_path(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        # Mock learning recommendations - in production, integrate with learning platforms
        recommendations = []
        for skill in missing_skills:
            recommendations.append({
                "skill": skill,
                "resources": [
                    f"Online course: {skill} Fundamentals",
                    f"Practice project: Build a {skill} application",
                    f"Certification: {skill} Professional"
                ],
                "estimated_time": "4-6 weeks"
            })
        return recommendations

class VideoAnalysisAgent(BaseAgent):
    """Optional agent to analyze recorded video interviews"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("VideoAnalysisAgent", config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        video_url = input_data["video_url"]
        candidate_id = input_data["candidate_id"]
        
        # Mock video analysis - in production, use computer vision APIs
        analysis = {
            "engagement_score": 8.2,
            "confidence_level": 7.5,
            "speaking_pace": "appropriate",
            "eye_contact": "good",
            "body_language": "confident",
            "audio_quality": "clear",
            "technical_setup": "professional"
        }
        
        return {
            "candidate_id": candidate_id,
            "video_analysis": analysis,
            "overall_impression": "positive",
            "recommendations": ["Candidate shows strong engagement and professionalism"]
        }

class SentimentAgent(BaseAgent):
    """Optional agent to analyze candidate sentiment and enthusiasm"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("SentimentAgent", config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text_data = input_data["conversation_text"]
        candidate_id = input_data["candidate_id"]
        
        # Mock sentiment analysis - in production, use NLP sentiment models
        sentiment_score = 0.75  # Positive sentiment
        enthusiasm_indicators = [
            "Used positive language about role",
            "Asked thoughtful questions",
            "Expressed genuine interest"
        ]
        
        return {
            "candidate_id": candidate_id,
            "sentiment_score": sentiment_score,
            "enthusiasm_level": "high",
            "indicators": enthusiasm_indicators,
            "concerns": []
        }

# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

class IntegrationManager:
    """Manages external service integrations"""
    
    def __init__(self):
        self.services = {
            "twilio": None,      # Voice calls
            "elevenlabs": None,  # Voice synthesis
            "openai": None,      # LLM processing
            "google_calendar": None,  # Calendar integration
            "sendgrid": None,    # Email notifications
            "slack": None        # Team notifications
        }
    
    async def setup_integrations(self, config: Dict[str, str]):
        """Initialize external service connections"""
        # Mock setup - in production, initialize actual API clients
        for service_name, api_key in config.items():
            if service_name in self.services:
                self.services[service_name] = f"mock_{service_name}_client"
        
        print("🔗 External integrations configured")
    
    def get_service(self, service_name: str):
        """Get configured service client"""
        return self.services.get(service_name)

# =============================================================================
# CONFIGURATION AND DEPLOYMENT
# =============================================================================

class SystemConfig:
    """System configuration management"""
    
    DEFAULT_CONFIG = {
        "parsing": {
            "models": ["spacy_en_core_web_sm"],
            "similarity_threshold": 0.7
        },
        "screening": {
            "default_mode": "chat",
            "voice_enabled": True,
            "max_call_duration": 900  # 15 minutes
        },
        "matching": {
            "skill_weight": 0.4,
            "experience_weight": 0.3,
            "screening_weight": 0.3,
            "tier_a_threshold": 80,
            "tier_b_threshold": 60
        },
        "scheduling": {
            "available_hours": "9-17",
            "timezone": "UTC",
            "buffer_minutes": 15
        },
        "notifications": {
            "email_enabled": True,
            "sms_enabled": True,
            "slack_enabled": False
        }
    }
    
    def __init__(self, config_override: Dict[str, Any] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_override:
            self._merge_config(config_override)
    
    def _merge_config(self, override: Dict[str, Any]):
        """Recursively merge configuration overrides"""
        for key, value in override.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for the AI screening system"""
    
    print("🚀 Starting AI Screening System")
    print("=" * 50)
    
    # Run the demo
    await demo_usage()
    
    # Show system capabilities
    print(f"\n🎯 System Capabilities:")
    print(f"✅ Resume parsing with NLP")
    print(f"✅ Duplicate candidate detection")
    print(f"✅ AI-powered voice/chat screening")
    print(f"✅ Intelligent candidate matching")
    print(f"✅ Automated interview scheduling")
    print(f"✅ Feedback collection and analysis")
    print(f"✅ Full pipeline orchestration")
    
    print(f"\n🔧 Optional Extensions Available:")
    print(f"• Learning path recommendations")
    print(f"• Video interview analysis")
    print(f"• Sentiment analysis")
    print(f"• Background verification")
    print(f"• Automated offer generation")
    
    print(f"\n📝 To deploy in production:")
    print(f"1. Install required packages: pip install -r requirements.txt")
    print(f"2. Configure external APIs (OpenAI, Twilio, etc.)")
    print(f"3. Set up database (PostgreSQL/MongoDB)")
    print(f"4. Configure Redis for caching")
    print(f"5. Deploy with Docker/Kubernetes")

if __name__ == "__main__":
    # Run the system
    asyncio.run(main())