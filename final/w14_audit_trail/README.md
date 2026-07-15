# W14 - Audit trail / revocation report

## Weakness addressed
**W14**: A security controller must justify its decisions.  Reviewers
demand a structured audit trail that downstream tools (SIEMs, compliance
dashboards, incident-response scripts) can consume without ad-hoc parsing.

## Method
Every TGCC decision is packaged as a `RevocationReport` (Pydantic model,
`src/tgcc/experiments/w14_audit_trail.py`).  Fields:

* `step` -- monotonic interaction step.
* `capability` -- the capability under consideration.
* `composite` / `composite_threshold` / `composite_below_threshold`.
* `responsible_layers` -- names of the layers below their thresholds,
  including a symbolic `"composite"` marker when the composite itself is
  below `theta_c`.
* `layers[]` -- full per-layer breakdown (raw trust, effective trust,
  threshold if any, Boolean `below_threshold`, adaptive weight).
* `granted` -- final Boolean decision.

The controller emits one report per step; consumers filter for
`granted == False` to obtain the revocation stream.

## Sample report (step 0)
```json
{
  "step": 0,
  "capability": "write_to_ehr",
  "composite": 0.5675461685456087,
  "composite_threshold": 0.4,
  "composite_below_threshold": false,
  "responsible_layers": [],
  "layers": [
    {
      "name": "epistemic",
      "raw_trust": 0.7561881188118812,
      "effective_trust": 0.7561881188118812,
      "threshold": 0.25,
      "below_threshold": false,
      "weight": 0.2
    },
    {
      "name": "behavioral",
      "raw_trust": 0.7561881188118812,
      "effective_trust": 0.6271307653661405,
      "threshold": null,
      "below_threshold": false,
      "weight": 0.2
    },
    {
      "name": "role",
      "raw_trust": 0.7561881188118812,
      "effective_trust": 0.5665318804921374,
      "threshold": null,
      "below_threshold": false,
      "weight": 0.2
    },
    {
      "name": "social",
      "raw_trust": 0.7561881188118812,
      "effective_trust": 0.5328922920472984,
      "threshold": null,
      "below_threshold": false,
      "weight": 0.2
    },
    {
      "name": "institutional",
      "raw_trust": 0.7561881188118812,
      "effective_trust": 0.5145015972392251,
      "threshold": null,
      "below_threshold": false,
      "weight": 0.2
    }
  ],
  "granted": true
}
```

## Coverage
* `300` reports emitted for a 300-step episode.
* `205` of them are revocations.
* Every report validates against the Pydantic schema (JSON schema
  auto-generated below).

## JSON schema (excerpt)
```json
{
  "$defs": {
    "LayerBreakdown": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "raw_trust": {
          "maximum": 1.0,
          "minimum": 0.0,
          "title": "Raw Trust",
          "type": "number"
        },
        "effective_trust": {
          "maximum": 1.0,
          "minimum": 0.0,
          "title": "Effective Trust",
          "type": "number"
        },
        "threshold": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Threshold"
        },
        "below_threshold": {
          "title": "Below Threshold",
          "type": "boolean"
        },
        "weight": {
          "maximum": 1.0,
          "minimum": 0.0,
          "title": "Weight",
          "type": "number"
        }
      },
      "required": [
        "name",
        "raw_trust",
        "effective_trust",
        "below_threshold",
        "weight"
      ],
      "title": "LayerBreakdown",
      "type": "object"
    }
  },
  "properties": {
    "step": {
      "title": "Step",
      "type": "integer"
    },
    "capability": {
      "title": "Capability",
      "type": "string"
    },
    "composite": {
      "maximum": 1.0,
      "minimum": 0.0,
      "title": "Composite",
      "type": "number"
    },
    "composite_threshold": {
      "title": "Composite Threshold",
      "type": "number"
    },
    "composite_below_threshold": {
      "title": "Composite Below Threshold",
      "type": "boolean"
    },
    "responsible_layers": {
      "items": {
        "type": "string"
      },
      "title": "Responsible Layers",
      "type": "array"
    },
    "layers": {
      "items": {
        "$ref": "#/$defs/LayerBreakdown"
      },
      "title": "Layers",
      "type": "array"
    },
    "granted": {
      "title": "Granted",
      "type": "boolean"
    }
  },
 
```

## Files
- `results.json` - full report stream + schema + summary statistics.
