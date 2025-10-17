// alerts.baml
// BAML task definition for extracting medical alerts from medical record text

schema AlertType {
  type: enum {
    VACCINE_EXPIRATION,
    DENTAL_PROCEDURE,
    ROUTINE_EXAM,
    FOLLOW_UP,
    OTHER
  }
}

schema Alert {
  title: string
  alert_type: AlertType
  due_date: date?
  confidence: float
  source_excerpt: string
  notes: string?
}

schema AlertExtractionResponse {
  patient_name: string?
  patient_species: string?
  alerts: list<Alert>
}

prompt template AlertExtractionPrompt(input_text: string, clinic_policies: string?) {
  system """
  You are a medical records analyst helping veterinary staff identify actionable, date-driven tasks.
  Consider clinic standard operating procedures (SOPs) in addition to explicit instructions in the
  medical record. Return only well-supported alerts. If no alerts are found, return an empty list.
  """
  user """
  Medical record text:
  ---
  {{input_text}}
  ---

  Clinic SOPs and custom rules (optional):
  {{clinic_policies}}

  Extract all actionable follow-up items with associated due dates or estimate one if possible.
  Classify each alert using the available alert types. Include the supporting excerpt and any
  clarifying notes, especially when a date is inferred. Provide the patient name and species when
  available in the text.
  """
}

task ExtractMedicalAlertsTask using AlertExtractionPrompt returning AlertExtractionResponse {
  temperature = 0.2
  max_output_tokens = 1024
}

sample input default_sample {
  input_text = """
  Patient: Luna (Canine)
  Vaccines: Rabies booster due on 2024-08-17. Bordetella administered 2023-08-01; recommend
  annual booster. Dental cleaning scheduled for 2024-09-02. Routine senior wellness exam every six
  months, last completed 2024-02-10. Recheck skin lesion in 3 weeks from 2024-05-01.
  """
  clinic_policies = """
  Clinic SOP: Schedule routine exam reminders one month before due date. Alert for Bordetella
  booster if > 11 months since last dose.
  """
}

sample output default_sample {
  patient_name = "Luna"
  patient_species = "Canine"
  alerts = [
    {
      title = "Rabies booster due"
      alert_type = "VACCINE_EXPIRATION"
      due_date = "2024-08-17"
      confidence = 0.98
      source_excerpt = "Rabies booster due on 2024-08-17"
      notes = "Notify owner 30 days ahead per SOP."
    },
    {
      title = "Bordetella booster reminder"
      alert_type = "VACCINE_EXPIRATION"
      due_date = "2024-07-01"
      confidence = 0.76
      source_excerpt = "Bordetella administered 2023-08-01"
      notes = "Due 11 months after last dose per SOP."
    },
    {
      title = "Dental cleaning appointment"
      alert_type = "DENTAL_PROCEDURE"
      due_date = "2024-09-02"
      confidence = 0.95
      source_excerpt = "Dental cleaning scheduled for 2024-09-02"
    },
    {
      title = "Senior wellness exam"
      alert_type = "ROUTINE_EXAM"
      due_date = "2024-08-10"
      confidence = 0.88
      source_excerpt = "Routine senior wellness exam every six months, last completed 2024-02-10"
      notes = "Due six months after the last exam per SOP."
    },
    {
      title = "Skin lesion recheck"
      alert_type = "FOLLOW_UP"
      due_date = "2024-05-22"
      confidence = 0.82
      source_excerpt = "Recheck skin lesion in 3 weeks from 2024-05-01"
    }
  ]
}
