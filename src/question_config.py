"""
Question configuration for each option in the user interface
"""
from typing import Dict, List, Any
from src.validators import INDIAN_STATES, EMPLOYMENT_STATUSES, EDUCATION_LEVELS, SOCIAL_CATEGORIES
from src.languages import TRANSLATIONS

def get_option_config(option_key: str, lang: str = "en") -> Dict[str, Any]:
    """Get configuration for a specific option in the selected language."""
    configs = get_all_option_questions(lang)
    return configs.get(option_key, {})

def get_all_options(lang: str = "en") -> List[Dict[str, str]]:
    """Get list of all available options for display in the selected language."""
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    opts = t["options"]
    
    return [
        {
            "key": "ask_for_help",
            "title": opts["ask_for_help"]["title"],
            "description": opts["ask_for_help"]["desc"],
            "primary": True
        },
        {
            "key": "check_benefits",
            "title": opts["check_benefits"]["title"],
            "description": opts["check_benefits"]["desc"]
        },
        {
            "key": "eligibility_verification",
            "title": opts["eligibility_verification"]["title"],
            "description": opts["eligibility_verification"]["desc"]
        },
        {
            "key": "explain_policy",
            "title": opts["explain_policy"]["title"],
            "description": opts["explain_policy"]["desc"]
        },
        {
            "key": "help_application",
            "title": opts["help_application"]["title"],
            "description": opts["help_application"]["desc"]
        }
    ]

def get_all_option_questions(lang: str = "en") -> Dict[str, Any]:
    """
    Construct the full OPTION_QUESTIONS dictionary dynamically based on language.
    This replaces the static OPTION_QUESTIONS dictionary.
    """
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    q_text = t["questions"]
    p_text = t["prompts"]
    opt_text = t["options"]
    
    return {
        # NEW: Life-First Conversational Entry (Gold Standard)
        "ask_for_help": {
            "title": opt_text["ask_for_help"]["title"],
            "description": opt_text["ask_for_help"]["desc"],
            "agent_mapping": "CONVERSATION_DISCOVERY",
            "conversational": True,
            "entry_message": t["entry_messages"]["ask_for_help"],
            "privacy_assurance": t["privacy"],
            "questions": [
                {
                    "id": "support_type",
                    "label": q_text["support_type"],
                    "type": "quick_select",
                    "required": True,
                    "options": [
                        "🏥 Healthcare",
                        "📚 Education",
                        "🏠 Housing",
                        "💰 Income Support",
                        "👨‍👩‍👧 Family Benefits",
                        "🤔 I'm not sure — help me figure it out"
                    ],
                    "conversational_prompt": p_text["support"],
                    "help_text": "Select what best describes your need"
                },
                {
                    "id": "age_range",
                    "label": q_text["age_range"],
                    "type": "quick_select",
                    "required": True,
                    "options": ["18-25 years", "26-40 years", "41-60 years", "60+ years"],
                    "conversational_prompt": p_text["age"],
                    "help_text": "Your age helps determine age-specific schemes"
                },
                {
                    "id": "employment",
                    "label": q_text["employment"],
                    "type": "quick_select",
                    "required": True,
                    "options": [
                        "Yes, employed",
                        "Self-employed/Business",
                        "Looking for work",
                        "Student",
                        "Retired",
                        "Homemaker"
                    ],
                    "conversational_prompt": p_text["work"],
                    "help_text": "Your employment status affects eligibility"
                },
                {
                    "id": "income_bracket",
                    "label": q_text["income_bracket"],
                    "type": "quick_select",
                    "required": False,
                    "options": [
                        "Below ₹1 lakh",
                        "₹1-2.5 lakh",
                        "₹2.5-5 lakh",
                        "Above ₹5 lakh",
                        "Prefer not to say"
                    ],
                    "conversational_prompt": p_text["income"],
                    "help_text": "Many schemes have income limits, but you can skip this"
                },
                {
                    "id": "location",
                    "label": q_text["location"],
                    "type": "selectbox",
                    "required": True,
                    "options": INDIAN_STATES,
                    "conversational_prompt": p_text["state"],
                    "help_text": "Some benefits are state-specific"
                },
                {
                    "id": "family_size",
                    "label": q_text["family_size"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 4",
                    "conversational_prompt": p_text["family"],
                    "help_text": "Include yourself and all dependents"
                },
                {
                    "id": "special_conditions",
                    "label": q_text["special_conditions"],
                    "type": "multiselect",
                    "required": False,
                    "options": [
                        "Person with disability",
                        "Senior citizen (60+) in family",
                        "Children in school/college",
                        "Woman-headed household",
                        "Belong to SC/ST/OBC category",
                        "None of these"
                    ],
                    "conversational_prompt": p_text["special"],
                    "help_text": "These help identify special schemes you may qualify for"
                }
            ]
        },
        
        "check_benefits": {
            "title": opt_text["check_benefits"]["title"],
            "description": opt_text["check_benefits"]["desc"],
            "agent_mapping": "BENEFIT_MATCHER",
            "questions": [
                {
                    "id": "age",
                    "label": q_text["age"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 35",
                    "help_text": "Your age helps determine age-specific schemes"
                },
                {
                    "id": "annual_income",
                    "label": q_text["annual_income"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 200000",
                    "help_text": "Many schemes have income criteria. Enter 0 if no income."
                },
                {
                    "id": "location",
                    "label": q_text["location"],
                    "type": "selectbox",
                    "required": True,
                    "options": INDIAN_STATES,
                    "help_text": "Some benefits are state-specific"
                },
                {
                    "id": "employment_status",
                    "label": q_text["employment_status"],
                    "type": "selectbox",
                    "required": True,
                    "options": EMPLOYMENT_STATUSES,
                    "help_text": "Select the option that best describes your current situation"
                },
                {
                    "id": "family_size",
                    "label": q_text["family_size"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 4",
                    "help_text": "Include yourself and all dependents"
                },
                {
                    "id": "education_level",
                    "label": q_text["education_level"],
                    "type": "selectbox",
                    "required": False,
                    "options": EDUCATION_LEVELS,
                    "help_text": "Some scholarships and skill programs have education requirements"
                },
                {
                    "id": "social_category",
                    "label": q_text["social_category"],
                    "type": "selectbox",
                    "required": False,
                    "options": SOCIAL_CATEGORIES,
                    "help_text": "Many schemes have reservations or special provisions"
                }
            ]
        },
        
        "eligibility_verification": {
            "title": opt_text["eligibility_verification"]["title"],
            "description": opt_text["eligibility_verification"]["desc"],
            "agent_mapping": "ELIGIBILITY_VERIFIER",
            "questions": [
                {
                    "id": "scheme_name",
                    "label": q_text["scheme_name"],
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g., PM-KISAN, Ayushman Bharat, PM-SVANidhi",
                    "help_text": "Enter the full or partial name of the scheme"
                },
                {
                    "id": "age",
                    "label": q_text["age"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 35",
                    "help_text": "Your age helps verify eligibility criteria"
                },
                {
                    "id": "annual_income",
                    "label": q_text["annual_income"],
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 200000",
                    "help_text": "Most schemes have income thresholds"
                },
                {
                    "id": "location",
                    "label": q_text["location"],
                    "type": "selectbox",
                    "required": True,
                    "options": INDIAN_STATES,
                    "help_text": "Some schemes are state-specific"
                },
                {
                    "id": "employment_status",
                    "label": q_text["employment_status"],
                    "type": "selectbox",
                    "required": True,
                    "options": EMPLOYMENT_STATUSES,
                    "help_text": "Employment status affects eligibility"
                },
                {
                    "id": "social_category",
                    "label": q_text["social_category"],
                    "type": "selectbox",
                    "required": False,
                    "options": SOCIAL_CATEGORIES,
                    "help_text": "Some schemes have category-based criteria"
                },
                {
                    "id": "additional_info",
                    "label": q_text["additional_info"],
                    "type": "textarea",
                    "required": False,
                    "placeholder": "e.g., I am a farmer with 2 acres of land",
                    "help_text": "This helps provide more accurate eligibility assessment"
                }
            ]
        },
        
        "explain_policy": {
            "title": opt_text["explain_policy"]["title"],
            "description": opt_text["explain_policy"]["desc"],
            "agent_mapping": "POLICY_INTERPRETER",
            "questions": [
                {
                    "id": "policy_name",
                    "label": q_text["policy_name"],
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g., PM-KISAN, MGNREGA, Ayushman Bharat",
                    "help_text": "Enter the name of the policy or scheme"
                },
                {
                    "id": "specific_aspect",
                    "label": q_text["specific_aspect"],
                    "type": "selectbox",
                    "required": True,
                    "options": [
                        "General overview of the policy",
                        "Who is eligible?",
                        "What benefits does it provide?",
                        "What are the obligations or requirements?",
                        "What are the risks or unclear areas?",
                        "Everything about this policy"
                    ],
                    "help_text": "Choose what aspect you'd like explained"
                },
                {
                    "id": "additional_questions",
                    "label": q_text["additional_questions"],
                    "type": "textarea",
                    "required": False,
                    "placeholder": "e.g., Does this apply to my state? Can I apply online?",
                    "help_text": "Add any specific questions you have"
                }
            ]
        },
        
        "help_application": {
            "title": opt_text["help_application"]["title"],
            "description": opt_text["help_application"]["desc"],
            "agent_mapping": "CITIZEN_ADVOCATE",
            "questions": [
                {
                    "id": "scheme_name",
                    "label": q_text["scheme_name"],
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g., PM-KISAN, Ayushman Bharat, PM-SVANidhi",
                    "help_text": "Enter the scheme name you'd like help applying to"
                },
                {
                    "id": "documents_available",
                    "label": q_text["documents_available"],
                    "type": "multiselect",
                    "required": False,
                    "options": [
                        "Aadhaar Card",
                        "PAN Card",
                        "Income Certificate",
                        "Caste Certificate",
                        "Residence Proof",
                        "Bank Account Passbook",
                        "Land Ownership Documents",
                        "Ration Card",
                        "Voter ID",
                        "None of the above"
                    ],
                    "help_text": "Select all documents you currently have"
                },
                {
                    "id": "application_stage",
                    "label": q_text["application_stage"],
                    "type": "selectbox",
                    "required": True,
                    "options": [
                        "Just starting - need complete guidance",
                        "Gathering documents",
                        "Ready to fill application",
                        "Application submitted - tracking status",
                        "Application rejected - need appeal help"
                    ],
                    "help_text": "Tell us where you are in the process"
                },
                {
                    "id": "specific_help",
                    "label": q_text["specific_help"],
                    "type": "textarea",
                    "required": False,
                    "placeholder": "e.g., I don't understand what 'land ownership certificate' means, or I'm stuck at step 5 of the online form",
                    "help_text": "Describe any specific challenges you're facing"
                }
            ]
        }
    }
