"""Fixed user-facing texts in each supported language.

These are shown when the system refuses, so they must be correct without any model in the
loop. The Tamil and Hindi wording should be reviewed by a native speaker before release.
"""

from typing import Literal

from schemebot.ingest.langid import Language

RefusalReason = Literal[
    "low_confidence",  # retrieval found nothing relevant enough
    "not_in_documents",  # the model read the passages and found no answer
    "unsupported",  # the guardrail removed every sentence
    "model_declined",  # the model's safety filter declined
    "service_unavailable",  # the API failed
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


def message_language(language: Language) -> MessageLanguage:
    return "en" if language == "unknown" else language


def refusal_text(reason: RefusalReason, language: Language) -> str:
    texts = UNAVAILABLE if reason == "service_unavailable" else NOT_FOUND
    return texts[message_language(language)]


def contact_text(scheme: str, helpline: str | None, website: str, language: Language) -> str:
    templates = CONTACT_WITH_HELPLINE if helpline else CONTACT_WEBSITE_ONLY
    return templates[message_language(language)].format(
        scheme=scheme, helpline=helpline, website=website
    )


def disclaimer(language: Language) -> str:
    return DISCLAIMER[message_language(language)]
