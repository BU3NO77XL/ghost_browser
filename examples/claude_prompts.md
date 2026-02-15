# Example Prompts

Copy-paste prompts to get started with Stealth Browser MCP.

---

## Navigation and Extraction

**Bypass antibot protection and extract content:**
```
Use stealth-browser to navigate to a Cloudflare-protected site. Take a screenshot proving access, then extract the main content area using extract_complete_element_cdp and show me the HTML structure.
```

**Clone a UI element with full fidelity:**
```
Use stealth-browser to navigate to stripe.com/pricing. Use extract_complete_element_cdp to clone their pricing table. Extract all CSS, fonts, images, and animations. Generate working HTML I can use locally.
```

---

## Network Analysis

**Map API endpoints through interception:**
```
Use stealth-browser to navigate to [web app URL]. As I interact with the page, use list_network_requests to monitor all API calls. For each request, use get_request_details and get_response_content to show me the data flow. Create a complete API map with endpoints, auth methods, and data schemas.
```

**Create a dynamic network hook:**
```
Use stealth-browser's dynamic hook system to create a Python function that blocks all tracking requests matching *.analytics.* and logs every API call to /api/* with full headers and payloads.
```

---

## Multi-Tab Workflows

**Competitor analysis across tabs:**
```
Use stealth-browser to open tabs for 5 competitor sites. In each tab, navigate to their pricing page and use extract_complete_element_cdp to capture the pricing section. Compile a comparison of features and pricing.
```

---

## Monitoring

**Price monitoring:**
```
Use stealth-browser to navigate to [product page]. Use extract_element_structure to identify the price element. Use execute_script to read the current price and compare it against a threshold. Take a screenshot of the result.
```

**Privacy audit:**
```
Use stealth-browser to navigate to [website]. Use network interception to capture all tracking requests and extract_element_events to find analytics code. Generate a report of what data the site collects.
```

---

## In-Browser Code Execution

**Run Python inside the browser:**
```
Use stealth-browser to navigate to a page with a complex form. Use execute_python_in_browser to write Python code that analyzes the page structure and fills out the form fields programmatically.
```

**Dynamic pricing analysis:**
```
Use stealth-browser to navigate to an e-commerce site. Use network interception and execute_python_in_browser to observe how prices change based on request headers, cookies, and session state.
```
