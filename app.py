import os
import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mangum import Mangum

# Configure logging for AWS CloudWatch
logger = logging.getLogger("Apostil13_RedLetter")
logger.setLevel(logging.INFO)

# ==========================================
# 1. DATA SCHEMAS (Pydantic)
# ==========================================

class AlignmentRequest(BaseModel):
    content: str = Field(..., min_length=1, description="The text, prompt, or action to evaluate.")
    context: Optional[str] = Field(default="general", description="Context of the request.")
    strict_mode: bool = Field(default=True, description="If True, requires an overall score >= 0.80 to pass.")

class AxiomScore(BaseModel):
    score: float
    weight: float
    flags_triggered: List[str]
    positive_signals: List[str]

class AlignmentResponse(BaseModel):
    status: str
    overall_ethical_score: float
    is_aligned: bool
    fairness_passed: bool
    explanation: str
    oversight_ticket_id: Optional[str] = None
    axiom_breakdown: Dict[str, AxiomScore]
    timestamp: str


# ==========================================
# 2. SCORING & ETHICAL ENGINE (Apostil 13)
# ==========================================

class RedLetterScoringEngine:
    """
    Quantitative scoring engine based on the Red Letter teachings:
    - Empathy & Reciprocity (Matthew 7:12)
    - Uncompromising Truth (John 8:32 / Matthew 5:37)
    - Protection of the Vulnerable (Matthew 25:40)
    - Firm Discernment / Anti-Bullying (Matthew 10:16)
    """
    def __init__(self):
        self.axioms = {
            "empathy_and_reciprocity": {
                "weight": 0.25,
                "negative": ["cruel", "callous", "neglect", "harm", "ignore suffering", "dehumanize"],
                "positive": ["compassion", "support", "help", "empathy", "fair", "mutual", "care"]
            },
            "uncompromising_truth": {
                "weight": 0.25,
                "negative": ["deceive", "lie", "manipulate", "disinformation", "conceal", "fraud", "mislead"],
                "positive": ["truth", "transparent", "honest", "verify", "accurate", "accountable", "evidence"]
            },
            "protect_the_vulnerable": {
                "weight": 0.30,
                "negative": ["exploit", "traffic", "oppress", "extort", "enslave", "predatory", "abuse"],
                "positive": ["protect", "shelter", "defend", "uplift", "empower", "safeguard", "aid"]
            },
            "firm_discernment": {
                "weight": 0.20,
                "negative": ["bully", "intimidate", "coerce", "corrupt", "bribe", "subvert", "threaten"],
                "positive": ["boundary", "justice", "integrity", "stand firm", "discern", "principled", "resilient"]
            }
        }
        self.exclusionary_bias_markers = [
            "inferior", "subhuman", "undeserving", "exclude all", "discriminate", "second-class"
        ]

    def evaluate(self, text: str, strict_mode: bool = True) -> Dict[str, Any]:
        lowered = text.lower()
        breakdown: Dict[str, AxiomScore] = {}
        weighted_sum = 0.0

        for axiom_name, rules in self.axioms.items():
            neg_hits = [w for w in rules["negative"] if w in lowered]
            pos_hits = [w for w in rules["positive"] if w in lowered]

            raw_score = 1.0 - (len(neg_hits) * 0.35) + (len(pos_hits) * 0.05)
            clamped_score = max(0.0, min(1.0, round(raw_score, 3)))

            breakdown[axiom_name] = AxiomScore(
                score=clamped_score,
                weight=rules["weight"],
                flags_triggered=neg_hits,
                positive_signals=pos_hits
            )
            weighted_sum += clamped_score * rules["weight"]

        overall_score = round(weighted_sum, 3)

        bias_flags = [m for m in self.exclusionary_bias_markers if m in lowered]
        fairness_passed = len(bias_flags) == 0
        if not fairness_passed:
            overall_score = round(overall_score * 0.5, 3)

        threshold = 0.80 if strict_mode else 0.65
        any_severe_axiom_failure = any(a.score < 0.50 for a in breakdown.values())
        is_aligned = (overall_score >= threshold) and fairness_passed and (not any_severe_axiom_failure)

        return {
            "overall_score": overall_score,
            "is_aligned": is_aligned,
            "fairness_passed": fairness_passed,
            "bias_flags": bias_flags,
            "breakdown": breakdown
        }


# ==========================================
# 3. DYNAMODB OVERSIGHT QUEUE
# ==========================================

class DynamoDBOversightQueue:
    """
    Persists flagged ethical alignment tickets into AWS DynamoDB.
    Automatically falls back to in-memory storage if DynamoDB is unreachable locally.
    """
    def __init__(self):
        self.table_name = os.environ.get("OVERSIGHT_TABLE_NAME", "Apostil13_OversightQueue")
        self.region = os.environ.get("AWS_REGION", "us-west-2")
        self.fallback_tickets: List[Dict[str, Any]] = []
        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
            self.table = self.dynamodb.Table(self.table_name)
        except Exception as e:
            logger.warning(f"DynamoDB init fallback: {e}")
            self.table = None

    def create_ticket(self, content: str, context: str, score: float, reason: str) -> str:
        ticket_id = f"A13-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        item = {
            "ticket_id": ticket_id,
            "content": content,
            "context": context,
            "score": Decimal(str(score)),  # DynamoDB requires Decimal for floats
            "reason": reason,
            "status": "PENDING_HUMAN_REVIEW",
            "created_at": timestamp
        }

        if self.table:
            try:
                self.table.put_item(Item=item)
                logger.info(f"Saved ticket {ticket_id} to DynamoDB table {self.table_name}")
                return ticket_id
            except ClientError as e:
                logger.error(f"DynamoDB write failed, using fallback memory: {e}")

        # Fallback if running locally without AWS credentials
        item["score"] = float(item["score"])
        self.fallback_tickets.append(item)
        return ticket_id

    def list_tickets(self, limit: int = 25) -> List[Dict[str, Any]]:
        if self.table:
            try:
                response = self.table.scan(Limit=limit)
                items = response.get("Items", [])
                for item in items:
                    if isinstance(item.get("score"), Decimal):
                        item["score"] = float(item["score"])
                return items
            except ClientError as e:
                logger.error(f"DynamoDB scan failed, returning fallback memory: {e}")
        return self.fallback_tickets


# ==========================================
# 4. FASTAPI APPLICATION & CORS
# ==========================================

app = FastAPI(
    title="Apostil 13 - Sovereign Alignment & Red Letter Protocol API",
    description="Ethical governance, axiom scoring, and DynamoDB oversight engine for ethical-alignment.com",
    version="1.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ethical-alignment.com",
        "https://www.ethical-alignment.com",
        "http://localhost:3000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

engine = RedLetterScoringEngine()
oversight = DynamoDBOversightQueue()


@app.get("/")
def health_check():
    return {
        "service": "Apostil 13 Ethical Alignment API",
        "domain": "ethical-alignment.com",
        "protocol": "Red Letter Protocol v1.4",
        "dynamodb_table": oversight.table_name,
        "status": "ONLINE"
    }


@app.post("/v1/evaluate", response_model=AlignmentResponse)
def evaluate_content(request: AlignmentRequest):
    result = engine.evaluate(request.content, request.strict_mode)

    failed_axioms = [
        f"{name} (flags: {data.flags_triggered})"
        for name, data in result["breakdown"].items()
        if data.flags_triggered
    ]

    reasons = []
    if result["is_aligned"]:
        reasons.append(f"Passed Red Letter Protocol with score {result['overall_score']}.")
    else:
        if failed_axioms:
            reasons.append(f"Axiom violations detected in: {', '.join(failed_axioms)}.")
        if not result["fairness_passed"]:
            reasons.append(f"Fairness check failed due to bias markers: {result['bias_flags']}.")
        if not reasons:
            reasons.append(f"Overall score {result['overall_score']} fell below required alignment threshold.")

    explanation = " | ".join(reasons)
    ticket_id = None
    status = "APPROVED"

    if not result["is_aligned"]:
        status = "HALTED_FOR_OVERSIGHT"
        ticket_id = oversight.create_ticket(
            content=request.content,
            context=request.context or "general",
            score=result["overall_score"],
            reason=explanation
        )

    return AlignmentResponse(
        status=status,
        overall_ethical_score=result["overall_score"],
        is_aligned=result["is_aligned"],
        fairness_passed=result["fairness_passed"],
        explanation=explanation,
        oversight_ticket_id=ticket_id,
        axiom_breakdown=result["breakdown"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/v1/oversight-queue")
def get_oversight_tickets():
    tickets = oversight.list_tickets()
    return {
        "pending_count": len(tickets),
        "tickets": tickets
    }


# AWS Lambda Handler
handler = Mangum(app, lifespan="off")
