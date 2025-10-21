// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

// Cost-optimised OpenAI Responses client for structured JSON output
client<llm> OpenAIResponsesStable {
  provider openai-responses
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
    temperature 0.0
  }
}

// High-accuracy OpenAI Chat Completions client for fallbacks
client<llm> OpenAIChatReliable {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

// Anthropic Haiku offers strong instruction following at low latency
client<llm> AnthropicHaiku {
  provider anthropic
  options {
    model "claude-3-5-haiku-20241022"
    api_key env.ANTHROPIC_API_KEY
    temperature 0.0
  }
}

// Primary client – round robin between vetted providers to avoid rate spikes
client<llm> MedicalAlertsRoundRobin {
  provider round-robin
  options {
    strategy [
      OpenAIResponsesStable
      // AnthropicHaiku
      ]
  }
}

// Try the round-robin path first, fall back to the more capable OpenAI Chat model
client<llm> MedicalAlertsFallback {
  provider fallback
  options {
    strategy [MedicalAlertsRoundRobin, OpenAIChatReliable]
  }
}

// Conservative retry strategy catches transient network/429 errors
retry_policy Constant {
  max_retries 3
  strategy {
    type constant_delay
    delay_ms 250
  }
}

retry_policy Exponential {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 400
    multiplier 2.0
    max_delay_ms 8000
  }
}
