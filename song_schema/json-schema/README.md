# JSON Schema Directory

This directory contains three types of JSON schemas for the PCGL project, each serving a distinct purpose:

## 1. `full`
- **Purpose:** Used to validate payloads.
- **Description:** The `full` schemas contain all properties and constraints defined in both base and dynamic schemas for validating data payloads submitted to the data submission system. Use these schemas to ensure that your data conforms to the expected structure and rules.

## 2. `dynamic`
- **Purpose:** Used for dynamic schema registration.
- **Description:** The `dynamic` schemas are flexible components that PCGL administrators can configure and upload to define specific analysis types.

## 3. `template`
- **Purpose:** Used to generate payloads.
- **Description:** The `template` schemas provide example structures or templates that can be used as a starting point for creating new data payloads. These templates help users understand the expected format and required fields.

---

**Summary Table**

| Schema Type | Purpose                | Typical Use Case                |
|-------------|------------------------|---------------------------------|
| full        | Validate payloads      | Data validation                 |
| dynamic     | Schema registration    | Registering to define specific analysis types|
| template    | Generate payloads      | Payload creation   |

Please refer to the appropriate schema type based on your needs.