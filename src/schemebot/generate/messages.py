"""Fixed user-facing texts in each supported language.

These are shown when the system refuses, so they must be correct without any model in the
loop. The Tamil and Hindi wording should be reviewed by a native speaker before release.
"""

import re
from typing import Literal

from schemebot.ingest.langid import Language

RefusalReason = Literal[
    "low_confidence",  # retrieval found nothing relevant enough
    "not_in_documents",  # the model read the passages and found no answer
    "unsupported",  # the guardrail removed every sentence
    "model_declined",  # the model's safety filter declined
    "service_unavailable",  # the API failed
    "pii_detected",  # Aadhaar or phone number detected in question
    "unsupported_language",  # question is in an unsupported language or script
]

MessageLanguage = Literal["en", "ta", "hi", "ta-Latn"]

NOT_FOUND: dict[MessageLanguage, str] = {
    "en": (
        "I couldn't find this in the official scheme documents I have, so I can't answer it "
        "reliably. Please check the scheme's official website or ask at your nearest "
        "government service centre."
    ),
    "ta": (
        "என்னிடம் உள்ள அதிகாரப்பூர்வ திட்ட ஆவணங்களில் இதற்கான தகவல் கிடைக்கவில்லை, எனவே "
        "நம்பகமாக பதில் சொல்ல முடியவில்லை. திட்டத்தின் அதிகாரப்பூர்வ இணையதளத்தைப் பார்க்கவும் "
        "அல்லது அருகிலுள்ள அரசு சேவை மையத்தில் கேட்கவும்."
    ),
    "hi": (
        "मेरे पास मौजूद आधिकारिक योजना दस्तावेज़ों में यह जानकारी नहीं मिली, इसलिए मैं भरोसेमंद "
        "जवाब नहीं दे सकता। कृपया योजना की आधिकारिक वेबसाइट देखें या अपने नज़दीकी सरकारी सेवा "
        "केंद्र पर पूछें।"
    ),
    "ta-Latn": (
        "Ennidam irukkura official scheme documents-la indha thagaval kidaikkala, adhanala "
        "nambagamaa badhil solla mudiyala. Scheme-oda official website-a paarunga, illa "
        "pakkathula irukkura arasu sevai maiyathula kelunga."
    ),
}

INDIC_TO_ASCII = str.maketrans({
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
    "௦": "0", "௧": "1", "௨": "2", "௩": "3", "௪": "4",
    "௫": "5", "௬": "6", "௭": "7", "௮": "8", "௯": "9",
})

AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b")
PHONE_PATTERN = re.compile(
    r"(?:\b(?:\+91|0)[ -]?)?[6-9]\d{4}[ -]?\d{5}\b|" r"\b(?:\+91|0)?[6-9]\d{9}\b"
)


def contains_pii(text: str) -> bool:
    norm = text.translate(INDIC_TO_ASCII)
    return bool(AADHAAR_PATTERN.search(norm) or PHONE_PATTERN.search(norm))


PII_WARNING: dict[MessageLanguage, str] = {
    "en": (
        "For your privacy and security, please do not share personal numbers such as Aadhaar or "
        "phone numbers. Pakkam only provides general scheme eligibility information."
    ),
    "ta": (
        "உங்கள் தனியுரிமை மற்றும் பாதுகாப்பிற்காக, ஆதார் எண் அல்லது தொலைபேசி எண் போன்ற தனிநபர் "
        "எண்களைப் பகிர வேண்டாம். திட்டம் பற்றிய பொதுவான தகவல்களை மட்டுமே பாக்கம் வழங்கும்."
    ),
    "hi": (
        "आपकी सुरक्षा और गोपनीयता के लिए, कृपया आधार या फोन नंबर जैसी व्यक्तिगत जानकारी साझा न करें। "
        "पक्कम केवल सामान्य योजना पात्रता जानकारी प्रदान करता है।"
    ),
    "ta-Latn": (
        "Ungal privacy kaaga, Aadhaar number alladhu phone number share panna vendaam. "
        "Pakkam general scheme thagavalgalai mattume vazhangum."
    ),
}

UNAVAILABLE: dict[MessageLanguage, str] = {
    "en": "The answering model is currently busy. Here is what the official document states:",
    "ta": "மாதிரி தற்போது பிஸியாக உள்ளது. அதிகாரப்பூர்வ ஆவணத்தில் உள்ள தகவல் இதோ:",
    "hi": "मॉडल अभी व्यस्त है। आधिकारिक दस्तावेज़ में यह जानकारी दी गई है:",
    "ta-Latn": "Model ippo busy-aa irukku. Official document-la irukkura thagaval idho:",
}

DISCLAIMER: dict[MessageLanguage, str] = {
    "en": (
        "Informational only, not an official government service. Verify with the official "
        "source before acting on it."
    ),
    "ta": (
        "இது தகவலுக்காக மட்டுமே; அதிகாரப்பூர்வ அரசு சேவை அல்ல. செயல்படும் முன் அதிகாரப்பூர்வ "
        "ஆதாரத்துடன் சரிபார்க்கவும்."
    ),
    "hi": (
        "यह केवल जानकारी के लिए है, आधिकारिक सरकारी सेवा नहीं। कोई कदम उठाने से पहले आधिकारिक "
        "स्रोत से पुष्टि करें।"
    ),
    "ta-Latn": (
        "Idhu thagavalukkaga mattum; official arasu sevai illa. Edhuvum seyyum munnaadi "
        "official source-la check pannunga."
    ),
}


CONTACT_WITH_HELPLINE: dict[MessageLanguage, str] = {
    "en": "For help with {scheme}, call {helpline} (toll free) or visit {website}.",
    "ta": "{scheme} குறித்த உதவிக்கு {helpline} (கட்டணமில்லா எண்) அழைக்கவும் அல்லது {website} பார்க்கவும்.",
    "hi": "{scheme} से जुड़ी मदद के लिए {helpline} (टोल फ्री) पर कॉल करें या {website} देखें।",
    "ta-Latn": (
        "{scheme} pathi udhavikku {helpline} (toll free) ku call pannunga, illa {website} paarunga."
    ),
}

CONTACT_WEBSITE_ONLY: dict[MessageLanguage, str] = {
    "en": "For help with {scheme}, visit {website}.",
    "ta": "{scheme} குறித்த உதவிக்கு {website} பார்க்கவும்.",
    "hi": "{scheme} से जुड़ी मदद के लिए {website} देखें।",
    "ta-Latn": "{scheme} pathi udhavikku {website} paarunga.",
}


UNSUPPORTED_LANGUAGE: dict[MessageLanguage, str] = {
    "en": (
        "Pakkam only supports questions in Tamil, Hindi, English, and Tanglish. "
        "Please ask in one of these languages."
    ),
    "ta": "பக்கம் தமிழ், இந்தி, ஆங்கிலம் மற்றும் தங்கிலீஷ் மொழிகளில் மட்டுமே கேள்விகளை ஆதரிக்கிறது.",
    "hi": "पक्कम केवल तमिल, हिंदी, अंग्रेजी और तांगलिश में प्रश्नों का समर्थन करता है।",
    "ta-Latn": "Pakkam Tamil, Hindi, English mattrum Tanglish-la mattum dhaan support pannum.",
}


def message_language(language: Language) -> MessageLanguage:
    return "en" if language == "unknown" else language


def refusal_text(reason: RefusalReason, language: Language) -> str:
    if reason == "pii_detected":
        texts = PII_WARNING
    elif reason == "service_unavailable":
        texts = UNAVAILABLE
    elif reason == "unsupported_language":
        texts = UNSUPPORTED_LANGUAGE
    else:
        texts = NOT_FOUND
    return texts[message_language(language)]


def contact_text(scheme: str, helpline: str | None, website: str, language: Language) -> str:
    templates = CONTACT_WITH_HELPLINE if helpline else CONTACT_WEBSITE_ONLY
    return templates[message_language(language)].format(
        scheme=scheme, helpline=helpline, website=website
    )


def disclaimer(language: Language) -> str:
    return DISCLAIMER[message_language(language)]


CONFIRMATION: dict[MessageLanguage, str] = {
    "en": "I heard {scheme}. Is that right?",
    "ta": "நான் {scheme} என்று கேட்டேன். சரியா?",
    "hi": "मैंने {scheme} सुना। क्या यह सही है?",
    "ta-Latn": "Naan {scheme} nu ketten. Sariyaa?",
}


def confirmation_text(scheme: str, language: Language) -> str:
    return CONFIRMATION[message_language(language)].format(scheme=scheme)


def clarification_text(candidates: list[str], language: Language) -> str:
    lang = message_language(language)
    if not candidates:
        return NOT_FOUND[lang]
    if len(candidates) == 1:
        c1 = candidates[0]
        templates = {
            "en": f"Did you mean {c1}? Here is what the official document states:",
            "ta": f"நீங்கள் {c1} பற்றிக் கேட்கிறீர்களா? அதிகாரப்பூர்வ ஆவணத்தில் உள்ள தகவல் இதோ:",
            "hi": f"क्या आपका मतलब {c1} से था? आधिकारिक दस्तावेज़ में यह जानकारी दी गई है:",
            "ta-Latn": (
                f"Neenga {c1} pathi kekkareengala? "
                "Official document-la irukkura thagaval idho:"
            ),
        }
        return templates[lang]
    c1, c2 = candidates[0], candidates[1]
    templates = {
        "en": f"Did you mean {c1} or {c2}? Here is what the official document states:",
        "ta": f"நீங்கள் {c1} அல்லது {c2} பற்றிக் கேட்கிறீர்களா? அதிகாரப்பூர்வ ஆவணத்தில் உள்ள தகவல் இதோ:",
        "hi": f"क्या आपका मतलब {c1} या {c2} से था? आधिकारिक दस्तावेज़ में यह जानकारी दी गई है:",
        "ta-Latn": (
            f"Neenga {c1} illa {c2} pathi kekkareengala? "
            "Official document-la irukkura thagaval idho:"
        ),
    }
    return templates[lang]
