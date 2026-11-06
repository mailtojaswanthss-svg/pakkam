// web/js/talk.js
// Small talk for Pakkam's chat: greetings, thanks, goodbyes, "explain again", "summary", help,
// complaints and off-topic questions get a fixed, friendly reply in the page itself (no LLM,
// no server call). Anything about a scheme still goes to the backend, which answers only from
// the official documents. Matching covers English, Tamil script, Tanglish and Hindi.

const WORDS = {
  greeting: /^(hi+|hello+|hey+|hai|helo|vanakkam|vanakam|vannakam|வணக்கம்|namaste|namaskar|namaskaram|नमस्ते|नमस्कार|good\s*(morning|afternoon|evening)|gm|kaalai\s*vanakkam|காலை\s*வணக்கம்)\b/,
  goodbye: /\b(bye+|goodbye|good\s*bye|see\s*you|tata|poitu\s*varen|poittu\s*varen|poyittu\s*varen|varen|போய்ட்டு\s*வரேன்|போயிட்டு\s*வரேன்|விடைபெறுகிறேன்|alvida|अलविदा|phir\s*milenge|फिर\s*मिलेंगे)\b/,
  thanks: /\b(thanks|thank\s*you|thank\s*u|thx|tq|ty|nandri|nanri|நன்றி|dhanyavaad|dhanyawad|धन्यवाद|shukriya|शुक्रिया)\b/,
  ack: /^(ok+|okay|k|kk|got\s*it|understood|clear|super|great|nice|good|fine|purinjidhu|purinjathu|puriyudhu|sari|சரி|புரிந்தது|புரிஞ்சுது|புரியுது|samajh\s*gaya|samajh\s*gayi|समझ\s*गया|समझ\s*गई|theek\s*hai|ठीक\s*है|accha|अच्छा)$/,
  notClear: /\b(puriyala|puriyalai|puriyalla|புரியல|புரியவில்லை|not\s*clear|unclear|don'?t\s*understand|didn'?t\s*understand|confus\w*|samajh\s*nahi|समझ\s*नहीं)\b/,
  again: /\b(explain\s*again|say\s*again|again|repeat|once\s*more|one\s*more\s*time|thirumba|marupadiyum|marubadiyum|மறுபடியும்|திரும்ப|phir\s*se|फिर\s*से|dobara|दोबारा)\b/,
  summary: /\b(summary|summari[sz]e|in\s*short|short\s*(answer|form)?|brief|churukkam|surukkam|சுருக்கம்|சுருக்கமா|saransh|सारांश|short\s*mein)\b/,
  complaint: /\b(wrong|not\s*helpful|useless|bad\s*answer|incorrect|thappu|தப்பு|தவறு|galat|गलत|bekar|बेकार)\b/,
  howAreYou: /\b(how\s*are\s*you|how\s*r\s*u|eppadi\s*irukeenga|eppadi\s*irukinga|eppadi\s*iruka|எப்படி\s*இருக்கீங்க|எப்படி\s*இருக்கிறீர்கள்|kaise\s*ho|कैसे\s*हो|kaise\s*hain|कैसे\s*हैं)\b/,
  about: /\b(who\s*are\s*you|what\s*are\s*you|what\s*is\s*pakkam|about\s*(you|pakkam)|nee\s*yaaru|neenga\s*yaaru|நீ\s*யார்|நீங்கள்\s*யார்|நீங்க\s*யாரு|tum\s*kaun|aap\s*kaun|आप\s*कौन|तुम\s*कौन)\b/,
  help: /^(help|help\s*me|what\s*can\s*you\s*do|how\s*(to|do\s*i)\s*use(\s*this)?|udhavi|உதவி|madad|मदद|enna\s*panna\s*mudiyum|என்ன\s*செய்ய\s*முடியும்|kya\s*kar\s*sakte\s*ho|क्या\s*कर\s*सकते\s*हो)\b/,
  schemes: /^((which|what)\s*schemes?(\s*(do\s*you|can\s*you)\s*(know|cover|answer|have))?|list\s*(of\s*)?schemes|all\s*schemes|endha\s*schemes?|எந்த\s*திட்டங்கள்|कौन\s*सी\s*योजनाएं)\s*\??$/,
  languages: /\b((which|what)\s*languages?|languages?\s*(do\s*you|can\s*you)|endha\s*mozhi|எந்த\s*மொழி|कौन\s*सी\s*भाषा)\b/,
  official: /\b((are\s*you|is\s*this|is\s*pakkam)\s*(a\s*)?(government|official|govt)|arasu\s*site|அரசு\s*தளமா|सरकारी\s*(है|हो))\b/,
  privacy: /\b(is\s*my\s*data\s*safe|privacy|do\s*you\s*(store|save|keep)|my\s*data|தகவல்\s*பாதுகாப்பு|डेटा\s*सुरक्षित)\b/,
  issue: /^(problem|issue|not\s*working|error|it\s*doesn'?t\s*work|prachanai|பிரச்சனை|பிரச்சினை|samasya|समस्या|dikkat|दिक्कत)\b/,
  offTopic: /\b(weather|rain\s*today|cricket|ipl|match\s*score|movie|film|cinema|song|joke|homework|recipe|stock|bitcoin|crypto|வானிலை|சினிமா|படம்|மழை|मौसम|फिल्म|क्रिकेट|चुटकुला)\b/,
};

// Words that mean the message is about a scheme: then it goes to the backend, not small talk.
const SCHEME_HINT = /\b(scheme|schemes|thittam|thittathil|yojana|yojna|pension|kisan|ujjwala|urimai|magalir|pudhumai|breakfast|amount|eligib\w*|documents?|apply|income|subsidy|loan|scholarship|ration|aadhaar)\b|திட்ட|உரிமை|ஓய்வூதிய|தகுதி|ஆவண|योजना|पेंशन|पात्र|दस्तावेज़/;

// JavaScript's \b only knows English letters, so Tamil and Hindi words never matched. Rebuild
// every pattern with a Unicode word boundary (letters, combining marks and digits of any script).
const L = '[\\p{L}\\p{M}\\p{N}]';
const BOUNDARY = `(?:(?<!${L})(?=${L})|(?<=${L})(?!${L}))`;
const unicode = (re) => new RegExp(re.source.replaceAll('\\b', BOUNDARY), 'u');
Object.keys(WORDS).forEach((key) => { WORDS[key] = unicode(WORDS[key]); });
const SCHEME = unicode(SCHEME_HINT);

const words = (text) => text.split(/\s+/).filter(Boolean).length;

/** What kind of message this is: { intent, rest } or null for a real question. */
export function detectTalk(raw) {
  const text = raw.toLowerCase().replace(/[!?.,।]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!text) return null;
  const short = words(text) <= 6;
  const aboutScheme = SCHEME.test(text);

  // "vanakkam, PM Kisan evlo?" -> greet, then ask the rest.
  const greet = text.match(WORDS.greeting);
  if (greet) {
    const rest = raw.slice(raw.toLowerCase().indexOf(greet[0]) + greet[0].length).replace(/^[\s,!.:;-]+/, '').trim();
    if (rest && words(rest) >= 2 && !WORDS.howAreYou.test(rest.toLowerCase())) return { intent: 'greeting', rest };
    if (!rest || short) return { intent: WORDS.howAreYou.test(text) ? 'howAreYou' : 'greeting' };
  }
  if (aboutScheme && !short) return null;
  for (const intent of ['goodbye', 'thanks', 'howAreYou', 'about', 'help', 'schemes', 'languages', 'official', 'privacy']) {
    if (WORDS[intent].test(text) && (short || ['about', 'official', 'privacy', 'languages'].includes(intent))) return { intent };
  }
  if (short && WORDS.ack.test(text)) return { intent: 'ack' };
  if (short && WORDS.notClear.test(text)) return { intent: 'notClear' };
  if (short && WORDS.summary.test(text)) return { intent: 'summary' };
  if (short && WORDS.again.test(text)) return { intent: 'again' };
  if (short && WORDS.complaint.test(text)) return { intent: 'complaint' };
  if (short && WORDS.issue.test(text)) return { intent: 'issue' };
  if (!aboutScheme && WORDS.offTopic.test(text)) return { intent: 'offTopic' };
  return null;
}

/** Reply language: the script of the message if it is Tamil or Hindi, else the site language. */
export function replyLanguage(raw, siteLanguage) {
  if (/[஀-௿]/.test(raw)) return 'ta-IN';
  if (/[ऀ-ॿ]/.test(raw)) return 'hi-IN';
  return siteLanguage;
}

export const TALK = {
  'en-IN': {
    greeting: 'Vanakkam! 🙏 I am Pakkam. Ask me about a Tamil Nadu or central welfare scheme, by voice or text, and I will show you the official page the answer comes from.',
    howAreYou: 'I am doing well, thank you for asking! 😊 How can I help you today? Ask me about any scheme below.',
    goodbye: 'Goodbye! 🙏 Come back any time you have a question about a scheme. Take care.',
    thanks: 'You are welcome! 😊 Is there anything else you would like to know? You can also share the answer with your family.',
    ack: 'Great! Would you like to know anything else, like the documents to carry or how to apply?',
    notClear: 'Sorry, let me help. I can explain it again more slowly, give you a short summary, or show you the exact page from the government document. Which would you like?',
    complaint: 'Sorry about that. 🙏 You can open the page to check it yourself, call the scheme helpline, or send your question to an officer. Your feedback also helps us improve.',
    about: 'I am Pakkam (பக்கம் = "page"), a voice assistant for welfare schemes. I answer only from official government documents and show you the page each answer comes from. If the documents do not say it, I tell you honestly. I am a student project, not a government service.',
    help: 'Here is how to use me:\n• Tap the orb and speak, or type your question.\n• Ask in Tamil, Tanglish, Hindi or English.\n• Tap "See the page" to view the proof.\n• Say "summary" for a short version, or "explain again".\n• Use "Check a forward" to test a WhatsApp message.',
    schemes: 'I can answer about these schemes, from their official documents:',
    languages: 'You can ask in Tamil, Tanglish (Tamil in English letters), Hindi or English, by voice or text. I answer in the language you ask in.',
    official: 'No. Pakkam is a student project, not a government service. But every answer comes from an official government document, and I show you the exact page so you can check it.',
    privacy: 'Your question text and voice are not stored by Pakkam. The speech and answer services receive only what they need to answer. Please do not type Aadhaar or bank numbers.',
    issue: 'Sorry you are facing a problem. 🙏 Try these: speak a little slower, or type the question; name the scheme (for example "Magalir Urimai"). If it still does not work, send it to an officer below.',
    offTopic: 'I can only answer questions about welfare schemes, from the official government documents. Try one of these:',
    noLast: 'Ask me a question first, and then I can explain it again or summarise it.',
    summaryTitle: 'In short:',
    againTitle: 'Here it is again, step by step:',
  },
  'ta-IN': {
    greeting: 'வணக்கம்! 🙏 நான் பக்கம். தமிழ்நாடு அல்லது மத்திய அரசு நலத்திட்டங்கள் பற்றி குரலிலோ எழுத்திலோ கேளுங்கள். பதில் வந்த அரசு பக்கத்தையும் காட்டுவேன்.',
    howAreYou: 'நன்றாக இருக்கிறேன், கேட்டதற்கு நன்றி! 😊 இன்று உங்களுக்கு எப்படி உதவலாம்? கீழே உள்ள ஏதாவது திட்டம் பற்றி கேளுங்கள்.',
    goodbye: 'போய்ட்டு வாங்க! 🙏 திட்டம் பற்றி சந்தேகம் வந்தால் எப்போது வேண்டுமானாலும் வாருங்கள்.',
    thanks: 'மகிழ்ச்சி! 😊 வேறு ஏதாவது தெரிந்துகொள்ள வேண்டுமா? இந்தப் பதிலைக் குடும்பத்தினருடனும் பகிரலாம்.',
    ack: 'நல்லது! எடுத்துச் செல்ல வேண்டிய ஆவணங்கள் அல்லது விண்ணப்பிக்கும் முறை பற்றி தெரிய வேண்டுமா?',
    notClear: 'மன்னிக்கவும், உதவுகிறேன். மெதுவாக மீண்டும் விளக்கலாம், சுருக்கமாகச் சொல்லலாம், அல்லது அரசு ஆவணத்தின் சரியான பக்கத்தைக் காட்டலாம். எது வேண்டும்?',
    complaint: 'மன்னிக்கவும். 🙏 பக்கத்தைத் திறந்து நீங்களே சரிபார்க்கலாம், திட்ட உதவி எண்ணை அழைக்கலாம், அல்லது கேள்வியை அதிகாரிக்கு அனுப்பலாம். உங்கள் கருத்து எங்களை மேம்படுத்த உதவும்.',
    about: 'நான் பக்கம், நலத்திட்டங்களுக்கான குரல் உதவியாளர். அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து மட்டுமே பதில் சொல்வேன், ஒவ்வொரு பதிலும் வந்த பக்கத்தைக் காட்டுவேன். ஆவணத்தில் இல்லையென்றால் நேர்மையாகச் சொல்வேன். இது ஒரு மாணவர் திட்டம், அரசு சேவை அல்ல.',
    help: 'என்னை இப்படிப் பயன்படுத்தலாம்:\n• உருண்டையைத் தொட்டுப் பேசுங்கள், அல்லது கேள்வியைத் தட்டச்சு செய்யுங்கள்.\n• தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில் கேளுங்கள்.\n• ஆதாரத்திற்கு "பக்கத்தைப் பாருங்கள்" என்பதைத் தொடுங்கள்.\n• சுருக்கமாக வேண்டுமென்றால் "சுருக்கம்", மீண்டும் வேண்டுமென்றால் "மறுபடியும்" என்று சொல்லுங்கள்.\n• வாட்ஸ்அப் செய்தியைச் சரிபார்க்க "செய்தியைச் சரிபார்" பயன்படுத்துங்கள்.',
    schemes: 'இந்தத் திட்டங்கள் பற்றி அவற்றின் அதிகாரப்பூர்வ ஆவணங்களிலிருந்து பதில் சொல்லலாம்:',
    languages: 'தமிழ், Tanglish (ஆங்கில எழுத்தில் தமிழ்), இந்தி அல்லது ஆங்கிலத்தில், குரலிலோ எழுத்திலோ கேட்கலாம். நீங்கள் கேட்கும் மொழியிலேயே பதில் சொல்வேன்.',
    official: 'இல்லை. பக்கம் ஒரு மாணவர் திட்டம், அரசு சேவை அல்ல. ஆனால் ஒவ்வொரு பதிலும் அதிகாரப்பூர்வ அரசு ஆவணத்திலிருந்து வருகிறது; நீங்கள் சரிபார்க்க அந்தப் பக்கத்தையே காட்டுவேன்.',
    privacy: 'உங்கள் கேள்வியையோ குரலையோ பக்கம் சேமிப்பதில்லை. பதில் தரத் தேவையானதை மட்டுமே குரல் மற்றும் பதில் சேவைகள் பெறுகின்றன. ஆதார் அல்லது வங்கி எண்களைத் தட்டச்சு செய்ய வேண்டாம்.',
    issue: 'சிரமத்திற்கு மன்னிக்கவும். 🙏 சற்று மெதுவாகப் பேசுங்கள் அல்லது தட்டச்சு செய்யுங்கள்; திட்டத்தின் பெயரைச் சொல்லுங்கள் (எ.கா. "மகளிர் உரிமை"). அப்போதும் வேலை செய்யவில்லையென்றால் கீழே அதிகாரிக்கு அனுப்புங்கள்.',
    offTopic: 'அரசு நலத்திட்டங்கள் பற்றி மட்டுமே, அதிகாரப்பூர்வ ஆவணங்களிலிருந்து பதில் சொல்ல முடியும். இவற்றில் ஒன்றைக் கேளுங்கள்:',
    noLast: 'முதலில் ஒரு கேள்வி கேளுங்கள், பிறகு மீண்டும் விளக்குகிறேன் அல்லது சுருக்குகிறேன்.',
    summaryTitle: 'சுருக்கமாக:',
    againTitle: 'மீண்டும், படிப்படியாக:',
  },
  'hi-IN': {
    greeting: 'नमस्ते! 🙏 मैं पक्कम हूँ। तमिलनाडु या केंद्र सरकार की कल्याण योजनाओं के बारे में बोलकर या लिखकर पूछें। जवाब किस सरकारी पन्ने से है, वह भी दिखाऊँगा।',
    howAreYou: 'मैं ठीक हूँ, पूछने के लिए धन्यवाद! 😊 आज मैं आपकी कैसे मदद करूँ? नीचे किसी योजना के बारे में पूछें।',
    goodbye: 'अलविदा! 🙏 योजना के बारे में कोई सवाल हो तो कभी भी आइए।',
    thanks: 'आपका स्वागत है! 😊 क्या कुछ और जानना है? आप यह जवाब परिवार के साथ भी साझा कर सकते हैं।',
    ack: 'बढ़िया! क्या ज़रूरी दस्तावेज़ या आवेदन का तरीका जानना है?',
    notClear: 'माफ़ कीजिए, मैं मदद करता हूँ। मैं धीरे-धीरे फिर से समझा सकता हूँ, छोटा सारांश दे सकता हूँ, या सरकारी दस्तावेज़ का सही पन्ना दिखा सकता हूँ। क्या चाहिए?',
    complaint: 'माफ़ कीजिए। 🙏 पन्ना खोलकर ख़ुद जाँचें, योजना की हेल्पलाइन पर कॉल करें, या सवाल अधिकारी को भेजें। आपकी राय हमें बेहतर बनाती है।',
    about: 'मैं पक्कम हूँ, कल्याण योजनाओं के लिए आवाज़ सहायक। मैं सिर्फ़ आधिकारिक सरकारी दस्तावेज़ों से जवाब देता हूँ और हर जवाब का पन्ना दिखाता हूँ। दस्तावेज़ों में न हो तो साफ़ बता देता हूँ। यह एक छात्र प्रोजेक्ट है, सरकारी सेवा नहीं।',
    help: 'ऐसे इस्तेमाल करें:\n• ऑर्ब दबाकर बोलें, या सवाल लिखें।\n• तमिल, Tanglish, हिंदी या अंग्रेज़ी में पूछें।\n• सबूत के लिए "पन्ना देखें" दबाएँ।\n• छोटे जवाब के लिए "सारांश", दोबारा के लिए "फिर से" कहें।\n• व्हाट्सऐप संदेश जाँचने के लिए "संदेश जाँचें" इस्तेमाल करें।',
    schemes: 'इन योजनाओं के बारे में उनके आधिकारिक दस्तावेज़ों से जवाब दे सकता हूँ:',
    languages: 'आप तमिल, Tanglish, हिंदी या अंग्रेज़ी में, बोलकर या लिखकर पूछ सकते हैं। आप जिस भाषा में पूछेंगे, उसी में जवाब दूँगा।',
    official: 'नहीं। पक्कम एक छात्र प्रोजेक्ट है, सरकारी सेवा नहीं। लेकिन हर जवाब आधिकारिक सरकारी दस्तावेज़ से आता है, और जाँचने के लिए वही पन्ना दिखाता हूँ।',
    privacy: 'पक्कम आपका सवाल या आवाज़ सेव नहीं करता। आवाज़ और जवाब की सेवाओं को सिर्फ़ जवाब के लिए ज़रूरी जानकारी मिलती है। आधार या बैंक नंबर न लिखें।',
    issue: 'परेशानी के लिए माफ़ कीजिए। 🙏 थोड़ा धीरे बोलें या सवाल लिखें; योजना का नाम बताएँ। फिर भी काम न करे तो नीचे अधिकारी को भेजें।',
    offTopic: 'मैं सिर्फ़ कल्याण योजनाओं के बारे में, आधिकारिक सरकारी दस्तावेज़ों से जवाब दे सकता हूँ। इनमें से कुछ पूछें:',
    noLast: 'पहले कोई सवाल पूछें, फिर मैं उसे दोबारा समझा सकता हूँ या सारांश दे सकता हूँ।',
    summaryTitle: 'संक्षेप में:',
    againTitle: 'फिर से, एक-एक करके:',
  },
};

export const EXAMPLES = {
  'en-IN': ['How much is Magalir Urimai Thogai?', 'magalir urimai ku evlo varum?', 'Who can apply for PM-KISAN?', 'Documents needed for Ujjwala gas connection?'],
  'ta-IN': ['மகளிர் உரிமைத் தொகை எவ்வளவு?', 'magalir urimai ku evlo varum?', 'PM-KISAN திட்டத்திற்கு யார் விண்ணப்பிக்கலாம்?', 'உஜ்வாலா எரிவாயு இணைப்புக்கு என்ன ஆவணங்கள் தேவை?'],
  'hi-IN': ['PM-KISAN में कितना पैसा मिलता है?', 'उज्ज्वला के लिए कौन पात्र है?', 'अटल पेंशन योजना में कितनी पेंशन मिलती है?', 'magalir urimai ku evlo varum?'],
};
