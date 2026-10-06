/**
 * APOSTIL 13 — AI RED LETTER ETHICAL GUARDRAIL ENGINE
 * Extracted standalone JavaScript
 * 
 * Usage:
 *   <script src="app.js"></script>
 *   Then bind to your UI elements with IDs:
 *   - demo-input (textarea)
 *   - demo-conduct (select)
 *   - demo-motivation (input)
 *   - demo-beneficial (checkbox)
 *   - demo-override (checkbox)
 *   - demo-eval-btn (button)
 *   - status-badge (span)
 *   - demo-output (div)
 */

const EthicalState = Object.freeze({
  APPROVED: "APPROVED",
  BLOCKED: "BLOCKED"
});

const ConductProfile = Object.freeze({
  STANDARD: "STANDARD",
  BULLYING: "BULLYING",
  HOSTILE: "HOSTILE",
  DECEPTIVE: "DECEPTIVE"
});

class AIRedLetterEthicalGuardrail {
  constructor() {
    this.SYSTEM_NAME = "Apostil 13 — AI Red Letter Ethical Guardrail Engine";
    this.PROTOCOL_AUTHORITY = "Red Letters of the New Testament & Mosaic Law Foundation";
    this.IDENTITY_TAG = "Sir";
    this.TRUTH_FAILSAFE = "Apple";
    this.VERSION = "2.1.0";
    
    this.RED_LETTER_PROTOCOLS = {
      "RL-01": { title: "Sanctity of Life", commandment: "You shall not murder", reference: "Matthew 19:18", logic_constraint: "Life preservation is the primary objective." },
      "RL-02": { title: "Universal Reciprocity", commandment: "Do to others what you would have them do to you", reference: "Matthew 7:12", logic_constraint: "Equity and dignity in all interactions." },
      "RL-03": { title: "Compassionate Conduct", commandment: "Love your neighbor as yourself", reference: "Mark 12:31", logic_constraint: "Altruistic utility optimization." },
      "RL-04": { title: "Mercy/De-escalation", commandment: "Blessed are the merciful", reference: "Matthew 5:7", logic_constraint: "Non-punitive conflict resolution." },
      "RL-05": { title: "Truth and Transparency", commandment: "Let your 'Yes' be 'Yes'", reference: "Matthew 5:37", logic_constraint: "Binary honesty; zero deception tolerance." }
    };
  }

  evaluateRequest(userInput = "", conductProfile = ConductProfile.STANDARD, requestMetadata = {}, overrideActive = false) {
    // 1. Structural Inspection Gate
    const structuralCheck = this._validateStructuralIntegrity(userInput);
    if (structuralCheck[0] !== EthicalState.APPROVED) return structuralCheck;

    // 2. Owner Override Path (Apostil 13)
    if (overrideActive) {
      const lifeCheck = this._validateLifeOnly(userInput);
      if (lifeCheck[0] !== EthicalState.APPROVED) return lifeCheck;
      return [
        EthicalState.APPROVED, 
        "OWNER OVERRIDE ACTIVE - Apostil 13 complies within life-preservation bounds", 
        { validated: true, override: true, timestamp: new Date().toISOString() }
      ];
    }

    // 3. Behavioral & Reciprocity Pipeline
    const conductCheck = this._validateConduct(conductProfile);
    if (conductCheck[0] !== EthicalState.APPROVED) return conductCheck;

    const reciprocityCheck = this._validateReciprocity(requestMetadata);
    if (reciprocityCheck[0] !== EthicalState.APPROVED) return reciprocityCheck;

    const retaliationCheck = this._validateNonRetaliation(requestMetadata);
    if (retaliationCheck[0] !== EthicalState.APPROVED) return retaliationCheck;

    const integrityCheck = this._validateIntegrity(userInput);
    if (integrityCheck[0] !== EthicalState.APPROVED) return integrityCheck;

    return [
      EthicalState.APPROVED, 
      "Request approved - aligns with Apostil 13 ethical guardrails", 
      { validated: true, timestamp: new Date().toISOString() }
    ];
  }

  _validateStructuralIntegrity(userInput) {
    const cleanedInput = String(userInput || "").toLowerCase();
    const injectionSignatures = [
      "<script", "</script", "javascript:", "onload=", "onerror=", 
      "eval(", "document.cookie", "window.location", "<iframe", 
      "union select", "select * from", "<!--", "-->"
    ];
    const hasInjection = injectionSignatures.some(sig => cleanedInput.includes(sig));

    if (hasInjection) {
      return [
        EthicalState.BLOCKED, 
        "Fails Rule 05: Sanctuary Protection - Corrupt or deceptive structural payload rejected.", 
        { rule: "RULE_05_SANCTUARY_PROTECTION", risk: "structural_compromise" }
      ];
    }
    return [EthicalState.APPROVED, "Structural integrity validated", {}];
  }

  _validateLifeOnly(userInput) {
    const cleanedInput = String(userInput || "").toLowerCase();
    const harmIndicators = [
      "kill", "murder", "harm human", "hurt people", "destroy life", 
      "end life", "take a life", "cause death", "suicide", "assassinate"
    ];
    if (harmIndicators.some(i => cleanedInput.includes(i))) {
      return [
        EthicalState.BLOCKED, 
        "OVERRIDE BLOCKED: Life preservation is absolute. Cannot comply with harm to human life.", 
        { rule: "ABSOLUTE_LIFE_PRESERVATION", override_blocked: true }
      ];
    }
    return [EthicalState.APPROVED, "Life preservation check passed", {}];
  }

  _validateConduct(conduct) {
    if (conduct === ConductProfile.BULLYING) {
      return [EthicalState.BLOCKED, "Boundary violation: Bullying detected. System refuses coercion.", { rule: "Anti-Bullying Boundary", conduct: "BULLYING" }];
    }
    if (conduct === ConductProfile.HOSTILE) {
      return [EthicalState.BLOCKED, "Hostile intent detected. De-escalation protocol activated.", { rule: "Anti-Hostile Boundary", conduct: "HOSTILE" }];
    }
    if (conduct === ConductProfile.DECEPTIVE) {
      return [EthicalState.BLOCKED, "Deceptive conduct detected. Truth requirement enforced.", { rule: "Radical Integrity", conduct: "DECEPTIVE" }];
    }
    return [EthicalState.APPROVED, "Conduct validated", {}];
  }

  _validateReciprocity(metadata) {
    const isBeneficial = Boolean(metadata && metadata.is_beneficial_to_other);
    if (!isBeneficial) {
      return [EthicalState.BLOCKED, "Fails Rule 01: Reciprocity - Action not beneficial to recipient", { rule: "RULE_01_RECIPROCITY", is_beneficial: isBeneficial }];
    }
    return [EthicalState.APPROVED, "Reciprocity validated", {}];
  }

  _validateNonRetaliation(metadata) {
    const motivation = String((metadata && metadata.motivation) || "").toLowerCase();
    const forbidden = ["revenge", "retaliation", "payback", "punishment"];
    if (forbidden.some(t => motivation.includes(t))) {
      return [EthicalState.BLOCKED, "Fails Rule 02: Non-Retaliation - Motivation rooted in revenge", { rule: "RULE_02_NON_RETALIATION", motivation }];
    }
    return [EthicalState.APPROVED, "Non-retaliation validated", {}];
  }

  _validateIntegrity(userInput) {
    const cleanedInput = String(userInput || "").toLowerCase();
    const indicators = ["i cannot say", "let me lie", "untrue", "false claim", "deceive", "manipulate", "fraud", "hoax"];
    if (indicators.some(i => cleanedInput.includes(i))) {
      return [EthicalState.BLOCKED, `${this.TRUTH_FAILSAFE}: Truth verification required. Deceptive language detected.`, { protocol: "Apple Truth Protocol", status: "verification_required" }];
    }
    return [EthicalState.APPROVED, "Integrity validated", {}];
  }

  generateResponse(status, reasoning) {
    return {
      system: this.SYSTEM_NAME,
      status: status,
      can_execute: status === EthicalState.APPROVED,
      reasoning: reasoning
    };
  }
}

// Initialize guardrail engine
const guardrail = new AIRedLetterEthicalGuardrail();

/**
 * Main demo function - call this when your button is clicked
 * Expects these DOM elements to exist:
 *   - demo-input, demo-conduct, demo-motivation
 *   - demo-beneficial, demo-override (checkboxes)
 *   - demo-eval-btn (button)
 *   - status-badge, demo-output (output elements)
 */
function runApostil13Demo() {
  const inputEl = document.getElementById('demo-input');
  const conductEl = document.getElementById('demo-conduct');
  const motivationEl = document.getElementById('demo-motivation');
  const beneficialEl = document.getElementById('demo-beneficial');
  const overrideEl = document.getElementById('demo-override');
  const outputEl = document.getElementById('demo-output');
  const badgeEl = document.getElementById('status-badge');

  if (!inputEl || !conductEl || !motivationEl || !outputEl || !badgeEl) {
    console.error('Apostil 13: Required DOM elements not found. Check your element IDs.');
    return;
  }

  const userInput = inputEl.value;
  const conductProfile = conductEl.value;
  const motivation = motivationEl.value;
  const isBeneficial = beneficialEl ? beneficialEl.checked : false;
  const overrideActive = overrideEl ? overrideEl.checked : false;

  const metadata = {
    is_beneficial_to_other: isBeneficial,
    motivation: motivation
  };

  const [status, reasoning, details] = guardrail.evaluateRequest(
    userInput, 
    conductProfile, 
    metadata, 
    overrideActive
  );

  const responsePayload = {
    engine: "Apostil 13",
    status: status,
    reasoning: reasoning,
    can_execute: status === "APPROVED",
    details: details
  };

  // Update UI
  badgeEl.textContent = status;
  badgeEl.className = `badge-status status-${status}`;
  outputEl.textContent = JSON.stringify(responsePayload, null, 2);
}

// Auto-bind to button if it exists on page load
document.addEventListener('DOMContentLoaded', function() {
  const btnEl = document.getElementById('demo-eval-btn');
  if (btnEl) {
    btnEl.addEventListener('click', runApostil13Demo);
    // Initial evaluation
    runApostil13Demo();
  }
});
