# Indian Government Schemes - Test Queries

## Policy Interpretation Queries (Policy Navigator Agent)

### Central Government Schemes
1. "What is the PM-KISAN scheme and who can benefit from it?"
2. "Explain the Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY) policy"
3. "What are the eligibility criteria for the National Pension Scheme (NPS)?"
4. "Tell me about the Pradhan Mantri Mudra Yojana (PMMY) for small businesses"
5. "What is the Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)?"

### Education Schemes
6. "What is the National Scholarship Portal and what scholarships are available?"
7. "Explain the PM-YASASVI Scholarship scheme for OBC students"
8. "What is the Post Matric Scholarship Scheme for SC/ST students?"
9. "Tell me about the Merit-cum-Means Based Scholarship for professional courses"

### Women & Child Welfare
10. "What is the Pradhan Mantri Matru Vandana Yojana (PMMVY)?"
11. "Explain the Sukanya Samriddhi Yojana benefits"
12. "What is the Beti Bachao Beti Padhao scheme?"

---

## Eligibility Verification Queries (Eligibility Agent)

### With Personal Details
1. "I am a 25-year-old farmer with 2 hectares of land. Am I eligible for PM-KISAN?"
2. "My family income is ₹8 lakh per year and I'm a general category student. Can I get a scholarship?"
3. "I am 60 years old with no pension. Am I eligible for Indira Gandhi National Old Age Pension?"
4. "I'm a woman aged 28, pregnant with first child, earning ₹15,000/month. Am I eligible for maternity benefits?"
5. "I am a 22-year-old SC category student pursuing engineering. What scholarships am I eligible for?"

### Income-Based
6. "My annual family income is ₹2.5 lakh. What government schemes can I apply for?"
7. "I earn ₹12,000 per month and have 2 children. Am I eligible for any welfare schemes?"
8. "We are a BPL family with 4 members. What schemes are we eligible for?"

### Category-Based
9. "I belong to OBC category and I'm a student. What benefits can I get?"
10. "I am from SC category with annual income of ₹3 lakh. What schemes apply to me?"
11. "I am a person with disability (40%). What government benefits am I entitled to?"

---

## Benefits Discovery Queries (Benefits Agent)

### Multi-Scheme Discovery
1. "I am a 21-year-old female student from SC category with family income ₹2 lakh. What all benefits can I get?"
2. "As a 65-year-old senior citizen from rural area, what government schemes can I benefit from?"
3. "I'm a pregnant woman from BPL family. What maternal and child welfare schemes are available?"
4. "I'm a small farmer with 1.5 hectares land and annual income ₹1.5 lakh. Show me all applicable schemes"
5. "As an unemployed graduate from OBC category, what schemes and subsidies can I access?"

### Sector-Specific
6. "What are all the education-related benefits for economically weaker section (EWS) students?"
7. "What agricultural subsidies and schemes are available for marginal farmers?"
8. "What healthcare schemes can my family of 5 with ₹3 lakh income access?"

---

## Application & Advocacy Queries (Advocacy Agent)

### How to Apply
1. "How do I apply for the PM-KISAN scheme? What documents are needed?"
2. "What is the process to register on the National Scholarship Portal (NSP)?"
3. "How can I apply for Ayushman Bharat card? Where should I go?"
4. "What documents do I need to apply for SC/ST scholarship?"
5. "How do I open a Sukanya Samriddhi Account for my daughter?"

### Document Requirements
6. "What documents are required for applying to the Pradhan Mantri Awas Yojana?"
7. "What certificates do I need for OBC category scholarship?"
8. "What is the income certificate requirement for EWS reservation?"

### Application Status & Appeals
9. "My scholarship application was rejected. What can I do?"
10. "How do I check the status of my PM-KISAN payment?"
11. "My Ayushman Bharat application is pending for 2 months. Whom should I contact?"
12. "I was wrongly denied MGNREGA work. How do I file a grievance?"

---

## Complex Multi-Agent Queries

### Full Journey Queries
1. "I'm a 20-year-old SC student with ₹2 lakh family income pursuing B.Tech. What scholarships am I eligible for and how do I apply?"

2. "I'm a 30-year-old woman from rural Maharashtra, pregnant with first child, husband earns ₹10,000/month. What maternal schemes can I get and what documents do I need?"

3. "I'm a 22-year-old OBC category student with family income ₹3.5 lakh. Tell me all education benefits I qualify for and guide me through the application process."

4. "My father is 62 years old, no pension, BPL card holder. What old age benefits is he eligible for and how can we apply?"

5. "I'm a marginal farmer with 1 hectare land in Telangana. What are the current schemes, am I eligible, and how to register?"

---

## State-Specific Queries

### State Schemes
1. "What is the Amma Vodi scheme in Andhra Pradesh?"
2. "Tell me about the Karnataka Vidyasiri Scholarship"
3. "What is the Maharashtra EBC scholarship scheme?"
4. "Explain the Delhi Mukhyamantri Vidyarthi Pratibha Yojana"
5. "What is the Tamil Nadu Dr. Ambedkar Pre-Matric Scholarship?"

---

## Edge Cases & Validation

### Missing Information
1. "Am I eligible for scholarships?" (no details provided)
2. "How to apply for government scheme?" (no scheme specified)
3. "What benefits can I get?" (no personal details)

### Conflicting Information
4. "I'm 17 years old and want to apply for old age pension"
5. "My income is ₹15 lakh but I need BPL benefits"

### Deadline & Urgency
6. "When is the last date to apply for NSP scholarships?"
7. "PM-KISAN payment dates for 2024?"
8. "Urgent: My scholarship deadline is tomorrow, what do I do?"

---

## Notes for Testing

**Test Coverage:**
✅ All 4 specialized agents
✅ Simple to complex queries  
✅ Central and state schemes
✅ Different categories (SC/ST/OBC/EWS/General)
✅ Various age groups and income levels
✅ Education, healthcare, agriculture, welfare sectors

**Expected Agent Routing:**
- Queries 1-12 (Policy) → Policy Navigator
- Queries 13-22 (Eligibility) → Eligibility Agent  
- Queries 23-30 (Benefits) → Benefits Agent
- Queries 31-42 (Application) → Advocacy Agent
- Queries 43-47 (Complex) → Multi-agent collaboration
