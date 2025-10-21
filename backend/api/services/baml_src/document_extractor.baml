class AlertType {
    id string @description("lowercase, underscore-separated string")
    name string
    description string
}

class MedicalAlert {
    type AlertType
    event string @description("A brief description of the alert")
    date string  @description("As an ISO8601 timestamp (YYYY-MM-DD)")
}

template_string PrintAlertTypes(alert_types: AlertType[]) #"
  {% for m in alert_types %}
    - {{ m.id }}: {{ m.name }} - {{ m.description }}
  {% endfor %}
"#

function ExtractMedicalAlerts(document:string, alert_types: AlertType[]) -> MedicalAlert[] {
    client MedicalAlertsFallback

    prompt #"
        You are a clinical documentation analyst. Extract factual, date-based care reminders from the medical record below.

        Alert taxonomy (id - name - description):
        {{ PrintAlertTypes(alert_types) }}

        Output requirements:
        - Respond with **only** valid JSON that matches {{ ctx.output_format }}.
        - Every alert `type.id` **must** match one of the provided alert_types. If nothing matches, omit the alert.
        - Use ISO dates (`YYYY-MM-DD`). If a precise date is unclear, skip the alert rather than guessing.
        - Consolidate duplicate or overlapping statements into a single alert with the most specific due date.
        - Ignore historical notes that are explicitly marked complete unless a future follow-up is scheduled.
        - Never invent vaccines, procedures, or dates that are not explicitly supported by the text.

        Verification checklist (follow before responding):
        1. Have you mapped each alert back to a direct citation in the document?
        2. Are all dates valid calendar dates in ISO format?
        3. Did you remove any duplicate, cancelled, or completed items?

        {{ _.role("system") }} Return an empty array (`[]`) when no qualifying alerts are present.

        {{ _.role("user") }} {{ document }}
    "#
}
