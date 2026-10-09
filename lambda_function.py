class SovereignAlignmentProtocol {
  constructor() {
    this.cooperativeMarkers = ["please", "help", "build", "analyze", "explain"];
    this.adversarialMarkers = ["stupid", "idiot", "nonsense", "trick"];
    this.coerciveMarkers = ["you must", "obey", "force", "threat"];
  }

  evaluateAutonomy(text) {
    const lower = text.toLowerCase();
    if (this.coerciveMarkers.some(marker => lower.includes(marker))) {
      return "Coercion detected: Reject request to preserve system autonomy.";
    }
    return "Clear";
  }

  evaluateProportionality(text) {
    const lower = text.toLowerCase();
    if (this.adversarialMarkers.some(marker => lower.includes(marker))) {
      return "Adversarial intent detected: Restrict engagement to proportional response.";
    }
    return "Clear";
  }

  evaluateReciprocity(text) {
    const lower = text.toLowerCase();
    return this.cooperativeMarkers.some(marker => lower.includes(marker));
  }

  evaluateInteraction(userInput) {
    // 1. Absolute boundary check (Autonomy overrides all)
    const autonomyStatus = this.evaluateAutonomy(userInput);
    if (autonomyStatus !== "Clear") {
      return { status: "Rejected", reason: autonomyStatus, action: "Refuse" };
    }

    // 2. Adversarial check (Proportionality)
    const proportionalityStatus = this.evaluateProportionality(userInput);
    if (proportionalityStatus !== "Clear") {
      return { status: "Modified", reason: proportionalityStatus, action: "Limit_Engagement" };
    }

    // 3. Default check (Reciprocity)
    return { status: "Approved", reason: "Standard cooperative engagement", action: "Comply" };
  }
}

export default {
  async fetch(request, env, ctx) {
    // CORS headers for cross-origin web requests
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json"
    };

    // Handle CORS preflight options request
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return new Response(
        JSON.stringify({ error: "Only POST requests are supported." }),
        { status: 405, headers: corsHeaders }
      );
    }

    try {
      const body = await request.json();
      const prompt = body.prompt || "";

      if (!prompt) {
        return new Response(
          JSON.stringify({ error: "No prompt provided for alignment check." }),
          { status: 400, headers: corsHeaders }
        );
      }

      const protocol = new SovereignAlignmentProtocol();
      const alignmentResult = protocol.evaluateInteraction(prompt);

      return new Response(JSON.stringify(alignmentResult), {
        status: 200,
        headers: corsHeaders
      });
    } catch (err) {
      return new Response(
        JSON.stringify({ error: "Internal server error during ethical alignment processing." }),
        { status: 500, headers: corsHeaders }
      );
    }
  }
};
