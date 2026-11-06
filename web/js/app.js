// web/js/app.js
import { detectTalk, replyLanguage, TALK, EXAMPLES } from './talk.js';
import { decorate, iconSvg, splitIcon } from './icons.js';
import { SAMPLE_FACTS, SAMPLE_SOURCES, sampleFor } from './samples.js';
import { runTour } from './tour.js';
import { ART, fillArt } from './art.js';

const API_BASE = window.PAKKAM_API_BASE || '';

const ASSETS = {
  darkOrb: './assets/images/dark-orb.webp',
  lightOrb: './assets/images/light-orb.webp',
};

const MESSAGES = {
  'en-IN': {
    'nav.home':'Home','nav.schemes':'Schemes','nav.documents':'Documents','nav.history':'History','nav.about':'About','nav.aria':'Primary navigation','language.aria':'Select language','assistant.shortcut':'Voice assistant','home.documentTitle':'PAKKAM — Government Services, Simplified for Everyone',
    'home.eyebrow':'OFFICIAL SERVICES. CLEAR ANSWERS.','home.title':'Government services, simplified for everyone.','home.subtitle':'Your language. Your rights. Your access.','home.ask':'ASK PAKKAM AI',
    'home.howLabel':'A CLEARER WAY TO GET STARTED','home.howTitle':'A little help, one step at a time.','home.step1Title':'Ask in your own words','home.step1Body':'Speak or type in Tamil, Hindi or English.','home.step2Title':'Bring a document','home.step2Body':'Get a plain-language explanation of the pages you share.','home.step3Title':'Check the sources','home.step3Body':'Review the references that support an answer.','home.trustLabel':'BUILT AROUND CLARITY','home.trustTitle':'Public information should be easier to understand.','home.trustBody':'Pakkam helps make complex services and documents more approachable. Check official sources for decisions and current requirements.','home.aboutLink':'The story behind Pakkam →',
    'feature.01':'Understand Documents','feature.01body':'Turn complex government PDFs into simple explanations.','feature.02':'Speak Naturally','feature.02body':'Ask questions in Tamil, Hindi or English.','feature.03':'Trust Your Information','feature.03body':'Explore answers supported by official documents and references.',
    'assistant.tap':'Tap Orb to Speak','assistant.languages':'Supports Tamil, Hindi & English','assistant.stop':'Stop Audio Playback','assistant.name':'Pakkam AI','assistant.welcome':'Ask about a government service, document or official procedure in Tamil, Hindi or English.','assistant.placeholder':'Type your question in Tamil, Hindi or English...','common.send':'Send','common.ask':'Ask',
    'schemes.eyebrow':'PUBLIC INFORMATION DIRECTORY','schemes.title':'Government Scheme Explorer','schemes.intro':'Search available scheme information and review eligibility details.','schemes.search':'Search schemes...','schemes.all':'All schemes','category.agriculture':'Agriculture','category.education':'Education','category.healthcare':'Healthcare','category.housing':'Housing','schemes.benefits':'Main benefit','schemes.eligibility':'Eligibility','schemes.documents':'Required documents','schemes.details':'View details','schemes.empty':'No matching scheme information is available.',
    'documents.eyebrow':'DOCUMENT WORKSPACE','documents.title':'Document Assistant','documents.intro':'Upload a PDF to review it and ask questions about its contents.','documents.uploadTitle':'Choose a PDF to get started','documents.uploadBody':'Drop a government letter, form or notice here, or browse your files.','documents.browse':'Browse files','documents.format':'PDF documents only','documents.askTitle':'Ask about this document','documents.askHint':'Upload a document to ask questions about its contents.','documents.questionPlaceholder':'Ask about this PDF...','documents.selected':'Selected file','documents.uploading':'Uploading document...','documents.processing':'The document was received. Preparing its contents...','documents.ready':'Document processed. You can ask a question about it.','documents.error':'The document could not be uploaded. Please try again.','documents.invalid':'Choose a PDF document.','documents.preview':'Document preview','documents.privacy':'Your document is sent to the connected Pakkam service for processing.',
    'history.eyebrow':'YOUR ARCHIVE','history.title':'Conversation History','history.clear':'Clear All History','history.empty':'No saved conversations yet.','history.confirm':'Clear all saved conversations?',
    'settings.eyebrow':'PREFERENCES & ACCESSIBILITY','settings.title':'Application Settings','settings.autoplay':'Auto-play voice responses','settings.autoplayHelp':'Automatically read AI answers aloud in your selected language.','settings.theme':'Appearance theme','settings.themeHelp':'Switch between dark and light themes.','settings.switchTheme':'Switch Theme',
    'about.eyebrow':'THE STORY BEHIND PAKKAM','about.title':'It started with a conversation.','about.lede':'A conversation with a grandfather about the everyday difficulty of reaching public services.','about.storyLabel':'A family conversation','about.story':'I love my grandparents very much. One day, my grandfather told me how hard it was to access loans, read government messages and find his way through complicated portals on a mobile phone. That conversation stayed with me.','about.problemLabel':'A question we kept asking','about.problem':'Why should essential information be so difficult to reach?','about.problemBody':'My friend and I began imagining an assistant that could speak in a person’s language, read documents aloud and make complicated information easier to understand.','about.nameLabel':'A name with a meaning','about.nameIntro':'Pakkam means a page or side in Tamil.','about.nameBody':'It reflects our original idea: helping people read and understand important documents, one page at a time. Information should not be out of reach because reading or navigating a digital system is difficult.','about.visionLabel':'OUR VISION','about.vision':'Make essential public information understandable and accessible to everyone.','about.close':'Technology should make public services feel closer, clearer and more human.','footer.line':'Public information, made easier to understand.',
    'status.listening':'Listening... Tap Orb to Finish','status.processing':'Processing speech...','status.micError':'Microphone permission is required.','status.voiceError':'Voice service unavailable. You can type your question instead.','status.chatError':'Unable to connect to the Pakkam service. Please try again.'
  },
  'ta-IN': {
    'nav.home':'முகப்பு','nav.schemes':'திட்டங்கள்','nav.documents':'ஆவணங்கள்','nav.history':'வரலாறு','nav.about':'எங்களைப் பற்றி','nav.aria':'முதன்மை வழிசெலுத்தல்','language.aria':'மொழியைத் தேர்ந்தெடுக்கவும்','assistant.shortcut':'குரல் உதவியாளர்','home.documentTitle':'பாக்கம் — அரசுச் சேவைகள் எளிமையாக',
    'home.eyebrow':'அரசுச் சேவைகள். தெளிவான பதில்கள்.','home.title':'அனைவருக்கும் எளிய அரசுச் சேவைகள்.','home.subtitle':'உங்கள் மொழி. உங்கள் உரிமைகள். உங்கள் அணுகல்.','home.ask':'பாக்கம் AI-யைக் கேளுங்கள்',
    'home.howLabel':'தொடங்குவதற்கான எளிய வழி','home.howTitle':'ஒவ்வொரு படியிலும் சிறிய உதவி.','home.step1Title':'உங்கள் சொற்களில் கேளுங்கள்','home.step1Body':'தமிழ், இந்தி அல்லது ஆங்கிலத்தில் பேசவும் அல்லது தட்டச்சு செய்யவும்.','home.step2Title':'ஆவணத்தைப் பகிருங்கள்','home.step2Body':'நீங்கள் பகிரும் பக்கங்களை எளிய மொழியில் புரிந்துகொள்ளுங்கள்.','home.step3Title':'ஆதாரங்களைச் சரிபாருங்கள்','home.step3Body':'பதிலுக்கான குறிப்புகளைப் பாருங்கள்.','home.trustLabel':'தெளிவை மையமாகக் கொண்டு','home.trustTitle':'பொது தகவல்கள் புரிந்துகொள்ள எளிதாக இருக்க வேண்டும்.','home.trustBody':'சிக்கலான சேவைகள் மற்றும் ஆவணங்களைப் புரிந்துகொள்ள பாக்கம் உதவுகிறது. முடிவுகள் மற்றும் தற்போதைய தேவைகளுக்கு அதிகாரப்பூர்வ ஆதாரங்களைச் சரிபார்க்கவும்.','home.aboutLink':'பாக்கத்தின் பின்னணி →',
    'feature.01':'ஆவணங்களைப் புரிந்துகொள்ளுங்கள்','feature.01body':'சிக்கலான அரசு PDF-களை எளிய விளக்கங்களாக மாற்றுங்கள்.','feature.02':'இயல்பாகப் பேசுங்கள்','feature.02body':'தமிழ், இந்தி அல்லது ஆங்கிலத்தில் கேள்விகளைக் கேளுங்கள்.','feature.03':'தகவலைச் சரிபாருங்கள்','feature.03body':'அதிகாரப்பூர்வ ஆவணங்களின் ஆதரவுள்ள பதில்களைப் பாருங்கள்.',
    'assistant.tap':'பேச உருண்டையைத் தொடுங்கள்','assistant.languages':'தமிழ், இந்தி, ஆங்கிலம் ஆதரிக்கப்படும்','assistant.stop':'ஒலியை நிறுத்து','assistant.name':'பாக்கம் AI','assistant.welcome':'அரசுச் சேவை, ஆவணம் அல்லது அதிகாரப்பூர்வ நடைமுறை பற்றி கேளுங்கள்.','assistant.placeholder':'தமிழ், இந்தி அல்லது ஆங்கிலத்தில் கேள்வியைத் தட்டச்சு செய்யுங்கள்...','common.send':'அனுப்பு','common.ask':'கேளுங்கள்',
    'schemes.eyebrow':'பொது தகவல் பட்டியல்','schemes.title':'அரசுத் திட்டங்களைத் தேடுங்கள்','schemes.intro':'கிடைக்கும் திட்டத் தகவல்களைத் தேடி தகுதி விவரங்களைப் பாருங்கள்.','schemes.search':'திட்டங்களைத் தேடுங்கள்...','schemes.all':'அனைத்துத் திட்டங்கள்','category.agriculture':'விவசாயம்','category.education':'கல்வி','category.healthcare':'சுகாதாரம்','category.housing':'வீட்டுவசதி','schemes.benefits':'முக்கிய நன்மை','schemes.eligibility':'தகுதி','schemes.documents':'தேவையான ஆவணங்கள்','schemes.details':'விவரங்களைப் பார்க்க','schemes.empty':'பொருந்தும் திட்டத் தகவல் இல்லை.',
    'documents.eyebrow':'ஆவணப் பணியிடம்','documents.title':'ஆவண உதவியாளர்','documents.intro':'PDF-ஐப் பதிவேற்றி அதன் உள்ளடக்கத்தைப் பற்றி கேளுங்கள்.','documents.uploadTitle':'தொடங்க PDF-ஐத் தேர்ந்தெடுக்கவும்','documents.uploadBody':'அரசுக் கடிதம், படிவம் அல்லது அறிவிப்பை இங்கே விடுங்கள் அல்லது கோப்புகளைத் தேர்ந்தெடுக்கவும்.','documents.browse':'கோப்புகளைத் தேர்ந்தெடு','documents.format':'PDF ஆவணங்கள் மட்டும்','documents.askTitle':'இந்த ஆவணத்தைப் பற்றி கேளுங்கள்','documents.askHint':'உள்ளடக்கத்தைப் பற்றி கேட்க ஆவணத்தைப் பதிவேற்றவும்.','documents.questionPlaceholder':'இந்த PDF பற்றி கேளுங்கள்...','documents.selected':'தேர்ந்தெடுத்த கோப்பு','documents.uploading':'ஆவணம் பதிவேற்றப்படுகிறது...','documents.processing':'ஆவணம் பெறப்பட்டது. அதன் உள்ளடக்கம் தயாராகிறது...','documents.ready':'ஆவணம் செயலாக்கப்பட்டது. இப்போது கேள்வி கேட்கலாம்.','documents.error':'ஆவணத்தைப் பதிவேற்ற முடியவில்லை. மீண்டும் முயற்சிக்கவும்.','documents.invalid':'PDF ஆவணத்தைத் தேர்ந்தெடுக்கவும்.','documents.preview':'ஆவண முன்னோட்டம்','documents.privacy':'செயலாக்கத்திற்காக உங்கள் ஆவணம் இணைக்கப்பட்ட பாக்கம் சேவைக்கு அனுப்பப்படும்.',
    'history.eyebrow':'உங்கள் சேமிப்பு','history.title':'உரையாடல் வரலாறு','history.clear':'வரலாற்றை அழி','history.empty':'சேமித்த உரையாடல்கள் இல்லை.','history.confirm':'சேமித்த உரையாடல்கள் அனைத்தையும் அழிக்கவா?',
    'settings.eyebrow':'விருப்பங்கள் மற்றும் அணுகல்தன்மை','settings.title':'பயன்பாட்டு அமைப்புகள்','settings.autoplay':'குரல் பதில்களைத் தானாக இயக்கு','settings.autoplayHelp':'தேர்ந்தெடுத்த மொழியில் AI பதில்களை ஒலிக்கச் செய்யும்.','settings.theme':'தோற்றத் தீம்','settings.themeHelp':'இருண்ட மற்றும் ஒளிரும் தீம்களுக்கு மாறுங்கள்.','settings.switchTheme':'தீமை மாற்று',
    'about.eyebrow':'பாக்கத்தின் பின்னணி','about.title':'ஒரு உரையாடலில் தொடங்கியது.','about.lede':'அரசுச் சேவைகளை அணுகுவதில் உள்ள சிரமங்களைப் பற்றித் தாத்தாவுடன் நடந்த உரையாடல்.','about.storyLabel':'குடும்ப உரையாடல்','about.story':'என் தாத்தா பாட்டியை நான் மிகவும் நேசிக்கிறேன். ஒரு நாள், கடன் பெறுவது, அரசு செய்திகளைப் படிப்பது, கைப்பேசியில் சிக்கலான இணையதளங்களைப் பயன்படுத்துவது அவருக்கு எவ்வளவு கடினம் என்று தாத்தா கூறினார். அந்த உரையாடல் என் மனதில் நிலைத்தது.','about.problemLabel':'நாங்கள் கேட்ட கேள்வி','about.problem':'அத்தியாவசியமான தகவலை அணுகுவது ஏன் இவ்வளவு கடினமாக இருக்க வேண்டும்?','about.problemBody':'ஒருவரின் மொழியில் பேசவும், ஆவணங்களை வாசித்துக் காட்டவும், சிக்கலான தகவல்களை எளிதாக்கவும் உதவும் ஒரு உதவியாளரை நானும் என் நண்பரும் கற்பனை செய்தோம்.','about.nameLabel':'பொருள் கொண்ட பெயர்','about.nameIntro':'“பக்கம்” என்பது தமிழில் ஒரு பக்கத்தைக் குறிக்கும்.','about.nameBody':'ஆவணங்களை ஒரு பக்கமாகப் படித்து புரிந்துகொள்ள உதவுவது எங்கள் தொடக்கக் கருத்து. வாசிப்போ டிஜிட்டல் அமைப்பைப் பயன்படுத்துவதோ கடினம் என்பதால் முக்கியத் தகவல் எட்டாததாக இருக்கக் கூடாது.','about.visionLabel':'எங்கள் நோக்கு','about.vision':'அத்தியாவசிய பொது தகவலை அனைவரும் புரிந்துகொள்ளவும் அணுகவும் செய்ய வேண்டும்.','about.close':'தொழில்நுட்பம் அரசுச் சேவைகளை மேலும் நெருக்கமாகவும் தெளிவாகவும் மனிதநேயத்துடனும் மாற்ற வேண்டும்.','footer.line':'பொது தகவலை எளிதில் புரிந்துகொள்ளுங்கள்.',
    'status.listening':'கேட்கிறது... முடிக்க உருண்டையைத் தொடுங்கள்','status.processing':'குரல் செயலாக்கப்படுகிறது...','status.micError':'ஒலிவாங்கி அனுமதி தேவை.','status.voiceError':'குரல் சேவை கிடைக்கவில்லை. கேள்வியைத் தட்டச்சு செய்யலாம்.','status.chatError':'பாக்கம் சேவையுடன் இணைக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்.'
  },
  'hi-IN': {
    'nav.home':'होम','nav.schemes':'योजनाएँ','nav.documents':'दस्तावेज़','nav.history':'इतिहास','nav.about':'परिचय','nav.aria':'मुख्य नेविगेशन','language.aria':'भाषा चुनें','assistant.shortcut':'आवाज़ सहायक','home.documentTitle':'पक्कम — सरकारी सेवाएँ, सबके लिए सरल',
    'home.eyebrow':'सरकारी सेवाएँ। स्पष्ट जवाब।','home.title':'सरकारी सेवाएँ, सभी के लिए आसान।','home.subtitle':'आपकी भाषा। आपके अधिकार। आपकी पहुँच।','home.ask':'पक्कम AI से पूछें',
    'home.howLabel':'शुरू करने का आसान तरीका','home.howTitle':'हर कदम पर थोड़ी मदद।','home.step1Title':'अपने शब्दों में पूछें','home.step1Body':'तमिल, हिंदी या अंग्रेज़ी में बोलें या लिखें।','home.step2Title':'दस्तावेज़ साझा करें','home.step2Body':'साझा किए गए पन्नों को सरल भाषा में समझें।','home.step3Title':'स्रोत जाँचें','home.step3Body':'जवाब के साथ दिए गए संदर्भ देखें।','home.trustLabel':'स्पष्टता पर आधारित','home.trustTitle':'सार्वजनिक जानकारी समझना आसान होना चाहिए।','home.trustBody':'पक्कम जटिल सेवाओं और दस्तावेज़ों को समझने में मदद करता है। निर्णय और मौजूदा ज़रूरतों के लिए आधिकारिक स्रोत देखें।','home.aboutLink':'पक्कम की कहानी →',
    'feature.01':'दस्तावेज़ समझें','feature.01body':'जटिल सरकारी PDF को सरल व्याख्या में बदलें।','feature.02':'स्वाभाविक रूप से बोलें','feature.02body':'तमिल, हिंदी या अंग्रेज़ी में सवाल पूछें।','feature.03':'जानकारी पर भरोसा करें','feature.03body':'आधिकारिक दस्तावेज़ों से समर्थित जवाब देखें।',
    'assistant.tap':'बोलने के लिए ऑर्ब पर टैप करें','assistant.languages':'तमिल, हिंदी और अंग्रेज़ी उपलब्ध','assistant.stop':'ऑडियो रोकें','assistant.name':'पक्कम AI','assistant.welcome':'सरकारी सेवा, दस्तावेज़ या आधिकारिक प्रक्रिया के बारे में पूछें।','assistant.placeholder':'तमिल, हिंदी या अंग्रेज़ी में अपना सवाल लिखें...','common.send':'भेजें','common.ask':'पूछें',
    'schemes.eyebrow':'सार्वजनिक जानकारी निर्देशिका','schemes.title':'सरकारी योजना खोजें','schemes.intro':'उपलब्ध योजना जानकारी खोजें और पात्रता विवरण देखें।','schemes.search':'योजनाएँ खोजें...','schemes.all':'सभी योजनाएँ','category.agriculture':'कृषि','category.education':'शिक्षा','category.healthcare':'स्वास्थ्य','category.housing':'आवास','schemes.benefits':'मुख्य लाभ','schemes.eligibility':'पात्रता','schemes.documents':'ज़रूरी दस्तावेज़','schemes.details':'विवरण देखें','schemes.empty':'मेल खाती योजना जानकारी उपलब्ध नहीं है.',
    'documents.eyebrow':'दस्तावेज़ कार्यक्षेत्र','documents.title':'दस्तावेज़ सहायक','documents.intro':'PDF अपलोड करें और उसकी सामग्री के बारे में पूछें।','documents.uploadTitle':'शुरू करने के लिए PDF चुनें','documents.uploadBody':'सरकारी पत्र, फ़ॉर्म या सूचना यहाँ छोड़ें या फ़ाइलें ब्राउज़ करें।','documents.browse':'फ़ाइलें चुनें','documents.format':'केवल PDF दस्तावेज़','documents.askTitle':'इस दस्तावेज़ के बारे में पूछें','documents.askHint':'सामग्री के बारे में सवाल पूछने के लिए दस्तावेज़ अपलोड करें।','documents.questionPlaceholder':'इस PDF के बारे में पूछें...','documents.selected':'चुनी गई फ़ाइल','documents.uploading':'दस्तावेज़ अपलोड हो रहा है...','documents.processing':'दस्तावेज़ मिल गया। सामग्री तैयार की जा रही है...','documents.ready':'दस्तावेज़ तैयार है। अब सवाल पूछ सकते हैं।','documents.error':'दस्तावेज़ अपलोड नहीं हो सका। फिर कोशिश करें।','documents.invalid':'PDF दस्तावेज़ चुनें।','documents.preview':'दस्तावेज़ पूर्वावलोकन','documents.privacy':'प्रसंस्करण के लिए आपका दस्तावेज़ जुड़ी हुई पक्कम सेवा को भेजा जाएगा।',
    'history.eyebrow':'आपका संग्रह','history.title':'बातचीत का इतिहास','history.clear':'इतिहास मिटाएँ','history.empty':'अभी कोई बातचीत सेव नहीं है।','history.confirm':'सभी सेव की गई बातचीत मिटाएँ?',
    'settings.eyebrow':'प्राथमिकताएँ और पहुँच','settings.title':'ऐप सेटिंग्स','settings.autoplay':'आवाज़ में जवाब अपने आप चलाएँ','settings.autoplayHelp':'चुनी हुई भाषा में AI जवाब सुनें।','settings.theme':'दिखावट की थीम','settings.themeHelp':'डार्क और लाइट थीम के बीच बदलें।','settings.switchTheme':'थीम बदलें',
    'about.eyebrow':'पक्कम की कहानी','about.title':'यह एक बातचीत से शुरू हुआ।','about.lede':'दादा के साथ सार्वजनिक सेवाओं तक पहुँचने की रोज़मर्रा की मुश्किलों पर हुई बातचीत।','about.storyLabel':'परिवार की बातचीत','about.story':'मैं अपने दादा-दादी से बहुत प्यार करता हूँ। एक दिन दादाजी ने बताया कि ऋण पाना, सरकारी संदेश पढ़ना और मोबाइल पर जटिल पोर्टल चलाना उनके लिए कितना कठिन था। वह बातचीत मेरे मन में रह गई।','about.problemLabel':'हमारा सवाल','about.problem':'ज़रूरी जानकारी तक पहुँचना इतना मुश्किल क्यों होना चाहिए?','about.problemBody':'मैंने और मेरे दोस्त ने ऐसे सहायक की कल्पना की जो व्यक्ति की भाषा में बात करे, दस्तावेज़ पढ़कर सुनाए और जटिल जानकारी समझने में आसान बनाए।','about.nameLabel':'अर्थ वाला नाम','about.nameIntro':'तमिल में “पक्कम” का अर्थ पन्ना या पक्ष है।','about.nameBody':'यह हमारे शुरुआती विचार को दर्शाता है: लोगों को दस्तावेज़ एक पन्ने के बाद एक पन्ना पढ़ने और समझने में मदद करना। पढ़ने या डिजिटल प्रणाली चलाने में कठिनाई के कारण ज़रूरी जानकारी पहुँच से बाहर नहीं होनी चाहिए।','about.visionLabel':'हमारा दृष्टिकोण','about.vision':'ज़रूरी सार्वजनिक जानकारी को सभी के लिए समझने योग्य और सुलभ बनाना।','about.close':'तकनीक से सार्वजनिक सेवाएँ अधिक नज़दीकी, स्पष्ट और मानवीय बननी चाहिए।','footer.line':'सार्वजनिक जानकारी, जिसे समझना आसान हो।',
    'status.listening':'सुन रहा है... रोकने के लिए ऑर्ब टैप करें','status.processing':'आवाज़ संसाधित हो रही है...','status.micError':'माइक्रोफ़ोन की अनुमति ज़रूरी है।','status.voiceError':'आवाज़ सेवा उपलब्ध नहीं है। आप सवाल लिख सकते हैं।','status.chatError':'पक्कम सेवा से संपर्क नहीं हो पाया। फिर कोशिश करें।'
  }
};

let activeSchemeCategory = 'all';
const t = (key) => MESSAGES[state.language]?.[key] || MESSAGES['en-IN'][key] || key;

function applyLanguage(language) {
  state.language = MESSAGES[language] ? language : 'en-IN';
  localStorage.setItem('pakkam_lang', state.language);
  document.documentElement.lang = state.language.slice(0, 2);
  const selector = document.getElementById('global-lang-select');
  if (selector) selector.value = state.language;
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const value = t(element.dataset.i18n);
    if (value) decorate(element, value);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((element) => {
    element.setAttribute('aria-label', t(element.dataset.i18nAria));
  });
  document.querySelectorAll('[data-i18n-alt]').forEach((element) => { element.alt = t(element.dataset.i18nAlt); });
  document.querySelectorAll('[data-i18n-title]').forEach((element) => {
    const translated = t(element.dataset.i18nTitle);
    if (element.tagName === 'TITLE') document.title = translated;
    else element.title = translated;
  });
  renderSchemes(activeSchemeCategory, document.getElementById('scheme-search-input')?.value || '');
  renderHistory();
  labelPlayer();
}

const state = {
  theme: localStorage.getItem('pakkam_theme') || 'dark',
  language: (() => {
    let saved = null;
    try { saved = localStorage.getItem('pakkam_lang'); } catch (_) { /* private mode */ }
    if (saved) return saved;
    const browser = (navigator.language || '').toLowerCase();
    return browser.startsWith('ta') ? 'ta-IN' : browser.startsWith('hi') ? 'hi-IN' : 'en-IN';
  })(),
  autoPlayTTS: localStorage.getItem('pakkam_tts') !== 'false',
  isRecording: false,
  mediaRecorder: null,
  audioChunks: [],
  currentAudio: null,
  audioContext: null,
  analyser: null,
  waveformFrame: null,
  micStream: null,
  activeDocumentId: null,
  history: (() => { try { return JSON.parse(localStorage.getItem('pakkam_history') || '[]'); } catch (_) { return []; } })(),
};

function setOrbState(name) {
  ['hero-orb-assembly', 'assistant-orb-assembly'].forEach((id) => {
    const assembly = document.getElementById(id);
    if (!assembly) return;
    assembly.classList.toggle('listening', name === 'listening');
    assembly.classList.toggle('processing', name === 'processing');
    assembly.classList.toggle('speaking', name === 'speaking');
    assembly.classList.toggle('error', name === 'error');
    assembly.setAttribute('data-state', name);
  });
  document.body.dataset.orb = name;
}

function stopWaveformMeter() {
  if (state.waveformFrame) cancelAnimationFrame(state.waveformFrame);
  state.waveformFrame = null;
  document.querySelectorAll('.orb-waveform-assembly').forEach((assembly) => {
    assembly.classList.remove('audio-reactive');
    assembly.querySelectorAll('.wave-bar').forEach((bar) => bar.style.removeProperty('--bar-level'));
  });
  state.analyser = null;
}

function startWaveformMeter(source, monitor = false) {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return false;
    state.audioContext ||= new AudioContextClass();
    state.analyser = state.audioContext.createAnalyser();
    state.analyser.fftSize = 256;
    source.connect(state.analyser);
    if (monitor) state.analyser.connect(state.audioContext.destination);
    const samples = new Uint8Array(state.analyser.fftSize);
    document.querySelectorAll('.orb-waveform-assembly').forEach((assembly) => assembly.classList.add('audio-reactive'));

    const draw = () => {
      if (!state.analyser) return;
      state.analyser.getByteTimeDomainData(samples);
      let sum = 0;
      for (const sample of samples) {
        const normalized = (sample - 128) / 128;
        sum += normalized * normalized;
      }
      const amplitude = Math.min(1, Math.sqrt(sum / samples.length) * 3.8);
      const shape = [0.38, 0.62, 0.9, 0.72, 0.48];
      document.querySelectorAll('.orb-waveform-assembly').forEach((assembly) => {
        assembly.querySelectorAll('.waveform-wing').forEach((wing) => {
          wing.querySelectorAll('.wave-bar').forEach((bar, index) => {
            const factor = shape[index % shape.length];
            bar.style.setProperty('--bar-level', String(0.3 + amplitude * factor * 1.5));
          });
        });
      });
      state.waveformFrame = requestAnimationFrame(draw);
    };
    draw();
    return true;
  } catch (_) {
    stopWaveformMeter();
    return false;
  }
}

/* ==========================================================================
   1. THEME ENGINE (DARK & LIGHT REFERENCE SYNCHRONIZATION)
   ========================================================================== */
function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('pakkam_theme', theme);

  const orbSrc = theme === 'light' ? ASSETS.lightOrb : ASSETS.darkOrb;
  const heroOrb = document.getElementById('hero-orb-img');
  if (heroOrb) heroOrb.src = orbSrc;

  document.querySelectorAll('.theme-bound-orb').forEach((img) => {
    img.src = orbSrc;
  });
}

function toggleTheme() {
  applyTheme(state.theme === 'dark' ? 'light' : 'dark');
}

/* ==========================================================================
   2. NAVIGATION ROUTER
   ========================================================================== */
function navigateTo(pageKey) {
  document.querySelectorAll('.page-section').forEach((sec) => {
    sec.classList.remove('active');
  });
  const target = document.getElementById(`page-${pageKey}`);
  if (target) target.classList.add('active');

  document.querySelectorAll('.nav-item[data-nav], .tab-item[data-nav]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.nav === pageKey);
    if (btn.classList.contains('tab-item')) btn.setAttribute('aria-current', btn.dataset.nav === pageKey ? 'page' : 'false');
  });
  document.dispatchEvent(new CustomEvent('pakkam:page', { detail: pageKey }));
}


/* ==========================================================================
   Text for the parts connected to the Pakkam backend (merged into MESSAGES)
   ========================================================================== */
Object.assign(MESSAGES['en-IN'], {
  'home.title': 'Government schemes, explained from the official page.',
  'home.eyebrow': 'OFFICIAL DOCUMENTS. CLEAR ANSWERS.',
  'home.shield': '🛡️ Check a WhatsApp forward', 'home.tapOrb': 'Tap the orb and ask your question',
  'home.openChat': 'Open in chat', 'home.heard': 'You said',
  'nav.shield': 'Check a forward',
  'conv.mode': 'Conversation mode: keep listening after each answer', 'conv.short': 'Conversation mode',
  'conv.paused': 'Conversation paused. Tap the orb to continue.',
  'home.step1Body': 'Speak or type in Tamil, Tanglish, Hindi or English.',
  'home.step2Title': 'See the official page', 'home.step2Body': 'Every answer shows the government document and page it comes from.',
  'home.step3Title': 'No page, no answer', 'home.step3Body': 'When the documents do not say it, Pakkam says so instead of guessing.',
  'feature.01': 'See the Proof', 'feature.01body': 'Each answer opens the exact page of the official document.',
  'feature.02body': 'Ask in Tamil, Tanglish, Hindi or English.',
  'feature.03': 'No Page, No Answer', 'feature.03body': 'If the documents do not say it, Pakkam tells you honestly.',
  'assistant.languages': 'Supports Tamil, Tanglish, Hindi & English',
  'assistant.welcome': 'Vanakkam! Ask me about a Tamil Nadu or central welfare scheme, by voice or text. Every answer shows the official page it comes from. Try one of these:',
  'assistant.placeholder': 'Ask in Tamil, Tanglish, Hindi or English...',
  'assistant.stop': '⏹ Stop audio',
  'documents.eyebrow': 'OFFICIAL SOURCES', 'documents.title': 'The documents Pakkam reads',
  'documents.intro': 'Every answer comes from one of these official documents, with the page it is on.',
  'documents.note': 'Pakkam answers only from these documents, downloaded from official government websites. Open any of them to read it yourself.',
  'documents.open': 'Open official PDF', 'documents.dated': 'Dated', 'documents.loading': 'Loading the documents...',
  'documents.offline': 'The document list is unavailable while the Pakkam server is offline.',
  'schemes.intro': 'The schemes Pakkam can answer about. Tap a question to ask it.',
  'schemes.askAmount': 'How much?', 'schemes.askWho': 'Who can apply?', 'schemes.askDocs': 'Documents needed?',
  'schemes.docCount': 'official documents',
  'proof.open': 'See the page', 'proof.title': 'Proof from the official document', 'proof.page': 'Page',
  'proof.checked': 'Checked against the printed page by', 'proof.unchecked': 'Taken from the document text by Pakkam; check the page yourself.',
  'proof.source': 'Open the official PDF', 'proof.close': 'Close', 'proof.noImage': 'The page image is not available right now.',
  'proof.corrected': 'This line was corrected by hand from the printed page (the scan misread it).',
  'answer.refused': 'Not in the documents', 'answer.call': 'Helpline', 'answer.didYouMean': 'Which scheme do you mean?',
  'section.amount': 'How much', 'section.eligibility': 'Who can apply', 'section.documents': 'Documents', 'section.apply': 'How to apply',
  'answer.understood': 'Did you understand?', 'answer.yes': '✅ Yes', 'answer.notClear': '🤔 Not clear',
  'answer.helpful': 'Was this helpful?', 'answer.again': '🔁 Explain again', 'answer.summary': '📝 Summary',
  'answer.simpler': '🗣️ Simpler answer', 'answer.docs': '📋 Documents to carry', 'answer.share': '📤 Share on WhatsApp',
  'answer.print': '🖨️ Print', 'answer.appeal': '📝 Rejected? Appeal', 'answer.officer': '👤 Ask an officer',
  'answer.issue': 'Facing any issue? I can help:', 'answer.tips': '💡 Tips to ask',
  'answer.tipsText': 'Tips: name the scheme (for example "Magalir Urimai"), ask one thing at a time (amount, who can apply, documents), and speak a little slower if using voice.',
  'answer.feedbackThanks': 'Thank you for the feedback! 🙏',
  'answer.heardCheck': 'Is that what you asked?', 'answer.yesRight': '👍 Yes', 'answer.sayAgain': '🎙️ Say again',
  'facts.total': 'Up to {total} a year from these schemes (signed amounts).',
  'progress.searching': 'Searching the official documents…', 'progress.found': 'Found in {doc}, page {page}. Writing the answer…',
  'progress.slow': 'This is taking longer than usual. Still checking…',
  'checklist.title': 'Documents to carry and how to apply', 'checklist.none': 'No signed checklist for this scheme yet. Ask: "What documents are needed for {scheme}?"',
  'officer.title': 'Send your question to an officer', 'officer.intro': 'The documents did not answer this. An officer can follow up. Do not include Aadhaar or bank numbers.',
  'officer.question': 'Your question', 'officer.contact': 'Phone or email (optional)', 'officer.send': 'Send', 'officer.sent': 'Sent. Your reference number: {ticket}', 'officer.failed': 'Could not send it now. Please try again.',
  'about.listen': '🔊 Hear Pakkam explain itself', 'about.stop': '⏹ Stop',
  'about.intro': 'Vanakkam! I am Pakkam. Pakkam means page in Tamil. Ask me about a welfare scheme in Tamil, Tanglish, Hindi or English, by voice or text. I answer only from official government documents, and I show you the exact page the answer comes from. If the documents do not say it, I tell you honestly instead of guessing. I can also check WhatsApp forwards for false claims and scam signs.',
  'status.tooMany': 'Pakkam is getting a lot of questions. Wait a minute, then ask again.',
  'status.timeout': 'Pakkam took too long to answer. Ask again in a moment.',
  'status.noSpeech': 'I did not hear anything. Tap the orb and try again.',
  'footer.line': 'A student project, not a government service. Always check the official source before you act.',
});
Object.assign(MESSAGES['ta-IN'], {
  'home.title': 'அரசு திட்டங்கள், அதிகாரப்பூர்வ பக்கத்திலிருந்தே.',
  'home.eyebrow': 'அதிகாரப்பூர்வ ஆவணங்கள். தெளிவான பதில்கள்.',
  'home.shield': '🛡️ வாட்ஸ்அப் செய்தியைச் சரிபார்', 'home.tapOrb': 'உருண்டையைத் தொட்டு உங்கள் கேள்வியைக் கேளுங்கள்',
  'home.openChat': 'அரட்டையில் திற', 'home.heard': 'நீங்கள் சொன்னது',
  'nav.shield': 'செய்தியைச் சரிபார்',
  'conv.mode': 'உரையாடல் முறை: ஒவ்வொரு பதிலுக்குப் பிறகும் கேட்டுக்கொண்டிருக்கும்', 'conv.short': 'உரையாடல் முறை',
  'conv.paused': 'உரையாடல் நிறுத்தப்பட்டது. தொடர உருண்டையைத் தொடுங்கள்.',
  'home.step1Body': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில் பேசுங்கள் அல்லது தட்டச்சு செய்யுங்கள்.',
  'home.step2Title': 'அரசு பக்கத்தைப் பாருங்கள்', 'home.step2Body': 'ஒவ்வொரு பதிலும் அது வந்த அரசு ஆவணத்தையும் பக்கத்தையும் காட்டும்.',
  'home.step3Title': 'பக்கம் இல்லையேல் பதில் இல்லை', 'home.step3Body': 'ஆவணங்களில் இல்லாததை ஊகிக்காமல், இல்லை என்று நேர்மையாகச் சொல்லும்.',
  'feature.01': 'ஆதாரத்தைப் பாருங்கள்', 'feature.01body': 'ஒவ்வொரு பதிலும் அதிகாரப்பூர்வ ஆவணத்தின் சரியான பக்கத்தைத் திறக்கும்.',
  'feature.02body': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில் கேளுங்கள்.',
  'feature.03': 'பக்கம் இல்லையேல் பதில் இல்லை', 'feature.03body': 'ஆவணங்களில் இல்லையென்றால் நேர்மையாகச் சொல்லும்.',
  'assistant.languages': 'தமிழ், Tanglish, இந்தி, ஆங்கிலம்',
  'assistant.welcome': 'வணக்கம்! தமிழ்நாடு அல்லது மத்திய அரசு நலத்திட்டம் பற்றி குரலிலோ எழுத்திலோ கேளுங்கள். ஒவ்வொரு பதிலும் வந்த அரசு பக்கத்தைக் காட்டும். இவற்றில் ஒன்றை முயற்சிக்கவும்:',
  'assistant.placeholder': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில் கேளுங்கள்...',
  'assistant.stop': '⏹ ஒலியை நிறுத்து',
  'documents.eyebrow': 'அதிகாரப்பூர்வ ஆதாரங்கள்', 'documents.title': 'பக்கம் படிக்கும் ஆவணங்கள்',
  'documents.intro': 'ஒவ்வொரு பதிலும் இந்த அதிகாரப்பூர்வ ஆவணங்களில் ஒன்றிலிருந்து, பக்க எண்ணுடன் வருகிறது.',
  'documents.note': 'அரசு இணையதளங்களிலிருந்து பதிவிறக்கிய இந்த ஆவணங்களிலிருந்து மட்டுமே பக்கம் பதில் சொல்லும். எதை வேண்டுமானாலும் திறந்து நீங்களே படிக்கலாம்.',
  'documents.open': 'அதிகாரப்பூர்வ PDF-ஐத் திற', 'documents.dated': 'தேதி', 'documents.loading': 'ஆவணங்கள் ஏற்றப்படுகின்றன...',
  'documents.offline': 'பக்கம் சர்வர் இயங்காததால் ஆவணப் பட்டியல் இப்போது கிடைக்கவில்லை.',
  'schemes.intro': 'பக்கம் பதில் சொல்லக்கூடிய திட்டங்கள். கேள்வியைத் தொட்டுக் கேளுங்கள்.',
  'schemes.askAmount': 'எவ்வளவு?', 'schemes.askWho': 'யார் விண்ணப்பிக்கலாம்?', 'schemes.askDocs': 'என்ன ஆவணங்கள்?',
  'schemes.docCount': 'அதிகாரப்பூர்வ ஆவணங்கள்',
  'proof.open': 'பக்கத்தைப் பாருங்கள்', 'proof.title': 'அதிகாரப்பூர்வ ஆவணத்திலிருந்து ஆதாரம்', 'proof.page': 'பக்கம்',
  'proof.checked': 'அச்சுப் பக்கத்துடன் சரிபார்த்தவர்', 'proof.unchecked': 'ஆவண உரையிலிருந்து பக்கம் எடுத்தது; பக்கத்தை நீங்களே சரிபாருங்கள்.',
  'proof.source': 'அதிகாரப்பூர்வ PDF-ஐத் திற', 'proof.close': 'மூடு', 'proof.noImage': 'பக்கப் படம் இப்போது கிடைக்கவில்லை.',
  'proof.corrected': 'இந்த வரி அச்சுப் பக்கத்திலிருந்து கையால் திருத்தப்பட்டது (ஸ்கேன் தவறாகப் படித்தது).',
  'answer.refused': 'ஆவணங்களில் இல்லை', 'answer.call': 'உதவி எண்', 'answer.didYouMean': 'எந்தத் திட்டத்தைக் கேட்கிறீர்கள்?',
  'section.amount': 'எவ்வளவு', 'section.eligibility': 'யார் விண்ணப்பிக்கலாம்', 'section.documents': 'ஆவணங்கள்', 'section.apply': 'விண்ணப்பிக்கும் முறை',
  'answer.understood': 'புரிந்ததா?', 'answer.yes': '✅ புரிந்தது', 'answer.notClear': '🤔 புரியவில்லை',
  'answer.helpful': 'இது உதவியாக இருந்ததா?', 'answer.again': '🔁 மீண்டும் விளக்கு', 'answer.summary': '📝 சுருக்கம்',
  'answer.simpler': '🗣️ எளிய பதில்', 'answer.docs': '📋 எடுத்துச் செல்ல வேண்டிய ஆவணங்கள்', 'answer.share': '📤 வாட்ஸ்அப்பில் பகிர்',
  'answer.print': '🖨️ அச்சிடு', 'answer.appeal': '📝 நிராகரிக்கப்பட்டதா? மேல்முறையீடு', 'answer.officer': '👤 அதிகாரியிடம் கேள்',
  'answer.issue': 'ஏதாவது சிரமமா? உதவுகிறேன்:', 'answer.tips': '💡 கேட்கும் வழிகள்',
  'answer.tipsText': 'குறிப்பு: திட்டத்தின் பெயரைச் சொல்லுங்கள் (எ.கா. "மகளிர் உரிமை"), ஒரு நேரத்தில் ஒன்றைக் கேளுங்கள் (தொகை, தகுதி, ஆவணங்கள்), குரலில் கேட்டால் சற்று மெதுவாகப் பேசுங்கள்.',
  'answer.feedbackThanks': 'உங்கள் கருத்துக்கு நன்றி! 🙏',
  'answer.heardCheck': 'நீங்கள் கேட்டது இதுதானா?', 'answer.yesRight': '👍 ஆம்', 'answer.sayAgain': '🎙️ மீண்டும் சொல்',
  'facts.total': 'இந்தத் திட்டங்களிலிருந்து ஆண்டுக்கு {total} வரை (கையொப்பமிட்ட தொகைகள்).',
  'progress.searching': 'அதிகாரப்பூர்வ ஆவணங்களில் தேடுகிறது…', 'progress.found': '{doc}, பக்கம் {page}-ல் கிடைத்தது. பதில் எழுதப்படுகிறது…',
  'progress.slow': 'வழக்கத்தைவிட நேரமாகிறது. இன்னும் சரிபார்க்கிறது…',
  'checklist.title': 'எடுத்துச் செல்ல வேண்டிய ஆவணங்களும் விண்ணப்ப முறையும்', 'checklist.none': 'இந்தத் திட்டத்திற்கு இன்னும் சரிபார்த்த பட்டியல் இல்லை. "{scheme} திட்டத்திற்கு என்ன ஆவணங்கள் தேவை?" என்று கேளுங்கள்.',
  'officer.title': 'உங்கள் கேள்வியை அதிகாரிக்கு அனுப்புங்கள்', 'officer.intro': 'ஆவணங்களில் இதற்குப் பதில் இல்லை. அதிகாரி தொடர்பு கொள்ளலாம். ஆதார் அல்லது வங்கி எண்களைச் சேர்க்க வேண்டாம்.',
  'officer.question': 'உங்கள் கேள்வி', 'officer.contact': 'தொலைபேசி அல்லது மின்னஞ்சல் (விருப்பம்)', 'officer.send': 'அனுப்பு', 'officer.sent': 'அனுப்பப்பட்டது. உங்கள் குறிப்பு எண்: {ticket}', 'officer.failed': 'இப்போது அனுப்ப முடியவில்லை. மீண்டும் முயற்சிக்கவும்.',
  'about.listen': '🔊 பக்கம் தன்னைப் பற்றிச் சொல்வதைக் கேளுங்கள்', 'about.stop': '⏹ நிறுத்து',
  'about.intro': 'வணக்கம்! நான் பக்கம். பக்கம் என்றால் ஆவணத்தின் ஒரு பக்கம். தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில், குரலிலோ எழுத்திலோ நலத்திட்டம் பற்றி கேளுங்கள். அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து மட்டுமே பதில் சொல்வேன்; பதில் வந்த சரியான பக்கத்தையும் காட்டுவேன். ஆவணத்தில் இல்லையென்றால் ஊகிக்காமல் நேர்மையாகச் சொல்வேன். வாட்ஸ்அப் செய்திகளில் உள்ள தவறான தகவல்களையும் மோசடி அறிகுறிகளையும் சரிபார்ப்பேன்.',
  'status.tooMany': 'நிறைய கேள்விகள் வருகின்றன. ஒரு நிமிடம் கழித்துக் கேளுங்கள்.',
  'status.timeout': 'பதில் வர நேரமாகிவிட்டது. மீண்டும் கேளுங்கள்.',
  'status.noSpeech': 'எதுவும் கேட்கவில்லை. உருண்டையைத் தொட்டு மீண்டும் பேசுங்கள்.',
  'footer.line': 'இது ஒரு மாணவர் திட்டம், அரசு சேவை அல்ல. முடிவெடுக்கும் முன் அதிகாரப்பூர்வ ஆதாரத்தைச் சரிபாருங்கள்.',
});
Object.assign(MESSAGES['hi-IN'], {
  'home.title': 'सरकारी योजनाएँ, आधिकारिक पन्ने से समझें।',
  'home.eyebrow': 'आधिकारिक दस्तावेज़। स्पष्ट जवाब।',
  'home.shield': '🛡️ व्हाट्सऐप संदेश जाँचें', 'home.tapOrb': 'ऑर्ब दबाएँ और अपना सवाल पूछें',
  'home.openChat': 'चैट में खोलें', 'home.heard': 'आपने कहा',
  'nav.shield': 'संदेश जाँचें',
  'conv.mode': 'बातचीत मोड: हर जवाब के बाद सुनता रहेगा', 'conv.short': 'बातचीत मोड',
  'conv.paused': 'बातचीत रुकी। जारी रखने के लिए ऑर्ब दबाएँ।',
  'home.step1Body': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी में बोलें या लिखें।',
  'home.step2Title': 'आधिकारिक पन्ना देखें', 'home.step2Body': 'हर जवाब दिखाता है कि वह किस सरकारी दस्तावेज़ के किस पन्ने से है।',
  'home.step3Title': 'पन्ना नहीं, तो जवाब नहीं', 'home.step3Body': 'दस्तावेज़ों में न हो तो पक्कम अंदाज़ा नहीं लगाता, साफ़ बता देता है।',
  'feature.01': 'सबूत देखें', 'feature.01body': 'हर जवाब आधिकारिक दस्तावेज़ का सही पन्ना खोलता है।',
  'feature.02body': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी में पूछें।',
  'feature.03': 'पन्ना नहीं, तो जवाब नहीं', 'feature.03body': 'दस्तावेज़ों में न हो तो साफ़ बता देता है।',
  'assistant.languages': 'तमिल, Tanglish, हिंदी और अंग्रेज़ी',
  'assistant.welcome': 'नमस्ते! तमिलनाडु या केंद्र सरकार की कल्याण योजना के बारे में बोलकर या लिखकर पूछें। हर जवाब उसका सरकारी पन्ना दिखाता है। इनमें से कुछ आज़माएँ:',
  'assistant.placeholder': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी में पूछें...',
  'assistant.stop': '⏹ ऑडियो रोकें',
  'documents.eyebrow': 'आधिकारिक स्रोत', 'documents.title': 'पक्कम जो दस्तावेज़ पढ़ता है',
  'documents.intro': 'हर जवाब इन्हीं आधिकारिक दस्तावेज़ों में से किसी एक से, पन्ना संख्या के साथ आता है।',
  'documents.note': 'पक्कम सिर्फ़ इन्हीं दस्तावेज़ों से जवाब देता है, जो सरकारी वेबसाइटों से लिए गए हैं। कोई भी खोलकर ख़ुद पढ़ें।',
  'documents.open': 'आधिकारिक PDF खोलें', 'documents.dated': 'दिनांक', 'documents.loading': 'दस्तावेज़ लोड हो रहे हैं...',
  'documents.offline': 'पक्कम सर्वर बंद होने से दस्तावेज़ सूची अभी उपलब्ध नहीं है।',
  'schemes.intro': 'जिन योजनाओं के बारे में पक्कम जवाब दे सकता है। सवाल पर टैप करके पूछें।',
  'schemes.askAmount': 'कितना पैसा?', 'schemes.askWho': 'कौन आवेदन कर सकता है?', 'schemes.askDocs': 'कौन से दस्तावेज़?',
  'schemes.docCount': 'आधिकारिक दस्तावेज़',
  'proof.open': 'पन्ना देखें', 'proof.title': 'आधिकारिक दस्तावेज़ से सबूत', 'proof.page': 'पन्ना',
  'proof.checked': 'छपे पन्ने से जाँचा', 'proof.unchecked': 'दस्तावेज़ के पाठ से लिया गया; पन्ना ख़ुद जाँच लें।',
  'proof.source': 'आधिकारिक PDF खोलें', 'proof.close': 'बंद करें', 'proof.noImage': 'पन्ने की तस्वीर अभी उपलब्ध नहीं है।',
  'proof.corrected': 'यह पंक्ति छपे पन्ने से हाथ से सुधारी गई है (स्कैन ने गलत पढ़ा था)।',
  'answer.refused': 'दस्तावेज़ों में नहीं', 'answer.call': 'हेल्पलाइन', 'answer.didYouMean': 'आप किस योजना के बारे में पूछ रहे हैं?',
  'section.amount': 'कितना', 'section.eligibility': 'कौन आवेदन कर सकता है', 'section.documents': 'दस्तावेज़', 'section.apply': 'आवेदन कैसे करें',
  'answer.understood': 'क्या समझ आया?', 'answer.yes': '✅ हाँ', 'answer.notClear': '🤔 साफ़ नहीं',
  'answer.helpful': 'क्या यह मददगार था?', 'answer.again': '🔁 फिर से समझाएँ', 'answer.summary': '📝 सारांश',
  'answer.simpler': '🗣️ आसान जवाब', 'answer.docs': '📋 ज़रूरी दस्तावेज़', 'answer.share': '📤 व्हाट्सऐप पर भेजें',
  'answer.print': '🖨️ प्रिंट', 'answer.appeal': '📝 अस्वीकृत? अपील', 'answer.officer': '👤 अधिकारी से पूछें',
  'answer.issue': 'कोई परेशानी? मैं मदद कर सकता हूँ:', 'answer.tips': '💡 पूछने के तरीके',
  'answer.tipsText': 'सुझाव: योजना का नाम बताएँ, एक बार में एक बात पूछें (राशि, पात्रता, दस्तावेज़), और आवाज़ से पूछें तो थोड़ा धीरे बोलें।',
  'answer.feedbackThanks': 'आपकी राय के लिए धन्यवाद! 🙏',
  'answer.heardCheck': 'क्या आपने यही पूछा?', 'answer.yesRight': '👍 हाँ', 'answer.sayAgain': '🎙️ फिर से बोलें',
  'facts.total': 'इन योजनाओं से साल में {total} तक (जाँची गई राशि)।',
  'progress.searching': 'आधिकारिक दस्तावेज़ों में खोज रहा है…', 'progress.found': '{doc}, पन्ना {page} में मिला। जवाब लिखा जा रहा है…',
  'progress.slow': 'सामान्य से ज़्यादा समय लग रहा है। अभी जाँच रहा है…',
  'checklist.title': 'ज़रूरी दस्तावेज़ और आवेदन का तरीका', 'checklist.none': 'इस योजना की जाँची गई सूची अभी नहीं है। पूछें: "{scheme} के लिए कौन से दस्तावेज़ चाहिए?"',
  'officer.title': 'अपना सवाल अधिकारी को भेजें', 'officer.intro': 'दस्तावेज़ों में इसका जवाब नहीं मिला। अधिकारी संपर्क कर सकते हैं। आधार या बैंक नंबर न लिखें।',
  'officer.question': 'आपका सवाल', 'officer.contact': 'फ़ोन या ईमेल (वैकल्पिक)', 'officer.send': 'भेजें', 'officer.sent': 'भेज दिया। आपका संदर्भ नंबर: {ticket}', 'officer.failed': 'अभी नहीं भेज सके। फिर कोशिश करें।',
  'about.listen': '🔊 पक्कम से उसका परिचय सुनें', 'about.stop': '⏹ रोकें',
  'about.intro': 'नमस्ते! मैं पक्कम हूँ। तमिल में पक्कम का मतलब है पन्ना। तमिल, Tanglish, हिंदी या अंग्रेज़ी में, बोलकर या लिखकर किसी कल्याण योजना के बारे में पूछें। मैं सिर्फ़ आधिकारिक सरकारी दस्तावेज़ों से जवाब देता हूँ और जवाब का सही पन्ना दिखाता हूँ। दस्तावेज़ों में न हो तो अंदाज़ा नहीं लगाता, साफ़ बता देता हूँ। मैं व्हाट्सऐप संदेशों में गलत दावे और धोखाधड़ी के संकेत भी जाँचता हूँ।',
  'status.tooMany': 'बहुत सवाल आ रहे हैं। एक मिनट बाद फिर पूछें।',
  'status.timeout': 'जवाब में देर हो गई। फिर से पूछें।',
  'status.noSpeech': 'कुछ सुनाई नहीं दिया। ऑर्ब टैप करके फिर बोलें।',
  'footer.line': 'यह एक छात्र प्रोजेक्ट है, सरकारी सेवा नहीं। फ़ैसले से पहले आधिकारिक स्रोत देखें।',
});

Object.assign(MESSAGES['en-IN'], {
  'home.tryLabel': 'TRY ASKING', 'home.tryTitle': 'Ask the way you speak at home',
  'home.doesLabel': 'WHAT PAKKAM DOES', 'home.doesTitle': 'Answers you can check, not just believe',
  'home.tile3Title': 'Stop the rumour', 'home.tile3Body': 'Paste a WhatsApp forward and see which claims are false, with scam warnings.',
  'status.speaking': 'Speaking… tap the orb to stop', 'status.listening': 'Listening… tap the orb when you finish', 'status.processing': 'Thinking…',
  'schemes.eyebrow': 'SCHEMES & OFFICIAL SOURCES', 'schemes.title': 'Schemes Pakkam knows',
  'schemes.intro': 'Each scheme with its signed key facts, the official documents Pakkam reads, and questions people ask.',
  'schemes.summary': '{schemes} schemes · {docs} official documents', 'schemes.ask': 'Ask:',
  'set.voiceTitle': 'Voice & speech', 'set.speed': 'Speaking speed', 'set.normal': 'Normal', 'set.slow': 'Slow',
  'set.voiceLang': 'Language you speak in', 'set.easyTitle': 'Easy mode for elders',
  'set.easyHelp': 'Bigger text and buttons, slower voice, and a simpler home page.', 'set.easy': 'Easy mode',
  'set.lookTitle': 'Look', 'set.dark': 'Dark', 'set.light': 'Light', 'set.textSize': 'Text size', 'set.calm': 'Reduce animations',
  'set.privacyTitle': 'Privacy & data', 'set.privacyHelp': 'Pakkam does not store your questions or voice on the server. Your history below stays only in this browser.',
  'set.phone': 'Phone-call voice test (8 kHz phone audio)', 'set.clearConfirm': 'Tap again to clear everything',
  'ab.title1': 'Pakkam means', 'ab.title2': 'page.',
  'ab.lede': 'A voice assistant that answers questions about welfare schemes from the official government documents, and shows you the exact page.',
  'ab.whyTitle': 'Why we built it',
  'ab.problem': "The real rules for schemes like Magalir Urimai Thogai or PM-KISAN are written in long Government Orders that few people read. So families rely on WhatsApp forwards, middlemen or chatbots that sound sure but can be wrong. For someone's ₹1,000 a month, a confident wrong answer is worse than no answer.",
  'ab.canTitle': 'What Pakkam can do',
  'ab.f1t': 'Listens in your language', 'ab.f1': 'Tamil, Tanglish, Hindi or English, by voice or text, and answers out loud.',
  'ab.f2t': 'Shows the proof', 'ab.f2': 'Every answer opens the page of the official document, with the line highlighted.',
  'ab.f3t': 'Says "I don\'t know"', 'ab.f3': 'If the documents do not say it, Pakkam tells you instead of guessing.',
  'ab.f4t': 'Checks WhatsApp forwards', 'ab.f4': 'Finds false claims and scam signs like fake links and OTP requests.',
  'ab.f5t': 'Helps you prepare', 'ab.f5': 'Documents to carry, and a draft appeal note if an application was rejected.',
  'ab.f6t': 'Connects you to people', 'ab.f6': 'Scheme helplines, and a way to send your question to an officer.',
  'ab.howTitle': 'How it answers',
  'ab.h1t': 'You ask', 'ab.h1': 'Gnani Prisma turns your voice into text, even mixed Tamil and English.',
  'ab.h2t': 'Pakkam finds the page', 'ab.h2': 'It searches 18 official government documents, never the open internet.',
  'ab.h3t': 'It checks before it speaks', 'ab.h3': 'Every sentence must point to a page and every number must be on it. Then Gnani Timbre reads the answer aloud.',
  'ab.numTitle': 'Tested, honestly', 'ab.n1': 'test questions in 4 languages', 'ab.n2': 'of answers cite the correct page', 'ab.n3': 'out-of-scope questions honestly refused',
  'ab.credit': 'Built for the Gnani.ai Great Indian AI Internship Challenge 2026, with Gnani Prisma and Timbre for voice. A student project, not a government service.',
});
Object.assign(MESSAGES['ta-IN'], {
  'home.tryLabel': 'இப்படிக் கேளுங்கள்', 'home.tryTitle': 'வீட்டில் பேசுவது போலவே கேளுங்கள்',
  'home.doesLabel': 'பக்கம் என்ன செய்யும்', 'home.doesTitle': 'நம்பினால் போதாது, சரிபார்க்கலாம்',
  'home.tile3Title': 'வதந்தியை நிறுத்துங்கள்', 'home.tile3Body': 'வாட்ஸ்அப் செய்தியை ஒட்டுங்கள்; எது தவறு, மோசடி அறிகுறிகள் என்ன என்று காட்டும்.',
  'status.speaking': 'பேசுகிறது… நிறுத்த உருண்டையைத் தொடுங்கள்', 'status.listening': 'கேட்கிறது… முடிந்ததும் உருண்டையைத் தொடுங்கள்', 'status.processing': 'யோசிக்கிறது…',
  'schemes.eyebrow': 'திட்டங்களும் அதிகாரப்பூர்வ ஆதாரங்களும்', 'schemes.title': 'பக்கம் அறிந்த திட்டங்கள்',
  'schemes.intro': 'ஒவ்வொரு திட்டமும் அதன் சரிபார்த்த முக்கியத் தகவல்கள், பக்கம் படிக்கும் அதிகாரப்பூர்வ ஆவணங்கள், மக்கள் கேட்கும் கேள்விகளுடன்.',
  'schemes.summary': '{schemes} திட்டங்கள் · {docs} அதிகாரப்பூர்வ ஆவணங்கள்', 'schemes.ask': 'கேளுங்கள்:',
  'set.voiceTitle': 'குரல்', 'set.speed': 'பேச்சு வேகம்', 'set.normal': 'சாதாரண', 'set.slow': 'மெதுவாக',
  'set.voiceLang': 'நீங்கள் பேசும் மொழி', 'set.easyTitle': 'முதியோருக்கான எளிய முறை',
  'set.easyHelp': 'பெரிய எழுத்து, பெரிய பொத்தான்கள், மெதுவான குரல், எளிய முகப்பு.', 'set.easy': 'எளிய முறை',
  'set.lookTitle': 'தோற்றம்', 'set.dark': 'இருண்ட', 'set.light': 'ஒளி', 'set.textSize': 'எழுத்து அளவு', 'set.calm': 'அசைவுகளைக் குறை',
  'set.privacyTitle': 'தனியுரிமை', 'set.privacyHelp': 'உங்கள் கேள்விகளையோ குரலையோ பக்கம் சர்வரில் சேமிப்பதில்லை. கீழே உள்ள வரலாறு இந்த உலாவியில் மட்டுமே இருக்கும்.',
  'set.phone': 'தொலைபேசி அழைப்புக் குரல் சோதனை (8 kHz)', 'set.clearConfirm': 'எல்லாவற்றையும் அழிக்க மீண்டும் தொடுங்கள்',
  'ab.title1': 'பக்கம் என்றால்', 'ab.title2': 'ஆவணத்தின் பக்கம்.',
  'ab.lede': 'நலத்திட்டங்கள் பற்றிய கேள்விகளுக்கு அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து பதில் சொல்லி, சரியான பக்கத்தைக் காட்டும் குரல் உதவியாளர்.',
  'ab.whyTitle': 'ஏன் உருவாக்கினோம்',
  'about.story': 'என் தாத்தா பாட்டியை நான் மிகவும் நேசிக்கிறேன். ஒரு நாள், கடன் பெறுவது, அரசு செய்திகளைப் படிப்பது, கைப்பேசியில் சிக்கலான இணையதளங்களைப் பயன்படுத்துவது எவ்வளவு கடினம் என்று தாத்தா கூறினார். அந்த உரையாடல் என் மனதில் நிலைத்தது.',
  'ab.problem': 'மகளிர் உரிமைத் தொகை, PM-KISAN போன்ற திட்டங்களின் உண்மையான விதிகள் நீளமான அரசாணைகளில் உள்ளன; அவற்றைப் படிப்பவர்கள் குறைவு. அதனால் குடும்பங்கள் வாட்ஸ்அப் செய்திகள், இடைத்தரகர்கள், உறுதியாகப் பேசினாலும் தவறக்கூடிய சாட்பாட்களை நம்புகின்றன. ஒருவரின் மாதம் ₹1,000-க்கு, உறுதியான தவறான பதில் பதிலே இல்லாததைவிட மோசம்.',
  'ab.canTitle': 'பக்கம் என்ன செய்யும்',
  'ab.f1t': 'உங்கள் மொழியில் கேட்கும்', 'ab.f1': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில், குரலிலோ எழுத்திலோ; பதிலைப் பேசிக் காட்டும்.',
  'ab.f2t': 'ஆதாரம் காட்டும்', 'ab.f2': 'ஒவ்வொரு பதிலும் அதிகாரப்பூர்வ ஆவணத்தின் பக்கத்தை, வரியைச் சிறப்பித்துத் திறக்கும்.',
  'ab.f3t': '"தெரியாது" என்று சொல்லும்', 'ab.f3': 'ஆவணங்களில் இல்லையென்றால் ஊகிக்காமல் சொல்லும்.',
  'ab.f4t': 'வாட்ஸ்அப் செய்திகளைச் சரிபார்க்கும்', 'ab.f4': 'தவறான கூற்றுகள், போலி இணைப்பு, OTP கேட்பது போன்ற மோசடி அறிகுறிகளைக் கண்டுபிடிக்கும்.',
  'ab.f5t': 'தயாராக உதவும்', 'ab.f5': 'எடுத்துச் செல்ல வேண்டிய ஆவணங்கள், விண்ணப்பம் நிராகரிக்கப்பட்டால் மேல்முறையீட்டுக் கடித வரைவு.',
  'ab.f6t': 'மனிதர்களுடன் இணைக்கும்', 'ab.f6': 'திட்ட உதவி எண்கள், உங்கள் கேள்வியை அதிகாரிக்கு அனுப்பும் வசதி.',
  'ab.howTitle': 'எப்படிப் பதில் சொல்கிறது',
  'ab.h1t': 'நீங்கள் கேட்கிறீர்கள்', 'ab.h1': 'Gnani Prisma உங்கள் குரலை எழுத்தாக மாற்றும், தமிழும் ஆங்கிலமும் கலந்தாலும்.',
  'ab.h2t': 'பக்கம் பக்கத்தைக் கண்டுபிடிக்கிறது', 'ab.h2': '18 அதிகாரப்பூர்வ அரசு ஆவணங்களில் மட்டுமே தேடும், இணையத்தில் அல்ல.',
  'ab.h3t': 'பேசும் முன் சரிபார்க்கும்', 'ab.h3': 'ஒவ்வொரு வாக்கியமும் ஒரு பக்கத்தைக் காட்ட வேண்டும், ஒவ்வொரு எண்ணும் அதில் இருக்க வேண்டும். பிறகு Gnani Timbre பதிலைப் படிக்கும்.',
  'ab.numTitle': 'நேர்மையாகச் சோதித்தோம்', 'ab.n1': '4 மொழிகளில் சோதனைக் கேள்விகள்', 'ab.n2': 'பதில்கள் சரியான பக்கத்தைக் காட்டுகின்றன', 'ab.n3': 'ஆவணங்களில் இல்லாத கேள்விகள் நேர்மையாக மறுக்கப்பட்டன',
  'ab.credit': 'Gnani.ai Great Indian AI Internship Challenge 2026-க்காக, குரலுக்கு Gnani Prisma, Timbre பயன்படுத்தி உருவாக்கப்பட்டது. இது ஒரு மாணவர் திட்டம், அரசு சேவை அல்ல.',
});
Object.assign(MESSAGES['hi-IN'], {
  'home.tryLabel': 'ऐसे पूछें', 'home.tryTitle': 'जैसे घर पर बोलते हैं, वैसे ही पूछें',
  'home.doesLabel': 'पक्कम क्या करता है', 'home.doesTitle': 'सिर्फ़ भरोसा नहीं, जाँच भी करें',
  'home.tile3Title': 'अफ़वाह रोकें', 'home.tile3Body': 'व्हाट्सऐप संदेश चिपकाएँ और देखें कौन से दावे गलत हैं, धोखाधड़ी के संकेतों के साथ।',
  'status.speaking': 'बोल रहा है… रोकने के लिए ऑर्ब दबाएँ', 'status.listening': 'सुन रहा है… बोलकर ऑर्ब दबाएँ', 'status.processing': 'सोच रहा है…',
  'schemes.eyebrow': 'योजनाएँ और आधिकारिक स्रोत', 'schemes.title': 'पक्कम जिन योजनाओं को जानता है',
  'schemes.intro': 'हर योजना अपनी जाँची गई मुख्य जानकारी, पक्कम के पढ़े आधिकारिक दस्तावेज़ों और लोगों के सवालों के साथ।',
  'schemes.summary': '{schemes} योजनाएँ · {docs} आधिकारिक दस्तावेज़', 'schemes.ask': 'पूछें:',
  'set.voiceTitle': 'आवाज़', 'set.speed': 'बोलने की गति', 'set.normal': 'सामान्य', 'set.slow': 'धीमी',
  'set.voiceLang': 'आप जिस भाषा में बोलते हैं', 'set.easyTitle': 'बुज़ुर्गों के लिए आसान मोड',
  'set.easyHelp': 'बड़े अक्षर और बटन, धीमी आवाज़, आसान होम पेज।', 'set.easy': 'आसान मोड',
  'set.lookTitle': 'रूप', 'set.dark': 'डार्क', 'set.light': 'लाइट', 'set.textSize': 'अक्षर का आकार', 'set.calm': 'एनिमेशन कम करें',
  'set.privacyTitle': 'गोपनीयता', 'set.privacyHelp': 'पक्कम आपके सवाल या आवाज़ सर्वर पर सेव नहीं करता। नीचे का इतिहास सिर्फ़ इस ब्राउज़र में रहता है।',
  'set.phone': 'फ़ोन कॉल आवाज़ परीक्षण (8 kHz)', 'set.clearConfirm': 'सब मिटाने के लिए फिर दबाएँ',
  'ab.title1': 'पक्कम का मतलब है', 'ab.title2': 'पन्ना।',
  'ab.lede': 'एक आवाज़ सहायक जो कल्याण योजनाओं के सवालों का जवाब आधिकारिक सरकारी दस्तावेज़ों से देता है और सही पन्ना दिखाता है।',
  'ab.whyTitle': 'हमने इसे क्यों बनाया',
  'ab.problem': 'मगलिर उरिमै या PM-KISAN जैसी योजनाओं के असली नियम लंबे सरकारी आदेशों में लिखे हैं, जिन्हें कम लोग पढ़ते हैं। इसलिए परिवार व्हाट्सऐप संदेशों, बिचौलियों या ऐसे चैटबॉट पर भरोसा करते हैं जो पक्के लगते हैं पर गलत हो सकते हैं। किसी के ₹1,000 महीने के लिए, पक्का गलत जवाब, जवाब न होने से बुरा है।',
  'ab.canTitle': 'पक्कम क्या कर सकता है',
  'ab.f1t': 'आपकी भाषा में सुनता है', 'ab.f1': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी में, बोलकर या लिखकर, और जवाब बोलकर सुनाता है।',
  'ab.f2t': 'सबूत दिखाता है', 'ab.f2': 'हर जवाब आधिकारिक दस्तावेज़ का पन्ना पंक्ति हाइलाइट करके खोलता है।',
  'ab.f3t': '"मुझे नहीं पता" कहता है', 'ab.f3': 'दस्तावेज़ों में न हो तो अंदाज़ा नहीं लगाता, बता देता है।',
  'ab.f4t': 'व्हाट्सऐप संदेश जाँचता है', 'ab.f4': 'गलत दावे और नकली लिंक, OTP माँगने जैसे धोखाधड़ी संकेत पकड़ता है।',
  'ab.f5t': 'तैयारी में मदद', 'ab.f5': 'ज़रूरी दस्तावेज़, और आवेदन अस्वीकार होने पर अपील पत्र का मसौदा।',
  'ab.f6t': 'लोगों से जोड़ता है', 'ab.f6': 'योजना हेल्पलाइन, और सवाल अधिकारी को भेजने का तरीका।',
  'ab.howTitle': 'यह जवाब कैसे देता है',
  'ab.h1t': 'आप पूछते हैं', 'ab.h1': 'Gnani Prisma आपकी आवाज़ को लिखित में बदलता है, मिली-जुली तमिल-अंग्रेज़ी भी।',
  'ab.h2t': 'पक्कम पन्ना ढूँढता है', 'ab.h2': 'यह सिर्फ़ 18 आधिकारिक सरकारी दस्तावेज़ों में खोजता है, इंटरनेट पर नहीं।',
  'ab.h3t': 'बोलने से पहले जाँचता है', 'ab.h3': 'हर वाक्य किसी पन्ने से जुड़ा हो और हर संख्या उसी पर हो। फिर Gnani Timbre जवाब पढ़कर सुनाता है।',
  'ab.numTitle': 'ईमानदारी से जाँचा', 'ab.n1': '4 भाषाओं में परीक्षण सवाल', 'ab.n2': 'जवाब सही पन्ना बताते हैं', 'ab.n3': 'दायरे से बाहर के सवाल ईमानदारी से मना किए',
  'ab.credit': 'Gnani.ai Great Indian AI Internship Challenge 2026 के लिए, आवाज़ के लिए Gnani Prisma और Timbre के साथ बनाया गया। यह एक छात्र प्रोजेक्ट है, सरकारी सेवा नहीं।',
});

Object.assign(MESSAGES['en-IN'], {
  'nav.menu': 'Menu', 'set.readTitle': 'Reading & accessibility', 'set.langTitle': 'Language & theme', 'set.siteLang': 'Language of the site',
  'set.easy': 'Easy mode for elders',
  'cat.women': 'Women', 'cat.farmers': 'Farmers', 'cat.pension': 'Pension', 'cat.gas': 'Cooking gas', 'cat.children': 'Children',
  'cat.health': 'Health', 'cat.education': 'Education', 'cat.welfare': 'Welfare', 'issuer.tn': 'Tamil Nadu', 'issuer.central': 'Central',
  'schemes.all': 'All', 'schemes.details': 'Details', 'schemes.verified': 'Verified', 'schemes.noAmount': 'Amount: see the official document',
  'schemes.documents': 'Official documents', 'schemes.questions': 'Ask Pakkam',
});
Object.assign(MESSAGES['ta-IN'], {
  'nav.menu': 'பட்டி', 'set.readTitle': 'வாசிப்பு & அணுகல்', 'set.langTitle': 'மொழி & தீம்', 'set.siteLang': 'தளத்தின் மொழி',
  'set.easy': 'முதியோருக்கான எளிய முறை',
  'cat.women': 'பெண்கள்', 'cat.farmers': 'விவசாயிகள்', 'cat.pension': 'ஓய்வூதியம்', 'cat.gas': 'சமையல் எரிவாயு', 'cat.children': 'குழந்தைகள்',
  'cat.health': 'சுகாதாரம்', 'cat.education': 'கல்வி', 'cat.welfare': 'நலன்', 'issuer.tn': 'தமிழ்நாடு', 'issuer.central': 'மத்திய அரசு',
  'schemes.all': 'அனைத்தும்', 'schemes.details': 'விவரம்', 'schemes.verified': 'சரிபார்த்தது', 'schemes.noAmount': 'தொகை: அதிகாரப்பூர்வ ஆவணத்தைப் பாருங்கள்',
  'schemes.documents': 'அதிகாரப்பூர்வ ஆவணங்கள்', 'schemes.questions': 'பக்கத்திடம் கேளுங்கள்',
});
Object.assign(MESSAGES['hi-IN'], {
  'nav.menu': 'मेन्यू', 'set.readTitle': 'पढ़ना और सुलभता', 'set.langTitle': 'भाषा और थीम', 'set.siteLang': 'साइट की भाषा',
  'set.easy': 'बुज़ुर्गों के लिए आसान मोड',
  'cat.women': 'महिलाएँ', 'cat.farmers': 'किसान', 'cat.pension': 'पेंशन', 'cat.gas': 'रसोई गैस', 'cat.children': 'बच्चे',
  'cat.health': 'स्वास्थ्य', 'cat.education': 'शिक्षा', 'cat.welfare': 'कल्याण', 'issuer.tn': 'तमिलनाडु', 'issuer.central': 'केंद्र',
  'schemes.all': 'सभी', 'schemes.details': 'विवरण', 'schemes.verified': 'जाँचा गया', 'schemes.noAmount': 'राशि: आधिकारिक दस्तावेज़ देखें',
  'schemes.documents': 'आधिकारिक दस्तावेज़', 'schemes.questions': 'पक्कम से पूछें',
});

// Round 4: the orb's thought line and bubble, and the story on the About page.
Object.assign(MESSAGES['en-IN'], {
  'th.try': 'Try:', 'th.listen': 'Listening…', 'th.writing': 'Writing down what you said…',
  'th.search': 'Searching the official documents…', 'th.found': 'Found in {doc}, page {page}…',
  'th.check': 'Checking the numbers on the page…', 'th.speak': 'Speaking…', 'th.you': 'You',
  'home.shield': 'Check a WhatsApp forward',
  "st.eyebrow": "THE STORY BEHIND PAKKAM",
  "st.title": "It started with someone we love.",
  "st.p1": "We often think of technology as something that makes life easier. Faster payments, instant information, services at our fingertips.",
  "st.p2": "But one day, I realised that not everyone experiences technology that way.",
  "st.p3": "I love my grandparents. During one of our conversations, my grandfather spoke about something that had been troubling him. Accessing government services wasn’t easy. Understanding government messages was a struggle, and navigating mobile applications and government portals felt like an entirely different world.",
  "st.p4": "The information existed. The services existed. But accessing them was another challenge altogether.",
  "st.p5": "And that conversation stayed with me.",
  "st.h2": "What if technology could speak their language?",
  "st.p6": "A friend and I talked it through, and it came down to a simple question:",
  "st.q1": "Why should someone struggle to understand a government document when technology could simply explain it to them?",
  "st.p7": "What if an elderly person could ask a question in Tamil and receive an answer in Tamil, with the page of the official document shown right there?",
  "st.p8": "What if accessing information didn’t require knowing how to navigate complicated websites or understand official language?",
  "st.p9": "We didn’t want to build another portal that people had to learn how to use.",
  "st.p10": "We wanted to build something people could simply talk to.",
  "st.p11": "That’s how Pakkam was born.",
  "st.p12": "I began building an assistant that reads official scheme documents and answers questions in people’s own languages: Tamil, Hindi and English, with Tamil-English mixed typing too.",
  "st.p13": "An assistant that doesn’t just give an answer, but shows where that answer came from.",
  "st.p14": "And most importantly, one that knows when the documents don’t contain an answer, and says so rather than pretending to know.",
  "st.p15": "We started with the schemes we could check against official documents. There is more to cover, and we say so openly.",
  "st.h3": "Why the name Pakkam?",
  "st.p16": "A page in Tamil.",
  "st.p17": "The name comes from the simplest part of our original idea.",
  "st.p18": "A government document is made of pages. Each page contains information that could affect someone’s life, but understanding it shouldn’t require specialist knowledge.",
  "st.p19": "We wanted to make every page easier to understand.",
  "st.h4": "More than an AI assistant.",
  "st.p20": "Pakkam is about reducing the distance between people and the information they need: between a government scheme and the person who could benefit from it.",
  "st.p21": "Because technology should adapt to people, not the other way around.",
  "st.tag": "Your language. Your schemes. Your access.",
  "st.tag2": "One page at a time.",
  "st.disclaimer": "Pakkam is an early research prototype by students, not affiliated with any government body. Answers are for information only. Check the official source before you act.",
});
Object.assign(MESSAGES['ta-IN'], {
  'th.try': 'கேட்டுப் பாருங்கள்:', 'th.listen': 'கேட்கிறேன்…', 'th.writing': 'நீங்கள் சொன்னதை எழுதுகிறேன்…',
  'th.search': 'அதிகாரப்பூர்வ ஆவணங்களில் தேடுகிறேன்…', 'th.found': '{doc}, பக்கம் {page}-ல் கிடைத்தது…',
  'th.check': 'பக்கத்தில் உள்ள எண்களைச் சரிபார்க்கிறேன்…', 'th.speak': 'பேசுகிறேன்…', 'th.you': 'நீங்கள்',
  'home.shield': 'வாட்ஸ்அப் செய்தியைச் சரிபாருங்கள்',
  'st.eyebrow': 'பக்கத்தின் பின்னால் உள்ள கதை',
  'st.title': 'இது நாங்கள் நேசிக்கும் ஒருவரிடமிருந்து தொடங்கியது.',
  'st.p1': 'தொழில்நுட்பம் வாழ்க்கையை எளிதாக்குகிறது என்றுதான் நாம் அடிக்கடி நினைக்கிறோம். விரைவான பணப் பரிமாற்றம், உடனடித் தகவல், விரல் நுனியில் சேவைகள்.',
  'st.p2': 'ஆனால் ஒருநாள், எல்லோரும் தொழில்நுட்பத்தை அப்படி அனுபவிப்பதில்லை என்று எனக்குப் புரிந்தது.',
  'st.p3': 'நான் என் தாத்தா பாட்டியை நேசிக்கிறேன். ஒருமுறை பேசிக்கொண்டிருந்தபோது, என் தாத்தா தன்னை வருத்திக்கொண்டிருந்த ஒரு விஷயத்தைப் பற்றிச் சொன்னார். அரசுச் சேவைகளை அணுகுவது எளிதாக இல்லை. அரசுச் செய்திகளைப் புரிந்துகொள்வது கடினமாக இருந்தது; மொபைல் செயலிகளும் அரசு இணையதளங்களும் முற்றிலும் வேறு உலகமாகத் தோன்றின.',
  'st.p4': 'தகவல் இருந்தது. சேவைகள் இருந்தன. ஆனால் அவற்றை அணுகுவது முற்றிலும் வேறு சவாலாக இருந்தது.',
  'st.p5': 'அந்த உரையாடல் என் மனதிலேயே தங்கிவிட்டது.',
  'st.h2': 'தொழில்நுட்பம் அவர்களின் மொழியில் பேசினால் என்ன?',
  'st.p6': 'நானும் என் நண்பரும் இதைப் பற்றிப் பேசினோம்; அது ஒரு எளிய கேள்வியில் வந்து நின்றது:',
  'st.q1': 'தொழில்நுட்பமே எளிதாக விளக்கிவிட முடியும் போது, ஒருவர் ஏன் அரசு ஆவணத்தைப் புரிந்துகொள்ளச் சிரமப்பட வேண்டும்?',
  'st.p7': 'ஒரு முதியவர் தமிழில் கேள்வி கேட்டு, தமிழிலேயே பதில் பெற்று, அதிகாரப்பூர்வ ஆவணத்தின் பக்கத்தையும் அங்கேயே பார்க்க முடிந்தால் என்ன?',
  'st.p8': 'தகவலை அணுகச் சிக்கலான இணையதளங்களைக் கையாளவோ அதிகாரப்பூர்வ மொழியைப் புரிந்துகொள்ளவோ தேவையில்லை என்றால் என்ன?',
  'st.p9': 'மக்கள் கற்றுக்கொள்ள வேண்டிய இன்னொரு இணையதளத்தை உருவாக்க நாங்கள் விரும்பவில்லை.',
  'st.p10': 'மக்கள் எளிதாகப் பேசக்கூடிய ஒன்றை உருவாக்க விரும்பினோம்.',
  'st.p11': 'இப்படித்தான் பக்கம் பிறந்தது.',
  'st.p12': 'அதிகாரப்பூர்வத் திட்ட ஆவணங்களைப் படித்து, மக்களின் சொந்த மொழியில் பதில் சொல்லும் ஒரு உதவியாளரை உருவாக்கத் தொடங்கினேன்: தமிழ், இந்தி, ஆங்கிலம், தமிழ்-ஆங்கிலக் கலப்பு எழுத்தும் கூட.',
  'st.p13': 'பதிலை மட்டும் சொல்லாமல், அந்தப் பதில் எங்கிருந்து வந்தது என்றும் காட்டும் உதவியாளர்.',
  'st.p14': 'எல்லாவற்றுக்கும் மேலாக, ஆவணங்களில் பதில் இல்லாதபோது அதை உணர்ந்து, தெரிந்ததுபோல் நடிக்காமல் நேர்மையாகச் சொல்லும் ஒன்று.',
  'st.p15': 'அதிகாரப்பூர்வ ஆவணங்களுடன் சரிபார்க்க முடிந்த திட்டங்களுடன் தொடங்கினோம். இன்னும் நிறைய சேர்க்க வேண்டியுள்ளது; அதை வெளிப்படையாகச் சொல்கிறோம்.',
  'st.h3': 'ஏன் பக்கம் என்று பெயர்?',
  'st.p16': 'தமிழில் ஒரு பக்கம்.',
  'st.p17': 'இந்தப் பெயர் எங்கள் தொடக்க யோசனையின் மிக எளிய பகுதியிலிருந்து வருகிறது.',
  'st.p18': 'ஒரு அரசு ஆவணம் பக்கங்களால் ஆனது. ஒவ்வொரு பக்கத்திலும் ஒருவரின் வாழ்க்கையைப் பாதிக்கக்கூடிய தகவல் இருக்கிறது; ஆனால் அதைப் புரிந்துகொள்ள நிபுணத்துவம் தேவைப்படக் கூடாது.',
  'st.p19': 'ஒவ்வொரு பக்கத்தையும் எளிதாகப் புரியும்படி செய்ய விரும்பினோம்.',
  'st.h4': 'ஒரு AI உதவியாளரை விட மேலானது.',
  'st.p20': 'மக்களுக்கும் அவர்களுக்குத் தேவையான தகவலுக்கும் இடையிலான தூரத்தைக் குறைப்பதே பக்கம்: ஒரு அரசுத் திட்டத்திற்கும் அதனால் பயன்பெறக்கூடிய நபருக்கும் இடையிலான தூரம்.',
  'st.p21': 'ஏனென்றால் தொழில்நுட்பம்தான் மக்களுக்கு ஏற்ப மாற வேண்டும்; மக்கள் தொழில்நுட்பத்துக்கு ஏற்ப அல்ல.',
  'st.tag': 'உங்கள் மொழி. உங்கள் திட்டங்கள். உங்கள் அணுகல்.',
  'st.tag2': 'ஒரு நேரத்தில் ஒரு பக்கம்.',
  'st.disclaimer': 'பக்கம் மாணவர்கள் உருவாக்கிய தொடக்க நிலை ஆய்வு முன்மாதிரி; எந்த அரசு அமைப்புடனும் தொடர்பில்லை. பதில்கள் தகவலுக்கு மட்டுமே. செயல்படும் முன் அதிகாரப்பூர்வ மூலத்தைச் சரிபாருங்கள்.',
});
Object.assign(MESSAGES['hi-IN'], {
  'th.try': 'पूछकर देखें:', 'th.listen': 'सुन रहा हूँ…', 'th.writing': 'आपने जो कहा, लिख रहा हूँ…',
  'th.search': 'आधिकारिक दस्तावेज़ों में खोज रहा हूँ…', 'th.found': '{doc}, पन्ना {page} में मिला…',
  'th.check': 'पन्ने पर दी गई रकम जाँच रहा हूँ…', 'th.speak': 'बोल रहा हूँ…', 'th.you': 'आप',
  'home.shield': 'व्हाट्सऐप फ़ॉरवर्ड जाँचें',
  'st.eyebrow': 'पक्कम के पीछे की कहानी',
  'st.title': 'यह किसी ऐसे व्यक्ति से शुरू हुआ जिसे हम प्यार करते हैं।',
  'st.p1': 'हम अक्सर सोचते हैं कि तकनीक ज़िंदगी आसान बनाती है। तेज़ भुगतान, तुरंत जानकारी, उँगलियों पर सेवाएँ।',
  'st.p2': 'लेकिन एक दिन मुझे एहसास हुआ कि हर कोई तकनीक को इस तरह महसूस नहीं करता।',
  'st.p3': 'मुझे अपने दादा-दादी से बहुत प्यार है। एक बातचीत में मेरे दादाजी ने एक ऐसी बात बताई जो उन्हें परेशान कर रही थी। सरकारी सेवाओं तक पहुँचना आसान नहीं था। सरकारी संदेश समझना मुश्किल था, और मोबाइल ऐप व सरकारी पोर्टल चलाना बिल्कुल अलग दुनिया जैसा लगता था।',
  'st.p4': 'जानकारी मौजूद थी। सेवाएँ मौजूद थीं। लेकिन उन तक पहुँचना एक अलग ही चुनौती थी।',
  'st.p5': 'और वह बातचीत मेरे मन में रह गई।',
  'st.h2': 'क्या हो अगर तकनीक उनकी भाषा बोल सके?',
  'st.p6': 'मैंने और मेरे एक दोस्त ने इस पर बात की, और बात एक सीधे सवाल पर आकर रुकी:',
  'st.q1': 'जब तकनीक सरकारी दस्तावेज़ को आसानी से समझा सकती है, तो किसी को उसे समझने में संघर्ष क्यों करना पड़े?',
  'st.p7': 'क्या हो अगर कोई बुज़ुर्ग तमिल में सवाल पूछे और तमिल में ही जवाब पाए, और आधिकारिक दस्तावेज़ का पन्ना वहीं दिखे?',
  'st.p8': 'क्या हो अगर जानकारी पाने के लिए मुश्किल वेबसाइटें चलाना या सरकारी भाषा समझना ज़रूरी न हो?',
  'st.p9': 'हम एक और पोर्टल नहीं बनाना चाहते थे जिसे लोगों को चलाना सीखना पड़े।',
  'st.p10': 'हम कुछ ऐसा बनाना चाहते थे जिससे लोग बस बात कर सकें।',
  'st.p11': 'इसी तरह पक्कम का जन्म हुआ।',
  'st.p12': 'मैंने एक ऐसा सहायक बनाना शुरू किया जो आधिकारिक योजना दस्तावेज़ पढ़ता है और लोगों की अपनी भाषा में जवाब देता है: तमिल, हिंदी और अंग्रेज़ी, साथ में तमिल-अंग्रेज़ी मिली टाइपिंग भी।',
  'st.p13': 'एक सहायक जो सिर्फ़ जवाब नहीं देता, बल्कि यह भी दिखाता है कि जवाब कहाँ से आया।',
  'st.p14': 'और सबसे ज़रूरी, जो जानता है कि कब दस्तावेज़ों में जवाब नहीं है, और जानने का दिखावा करने के बजाय यह साफ़ कहता है।',
  'st.p15': 'हमने उन योजनाओं से शुरुआत की जिन्हें हम आधिकारिक दस्तावेज़ों से जाँच सकते थे। अभी बहुत कुछ जोड़ना बाक़ी है, और यह हम खुलकर कहते हैं।',
  'st.h3': 'नाम पक्कम क्यों?',
  'st.p16': 'तमिल में एक पन्ना।',
  'st.p17': 'यह नाम हमारे मूल विचार के सबसे सरल हिस्से से आया है।',
  'st.p18': 'सरकारी दस्तावेज़ पन्नों से बना होता है। हर पन्ने पर ऐसी जानकारी होती है जो किसी की ज़िंदगी बदल सकती है, लेकिन उसे समझने के लिए विशेषज्ञ ज्ञान की ज़रूरत नहीं होनी चाहिए।',
  'st.p19': 'हम हर पन्ने को समझने में आसान बनाना चाहते थे।',
  'st.h4': 'एक AI सहायक से कहीं ज़्यादा।',
  'st.p20': 'पक्कम का मक़सद लोगों और उनकी ज़रूरत की जानकारी के बीच की दूरी कम करना है: एक सरकारी योजना और उससे फ़ायदा पा सकने वाले व्यक्ति के बीच की दूरी।',
  'st.p21': 'क्योंकि तकनीक को लोगों के हिसाब से ढलना चाहिए, लोगों को तकनीक के हिसाब से नहीं।',
  'st.tag': 'आपकी भाषा। आपकी योजनाएँ। आपकी पहुँच।',
  'st.tag2': 'एक समय में एक पन्ना।',
  'st.disclaimer': 'पक्कम छात्रों का शुरुआती रिसर्च प्रोटोटाइप है, किसी सरकारी संस्था से जुड़ा नहीं। जवाब केवल जानकारी के लिए हैं। कोई कदम उठाने से पहले आधिकारिक स्रोत देखें।',
});


// Round 5: footer, About chapters and credits, offline mode.
Object.assign(MESSAGES['en-IN'], {
  'a11y.skip': 'Skip to content', 'footer.privacy': 'Privacy', 'footer.code': 'Source code', 'footer.contact': 'Report a problem',
  'about.listen': 'Hear Pakkam explain itself', 'about.stop': 'Stop',
  'st.c1': 'The conversation', 'st.c2': 'The question', 'st.c3': 'How Pakkam was born', 'st.c4': 'The name', 'st.c5': 'What it is for',
  'ab.canEyebrow': 'WHAT IT DOES', 'ab.howEyebrow': 'UNDER THE HOOD', 'ab.numEyebrow': 'MEASURED ON THE LIVE SITE',
  'ab.numLink': 'See the full benchmark →', 'ab.badgeDocs': '18 official documents',
  'ab.teamEyebrow': 'THE PEOPLE BEHIND PAKKAM', 'ab.teamTitle': 'Made by', 'ab.ctaTitle': 'Have a question about a scheme?',
  'credit.role1': 'Idea, AI, backend and frontend', 'credit.role2': 'Design and frontend',
  'answer.helpfulYes': 'Yes, helpful', 'answer.helpfulNo': 'Not helpful',
  'shield.yourMessage': 'Your message, with warning signs marked', 'shield.markTitle': 'Warning sign: check before trusting',
  'shield.signsNote': 'Warning signs mean: be careful. On their own they do not prove the message is false. The verdict above comes only from the official documents.',
  'proof.pdfAt': 'Open the official PDF (page {page})', 'proof.pdfNote': 'If the PDF opens at page 1, go to page {page}. The page image above always shows the right page.',
  'answer.checkedBy': 'Checked against the printed page by {names}', 'answer.fromDoc': 'From the official document. Open a page to check it yourself.',
  'catline.women': 'Schemes for women', 'catline.farmers': 'Schemes for farmers', 'catline.pension': 'Pension schemes', 'catline.gas': 'Cooking gas schemes',
  'catline.children': 'Schemes for children', 'catline.health': 'Health schemes', 'catline.education': 'Education schemes', 'catline.welfare': 'Other welfare schemes',
  'catline.hint': 'Tap a scheme to see its key facts and the official documents they come from.',
  'guide.title': 'How to use this list', 'guide.1': 'Pick a scheme', 'guide.1b': 'Use the tabs, or search by name.',
  'guide.2': 'Read the key facts', 'guide.2b': 'The amount and who can apply, each with the page it comes from.',
  'guide.3': 'Open the official page', 'guide.3b': 'Check it yourself in the government document.',
  'schemes.emptyArt': 'No scheme matches that. Try another word, or ask Pakkam.',
  'alt.schemesHero': 'Illustration: a woman and an elderly man at a ration shop counter on a Tamil Nadu street.',
  'alt.aboutOpening': 'Illustration: a grandfather and his grandchild looking at a phone together at home.',
  'sc.1t': 'The problem', 'sc.1': 'The rules are in long official papers that are hard to find and harder to read.',
  'sc.2t': 'Ask Pakkam', 'sc.2': 'Ask in your own language, by voice or by typing.',
  'sc.3t': 'See the proof', 'sc.3': 'The answer points to the exact line on the official page.',
  'easy.readAloud': 'Read answers aloud', 'composer.stop': 'Stop speaking', 'chat.latest': 'Jump to latest', 'answer.more': 'Show more', 'answer.less': 'Show less',
  'orb.idle': 'Tap the orb to speak', 'orb.listening': 'Listening… tap the orb when you finish', 'orb.busy': 'Finding the answer… tap to stop',
  'orb.speaking': 'Speaking… tap the orb to stop', 'orb.error': 'Something went wrong. Tap the orb to try again',
  'mic.title': "Pakkam can't hear you yet", 'mic.type': 'Type instead',
  'mic.body': 'Your browser has blocked the microphone. Tap the lock or (i) icon next to the web address, choose Allow for Microphone, then reload the page. You can also type your question.',
  'set.bg': 'Background', 'set.bgMinimal': 'Minimal', 'set.bgBalanced': 'Balanced', 'set.bgAmbient': 'Ambient',
  'feature.03': 'Check a Forward', 'feature.03body': 'Paste a WhatsApp message and see which claims are false.',
  'tour.start': 'Take the 60-second tour', 'tour.next': 'Next', 'tour.back': 'Back', 'tour.skip': 'Skip tour', 'tour.done': 'Finish', 'tour.count': 'Step {n} of {total}',
  'tour.1t': 'Ask in your own language', 'tour.1': 'Tap the orb and speak in Tamil, Tanglish, Hindi or English. You can also type.',
  'tour.2t': 'An answer with its sources', 'tour.2': 'Each answer lists the official pages it comes from. The small numbers after each line open the exact page.',
  'tour.3t': 'The real page, not a guess', 'tour.3': 'This is the page of the Government Order, with the line highlighted and the name of the person who checked it.',
  'tour.4t': 'Check a WhatsApp forward', 'tour.4': 'Paste a forward and Pakkam checks every claim against the official documents and warns about scam signs.',
  'tour.5t': 'Why we built it', 'tour.5': 'Pakkam started with a conversation with a grandfather. Read the story here.',
  'nav.ask': 'Ask', 'nav.forward': 'Forward', 'shield.paste': '📋 Paste from WhatsApp', 'answer.sources': 'Sources', 'answer.copy': '📋 Copy', 'answer.copied': 'Copied', 'proof.pageShort': 'p.', 'composer.mic': 'Speak your question',
  'offline.banner': "Pakkam's server is offline right now. You can still look around, and answers below are samples.",
  'offline.retry': 'Try again', 'offline.sample': 'Sample answer: the live server is offline',
  'offline.none': "The live server is offline, so I can't answer this one right now. Try again in a little while, or try one of these sample questions.",
});
Object.assign(MESSAGES['ta-IN'], {
  'a11y.skip': 'உள்ளடக்கத்திற்குச் செல்', 'footer.privacy': 'தனியுரிமை', 'footer.code': 'மூலக் குறியீடு', 'footer.contact': 'சிக்கலைத் தெரிவிக்க',
  'about.listen': 'பக்கம் தன்னைப் பற்றிச் சொல்வதைக் கேளுங்கள்', 'about.stop': 'நிறுத்து',
  'st.c1': 'அந்த உரையாடல்', 'st.c2': 'அந்தக் கேள்வி', 'st.c3': 'பக்கம் பிறந்த கதை', 'st.c4': 'பெயர்', 'st.c5': 'இது எதற்காக',
  'ab.canEyebrow': 'இது என்ன செய்யும்', 'ab.howEyebrow': 'உள்ளே எப்படி இயங்குகிறது', 'ab.numEyebrow': 'நேரடித் தளத்தில் அளவிடப்பட்டது',
  'ab.numLink': 'முழு சோதனை முடிவுகளைப் பாருங்கள் →', 'ab.badgeDocs': '18 அதிகாரப்பூர்வ ஆவணங்கள்',
  'ab.teamEyebrow': 'பக்கத்தின் பின்னால் உள்ளவர்கள்', 'ab.teamTitle': 'உருவாக்கியவர்கள்', 'ab.ctaTitle': 'ஒரு திட்டத்தைப் பற்றிக் கேள்வி உள்ளதா?',
  'credit.role1': 'யோசனை, AI, பின்தளம் மற்றும் முன்தளம்', 'credit.role2': 'வடிவமைப்பு மற்றும் முன்தளம்',
  'answer.helpfulYes': 'ஆம், உதவியாக இருந்தது', 'answer.helpfulNo': 'உதவவில்லை',
  'shield.yourMessage': 'உங்கள் செய்தி, எச்சரிக்கை அறிகுறிகள் குறிக்கப்பட்டு', 'shield.markTitle': 'எச்சரிக்கை அறிகுறி: நம்பும் முன் சரிபாருங்கள்',
  'shield.signsNote': 'எச்சரிக்கை அறிகுறிகள் என்றால் கவனம் தேவை. அவை மட்டுமே செய்தி தவறு என்று நிரூபிக்காது. மேலே உள்ள முடிவு அதிகாரப்பூர்வ ஆவணங்களிலிருந்து மட்டுமே.',
  'proof.pdfAt': 'அதிகாரப்பூர்வ PDF-ஐத் திற (பக்கம் {page})', 'proof.pdfNote': 'PDF முதல் பக்கத்தில் திறந்தால், பக்கம் {page}-க்குச் செல்லுங்கள். மேலே உள்ள பக்கப் படம் எப்போதும் சரியான பக்கத்தைக் காட்டும்.',
  'answer.checkedBy': 'அச்சுப் பக்கத்துடன் சரிபார்த்தவர்: {names}', 'answer.fromDoc': 'அதிகாரப்பூர்வ ஆவணத்திலிருந்து. பக்கத்தைத் திறந்து நீங்களே சரிபாருங்கள்.',
  'catline.women': 'பெண்களுக்கான திட்டங்கள்', 'catline.farmers': 'விவசாயிகளுக்கான திட்டங்கள்', 'catline.pension': 'ஓய்வூதியத் திட்டங்கள்', 'catline.gas': 'சமையல் எரிவாயுத் திட்டங்கள்',
  'catline.children': 'குழந்தைகளுக்கான திட்டங்கள்', 'catline.health': 'சுகாதாரத் திட்டங்கள்', 'catline.education': 'கல்வித் திட்டங்கள்', 'catline.welfare': 'பிற நலத் திட்டங்கள்',
  'catline.hint': 'ஒரு திட்டத்தைத் தொட்டு, அதன் முக்கியத் தகவல்களையும் அவை வந்த அதிகாரப்பூர்வ ஆவணங்களையும் பாருங்கள்.',
  'guide.title': 'இந்தப் பட்டியலைப் பயன்படுத்துவது எப்படி', 'guide.1': 'ஒரு திட்டத்தைத் தேர்ந்தெடுங்கள்', 'guide.1b': 'தாவல்களைப் பயன்படுத்துங்கள், அல்லது பெயரால் தேடுங்கள்.',
  'guide.2': 'முக்கியத் தகவல்களைப் படியுங்கள்', 'guide.2b': 'தொகையும் யார் விண்ணப்பிக்கலாம் என்பதும், அவை வந்த பக்கத்துடன்.',
  'guide.3': 'அதிகாரப்பூர்வப் பக்கத்தைத் திறங்கள்', 'guide.3b': 'அரசு ஆவணத்தில் நீங்களே சரிபாருங்கள்.',
  'schemes.emptyArt': 'பொருந்தும் திட்டம் இல்லை. வேறு சொல்லில் தேடுங்கள், அல்லது பக்கத்திடம் கேளுங்கள்.',
  'alt.schemesHero': 'ஓவியம்: தமிழ்நாட்டுத் தெருவில் நியாயவிலைக் கடையில் ஒரு பெண்ணும் ஒரு முதியவரும்.',
  'alt.aboutOpening': 'ஓவியம்: வீட்டில் ஒரு தாத்தாவும் பேரனும் சேர்ந்து கைப்பேசியைப் பார்க்கிறார்கள்.',
  'sc.1t': 'சிக்கல்', 'sc.1': 'விதிகள் நீண்ட அதிகாரப்பூர்வ ஆவணங்களில் உள்ளன; கண்டுபிடிப்பது கடினம், படிப்பது இன்னும் கடினம்.',
  'sc.2t': 'பக்கத்திடம் கேளுங்கள்', 'sc.2': 'உங்கள் மொழியில், குரலிலோ தட்டச்சிலோ கேளுங்கள்.',
  'sc.3t': 'ஆதாரத்தைப் பாருங்கள்', 'sc.3': 'பதில் அதிகாரப்பூர்வப் பக்கத்தின் சரியான வரியைக் காட்டும்.',
  'easy.readAloud': 'பதில்களை வாசித்துக் காட்டு', 'composer.stop': 'பேச்சை நிறுத்து', 'chat.latest': 'சமீபத்தியதுக்குச் செல்', 'answer.more': 'மேலும் காட்டு', 'answer.less': 'குறைவாகக் காட்டு',
  'orb.idle': 'பேச உருண்டையைத் தொடுங்கள்', 'orb.listening': 'கேட்கிறேன்… முடித்ததும் உருண்டையைத் தொடுங்கள்', 'orb.busy': 'பதிலைத் தேடுகிறேன்… நிறுத்தத் தொடுங்கள்',
  'orb.speaking': 'பேசுகிறேன்… நிறுத்த உருண்டையைத் தொடுங்கள்', 'orb.error': 'ஏதோ தவறு நடந்தது. மீண்டும் முயல உருண்டையைத் தொடுங்கள்',
  'mic.title': 'பக்கத்துக்கு உங்கள் குரல் இன்னும் கேட்கவில்லை', 'mic.type': 'தட்டச்சு செய்யுங்கள்',
  'mic.body': 'உங்கள் உலாவி ஒலிவாங்கியைத் தடுத்துள்ளது. இணைய முகவரிக்கு அருகிலுள்ள பூட்டு அல்லது (i) குறியைத் தொட்டு, ஒலிவாங்கிக்கு அனுமதி கொடுத்து, பக்கத்தை மீண்டும் ஏற்றுங்கள். கேள்வியைத் தட்டச்சும் செய்யலாம்.',
  'set.bg': 'பின்னணி', 'set.bgMinimal': 'குறைவு', 'set.bgBalanced': 'சீரானது', 'set.bgAmbient': 'அதிகம்',
  'feature.03': 'செய்தியைச் சரிபாருங்கள்', 'feature.03body': 'வாட்ஸ்அப் செய்தியை ஒட்டி, எந்தக் கூற்றுகள் தவறு என்று பாருங்கள்.',
  'tour.start': '60 வினாடி அறிமுகச் சுற்று', 'tour.next': 'அடுத்து', 'tour.back': 'பின்', 'tour.skip': 'சுற்றைத் தவிர்', 'tour.done': 'முடி', 'tour.count': 'படி {n} / {total}',
  'tour.1t': 'உங்கள் மொழியில் கேளுங்கள்', 'tour.1': 'உருண்டையைத் தொட்டு தமிழ், தமிங்கிலம், இந்தி அல்லது ஆங்கிலத்தில் பேசுங்கள். தட்டச்சும் செய்யலாம்.',
  'tour.2t': 'ஆதாரத்துடன் பதில்', 'tour.2': 'ஒவ்வொரு பதிலும் அது வந்த அதிகாரப்பூர்வப் பக்கங்களைக் காட்டும். ஒவ்வொரு வரிக்குப் பின் உள்ள எண் அந்தப் பக்கத்தைத் திறக்கும்.',
  'tour.3t': 'ஊகம் அல்ல, உண்மையான பக்கம்', 'tour.3': 'இது அரசாணையின் பக்கம்; அந்த வரி குறிக்கப்பட்டு, சரிபார்த்தவரின் பெயருடன்.',
  'tour.4t': 'வாட்ஸ்அப் செய்தியைச் சரிபாருங்கள்', 'tour.4': 'செய்தியை ஒட்டுங்கள்; ஒவ்வொரு கூற்றையும் அதிகாரப்பூர்வ ஆவணங்களுடன் சரிபார்த்து மோசடி அறிகுறிகளை எச்சரிக்கும்.',
  'tour.5t': 'நாங்கள் ஏன் உருவாக்கினோம்', 'tour.5': 'ஒரு தாத்தாவுடனான உரையாடலில் பக்கம் தொடங்கியது. அந்தக் கதையை இங்கே படியுங்கள்.',
  'nav.ask': 'கேள்', 'nav.forward': 'சரிபார்', 'shield.paste': '📋 வாட்ஸ்அப்பிலிருந்து ஒட்டு', 'answer.sources': 'ஆதாரங்கள்', 'answer.copy': '📋 நகலெடு', 'answer.copied': 'நகலெடுக்கப்பட்டது', 'proof.pageShort': 'பக்.', 'composer.mic': 'உங்கள் கேள்வியைச் சொல்லுங்கள்',
  'offline.banner': 'பக்கம் சர்வர் இப்போது இயங்கவில்லை. தளத்தைப் பார்க்கலாம்; கீழே உள்ள பதில்கள் மாதிரிகள்.',
  'offline.retry': 'மீண்டும் முயல்க', 'offline.sample': 'மாதிரிப் பதில்: நேரடி சர்வர் இயங்கவில்லை',
  'offline.none': 'நேரடி சர்வர் இயங்கவில்லை; இப்போது இதற்குப் பதில் சொல்ல முடியாது. சிறிது நேரம் கழித்து முயலுங்கள், அல்லது இந்த மாதிரிக் கேள்விகளில் ஒன்றைக் கேளுங்கள்.',
});
Object.assign(MESSAGES['hi-IN'], {
  'a11y.skip': 'सामग्री पर जाएँ', 'footer.privacy': 'निजता', 'footer.code': 'सोर्स कोड', 'footer.contact': 'समस्या बताएँ',
  'about.listen': 'पक्कम से उसका परिचय सुनें', 'about.stop': 'रोकें',
  'st.c1': 'वह बातचीत', 'st.c2': 'वह सवाल', 'st.c3': 'पक्कम का जन्म', 'st.c4': 'नाम', 'st.c5': 'यह किसलिए है',
  'ab.canEyebrow': 'यह क्या करता है', 'ab.howEyebrow': 'अंदर कैसे काम करता है', 'ab.numEyebrow': 'लाइव साइट पर मापा गया',
  'ab.numLink': 'पूरा बेंचमार्क देखें →', 'ab.badgeDocs': '18 आधिकारिक दस्तावेज़',
  'ab.teamEyebrow': 'पक्कम के पीछे के लोग', 'ab.teamTitle': 'बनाने वाले', 'ab.ctaTitle': 'किसी योजना के बारे में सवाल है?',
  'credit.role1': 'विचार, AI, बैकएंड और फ्रंटएंड', 'credit.role2': 'डिज़ाइन और फ्रंटएंड',
  'answer.helpfulYes': 'हाँ, मददगार', 'answer.helpfulNo': 'मददगार नहीं',
  'shield.yourMessage': 'आपका संदेश, चेतावनी के संकेत चिह्नित', 'shield.markTitle': 'चेतावनी का संकेत: भरोसा करने से पहले जाँचें',
  'shield.signsNote': 'चेतावनी के संकेत का मतलब है: सावधान रहें। अकेले ये साबित नहीं करते कि संदेश गलत है। ऊपर का फ़ैसला सिर्फ़ आधिकारिक दस्तावेज़ों से है।',
  'proof.pdfAt': 'आधिकारिक PDF खोलें (पन्ना {page})', 'proof.pdfNote': 'अगर PDF पहले पन्ने पर खुले, तो पन्ना {page} पर जाएँ। ऊपर की पन्ने की तस्वीर हमेशा सही पन्ना दिखाती है।',
  'answer.checkedBy': 'छपे पन्ने से जाँचा: {names}', 'answer.fromDoc': 'आधिकारिक दस्तावेज़ से। पन्ना खोलकर ख़ुद जाँचें।',
  'catline.women': 'महिलाओं के लिए योजनाएँ', 'catline.farmers': 'किसानों के लिए योजनाएँ', 'catline.pension': 'पेंशन योजनाएँ', 'catline.gas': 'रसोई गैस योजनाएँ',
  'catline.children': 'बच्चों के लिए योजनाएँ', 'catline.health': 'स्वास्थ्य योजनाएँ', 'catline.education': 'शिक्षा योजनाएँ', 'catline.welfare': 'अन्य कल्याण योजनाएँ',
  'catline.hint': 'किसी योजना को दबाएँ और उसकी मुख्य जानकारी और वे आधिकारिक दस्तावेज़ देखें जिनसे वह आई है।',
  'guide.title': 'इस सूची का उपयोग कैसे करें', 'guide.1': 'योजना चुनें', 'guide.1b': 'टैब का उपयोग करें, या नाम से खोजें।',
  'guide.2': 'मुख्य जानकारी पढ़ें', 'guide.2b': 'राशि और कौन आवेदन कर सकता है, हर एक उसके पन्ने के साथ।',
  'guide.3': 'आधिकारिक पन्ना खोलें', 'guide.3b': 'सरकारी दस्तावेज़ में ख़ुद जाँचें।',
  'schemes.emptyArt': 'कोई योजना नहीं मिली। कोई दूसरा शब्द आज़माएँ, या पक्कम से पूछें।',
  'alt.schemesHero': 'चित्र: तमिलनाडु की एक गली में राशन दुकान पर एक महिला और एक बुज़ुर्ग।',
  'alt.aboutOpening': 'चित्र: घर पर दादा और पोता साथ में फ़ोन देख रहे हैं।',
  'sc.1t': 'समस्या', 'sc.1': 'नियम लंबे सरकारी काग़ज़ों में हैं; ढूँढना मुश्किल, पढ़ना और भी मुश्किल।',
  'sc.2t': 'पक्कम से पूछें', 'sc.2': 'अपनी भाषा में, बोलकर या लिखकर पूछें।',
  'sc.3t': 'सबूत देखें', 'sc.3': 'जवाब आधिकारिक पन्ने की सही पंक्ति दिखाता है।',
  'easy.readAloud': 'जवाब पढ़कर सुनाएँ', 'composer.stop': 'बोलना रोकें', 'chat.latest': 'नए संदेश पर जाएँ', 'answer.more': 'और दिखाएँ', 'answer.less': 'कम दिखाएँ',
  'orb.idle': 'बोलने के लिए ऑर्ब दबाएँ', 'orb.listening': 'सुन रहा हूँ… बोल लें तो ऑर्ब दबाएँ', 'orb.busy': 'जवाब ढूँढ रहा हूँ… रोकने के लिए दबाएँ',
  'orb.speaking': 'बोल रहा हूँ… रोकने के लिए ऑर्ब दबाएँ', 'orb.error': 'कुछ गड़बड़ हुई। फिर से ऑर्ब दबाएँ',
  'mic.title': 'पक्कम अभी आपकी आवाज़ नहीं सुन पा रहा', 'mic.type': 'टाइप करें',
  'mic.body': 'आपके ब्राउज़र ने माइक्रोफ़ोन रोक दिया है। वेब पते के पास ताले या (i) निशान को दबाएँ, माइक्रोफ़ोन के लिए अनुमति दें, फिर पेज दोबारा खोलें। आप सवाल टाइप भी कर सकते हैं।',
  'set.bg': 'पृष्ठभूमि', 'set.bgMinimal': 'कम', 'set.bgBalanced': 'संतुलित', 'set.bgAmbient': 'ज़्यादा',
  'feature.03': 'फ़ॉरवर्ड जाँचें', 'feature.03body': 'व्हाट्सऐप संदेश चिपकाएँ और देखें कौन-से दावे गलत हैं।',
  'tour.start': '60 सेकंड का परिचय देखें', 'tour.next': 'आगे', 'tour.back': 'पीछे', 'tour.skip': 'परिचय छोड़ें', 'tour.done': 'पूरा', 'tour.count': 'चरण {n} / {total}',
  'tour.1t': 'अपनी भाषा में पूछें', 'tour.1': 'ऑर्ब दबाएँ और तमिल, तमिंग्लिश, हिंदी या अंग्रेज़ी में बोलें। टाइप भी कर सकते हैं।',
  'tour.2t': 'स्रोत के साथ जवाब', 'tour.2': 'हर जवाब उन आधिकारिक पन्नों को दिखाता है जिनसे वह आया। हर पंक्ति के बाद का छोटा नंबर वही पन्ना खोलता है।',
  'tour.3t': 'असली पन्ना, अंदाज़ा नहीं', 'tour.3': 'यह सरकारी आदेश का पन्ना है, पंक्ति हाइलाइट की हुई और जाँचने वाले व्यक्ति का नाम साथ में।',
  'tour.4t': 'व्हाट्सऐप फ़ॉरवर्ड जाँचें', 'tour.4': 'फ़ॉरवर्ड चिपकाएँ; पक्कम हर दावे को आधिकारिक दस्तावेज़ों से जाँचता है और धोखाधड़ी के संकेत बताता है।',
  'tour.5t': 'हमने इसे क्यों बनाया', 'tour.5': 'पक्कम की शुरुआत एक दादाजी से बातचीत से हुई। कहानी यहाँ पढ़ें।',
  'nav.ask': 'पूछें', 'nav.forward': 'जाँचें', 'shield.paste': '📋 व्हाट्सऐप से चिपकाएँ', 'answer.sources': 'स्रोत', 'answer.copy': '📋 कॉपी करें', 'answer.copied': 'कॉपी हो गया', 'proof.pageShort': 'पृ.', 'composer.mic': 'अपना सवाल बोलें',
  'offline.banner': 'पक्कम का सर्वर अभी बंद है। आप साइट देख सकते हैं; नीचे के जवाब नमूने हैं।',
  'offline.retry': 'फिर कोशिश करें', 'offline.sample': 'नमूना जवाब: लाइव सर्वर बंद है',
  'offline.none': 'लाइव सर्वर बंद है, इसलिए अभी इसका जवाब नहीं दे सकता। थोड़ी देर बाद कोशिश करें, या इनमें से कोई नमूना सवाल पूछें।',
});

// Round 7: stronger, honest copy (judge-ready), plus the Shield panel, story player and tabs.
Object.assign(MESSAGES['en-IN'], {
  'pipe.title': 'Under the hood', 'pipe.1t': 'Voice or text', 'pipe.1': 'Gnani Prisma turns speech into text, even mixed Tamil and English.', 'pipe.2t': 'Search', 'pipe.2': 'Hybrid search (BGE-M3) across 18 official documents, never the open internet.', 'pipe.3t': 'Rerank', 'pipe.3': 'A reranker keeps only the pages that really answer the question.', 'pipe.4t': 'Write', 'pipe.4': 'The answer is written only from those pages and the signed fact cards.', 'pipe.5t': 'Check', 'pipe.5': 'Every sentence must cite a page, and every number must be on that page.', 'pipe.6t': 'Show and speak', 'pipe.6': 'The page opens with the line highlighted; Gnani Timbre reads it aloud.', 'pipe.refuse': "If the pages don't answer it, or any check fails, Pakkam says it is not in the documents. It never guesses.", 'tm.title': 'How we tested', 'tm.1': '194 questions were sent to the live site one at a time, as a visitor would: 154 covered by the documents and 40 deliberately outside them.', 'tm.2': 'A covered answer counts as right only if it cites a page that really holds it: 133 of the 136 answered. The other 18 covered questions were declined rather than guessed.', 'tm.3': 'An out-of-scope question counts as right only if Pakkam refuses: 39 of 40.', 'tm.4': 'The one miss: a Hindi question about the date of the next PM-KISAN instalment was answered instead of refused. It is listed in the report.',
  'slogan.a': 'Speak.', 'slogan.b': 'Hear.', 'slogan.c': 'See the proof.', 'slogan.try': 'Try asking', 'slogan.ask': 'Ask this question',
  'schemes.docCount1': 'official document', 'schemes.noAmount': 'Details on the official page',
  'home.title1': 'Ask in your language.', 'home.title2': 'Get the answer with its proof.',
  'home.subtitle': "Speak Tamil, Hindi or English. Pakkam reads the official scheme documents and opens the exact page. If the documents don't say it, Pakkam says so.",
  'home.proof1': 'Tested on 194 real questions', 'home.proof2': '98% of answers cite the correct page', 'home.proof3': '39 of 40 out-of-scope questions honestly refused',
  'home.proofLink': 'See the full test report',
  'feature.01': 'Proof on every answer', 'feature.01body': 'The exact page of the official document, the line highlighted.',
  'feature.02': 'Just speak', 'feature.02body': 'Tamil, Tanglish, Hindi or English. No typing needed.',
  'feature.03': 'Stop the fake forward', 'feature.03body': 'Paste a WhatsApp message and see which claims are false.',
  'home.ask': 'Ask Pakkam', 'home.shield': 'Check a WhatsApp forward',
  'assistant.welcome': 'Vanakkam! Ask me about a welfare scheme, by voice or text. I answer only from official documents, and I show you the page.',
  'schemes.eyebrow': 'OFFICIAL SOURCES', 'schemes.title': 'Every scheme, straight from the source',
  'schemes.intro': 'Key facts checked against the printed official page, with the page one tap away.',
  'settings.title': 'Make Pakkam yours', 'settings.intro': 'Language, voice, text size and calm mode, set the way you like. Saved only on this device.',
  'ab.ctaTitle': 'Have a question about a scheme? Ask Pakkam, and see the proof.',
  'home.documentTitle': 'Pakkam: ask in your language, get the answer with its proof',
  'tab.does': 'What Pakkam does', 'tab.how': 'How it answers', 'tab.tested': 'Tested, honestly', 'tab.team': 'Made by', 'footer.tag': 'Your language. Your schemes. Your access. One page at a time.',
  'hc.title': 'How Pakkam checks a forward',
  'hc.1t': 'Paste the forward', 'hc.1': 'Copy the WhatsApp message and paste it here.',
  'hc.2t': 'Every claim is checked', 'hc.2': 'Each claim is matched against the official order, page by page.',
  'hc.3t': 'Verdict and warning signs', 'hc.3': 'True, false or not in the documents, plus any scam tricks.',
  'hc.good': 'True', 'hc.bad': 'False', 'hc.neutral': 'Not in the documents', 'hc.warn': 'Warning signs', 'hc.note': 'Warning signs alone never prove a message false. The verdict comes only from the official documents.', 'hc.result': 'This check', 'pill.lang': 'Your language', 'pill.rights': 'Your rights', 'pill.access': 'Your access',
  'pl.prev': 'Previous chapter', 'pl.next': 'Next chapter', 'pl.play': 'Play the story', 'pl.pause': 'Pause the story', 'pl.chapter': 'Chapter {n} of {total}',
});
Object.assign(MESSAGES['ta-IN'], {
  'pipe.title': 'உள்ளே நடப்பது', 'pipe.1t': 'குரல் அல்லது தட்டச்சு', 'pipe.1': 'ஞானி ப்ரிஸ்மா பேச்சை எழுத்தாக மாற்றும்; தமிழ்-ஆங்கிலக் கலப்பையும் புரிந்துகொள்ளும்.', 'pipe.2t': 'தேடல்', 'pipe.2': '18 அதிகாரப்பூர்வ ஆவணங்களில் மட்டும் கலப்புத் தேடல் (BGE-M3); திறந்த இணையத்தில் இல்லை.', 'pipe.3t': 'தரவரிசை', 'pipe.3': 'கேள்விக்கு உண்மையில் பதில் உள்ள பக்கங்களை மட்டும் ஒரு மறுதரவரிசை மாதிரி வைத்துக்கொள்ளும்.', 'pipe.4t': 'எழுதுதல்', 'pipe.4': 'அந்தப் பக்கங்களிலிருந்தும் சரிபார்த்த தகவல் அட்டைகளிலிருந்தும் மட்டுமே பதில் எழுதப்படும்.', 'pipe.5t': 'சரிபார்ப்பு', 'pipe.5': 'ஒவ்வொரு வாக்கியமும் ஒரு பக்கத்தைக் காட்ட வேண்டும்; ஒவ்வொரு எண்ணும் அந்தப் பக்கத்தில் இருக்க வேண்டும்.', 'pipe.6t': 'காட்டுதல், பேசுதல்', 'pipe.6': 'அந்த வரி குறிக்கப்பட்ட பக்கம் திறக்கும்; ஞானி டிம்ப்ரே அதை வாசிக்கும்.', 'pipe.refuse': 'பக்கங்களில் பதில் இல்லையென்றாலோ, ஏதாவது சரிபார்ப்பு தோற்றாலோ, ஆவணங்களில் இல்லை என்று பக்கம் சொல்லும். ஊகிக்காது.', 'tm.title': 'நாங்கள் எப்படிச் சோதித்தோம்', 'tm.1': '194 கேள்விகள் ஒரு பார்வையாளர் போல ஒவ்வொன்றாக நேரடித் தளத்துக்கு அனுப்பப்பட்டன: 154 ஆவணங்களில் உள்ளவை, 40 வேண்டுமென்றே வெளியே உள்ளவை.', 'tm.2': 'உண்மையில் அந்தத் தகவல் உள்ள பக்கத்தைக் காட்டினால் மட்டுமே பதில் சரி: பதிலளித்த 136-ல் 133. மீதமுள்ள 18 கேள்விகளுக்கு ஊகிக்காமல் மறுத்தது.', 'tm.3': 'வரம்புக்கு வெளியே உள்ள கேள்விக்கு மறுத்தால் மட்டுமே சரி: 40-ல் 39.', 'tm.4': 'ஒரே தவறு: அடுத்த பிஎம் கிசான் தவணை எப்போது என்ற இந்திக் கேள்விக்கு மறுக்காமல் பதில் சொன்னது. அது அறிக்கையில் உள்ளது.',
  'slogan.a': 'பேசுங்கள்.', 'slogan.b': 'கேளுங்கள்.', 'slogan.c': 'ஆதாரத்தைப் பாருங்கள்.', 'slogan.try': 'இப்படிக் கேளுங்கள்', 'slogan.ask': 'இந்தக் கேள்வியைக் கேளுங்கள்',
  'schemes.docCount1': 'அதிகாரப்பூர்வ ஆவணம்', 'schemes.noAmount': 'விவரங்கள் அதிகாரப்பூர்வப் பக்கத்தில்',
  'home.title1': 'உங்கள் மொழியில் கேளுங்கள்.', 'home.title2': 'ஆதாரத்துடன் பதில் பெறுங்கள்.',
  'home.subtitle': 'தமிழ், இந்தி அல்லது ஆங்கிலத்தில் பேசுங்கள். பக்கம் அதிகாரப்பூர்வத் திட்ட ஆவணங்களைப் படித்து, சரியான பக்கத்தைத் திறந்து காட்டும். ஆவணங்களில் இல்லையென்றால், அதை நேர்மையாகச் சொல்லும்.',
  'home.proof1': '194 உண்மையான கேள்விகளில் சோதிக்கப்பட்டது', 'home.proof2': '98% பதில்கள் சரியான பக்கத்தைக் காட்டுகின்றன', 'home.proof3': 'வரம்புக்கு வெளியே உள்ள 40-ல் 39 கேள்விகளுக்கு நேர்மையான மறுப்பு',
  'home.proofLink': 'முழு சோதனை அறிக்கையைப் பாருங்கள்',
  'feature.01': 'ஒவ்வொரு பதிலுக்கும் ஆதாரம்', 'feature.01body': 'அதிகாரப்பூர்வ ஆவணத்தின் சரியான பக்கம், அந்த வரி குறிக்கப்பட்டு.',
  'feature.02': 'பேசினால் போதும்', 'feature.02body': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலம். தட்டச்சு தேவையில்லை.',
  'feature.03': 'போலிச் செய்தியை நிறுத்துங்கள்', 'feature.03body': 'வாட்ஸ்அப் செய்தியை ஒட்டி, எந்தக் கூற்றுகள் தவறு என்று பாருங்கள்.',
  'home.ask': 'பக்கத்திடம் கேளுங்கள்', 'home.shield': 'வாட்ஸ்அப் செய்தியைச் சரிபாருங்கள்',
  'assistant.welcome': 'வணக்கம்! ஒரு நலத்திட்டத்தைப் பற்றி குரலிலோ தட்டச்சிலோ கேளுங்கள். அதிகாரப்பூர்வ ஆவணங்களிலிருந்து மட்டுமே பதில் சொல்லி, அந்தப் பக்கத்தையும் காட்டுவேன்.',
  'schemes.eyebrow': 'அதிகாரப்பூர்வ ஆதாரங்கள்', 'schemes.title': 'ஒவ்வொரு திட்டமும், மூல ஆவணத்திலிருந்தே',
  'schemes.intro': 'அச்சிட்ட அதிகாரப்பூர்வப் பக்கத்துடன் சரிபார்த்த முக்கியத் தகவல்கள்; பக்கம் ஒரு தொடுதலில்.',
  'settings.title': 'பக்கத்தை உங்களுக்கு ஏற்றபடி அமையுங்கள்', 'settings.intro': 'மொழி, குரல், எழுத்து அளவு, அமைதி முறை, உங்கள் விருப்பப்படி. இந்தச் சாதனத்தில் மட்டுமே சேமிக்கப்படும்.',
  'ab.ctaTitle': 'ஒரு திட்டத்தைப் பற்றிக் கேள்வியா? பக்கத்திடம் கேட்டு, ஆதாரத்தைப் பாருங்கள்.',
  'home.documentTitle': 'பக்கம்: உங்கள் மொழியில் கேளுங்கள், ஆதாரத்துடன் பதில் பெறுங்கள்',
  'tab.does': 'பக்கம் என்ன செய்யும்', 'tab.how': 'எப்படிப் பதில் சொல்கிறது', 'tab.tested': 'நேர்மையான சோதனை', 'tab.team': 'உருவாக்கியவர்கள்', 'footer.tag': 'உங்கள் மொழி. உங்கள் திட்டங்கள். உங்கள் அணுகல். ஒரு நேரத்தில் ஒரு பக்கம்.',
  'hc.title': 'பக்கம் ஒரு செய்தியை எப்படிச் சரிபார்க்கிறது',
  'hc.1t': 'செய்தியை ஒட்டுங்கள்', 'hc.1': 'வாட்ஸ்அப் செய்தியை நகலெடுத்து இங்கே ஒட்டுங்கள்.',
  'hc.2t': 'ஒவ்வொரு கூற்றும் சரிபார்க்கப்படும்', 'hc.2': 'ஒவ்வொரு கூற்றும் அதிகாரப்பூர்வ ஆணையுடன் பக்கம் பக்கமாக ஒப்பிடப்படும்.',
  'hc.3t': 'முடிவும் எச்சரிக்கை அறிகுறிகளும்', 'hc.3': 'உண்மை, தவறு, அல்லது ஆவணங்களில் இல்லை; கூடவே மோசடி அறிகுறிகள்.',
  'hc.good': 'உண்மை', 'hc.bad': 'தவறு', 'hc.neutral': 'ஆவணங்களில் இல்லை', 'hc.warn': 'எச்சரிக்கை அறிகுறிகள்', 'hc.note': 'எச்சரிக்கை அறிகுறிகள் மட்டுமே ஒரு செய்தியைத் தவறு என்று நிரூபிக்காது. முடிவு அதிகாரப்பூர்வ ஆவணங்களிலிருந்து மட்டுமே.', 'hc.result': 'இந்தச் சரிபார்ப்பு', 'pill.lang': 'உங்கள் மொழி', 'pill.rights': 'உங்கள் உரிமைகள்', 'pill.access': 'உங்கள் அணுகல்',
  'pl.prev': 'முந்தைய அத்தியாயம்', 'pl.next': 'அடுத்த அத்தியாயம்', 'pl.play': 'கதையை இயக்கு', 'pl.pause': 'கதையை இடைநிறுத்து', 'pl.chapter': 'அத்தியாயம் {n} / {total}',
});
Object.assign(MESSAGES['hi-IN'], {
  'pipe.title': 'अंदर क्या होता है', 'pipe.1t': 'आवाज़ या टेक्स्ट', 'pipe.1': 'ज्ञानी प्रिज़्मा बोली को टेक्स्ट में बदलता है, तमिल-अंग्रेज़ी मिली भाषा भी।', 'pipe.2t': 'खोज', 'pipe.2': '18 आधिकारिक दस्तावेज़ों में हाइब्रिड खोज (BGE-M3), खुले इंटरनेट पर कभी नहीं।', 'pipe.3t': 'छँटाई', 'pipe.3': 'एक रीरैंकर सिर्फ़ वे पन्ने रखता है जिनमें सच में जवाब है।', 'pipe.4t': 'लिखना', 'pipe.4': 'जवाब सिर्फ़ उन्हीं पन्नों और जाँचे गए तथ्य कार्डों से लिखा जाता है।', 'pipe.5t': 'जाँच', 'pipe.5': 'हर वाक्य को एक पन्ना बताना होता है, और हर संख्या उसी पन्ने पर होनी चाहिए।', 'pipe.6t': 'दिखाना और बोलना', 'pipe.6': 'पन्ना पंक्ति हाइलाइट करके खुलता है; ज्ञानी टिम्बर उसे पढ़कर सुनाता है।', 'pipe.refuse': 'अगर पन्नों में जवाब नहीं है, या कोई जाँच विफल होती है, तो पक्कम कहता है कि यह दस्तावेज़ों में नहीं है। वह अंदाज़ा नहीं लगाता।', 'tm.title': 'हमने कैसे परखा', 'tm.1': '194 सवाल एक-एक करके लाइव साइट पर भेजे गए, जैसे कोई आगंतुक भेजे: 154 दस्तावेज़ों के दायरे में और 40 जानबूझकर दायरे से बाहर।', 'tm.2': 'जवाब तभी सही माना गया जब वह ऐसा पन्ना बताए जिसमें बात सच में लिखी हो: दिए गए 136 में से 133। बाकी 18 पर अंदाज़ा लगाने के बजाय मना किया।', 'tm.3': 'दायरे से बाहर का सवाल तभी सही जब पक्कम मना करे: 40 में से 39।', 'tm.4': 'एक चूक: अगली पीएम-किसान किस्त की तारीख वाले हिंदी सवाल का जवाब दे दिया गया, जबकि मना करना था। यह रिपोर्ट में दर्ज है।',
  'slogan.a': 'बोलें।', 'slogan.b': 'सुनें।', 'slogan.c': 'सबूत देखें।', 'slogan.try': 'ऐसे पूछें', 'slogan.ask': 'यह सवाल पूछें',
  'schemes.docCount1': 'आधिकारिक दस्तावेज़', 'schemes.noAmount': 'विवरण आधिकारिक पन्ने पर',
  'home.title1': 'अपनी भाषा में पूछें।', 'home.title2': 'सबूत के साथ जवाब पाएँ।',
  'home.subtitle': 'तमिल, हिंदी या अंग्रेज़ी में बोलें। पक्कम आधिकारिक योजना दस्तावेज़ पढ़कर सही पन्ना खोलकर दिखाता है। अगर दस्तावेज़ों में बात नहीं है, तो पक्कम साफ़ बता देता है।',
  'home.proof1': '194 असली सवालों पर परखा गया', 'home.proof2': '98% जवाब सही पन्ना दिखाते हैं', 'home.proof3': 'दायरे से बाहर के 40 में से 39 सवालों पर ईमानदारी से मना किया',
  'home.proofLink': 'पूरी परीक्षण रिपोर्ट देखें',
  'feature.01': 'हर जवाब के साथ सबूत', 'feature.01body': 'आधिकारिक दस्तावेज़ का सही पन्ना, पंक्ति हाइलाइट की हुई।',
  'feature.02': 'बस बोलिए', 'feature.02body': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी। टाइप करने की ज़रूरत नहीं।',
  'feature.03': 'झूठे फ़ॉरवर्ड को रोकें', 'feature.03body': 'व्हाट्सऐप संदेश चिपकाएँ और देखें कौन-से दावे गलत हैं।',
  'home.ask': 'पक्कम से पूछें', 'home.shield': 'व्हाट्सऐप फ़ॉरवर्ड जाँचें',
  'assistant.welcome': 'नमस्ते! किसी कल्याण योजना के बारे में बोलकर या लिखकर पूछें। मैं सिर्फ़ आधिकारिक दस्तावेज़ों से जवाब देता हूँ, और पन्ना भी दिखाता हूँ।',
  'schemes.eyebrow': 'आधिकारिक स्रोत', 'schemes.title': 'हर योजना, सीधे स्रोत से',
  'schemes.intro': 'छपे आधिकारिक पन्ने से जाँची गई मुख्य जानकारी, पन्ना बस एक टैप दूर।',
  'settings.title': 'पक्कम को अपने हिसाब से बनाएँ', 'settings.intro': 'भाषा, आवाज़, अक्षर का आकार और शांत मोड, जैसा आपको पसंद हो। सिर्फ़ इसी डिवाइस पर सहेजा जाता है।',
  'ab.ctaTitle': 'किसी योजना के बारे में सवाल है? पक्कम से पूछें, और सबूत देखें।',
  'home.documentTitle': 'पक्कम: अपनी भाषा में पूछें, सबूत के साथ जवाब पाएँ',
  'tab.does': 'पक्कम क्या करता है', 'tab.how': 'जवाब कैसे देता है', 'tab.tested': 'ईमानदार परीक्षण', 'tab.team': 'बनाने वाले', 'footer.tag': 'आपकी भाषा। आपकी योजनाएँ। आपकी पहुँच। एक समय में एक पन्ना।',
  'hc.title': 'पक्कम फ़ॉरवर्ड को कैसे जाँचता है',
  'hc.1t': 'फ़ॉरवर्ड चिपकाएँ', 'hc.1': 'व्हाट्सऐप संदेश कॉपी करके यहाँ चिपकाएँ।',
  'hc.2t': 'हर दावे की जाँच', 'hc.2': 'हर दावे को आधिकारिक आदेश से, पन्ने-पन्ने मिलाया जाता है।',
  'hc.3t': 'फ़ैसला और चेतावनी के संकेत', 'hc.3': 'सच, गलत, या दस्तावेज़ों में नहीं; साथ में धोखाधड़ी के संकेत।',
  'hc.good': 'सच', 'hc.bad': 'गलत', 'hc.neutral': 'दस्तावेज़ों में नहीं', 'hc.warn': 'चेतावनी के संकेत', 'hc.note': 'सिर्फ़ चेतावनी के संकेत किसी संदेश को गलत साबित नहीं करते। फ़ैसला सिर्फ़ आधिकारिक दस्तावेज़ों से आता है।', 'hc.result': 'यह जाँच', 'pill.lang': 'आपकी भाषा', 'pill.rights': 'आपके अधिकार', 'pill.access': 'आपकी पहुँच',
  'pl.prev': 'पिछला अध्याय', 'pl.next': 'अगला अध्याय', 'pl.play': 'कहानी चलाएँ', 'pl.pause': 'कहानी रोकें', 'pl.chapter': 'अध्याय {n} / {total}',
});

// Rumour Shield and appeal texts (from the earlier chat page, web-backup/assets/chat.js).
const SHIELD = {
  'en-IN': {
    eyebrow: 'RUMOUR SHIELD', title: 'Is this WhatsApp forward true?', intro: 'Paste it. Pakkam checks every claim against the official orders and points out the scam tricks.',
    placeholder: 'Paste the WhatsApp message here', example: 'Try an example', check: 'Check it',
    checking: 'Checking each claim against the government orders…', failed: 'Pakkam could not check this now. Try again in a minute.',
    overall: { wrong: '❌ This forward is wrong', partly_wrong: '⚠️ Partly wrong', looks_right: '✅ Matches the official documents',
      not_in_documents: '⚠️ Not in any official document. Be careful.', no_claims: 'No scheme claim found in this message.' },
    verdict: { supported: '✅ True', contradicted: '❌ Wrong', not_in_documents: '⚠️ Not in the documents' },
    signs: { unofficial_link: 'The link is not a recognised official government website. Do not open it or enter your details.',
      official_link: 'The link is a recognised official website. That tells you who runs the site; it does not by itself make the message true.',
      otp: 'It asks for an OTP. Government schemes never ask for your OTP. Never share it.',
      payment: 'It asks for money. Applying for these schemes does not need payment to anyone in a message.',
      personal_data: 'It asks for Aadhaar or bank details. Do not send them to unknown people.',
      insecure_link: 'This is a government website, but the link is not secure (http, not https). Type the address yourself instead.',
      urgency: '"Today only" pressure is a common trick. Check first.' },
    warnings: 'Warning signs', share: '📤 Send the correction on WhatsApp',
    correction: 'Fact-check by Pakkam (from the official government documents):',
  },
  'ta-IN': {
    eyebrow: 'வதந்தி கவசம்', title: 'இந்த வாட்ஸ்அப் செய்தி உண்மையா?', intro: 'ஒட்டினால் போதும். ஒவ்வொரு கூற்றையும் அதிகாரப்பூர்வ ஆணைகளுடன் பக்கம் சரிபார்த்து, மோசடி தந்திரங்களைச் சுட்டிக்காட்டும்.',
    placeholder: 'வாட்ஸ்அப் செய்தியை இங்கே ஒட்டுங்கள்', example: 'ஒரு எடுத்துக்காட்டு', check: 'சரிபார்',
    checking: 'ஒவ்வொரு கூற்றும் அரசாணையுடன் சரிபார்க்கப்படுகிறது…', failed: 'இப்போது சரிபார்க்க முடியவில்லை. ஒரு நிமிடம் கழித்து முயற்சிக்கவும்.',
    overall: { wrong: '❌ இந்தச் செய்தி தவறு', partly_wrong: '⚠️ ஓரளவு தவறு', looks_right: '✅ அதிகாரப்பூர்வ ஆவணங்களுடன் பொருந்துகிறது',
      not_in_documents: '⚠️ எந்த அதிகாரப்பூர்வ ஆவணத்திலும் இல்லை. கவனம்.', no_claims: 'இந்தச் செய்தியில் திட்டம் பற்றிய கூற்று இல்லை.' },
    verdict: { supported: '✅ உண்மை', contradicted: '❌ தவறு', not_in_documents: '⚠️ ஆவணங்களில் இல்லை' },
    signs: { unofficial_link: 'இந்த இணைப்பு அங்கீகரிக்கப்பட்ட அதிகாரப்பூர்வ அரசு இணையதளம் அல்ல. திறக்க வேண்டாம், விவரங்களைக் கொடுக்க வேண்டாம்.',
      official_link: 'இந்த இணைப்பு அங்கீகரிக்கப்பட்ட அதிகாரப்பூர்வ இணையதளம். தளத்தை நடத்துவது யார் என்பதை இது காட்டும்; அதனால் மட்டும் செய்தி உண்மை ஆகாது.',
      otp: 'OTP கேட்கிறது. அரசுத் திட்டங்கள் ஒருபோதும் OTP கேட்பதில்லை. பகிர வேண்டாம்.',
      payment: 'பணம் கேட்கிறது. இந்தத் திட்டங்களுக்கு செய்தி மூலம் யாருக்கும் பணம் கட்டத் தேவையில்லை.',
      personal_data: 'ஆதார் அல்லது வங்கி விவரங்களைக் கேட்கிறது. தெரியாதவர்களுக்கு அனுப்ப வேண்டாம்.',
      insecure_link: 'இது அரசு இணையதளம், ஆனால் இணைப்பு பாதுகாப்பானது அல்ல (https இல்லை). முகவரியை நீங்களே தட்டச்சு செய்யுங்கள்.',
      urgency: '"இன்று மட்டும்" என்ற அவசரம் ஒரு வழக்கமான ஏமாற்று. முதலில் சரிபாருங்கள்.' },
    warnings: 'எச்சரிக்கை அறிகுறிகள்', share: '📤 திருத்தத்தை வாட்ஸ்அப்பில் அனுப்பு',
    correction: 'பக்கம் சரிபார்ப்பு (அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து):',
  },
  'hi-IN': {
    eyebrow: 'अफ़वाह कवच', title: 'क्या यह व्हाट्सऐप संदेश सच है?', intro: 'बस चिपकाएँ। पक्कम हर दावे को आधिकारिक आदेशों से जाँचता है और धोखाधड़ी की चालें पकड़ता है।',
    placeholder: 'व्हाट्सऐप संदेश यहाँ चिपकाएँ', example: 'एक उदाहरण', check: 'जाँचें',
    checking: 'हर दावे को सरकारी आदेश से जाँचा जा रहा है…', failed: 'अभी जाँच नहीं हो सकी। एक मिनट बाद कोशिश करें।',
    overall: { wrong: '❌ यह संदेश गलत है', partly_wrong: '⚠️ आंशिक रूप से गलत', looks_right: '✅ आधिकारिक दस्तावेज़ों से मेल खाता है',
      not_in_documents: '⚠️ किसी आधिकारिक दस्तावेज़ में नहीं। सावधान रहें।', no_claims: 'इस संदेश में योजना का कोई दावा नहीं मिला।' },
    verdict: { supported: '✅ सही', contradicted: '❌ गलत', not_in_documents: '⚠️ दस्तावेज़ों में नहीं' },
    signs: { unofficial_link: 'यह लिंक किसी मान्य आधिकारिक सरकारी वेबसाइट का नहीं है। इसे न खोलें।',
      official_link: 'यह लिंक मान्य आधिकारिक वेबसाइट का है। इससे पता चलता है कि साइट कौन चलाता है; सिर्फ़ इससे संदेश सच नहीं हो जाता।',
      otp: 'यह OTP माँगता है। सरकारी योजनाएँ कभी OTP नहीं माँगतीं। इसे साझा न करें।',
      payment: 'यह पैसे माँगता है। इन योजनाओं के लिए संदेश से किसी को भुगतान नहीं करना होता।',
      personal_data: 'यह आधार या बैंक विवरण माँगता है। अनजान लोगों को न भेजें।',
      insecure_link: 'यह सरकारी वेबसाइट है, पर लिंक सुरक्षित नहीं है (https नहीं)। पता ख़ुद टाइप करें।',
      urgency: '"आज ही" का दबाव एक आम चाल है। पहले जाँचें।' },
    warnings: 'चेतावनी के संकेत', share: '📤 सुधार व्हाट्सऐप पर भेजें',
    correction: 'पक्कम द्वारा जाँच (आधिकारिक सरकारी दस्तावेज़ों से):',
  },
};
const SHIELD_EXAMPLE = 'Magalir Urimai increased to Rs.2,000 a month! Register at bit.ly/kmut2000 today only and share OTP to confirm.';

const APPEAL = {
  'en-IN': { title: 'Application rejected?', scheme: 'Scheme', reason: 'Reason given in the rejection message',
    situation: 'Your situation (optional), e.g. "we only have a two-wheeler"', go: 'Find the rule', working: 'Finding the rule in the government order…',
    rule: 'What the rule says', note: 'Draft appeal note (edit before you use it)', copy: '📋 Copy', copied: 'Copied',
    noRule: 'The official documents in Pakkam do not cover this reason. You can ask an officer.',
    disclaimer: 'This is a draft to help you, not legal advice. Check every detail and ask at your e-Sevai centre how and by when to submit an appeal.',
    ask: (scheme, reason) => `Under ${scheme}, is this a reason not to be eligible: ${reason}? What does the rule say?`,
    template: (v) => `To\nThe officer concerned, ${v.scheme}\n\nSubject: Request to reconsider my application\n\nMy application under ${v.scheme} (Application No: __________) was rejected for this reason: "${v.reason}".\n${v.situation ? `My situation: ${v.situation}\n` : ''}\nThe government rule says (${v.document}, page ${v.page}):\n"${v.rule}"\n\nI request you to reconsider my application in the light of this rule.\n\nName: __________        Family card No: __________\nPhone: __________       Date: __________\nSignature: __________` },
  'ta-IN': { title: 'விண்ணப்பம் நிராகரிக்கப்பட்டதா?', scheme: 'திட்டம்', reason: 'நிராகரிப்புச் செய்தியில் சொன்ன காரணம்',
    situation: 'உங்கள் நிலைமை (விருப்பம்), எ.கா. "எங்களிடம் இரு சக்கர வாகனம் மட்டுமே உள்ளது"', go: 'விதியைக் கண்டுபிடி', working: 'அரசாணையில் விதி தேடப்படுகிறது…',
    rule: 'விதி சொல்வது', note: 'மேல்முறையீட்டுக் கடித வரைவு (பயன்படுத்தும் முன் திருத்துங்கள்)', copy: '📋 நகலெடு', copied: 'நகலெடுக்கப்பட்டது',
    noRule: 'இந்தக் காரணம் பக்கத்தில் உள்ள அதிகாரப்பூர்வ ஆவணங்களில் இல்லை. அதிகாரியிடம் கேட்கலாம்.',
    disclaimer: 'இது உதவிக்கான வரைவு மட்டுமே, சட்ட ஆலோசனை அல்ல. ஒவ்வொரு விவரத்தையும் சரிபார்த்து, மேல்முறையீட்டை எப்படி, எப்போதுக்குள் தர வேண்டும் என்று இ-சேவை மையத்தில் கேளுங்கள்.',
    ask: (scheme, reason) => `${scheme} திட்டத்தில், இது தகுதியின்மைக்கான காரணமா: ${reason}? விதி என்ன சொல்கிறது?`,
    template: (v) => `பெறுநர்\nசம்பந்தப்பட்ட அலுவலர், ${v.scheme}\n\nபொருள்: எனது விண்ணப்பத்தை மறுபரிசீலனை செய்யக் கோருதல்\n\n${v.scheme} திட்டத்தின் கீழ் எனது விண்ணப்பம் (விண்ணப்ப எண்: __________) "${v.reason}" என்ற காரணத்தால் நிராகரிக்கப்பட்டது.\n${v.situation ? `எனது நிலைமை: ${v.situation}\n` : ''}\nஅரசு விதி (${v.document}, பக்கம் ${v.page}) கூறுவது:\n"${v.rule}"\n\nஇந்த விதியின் அடிப்படையில் எனது விண்ணப்பத்தை மறுபரிசீலனை செய்யுமாறு கேட்டுக்கொள்கிறேன்.\n\nபெயர்: __________        குடும்ப அட்டை எண்: __________\nதொலைபேசி: __________       தேதி: __________\nகையொப்பம்: __________` },
};
APPEAL['hi-IN'] = APPEAL['en-IN'];

const SPOKEN_SOURCE = {
  en: (c) => `Source: ${c.document}, page ${c.page_start}.`,
  ta: (c) => `ஆதாரம்: ${c.document}, பக்கம் ${c.page_start}.`,
  'ta-Latn': (c) => `ஆதாரம்: ${c.document}, பக்கம் ${c.page_start}.`,
  hi: (c) => `स्रोत: ${c.document}, पेज ${c.page_start}.`,
};
// Said the moment a voice question is sent, so there is no silence while Pakkam reads.
const FILLER = {
  ta: 'ஒரு நிமிடம், அரசாணையில் பார்க்கிறேன்.',
  hi: 'एक पल, सरकारी आदेश में देख रहा हूँ।',
  en: 'One moment, checking the government order.',
};

/* ==========================================================================
   3. TALKING TO THE PAKKAM BACKEND (FastAPI)
   ========================================================================== */
const ASK_TIMEOUT_MS = 120000;
const SLOW_MS = 20000;
const MAX_VOICE_SECONDS = 30;
const VOICE_LANG = { 'en-IN': 'en', 'ta-IN': 'ta', 'hi-IN': 'hi' };
const SPEECH_LANG = { 'en-IN': 'en', 'ta-IN': 'ta', 'hi-IN': 'hi' };
const CITATION_MARKER = /\s*\[\d+(?:,\s*\d+)*\]/g;
const SECTION_ORDER = ['amount', 'eligibility', 'documents', 'apply', 'other'];
const fill = (text, values) => text.replace(/\{(\w+)\}/g, (_, key) => (values[key] ?? ''));
const shieldWords = () => SHIELD[state.language] || SHIELD['en-IN'];

class ApiError extends Error {
  constructor(status, detail) { super(detail || `HTTP ${status}`); this.status = status; }
}

async function api(path, options = {}, timeoutMs = ASK_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, { ...options, signal: controller.signal });
    if (!res.ok) {
      let detail = '';
      try { detail = (await res.json()).detail; } catch (_) { /* not JSON */ }
      throw new ApiError(res.status, typeof detail === 'string' ? detail : '');
    }
    return res;
  } catch (error) {
    if (error.name === 'AbortError') throw new ApiError(0, t('status.timeout'));
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

const postJson = (path, body, timeoutMs) => api(path, {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
}, timeoutMs);

function errorText(error) {
  if (error instanceof ApiError && error.status === 429) return t('status.tooMany');
  if (error instanceof ApiError && error.status === 0) return t('status.timeout');
  if (error instanceof ApiError && [400, 413, 422].includes(error.status) && error.message) return error.message;
  return t('status.chatError');
}

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
};

function chip(label, onClick, className = 'chip-btn') {
  const button = el('button', className);
  if (label) decorate(button, label);
  button.type = 'button';
  button.addEventListener('click', onClick);
  return button;
}

function labelled(node, label) { node.setAttribute('aria-label', label); node.title = label; return node; }

function linkChip(label, href) {
  const link = el('a', 'chip-btn');
  decorate(link, label);
  link.href = href;
  link.target = '_blank';
  link.rel = 'noopener';
  return link;
}

/* ==========================================================================
   4. ORB STATE, STATUS AND SPEECH
   ========================================================================== */
let orbErrorTimer = null;
const ORB_STEP = { listening: 'th.listen', processing: 'th.search', speaking: 'th.speak' };
const ORB_LABEL = { idle: 'orb.idle', listening: 'orb.listening', processing: 'orb.busy', speaking: 'orb.speaking', error: 'orb.error' };
let lastOrbState = 'idle';
/** The visible label under the home orb, and one short screen-reader message per state change. */
function orbLabel(name) {
  const key = ORB_LABEL[name] || 'orb.idle';
  document.querySelectorAll('[data-orb-label]').forEach((node) => { node.dataset.i18n = key; node.textContent = t(key); node.dataset.state = name; });
  if (name !== lastOrbState) {
    lastOrbState = name;
    const live = document.getElementById('orb-live');
    if (live) live.textContent = t(key);
  }
}

function orb(name) {
  setOrbState(name);
  orbLabel(name);
  if (ORB_STEP[name]) thought(t(ORB_STEP[name]));
  else thought(null);
  clearTimeout(orbErrorTimer);
  // An error ring never stays on: back to idle after 3 s.
  if (name === 'error') orbErrorTimer = setTimeout(() => { setOrbState('idle'); orbLabel('idle'); }, 3000);
}

/** The browser blocked the microphone: say so plainly, and how to fix it, under each orb. */
function showMicHelp(show) {
  document.querySelectorAll('.mic-help').forEach((n) => n.remove());
  if (!show) return;
  ['#home-convo .orb-label', '#voice-status-label'].forEach((selector) => {
    const anchor = document.querySelector(selector);
    if (!anchor) return;
    const card = el('div', 'mic-help');
    card.setAttribute('role', 'alert');
    const head = el('p', 'mic-help-title');
    decorate(head, `🎙️ ${t('mic.title')}`);
    card.append(head, el('p', '', t('mic.body')), chip(t('mic.type'), () => { showMicHelp(false); showPage('assistant'); setTimeout(() => document.getElementById('chat-input')?.focus(), 450); }, 'cta-button mic-help-type'));
    anchor.after(card);
  });
}

/* The orb's thought: a bubble beside it and a line under it while Pakkam works; when idle the
   line types example questions, one letter at a time (a still example in calm mode). */
let typer = { timer: null, q: 0, pos: 0, step: null };
function thought(text) {
  typer.step = text;
  document.querySelectorAll('.thought-bubble').forEach((node) => {
    if (text) node.textContent = text;
    node.classList.toggle('show', Boolean(text));
  });
  document.querySelectorAll('.thought-line').forEach((node) => { node.classList.toggle('busy', Boolean(text)); });
  if (text) { clearTimeout(typer.timer); typer.timer = null; setThoughtLine(text); }
  else startTyping();
}
function setThoughtLine(text) { document.querySelectorAll('.thought-line').forEach((node) => { node.textContent = text; }); }
function startTyping() {
  clearTimeout(typer.timer);
  typer.timer = null;
  const list = EXAMPLES[state.language] || EXAMPLES['en-IN'];
  const calm = document.documentElement.classList.contains('calm') || window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if (calm || document.hidden) { setThoughtLine(`${t('th.try')} ${list[0]}`); return; }
  setThoughtLine(`${t('th.try')} `);
  typer.pos = 0;
  const tick = () => {
    if (typer.step) return;
    const q = list[typer.q % list.length];
    typer.pos += 1;
    setThoughtLine(`${t('th.try')} ${q.slice(0, typer.pos)}`);
    if (typer.pos >= q.length) { typer.pos = 0; typer.q += 1; typer.timer = setTimeout(tick, 2600); }
    else typer.timer = setTimeout(tick, 55);
  };
  typer.timer = setTimeout(tick, 400);
}
document.addEventListener('visibilitychange', () => { if (!typer.step) startTyping(); });

function setStatus(text) {
  ['voice-status-label', 'home-status'].forEach((id) => {
    const node = document.getElementById(id);
    if (node) node.textContent = text;
  });
}

/** What Pakkam heard (isTranscript) or a short voice message, under both orbs. */
function showHeard(text, isTranscript = false) {
  const preview = document.getElementById('live-transcript-preview');
  if (preview) preview.textContent = text;
  const home = document.getElementById('home-heard');
  if (home) home.textContent = text && isTranscript ? `${t('home.heard')}: ${text}` : text;
}

function setBars(level) {
  document.querySelectorAll('.orb-waveform-assembly').forEach((assembly) => {
    assembly.classList.add('audio-reactive');
    assembly.style.setProperty('--level', String(Math.min(1, level).toFixed(2)));
    assembly.querySelectorAll('.wave-bar').forEach((bar, index) => {
      const shape = [0.38, 0.62, 0.9, 0.72, 0.48][index % 5];
      bar.style.setProperty('--bar-level', String(0.3 + level * shape * 1.5));
    });
  });
}

// Every stop bumps this; speech that was still loading checks it and is dropped.
let speechGen = 0;
let relistenTimer = null;
let replyLoading = false;

/** Silence Pakkam completely: current audio, speech still loading, the "checking…" line and
 *  a conversation-mode re-listen that was about to start. */
function stopSpeaking() {
  speechGen += 1;
  clearTimeout(relistenTimer);
  relistenTimer = null;
  stopPlayback();
  stopWaveformMeter();
  orb('idle');
  setStatus(t('assistant.tap'));
}

function stopPlayback() {
  if (state.currentAudio) {
    state.currentAudio.onended = null;
    state.currentAudio.pause();
    if (state.currentAudio.src.startsWith('blob:') && !state.currentAudio.keepUrl) URL.revokeObjectURL(state.currentAudio.src);
  }
  state.currentAudio = null;
  const stopBtn = document.getElementById('stop-audio-btn');
  if (stopBtn) stopBtn.style.display = 'none';
  document.body.classList.remove('audio-playing');
}

/** Read typed answers aloud? The person's own choice when they made one; otherwise yes, except in
 *  Easy mode, where nothing starts speaking until they turn on "Read answers aloud".
 *  (Spoken questions are always answered by voice.) */
function readAloud() {
  let saved = null;
  try { saved = localStorage.getItem('pakkam_tts'); } catch (_) { /* private mode */ }
  if (saved !== null) return saved !== 'false';
  return !prefs.easy;
}

async function speechUrl(text, language) {
  const res = await postJson('/speak', { text: text.slice(0, 1200), language: language === 'unknown' ? 'en' : language }, 60000);
  return URL.createObjectURL(await res.blob());
}

/** Play a WAV url; resolves when it ends (or fails). */
function playUrl(url, { rate = 1, keepUrl = false } = {}) {
  return new Promise((resolve) => {
    stopPlayback();
    const audio = new Audio(url);
    audio.keepUrl = keepUrl;
    audio.playbackRate = rate;
    state.currentAudio = audio;
    const stopBtn = document.getElementById('stop-audio-btn');
    if (stopBtn) stopBtn.style.display = 'inline-block';
    document.body.classList.add('audio-playing');
    const done = () => {
      if (state.currentAudio === audio) { stopPlayback(); stopWaveformMeter(); orb('idle'); setStatus(t('assistant.tap')); }
      resolve();
    };
    audio.onended = done;
    audio.onerror = done;
    audio.play().then(() => {
      orb('speaking');
      setStatus(t('status.speaking'));
      try {
        state.audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
        state.audioContext.resume();
        startWaveformMeter(state.audioContext.createMediaElementSource(audio), true);
      } catch (_) { /* playback works without the waveform */ }
    }).catch(done);
  });
}

async function speak(text, language, options = {}) {
  const spoken = (text || '').replace(CITATION_MARKER, '').trim();
  if (!spoken) return;
  const gen = speechGen;
  try {
    const url = await speechUrl(spoken, language);
    if (gen !== speechGen) { URL.revokeObjectURL(url); return; }  // stopped while loading
    await playUrl(url, { ...options, rate: options.rate || prefs.speed });
  } catch (_) {
    orb('idle');  // speech is optional: the written answer is on screen
  }
}

const fillerUrls = {};
function prefetchFiller(language) {
  if (fillerUrls[language] || !FILLER[language]) return;
  fillerUrls[language] = speechUrl(FILLER[language], language).catch(() => { delete fillerUrls[language]; return null; });
}

/* ==========================================================================
   5. CONVERSATION STATE AND CHAT BUBBLES
   ========================================================================== */
const convo = {
  last: null,          // { question, data, text }
  refusals: 0,
  mode: (() => { try { return localStorage.getItem('pakkam_conv') === '1'; } catch (_) { return false; } })(),
  surface: 'chat',     // where the latest voice turn started: 'home' or 'chat'
  voiceLang: null,     // voice language chip ('ta-Latn' for Tanglish), else from the site language
};

const voiceLanguage = () => convo.voiceLang || VOICE_LANG[state.language] || 'ta';

function setConversationMode(on) {
  convo.mode = on;
  try { localStorage.setItem('pakkam_conv', on ? '1' : '0'); } catch (_) { /* private mode */ }
  document.querySelectorAll('.conv-mode-input').forEach((box) => { box.checked = on; });
}

function chatBox() { return document.getElementById('chat-messages'); }

/** Long answers fold after about 8 lines, with Show more / Show less. */
function foldLongAnswer(body) {
  requestAnimationFrame(() => {
    const lineHeight = parseFloat(getComputedStyle(body).lineHeight) || 26;
    if (body.scrollHeight <= lineHeight * 9) return;
    body.classList.add('folded');
    const toggle = chip(t('answer.more'), () => {
      const open = body.classList.toggle('folded') === false;
      toggle.textContent = open ? t('answer.less') : t('answer.more');
      toggle.setAttribute('aria-expanded', String(open));
    }, 'text-link fold-toggle');
    toggle.setAttribute('aria-expanded', 'false');
    body.after(toggle);
  });
}

function scrollChat() {
  const box = chatBox();
  if (box) box.scrollTop = box.scrollHeight;
}

function addBubble(role, text) {
  const bubble = el('div', `chat-bubble ${role}`);
  if (text) bubble.append(el('div', 'answer-text', text));
  chatBox()?.appendChild(bubble);
  scrollChat();
  return bubble;
}

function chipRow(chips, label) {
  const wrap = el('div', 'answer-row');
  if (label) wrap.append(el('span', 'answer-row-label', label));
  const pills = el('div', 'citation-pills');
  pills.append(...chips);
  wrap.append(pills);
  return wrap;
}

function exampleChips(language = state.language) {
  const chips = (EXAMPLES[language] || EXAMPLES['en-IN']).map((q) => chip(q, () => submitChatQuery(q)));
  chips.push(chip((MESSAGES[language] || MESSAGES['en-IN'])['home.shield'], () => navigateTo('shield')));
  return chips;
}

function renderWelcomeChips() {
  const box = document.getElementById('welcome-chips');
  if (box) box.replaceChildren(...exampleChips());
}

/** Mirror a short reply on the home page, under the orb. */
function showOnHome(text, citations = []) {
  const card = document.getElementById('home-answer');
  if (!card) return;
  card.replaceChildren(el('p', 'home-answer-text', text));
  const actions = el('div', 'citation-pills');
  citations.slice(0, 2).forEach((c) => actions.append(proofButton(c)));
  actions.append(chip(`${t('home.openChat')} →`, () => navigateTo('assistant')));
  card.append(actions);
  card.hidden = false;
}

/* ==========================================================================
   6. SMALL TALK (talk.js): instant, no server call
   ========================================================================== */
function handleTalk(intent, question, options) {
  const language = replyLanguage(question, state.language);
  const words = TALK[language] || TALK['en-IN'];
  const bubble = addBubble('ai');
  let text = words[intent] || '';
  const say = (extra) => { bubble.append(extra); scrollChat(); };

  if (intent === 'again') return explainAgain(bubble, words, options);
  if (intent === 'summary') return summarize(bubble, words, options);

  bubble.append(el('div', 'answer-text', text));
  if (['greeting', 'howAreYou', 'offTopic'].includes(intent)) say(chipRow(exampleChips(language)));
  if (intent === 'goodbye') setConversationMode(false);
  if (intent === 'thanks' || intent === 'ack') say(chipRow(nextStepChips()));
  if (intent === 'schemes') say(chipRow(schemeChips()));
  if (intent === 'notClear') say(chipRow(notClearChips()));
  if (intent === 'complaint' || intent === 'issue') say(chipRow(issueChips()));
  showOnHome(text);
  finishTurn(text, SPEECH_LANG[language], options);
}

function nextStepChips() {
  const scheme = convo.last?.data?.scheme;
  if (!scheme) return exampleChips().slice(0, 3);
  const asks = QUICK_QUESTIONS[state.language] || QUICK_QUESTIONS['en-IN'];
  return [
    chip(t('answer.docs'), () => showChecklist(scheme)),
    chip(t('schemes.askWho'), () => submitChatQuery(asks.who(scheme))),
    chip(t('schemes.askAmount'), () => submitChatQuery(asks.amount(scheme))),
  ];
}

function schemeChips() {
  const asks = QUICK_QUESTIONS[state.language] || QUICK_QUESTIONS['en-IN'];
  return schemeNames().map((name) => chip(name, () => submitChatQuery(asks.amount(name))));
}

function notClearChips() {
  const chips = [chip(t('answer.again'), () => explainAgain(addBubble('ai'), TALK[state.language], {})),
    chip(t('answer.summary'), () => summarize(addBubble('ai'), TALK[state.language], {}))];
  const cite = convo.last?.data?.citations?.[0];
  if (cite) chips.push(proofButton(cite));
  if (convo.last) chips.push(chip(t('answer.simpler'), () => submitChatQuery(convo.last.question, { voice: true, quiet: true })));
  return chips;
}

function issueChips() {
  const chips = [];
  const helpline = convo.last?.data?.contact?.helpline;
  if (helpline) {
    const call = el('a', 'chip-btn');
    decorate(call, `📞 ${t('answer.call')}: ${helpline}`);
    call.href = `tel:${helpline.replace(/[^\d+]/g, '')}`;
    chips.push(call);
  }
  chips.push(chip(t('answer.officer'), () => openOfficer(convo.last?.question || '', convo.last?.data?.scheme)));
  chips.push(chip(t('answer.tips'), () => { addBubble('ai', t('answer.tipsText')); }));
  const cite = convo.last?.data?.citations?.[0];
  if (cite) chips.push(proofButton(cite));
  return chips;
}

function sectionsOf(data) {
  const groups = new Map();
  (data.sentences || []).forEach((s) => {
    const key = SECTION_ORDER.includes(s.section) ? s.section : 'other';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(s);
  });
  return SECTION_ORDER.filter((key) => groups.has(key)).map((key) => [key, groups.get(key)]);
}

function explainAgain(bubble, words, options) {
  if (!convo.last || convo.last.data.refused) { bubble.append(el('div', 'answer-text', words.noLast)); return; }
  bubble.append(el('div', 'answer-flag', words.againTitle));
  renderSections(bubble, convo.last.data);
  bubble.append(citationRow(convo.last.data.citations));
  scrollChat();
  finishTurn(convo.last.text, convo.last.data.language, { ...options, rate: 0.85, force: true });
}

function summarize(bubble, words, options) {
  if (!convo.last || convo.last.data.refused) { bubble.append(el('div', 'answer-text', words.noLast)); return; }
  bubble.append(el('div', 'answer-flag', words.summaryTitle));
  const list = el('ul', 'answer-summary');
  const lines = [];
  sectionsOf(convo.last.data).forEach(([key, sentences]) => {
    const line = sentences[0].text;
    lines.push(line);
    const item = el('li');
    if (key !== 'other') item.append(el('strong', '', `${t(`section.${key}`)}: `));
    item.append(document.createTextNode(line));
    list.append(item);
  });
  bubble.append(list, citationRow(convo.last.data.citations));
  scrollChat();
  finishTurn(lines.join(' '), convo.last.data.language, options);
}

/* ==========================================================================
   7. ANSWERS WITH PROOF
   ========================================================================== */
function citationLabel(c) {
  const pages = c.page_end && c.page_end !== c.page_start ? `${c.page_start}-${c.page_end}` : c.page_start;
  return `${c.document} · ${t('proof.page')} ${pages}`;
}

function proofButton(c) {
  const button = chip(`📄 ${t('proof.open')} · ${citationLabel(c)}${c.checked_by ? ' ✓' : ''}`, () => openProof(c), 'citation-tag proof-btn');
  button.title = t('proof.open');
  return button;
}

function citationRow(citations = []) {
  const wrap = el('div', 'citation-pills');
  citations.forEach((c) => wrap.append(proofButton(c)));
  return wrap;
}

function overlay(titleText) {
  closeOverlay();
  const shade = el('div', 'proof-overlay');
  shade.setAttribute('role', 'dialog');
  shade.setAttribute('aria-modal', 'true');
  shade.setAttribute('aria-label', titleText);
  const box = el('div', 'proof-box glass-panel');
  const close = chip('✕', closeOverlay, 'icon-btn proof-close');
  close.setAttribute('aria-label', t('proof.close'));
  box.append(close);
  shade.append(box);
  shade.addEventListener('click', (event) => { if (event.target === shade) closeOverlay(); });
  document.body.append(shade);
  close.focus();
  return box;
}

function closeOverlay() { document.querySelector('.proof-overlay')?.remove(); }

function openProof(c) {
  const box = overlay(t('proof.title'));
  box.append(el('p', 'hero-eyebrow', t('proof.title')), el('h2', 'proof-doc', c.document));
  box.append(el('p', 'proof-meta', `${c.scheme} · ${t('proof.page')} ${c.page_start}${c.document_date ? ` · ${t('documents.dated')} ${c.document_date}` : ''}`));
  box.append(c.checked_by
    ? el('p', 'proof-checked', `✓ ${t('proof.checked')} ${c.checked_by}${c.checked_on ? ` (${c.checked_on})` : ''}`)
    : el('p', 'proof-note', t('proof.unchecked')));
  if (c.ocr_corrected) box.append(el('p', 'proof-note', t('proof.corrected')));
  const pagePath = `/page?doc=${encodeURIComponent(c.doc_id)}&p=${c.page_start}&mark=${encodeURIComponent((c.excerpt || '').slice(0, 600))}`;
  const zoom = el('a', 'proof-page');
  zoom.href = `${API_BASE}${pagePath}`;
  zoom.target = '_blank';
  zoom.rel = 'noopener';
  const img = el('img');
  img.alt = `${c.document}, ${t('proof.page')} ${c.page_start}`;
  img.src = `${API_BASE}${pagePath}`;
  img.addEventListener('error', () => zoom.replaceWith(el('p', 'proof-note', t('proof.noImage'))));
  zoom.append(img);
  box.append(zoom);
  if (c.excerpt) box.append(el('blockquote', 'proof-excerpt', c.excerpt.slice(0, 400)));
  if (c.source_url) {
    // Open the official PDF at the page. Some PDF viewers ignore #page, so say what to do then;
    // the page image above always works.
    const isPdf = /\.pdf($|[?#])/i.test(c.source_url);
    const href = isPdf && !c.source_url.includes('#') ? `${c.source_url}#page=${c.page_start}` : c.source_url;
    box.append(linkChip(isPdf ? `📄 ${fill(t('proof.pdfAt'), { page: c.page_start })}` : t('proof.source'), href));
    if (isPdf) box.append(el('p', 'proof-note pdf-note', fill(t('proof.pdfNote'), { page: c.page_start })));
  }
}

/** Who stands behind the sources: a named person only when one really checked the page. */
function attributionLine(citations) {
  const names = [...new Set(citations.map((c) => c.checked_by).filter(Boolean))];
  const line = el('p', names.length ? 'attribution checked' : 'attribution');
  decorate(line, names.length ? `✓ ${fill(t('answer.checkedBy'), { names: names.join(', ') })}` : `📄 ${t('answer.fromDoc')}`);
  return line;
}

/** Sentences as text with small numbered citation marks; each mark opens its page. */
function sentenceNodes(sentences, data, tag = 'p', className = '') {
  const byNumber = new Map((data.citations || []).map((c) => [c.number, c]));
  const node = el(tag, className);
  sentences.forEach((sentence, index) => {
    if (index) node.append(' ');
    node.append(sentence.text);
    [...new Set(sentence.citations || [])].forEach((n) => {
      const cite = byNumber.get(n);
      if (!cite) return;
      const mark = chip(String(n), () => openProof(cite), 'cite-num');
      mark.setAttribute('aria-label', `${t('proof.open')}: ${citationLabel(cite)}`);
      mark.title = citationLabel(cite);
      const sup = el('sup');
      sup.append(mark);
      node.append(sup);
    });
  });
  return node;
}

function renderSections(bubble, data) {
  const sections = sectionsOf(data);
  const named = sections.filter(([key]) => key !== 'other');
  if (named.length < 2) {
    bubble.append(sentenceNodes(data.sentences, data, 'div', 'answer-text'));
    return;
  }
  sections.forEach(([key, sentences]) => {
    const block = el('div', 'answer-section');
    if (key !== 'other') block.append(el('h4', '', t(`section.${key}`)));
    block.append(sentenceNodes(sentences, data));
    bubble.append(block);
  });
}

/** "Sources" row above the answer: one small pill per official page. */
function sourcesRow(citations) {
  const row = el('div', 'sources-row');
  row.append(el('span', 'sources-label', t('answer.sources')));
  const pills = el('div', 'sources-pills');
  [...citations].sort((a, b) => (a.number ?? 0) - (b.number ?? 0)).forEach((c) => {
    const short = c.document.replace(/^G\.O\.\s*\(Ms\)\s*No\.\s*(\d+).*/i, 'G.O. $1');
    const pill = chip('', () => openProof(c), 'source-pill proof-btn');
    pill.append(el('span', 'source-n', String(c.number ?? '')), el('span', 'source-doc', short), el('span', 'source-page', `${t('proof.pageShort')} ${c.page_start}`));
    if (c.checked_by) { const tick = el('span', 'source-check'); tick.innerHTML = iconSvg('check'); pill.append(tick); }
    pill.title = `${t('proof.open')} · ${citationLabel(c)}`;
    pills.append(pill);
  });
  row.append(pills);
  return row;
}

function answerText(data) {
  return (data.sentences && data.sentences.length)
    ? data.sentences.map((s) => s.text).join(' ')
    : (data.answer || '').replace(CITATION_MARKER, '');
}

function renderAnswer(bubble, data, question) {
  bubble.replaceChildren();
  const text = answerText(data);
  if (data.refused) bubble.append(el('p', 'answer-flag', t('answer.refused')));

  if (data.confirmation_text) {
    bubble.append(el('p', 'answer-confirm', data.confirmation_text));
    bubble.append(chipRow([
      chip(t('answer.yesRight'), (event) => event.currentTarget.closest('.answer-row')?.remove()),
      chip(t('answer.sayAgain'), () => toggleVoiceRecording(convo.surface)),
    ], t('answer.heardCheck')));
  }

  if (data.citations && data.citations.length && !data.refused) bubble.append(sourcesRow(data.citations), attributionLine(data.citations));
  const answerBody = el('div', 'answer-body');
  if (data.sentences && data.sentences.length) renderSections(answerBody, data);
  else answerBody.append(el('div', 'answer-text', text));
  bubble.append(answerBody);
  foldLongAnswer(answerBody);

  // "What can I get?": a card per scheme with its signed amount, plus the yearly total.
  const facts = (data.scheme_facts || []).filter((f) => f.amount || f.who);
  if (facts.length) {
    const cards = el('div', 'facts-grid');
    let total = 0;
    facts.forEach((fact) => {
      const card = el('div', 'fact-card');
      card.append(el('strong', '', fact.scheme));
      if (fact.amount) card.append(el('p', '', fact.amount));
      if (fact.who) card.append(el('p', 'fact-who', fact.who));
      const cite = fact.amount_citation || fact.who_citation;
      if (cite) card.append(proofButton(cite));
      total += fact.yearly_amount || 0;
      cards.append(card);
    });
    bubble.append(cards);
    if (total) bubble.append(el('p', 'facts-total', fill(t('facts.total'), { total: `₹${total.toLocaleString('en-IN')}` })));
  }

  if (data.status === 'needs_clarification' && data.candidate_schemes?.length) {
    bubble.append(chipRow(data.candidate_schemes.slice(0, 4).map((scheme) => chip(scheme, () => submitChatQuery(`${question} (${scheme})`))), t('answer.didYouMean')));
  }

  if (data.refused) {
    const chips = [];
    if (data.contact?.helpline) {
      const call = el('a', 'chip-btn');
      decorate(call, `📞 ${t('answer.call')}: ${data.contact.helpline}`);
      call.href = `tel:${data.contact.helpline.replace(/[^\d+]/g, '')}`;
      chips.push(call);
    }
    if (data.refusal_reason !== 'pii_detected') chips.push(chip(t('answer.officer'), () => openOfficer(question, data.scheme)));
    bubble.append(chipRow(chips));
    bubble.append(chipRow(exampleChips().slice(0, 3)));
    return text;
  }

  // Next steps and the conversation check-in.
  if (data.sentences && data.sentences.length) {
    const actions = [];
    actions.push(chip(t('answer.copy'), (event) => copyAnswer(event.currentTarget, text, data.citations?.[0])));
    if (data.scheme) actions.push(chip(t('answer.docs'), () => showChecklist(data.scheme)));
    actions.push(waChip(t('answer.share'), () => shareAnswer(question, text, data.citations?.[0])));
    actions.push(chip(t('answer.print'), () => printAnswer(question, data)));
    if (data.scheme && schemeNames().includes(data.scheme)) actions.push(chip(t('answer.appeal'), () => openAppeal(data.scheme)));
    bubble.append(chipRow(actions));
    const check = chipRow([
      chip(t('answer.yes'), (event) => { event.currentTarget.closest('.answer-row')?.remove(); handleTalk('ack', 'ok', {}); }),
      chip(t('answer.notClear'), (event) => { event.currentTarget.closest('.answer-row')?.remove(); handleTalk('notClear', 'puriyala', {}); }),
    ], t('answer.understood'));
    const feedback = chipRow([
      labelled(chip('👍', (event) => sendFeedback(event, data, 'up'), 'chip-btn icon-chip'), t('answer.helpfulYes')),
      labelled(chip('👎', (event) => sendFeedback(event, data, 'down'), 'chip-btn icon-chip'), t('answer.helpfulNo')),
    ], t('answer.helpful'));
    bubble.append(check, feedback);
  }
  return text;
}

function spokenText(data) {
  const parts = [];
  if (data.confirmation_text) parts.push(data.confirmation_text);
  parts.push(answerText(data));
  const cited = !data.refused && data.citations?.find((c) => data.sentences?.some((s) => s.citations.includes(c.number)));
  if (cited) parts.push((SPOKEN_SOURCE[data.language] || SPOKEN_SOURCE.en)(cited));
  return parts.join(' ');
}

async function sendFeedback(event, data, thumbs) {
  const row = event.currentTarget.closest('.answer-row');
  if (row) row.replaceChildren(el('span', 'answer-row-label', t('answer.feedbackThanks')));
  try { await postJson('/feedback', { status: data.status, thumbs, language: data.language }, 20000); } catch (_) { /* best effort */ }
  if (thumbs === 'down') { const bubble = addBubble('ai', t('answer.issue')); bubble.append(chipRow(issueChips())); }
}

async function copyAnswer(button, text, cite) {
  const lines = [text];
  if (cite) lines.push(`${cite.document}, ${t('proof.page')} ${cite.page_start}: ${cite.source_url}`);
  try { await navigator.clipboard.writeText(lines.join('\n')); } catch (_) { return; }
  decorate(button, `✓ ${t('answer.copied')}`);
  button.classList.add('done');
  setTimeout(() => { decorate(button, t('answer.copy')); button.classList.remove('done'); }, 1800);
}

function shareAnswer(question, text, cite) {
  const lines = [`❓ ${question}`, `✅ ${text}`];
  if (cite) lines.push(`📄 ${cite.document}, ${t('proof.page')} ${cite.page_start}`, cite.source_url);
  lines.push('— Pakkam (பக்கம்)');
  window.open(`https://wa.me/?text=${encodeURIComponent(lines.filter(Boolean).join('\n'))}`, '_blank', 'noopener');
}

function printAnswer(question, data) {
  const win = window.open('', '_blank');
  if (!win) return;
  const doc = win.document;
  doc.title = 'Pakkam';
  const body = doc.body;
  body.style.fontFamily = 'system-ui, sans-serif';
  body.style.padding = '24px';
  body.append(Object.assign(doc.createElement('h2'), { textContent: question }));
  sectionsOf(data).forEach(([key, sentences]) => {
    if (key !== 'other') body.append(Object.assign(doc.createElement('h3'), { textContent: t(`section.${key}`) }));
    body.append(Object.assign(doc.createElement('p'), { textContent: sentences.map((s) => s.text).join(' ') }));
  });
  (data.citations || []).forEach((c) => body.append(Object.assign(doc.createElement('p'), { textContent: `📄 ${c.document}, ${t('proof.page')} ${c.page_start} — ${c.source_url}` })));
  body.append(Object.assign(doc.createElement('p'), { textContent: t('footer.line') }));
  win.focus();
  win.print();
}

async function showChecklist(scheme) {
  const bubble = addBubble('ai');
  bubble.append(el('p', 'answer-flag', `${t('checklist.title')} · ${scheme}`));
  try {
    const lang = state.language === 'ta-IN' ? 'ta' : 'en';
    const data = await (await api(`/checklist?scheme=${encodeURIComponent(scheme)}&lang=${lang}`, {}, 30000)).json();
    if (!data.items?.length) { bubble.append(el('p', '', fill(t('checklist.none'), { scheme }))); return; }
    const list = el('ul', 'answer-summary');
    data.items.forEach((item) => {
      const li = el('li', '', item.text);
      li.append(document.createTextNode(' '), proofButton(item.citation));
      list.append(li);
    });
    bubble.append(list);
  } catch (error) {
    bubble.append(el('p', '', errorText(error)));
  }
  scrollChat();
}

/* ==========================================================================
   8. ASKING: small talk first, then /ask/sources (progress) + /ask (answer)
   ========================================================================== */
async function submitChatQuery(queryText, options = {}) {
  let question = queryText.trim();
  if (!question) return;
  if (!options.voice) convo.surface = 'chat';
  if (convo.surface === 'chat' || !options.voice) navigateTo('assistant');
  if (!options.quiet) addBubble('user', question);

  const talk = detectTalk(question);
  if (talk && !talk.rest) { handleTalk(talk.intent, question, options); return; }
  if (talk?.rest) {
    const language = replyLanguage(question, state.language);
    addBubble('ai', (TALK[language] || TALK['en-IN']).greeting.split('!')[0] + '! 🙏');
    question = talk.rest;
  }

  const bubble = addBubble('ai');
  bubble.classList.add('thinking');
  const progress = el('p', 'answer-progress', t('progress.searching'));
  bubble.append(progress);
  orb('processing');
  setStatus(t('status.processing'));

  const body = { question: question.slice(0, 500), voice_mode: Boolean(options.voice) };
  if (convo.last?.data?.scheme) body.follow_up = { question: convo.last.question.slice(0, 500), scheme: convo.last.data.scheme };
  const fillerGen = speechGen;
  if (options.voice && fillerUrls[voiceSpeech()]) {
    fillerUrls[voiceSpeech()].then((url) => { if (url && fillerGen === speechGen && bubble.classList.contains('thinking')) playUrl(url, { keepUrl: true }); });
  }
  postJson('/ask/sources', body, 15000).then((res) => res.json()).then((found) => {
    const top = found.passages?.[0];
    if (top && bubble.classList.contains('thinking')) {
      progress.textContent = fill(t('progress.found'), { doc: top.document, page: top.page });
      thought(fill(t('th.found'), { doc: top.document, page: top.page }));
    }
  }).catch(() => {});
  const slow = setTimeout(() => { if (bubble.classList.contains('thinking')) bubble.append(el('p', 'answer-progress', t('progress.slow'))); }, SLOW_MS);

  replyLoading = true;
  const turnGen = speechGen;  // a stop while the answer loads cancels its speech
  try {
    const data = await (await postJson('/ask', body)).json();
    replyLoading = false;
    clearTimeout(slow);
    bubble.classList.remove('thinking');
    if (!data.refused) thought(t('th.check'));
    const text = renderAnswer(bubble, data, question);
    scrollChat();
    convo.last = { question, data, text };
    convo.refusals = data.refused ? convo.refusals + 1 : 0;
    if (convo.refusals >= 2) { const help = addBubble('ai', t('answer.issue')); help.append(chipRow(issueChips())); }
    saveToHistory(question, text);
    showOnHome(text, data.citations || []);
    setStatus(t('assistant.tap'));
    await finishTurn(spokenText(data), data.language, { ...options, gen: turnGen });
  } catch (error) {
    replyLoading = false;
    clearTimeout(slow);
    bubble.classList.remove('thinking');
    if (isOfflineError(error)) {
      setOffline(true);
      const sampleText = renderOfflineAnswer(bubble, question);
      showOnHome(sampleText || t('offline.none'));
      orb('idle');
      setStatus(t('assistant.tap'));
      return;
    }
    bubble.replaceChildren(el('div', 'answer-text', errorText(error)));
    showOnHome(errorText(error));
    orb('error');
    setStatus(t('assistant.tap'));
  }
}

const voiceSpeech = () => ({ 'ta-Latn': 'ta' }[voiceLanguage()] || voiceLanguage());

/** Speak the reply (voice questions always; typed ones when auto-play is on), then keep
 *  listening in conversation mode. */
async function finishTurn(text, language, options = {}) {
  if (options.gen !== undefined && options.gen !== speechGen) { orb('idle'); return; }  // stopped meanwhile
  const gen = speechGen;
  if (options.voice || options.force || readAloud()) await speak(text, language, { rate: options.rate });
  else orb('idle');
  // Keep listening in conversation mode, unless the person stopped Pakkam meanwhile.
  if (convo.mode && options.voice && !recording && gen === speechGen) {
    relistenTimer = setTimeout(() => { relistenTimer = null; toggleVoiceRecording(convo.surface, { again: true }); }, 500);
  }
}

/* ==========================================================================
   9. VOICE: record (WAV, recorder.js) -> /transcribe -> ask
   ========================================================================== */
let recording = null;
let recordingTimer = null;

/** Orb tap: listening -> send; speaking or still answering -> stop and stay quiet; idle -> listen. */
function orbTap(surface) {
  if (recording) { finishRecording(true); return; }
  if (state.currentAudio || replyLoading || relistenTimer) { stopSpeaking(); return; }
  toggleVoiceRecording(surface);
}

async function toggleVoiceRecording(surface = 'chat', { again = false } = {}) {
  if (recording) { await finishRecording(true); return; }
  if (!window.PakkamRecorder || !navigator.mediaDevices?.getUserMedia) {
    orb('error');
    setStatus(t('status.voiceError'));
    return;
  }
  convo.surface = surface;
  stopPlayback();
  if (surface === 'chat') navigateTo('assistant');
  prefetchFiller(voiceSpeech());
  try {
    recording = await window.PakkamRecorder.start({
      onLevel: setBars,
      onSilence: (heardSpeech) => finishRecording(heardSpeech),
      noSpeechMs: again ? 7000 : 9000,
    });
  } catch (_) {
    recording = null;
    orb('error');
    setStatus(t('status.micError'));
    showMicHelp(true);
    return;
  }
  showMicHelp(false);
  orb('listening');
  setStatus(t('status.listening'));
  showHeard('');
  recordingTimer = setTimeout(() => finishRecording(true), MAX_VOICE_SECONDS * 1000);
}

async function finishRecording(heardSpeech) {
  if (!recording) return;
  const current = recording;
  recording = null;
  clearTimeout(recordingTimer);
  stopWaveformMeter();
  if (!heardSpeech) {
    current.cancel();
    orb('idle');
    setStatus(convo.mode ? t('conv.paused') : t('assistant.tap'));
    if (!convo.mode) showHeard(t('status.noSpeech'));
    return;
  }
  orb('processing');
  thought(t('th.writing'));
  setStatus(t('status.processing'));
  let wav;
  try { wav = await current.stop(); } catch (_) { wav = null; }
  if (!wav || wav.size < 2000) {
    orb('idle');
    setStatus(t('assistant.tap'));
    showHeard(t('status.noSpeech'));
    return;
  }
  const form = new FormData();
  form.append('audio', wav, 'question.wav');
  form.append('language', voiceLanguage());
  const gen = speechGen;
  replyLoading = true;  // a tap now means "stop", not "listen again"
  try {
    const data = await (await api('/transcribe', { method: 'POST', body: form }, 60000)).json();
    replyLoading = false;
    const heard = (data.transcript || '').trim();
    if (gen !== speechGen) { if (heard) showHeard(`"${heard}"`, true); return; }  // stopped while transcribing
    if (!heard) {
      orb('idle');
      setStatus(t('assistant.tap'));
      showHeard(t('status.noSpeech'));
      return;
    }
    showHeard(`"${heard}"`, true);
    await submitChatQuery(heard, { voice: true });
  } catch (error) {
    replyLoading = false;
    orb('error');
    setStatus(t('assistant.tap'));
    showHeard(error instanceof ApiError && [400, 413, 415, 422].includes(error.status) && error.message ? error.message : t('status.voiceError'));
  }
}

function renderVoiceChips() {
  document.querySelectorAll('#voice-lang-chips, .settings-voice-chips').forEach((box) => renderVoiceChipsInto(box));
}

function renderVoiceChipsInto(box) {
  const options = [['ta', 'தமிழ்'], ['ta-Latn', 'Tanglish'], ['hi', 'हिन्दी'], ['en', 'English']];
  box.replaceChildren(...options.map(([code, label]) => {
    const button = chip(label, () => {
      convo.voiceLang = code;
      try { localStorage.setItem('pakkam_voice', code); } catch (_) { /* private mode */ }
      renderVoiceChips();
    }, `chip-btn${voiceLanguage() === code ? ' active' : ''}`);
    button.setAttribute('aria-pressed', String(voiceLanguage() === code));
    return button;
  }));
}

/* ==========================================================================
   10. RUMOUR SHIELD (POST /check-forward)
   ========================================================================== */
function applyShieldText() {
  const w = shieldWords();
  const set = (selector, text, attr) => { const node = document.querySelector(selector); if (node) { if (attr) node.setAttribute(attr, text); else node.textContent = text; } };
  set('#page-shield .hero-eyebrow', w.eyebrow);
  set('#page-shield h1 [data-i18n="shield.title"]', w.title);
  set('#page-shield .page-intro', w.intro);
  set('#shield-input', w.placeholder, 'placeholder');
  set('#shield-example', w.example);
  set('#shield-check', w.check);
}

// Same rules as src/schemebot/generate/forward.py and data/official_domains.json (keep in sync;
// a test checks the exact hosts match). Recognising a host never makes a claim true.
const OFFICIAL_SUFFIX = ['gov.in', 'nic.in'];
const OFFICIAL_EXACT = ['tncdw.org', 'pfrda.org.in', 'npstrust.org.in', 'enps.nsdl.com', 'npscra.nsdl.co.in'];
const LINK_RE = /(https?:\/\/|www\.)\S+|\b[\w-]+\.(?:com|in|org|net|xyz|online|site|info|ly|me|apk)\b\S*/gi;
const SIGN_RE = {
  otp: /\botp\b|ஓடிபி|ओटीपी|one.?time.?password|verification code/gi,
  payment: /\b(pay|fee|fees|charges?|deposit|processing|registration amount|upi|gpay|phonepe|paytm)\b|கட்டணம்|செலுத்த|शुल्क|फीस|भुगतान/gi,
  personal_data: /\b(aadhaar|aadhar|pan|bank account|account number|atm|card number|cvv|pin)\b|ஆதார்|आधार/gi,
  urgency: /\b(today only|last date today|hurry|urgent|immediately|before midnight|limited)\b|இன்று மட்டும்|உடனே|அவசர|आज ही|तुरंत|जल्दी/gi,
};

function linkSign(link) {
  let url;
  try { url = new URL(/^[a-z][a-z0-9+.-]*:\/\//i.test(link) ? link : `https://${link}`); } catch (_) { return 'unofficial_link'; }
  const host = url.hostname.replace(/\.$/, '').toLowerCase().replace(/^www\./, '');
  const official = OFFICIAL_SUFFIX.some((s) => host === s || host.endsWith(`.${s}`)) || OFFICIAL_EXACT.includes(host);
  if (!official) return 'unofficial_link';
  return url.protocol === 'http:' ? 'insecure_link' : null;
}

/** The pasted message shown back with its warning signs marked. Built from text nodes only,
 *  so nothing in the message can run as HTML. Each mark jumps to its warning explanation. */
function echoMessage(message, signs = []) {
  const box = el('div', 'shield-echo');
  box.append(el('p', 'shield-echo-label', t('shield.yourMessage')));
  const ranges = [];
  for (const m of message.matchAll(LINK_RE)) {
    const sign = linkSign(m[0].replace(/[.,;:!?)"']+$/, ''));
    if (sign && signs.includes(sign)) ranges.push([m.index, m.index + m[0].length, sign]);
  }
  Object.entries(SIGN_RE).forEach(([sign, re]) => {
    if (!signs.includes(sign)) return;
    for (const m of message.matchAll(re)) ranges.push([m.index, m.index + m[0].length, sign]);
  });
  ranges.sort((a, b) => a[0] - b[0]);
  const text = el('p', 'shield-echo-text');
  let at = 0;
  ranges.forEach(([start, end, sign]) => {
    if (start < at) return;  // overlapping marks: keep the first
    text.append(document.createTextNode(message.slice(at, start)));
    const jump = el('a', `sign-mark sign-${sign}`);
    jump.href = `#sign-${sign}`;
    jump.title = t('shield.markTitle');
    jump.addEventListener('click', (event) => { event.preventDefault(); const row = document.getElementById(`sign-${sign}`); row?.scrollIntoView({ block: 'center', behavior: reduceMotion() ? 'auto' : 'smooth' }); row?.focus({ preventScroll: true }); });
    const mark = el('mark', '', message.slice(start, end));
    jump.append(mark);
    text.append(jump);
    at = end;
  });
  text.append(document.createTextNode(message.slice(at)));
  box.append(text);
  return box;
}

/** "How it checks" panel: play its three drawings (again), and light up the outcomes a check gave. */
function playHowChecks() {
  const panel = document.querySelector('.how-checks');
  if (!panel) return;
  panel.classList.remove('play');
  void panel.offsetWidth;  // restart the CSS animations
  panel.classList.add('play');
}

function markOutcomes(found) {
  const panel = document.querySelector('.how-checks');
  if (!panel) return;
  const hit = new Set(found);
  panel.classList.toggle('has-result', hit.size > 0);
  panel.querySelectorAll('[data-outcome]').forEach((li) => li.classList.toggle('is-hit', hit.has(li.dataset.outcome)));
  panel.querySelectorAll('.art-hc-verdict .v').forEach((g) => {
    const outcome = ['good', 'bad', 'neutral', 'warn'].find((o) => g.classList.contains(`v-${o}`));
    g.classList.toggle('hit', hit.has(outcome));
  });
}

async function checkForward(message) {
  const w = shieldWords();
  const status = document.getElementById('shield-status');
  const result = document.getElementById('shield-result');
  const button = document.getElementById('shield-check');
  result.replaceChildren();
  status.textContent = w.checking;
  button.disabled = true;
  markOutcomes([]);
  try {
    const data = await (await postJson('/check-forward', { message: message.slice(0, 1500) }, 180000)).json();
    status.textContent = '';
    // Verdict first: a big, coloured badge (red wrong, amber partly or unknown, green right).
    const tone = { wrong: 'bad', partly_wrong: 'bad', looks_right: 'good', not_in_documents: 'neutral', no_claims: 'neutral' }[data.overall] || 'neutral';
    const verdict = el('div', `shield-verdict-card tone-${tone}`);
    const badge = el('span', 'verdict-badge');
    badge.innerHTML = iconSvg({ bad: 'x', good: 'check' }[tone] || 'help');
    const [, overallText] = splitIcon(w.overall[data.overall] || data.overall);
    verdict.append(badge, el('h2', `shield-overall shield-${data.overall}`, overallText));
    result.append(verdict);
    result.append(echoMessage(message, data.scam_signs));
    const correction = [w.correction];
    if (data.claims.length) {
      const list = el('div', 'claim-list');
      data.claims.forEach((claim) => {
        const claimTone = { supported: 'good', contradicted: 'bad' }[claim.verdict] || 'neutral';
        const card = el('article', `shield-claim tone-${claimTone}`);
        const pill = el('span', 'shield-verdict');
        decorate(pill, w.verdict[claim.verdict] || claim.verdict);
        card.append(pill, el('h3', '', claim.claim), el('p', '', claim.explanation));
        const cite = claim.answer?.citations?.[0];
        if (cite) card.append(proofButton(cite));
        list.append(card);
        correction.push(`${w.verdict[claim.verdict] || ''} ${claim.claim}: ${claim.explanation}${cite ? ` (${cite.document}, ${t('proof.page')} ${cite.page_start})` : ''}`);
      });
      result.append(list);
    }
    const signs = data.scam_signs.filter((sign) => sign !== 'official_link');
    if (signs.length) {
      const box = el('div', 'shield-signs');
      const head = el('h3');
      decorate(head, `⚠️ ${w.warnings}`);
      box.append(head, el('p', 'signs-note', t('shield.signsNote')));
      const list = el('ul');
      signs.forEach((sign) => {
        const li = el('li');
        li.id = `sign-${sign}`;
        li.tabIndex = -1;
        decorate(li, `⚠️ ${w.signs[sign] || sign}`);
        list.append(li);
        correction.push(`⚠️ ${w.signs[sign] || sign}`);
      });
      box.append(list);
      result.append(box);
    }
    if (data.scam_signs.includes('official_link')) result.append(el('p', 'proof-note', w.signs.official_link));
    const found = data.claims.map((claim) => ({ supported: 'good', contradicted: 'bad' }[claim.verdict] || 'neutral'));
    if (!data.claims.length) found.push(tone);
    if (signs.length) found.push('warn');
    markOutcomes(found);
    correction.push('— Pakkam (பக்கம்)');
    result.append(waChip(w.share, () => window.open(`https://wa.me/?text=${encodeURIComponent(correction.join('\n'))}`, '_blank', 'noopener'), 'cta-button shield-share'));
  } catch (error) {
    status.textContent = error instanceof ApiError && error.status === 422 && error.message ? error.message : w.failed;
  } finally {
    button.disabled = false;
  }
}

/* ==========================================================================
   11. ASK AN OFFICER and APPEAL NOTE (dialogs)
   ========================================================================== */
function openOfficer(question, scheme) {
  const box = overlay(t('officer.title'));
  box.append(el('h2', 'proof-doc', t('officer.title')), el('p', 'proof-note', t('officer.intro')));
  const form = el('form', 'dialog-form');
  const text = el('textarea', 'shield-input');
  text.rows = 3; text.maxLength = 500; text.required = true; text.value = question || '';
  text.setAttribute('aria-label', t('officer.question'));
  const contact = el('input', 'input-pill');
  contact.maxLength = 40; contact.placeholder = t('officer.contact');
  const send = el('button', 'cta-button', t('officer.send'));
  send.type = 'submit';
  const status = el('p', 'document-status');
  status.setAttribute('aria-live', 'polite');
  form.append(el('label', 'answer-row-label', t('officer.question')), text, contact, send, status);
  box.append(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    send.disabled = true;
    try {
      const data = await (await postJson('/officer-request', {
        question: text.value.trim(), scheme: scheme || null, language: VOICE_LANG[state.language] || 'en', contact: contact.value.trim() || null,
      }, 30000)).json();
      status.textContent = fill(t('officer.sent'), { ticket: data.ticket });
    } catch (error) {
      status.textContent = error instanceof ApiError && error.status === 422 && error.message ? error.message : t('officer.failed');
      send.disabled = false;
    }
  });
}

function openAppeal(schemeName) {
  const words = APPEAL[state.language] || APPEAL['en-IN'];
  const box = overlay(words.title);
  box.append(el('h2', 'proof-doc', `📝 ${words.title}`));
  const form = el('form', 'dialog-form');
  const scheme = el('select', 'input-pill');
  schemeNames().forEach((name) => { const option = el('option', '', name); option.value = name; scheme.append(option); });
  if (schemeName) scheme.value = schemeName;
  const reason = el('textarea', 'shield-input');
  reason.rows = 2; reason.maxLength = 300; reason.required = true; reason.placeholder = words.reason;
  const situation = el('textarea', 'shield-input');
  situation.rows = 2; situation.maxLength = 300; situation.placeholder = words.situation;
  const go = el('button', 'cta-button', words.go);
  go.type = 'submit';
  const status = el('p', 'document-status');
  status.setAttribute('aria-live', 'polite');
  const result = el('div');
  form.append(el('label', 'answer-row-label', words.scheme), scheme, reason, situation, go, status);
  box.append(form, result);
  reason.focus();
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const why = reason.value.trim();
    if (why.length < 3) return;
    go.disabled = true;
    status.textContent = words.working;
    result.replaceChildren();
    try {
      const data = await (await postJson('/ask', { question: words.ask(scheme.value, why).slice(0, 500), follow_up: { question: why, scheme: scheme.value } })).json();
      status.textContent = '';
      const cite = data.citations?.find((c) => data.sentences?.some((s) => s.citations.includes(c.number)));
      if (data.refused || !data.sentences?.length || !cite) {
        result.append(el('p', '', words.noRule), chip(t('answer.officer'), () => openOfficer(why, scheme.value)));
        return;
      }
      const rule = data.sentences.map((s) => s.text).join(' ');
      result.append(el('h3', '', words.rule), el('p', '', rule), proofButton(cite), el('h3', '', words.note));
      const note = el('textarea', 'shield-input appeal-note');
      note.rows = 14;
      note.value = words.template({ scheme: scheme.value, reason: why, situation: situation.value.trim(), document: cite.document, page: cite.page_start, rule });
      const copy = chip(words.copy, async () => { try { await navigator.clipboard.writeText(note.value); copy.textContent = words.copied; } catch (_) { note.select(); } });
      const share = waChip(t('answer.share'), () => window.open(`https://wa.me/?text=${encodeURIComponent(note.value)}`, '_blank', 'noopener'));
      const actions = el('div', 'citation-pills');
      actions.append(copy, share);
      result.append(note, actions, el('p', 'proof-note', words.disclaimer));
    } catch (error) {
      status.textContent = errorText(error);
    } finally {
      go.disabled = false;
    }
  });
}

/* ==========================================================================
   12. SCHEMES AND OFFICIAL DOCUMENTS (GET /sources)
   ========================================================================== */
let sources;  // undefined = loading, null = offline

async function loadSources() {
  try {
    sources = await (await api('/sources', {}, 30000)).json();
    setOffline(false);
  } catch (_) {
    sources = SAMPLE_SOURCES;  // browse the built-in sample list while the server is down
    setOffline(true);
  }
  return sources;
}

const schemeNames = () => [...new Set((sources || []).map((d) => d.scheme))];

const QUICK_QUESTIONS = {
  'en-IN': { amount: (s) => `How much money does ${s} give?`, who: (s) => `Who is eligible for ${s}?`, docs: (s) => `What documents are needed for ${s}?` },
  'ta-IN': { amount: (s) => `${s} திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?`, who: (s) => `${s} திட்டத்திற்கு யார் தகுதியானவர்கள்?`, docs: (s) => `${s} திட்டத்திற்கு என்ன ஆவணங்கள் தேவை?` },
  'hi-IN': { amount: (s) => `${s} में कितना पैसा मिलता है?`, who: (s) => `${s} के लिए कौन पात्र है?`, docs: (s) => `${s} के लिए कौन से दस्तावेज़ चाहिए?` },
};

let schemeFacts = {};  // scheme -> signed facts from GET /scheme-facts

async function loadSchemeFacts() {
  try {
    const lang = state.language === 'ta-IN' ? 'ta' : 'en';
    const list = await (await api(`/scheme-facts?lang=${lang}`, {}, 30000)).json();
    schemeFacts = Object.fromEntries(list.map((f) => [f.scheme, f]));
  } catch (_) {
    schemeFacts = server.online ? {} : Object.fromEntries(SAMPLE_FACTS.map((f) => [f.scheme, f]));
  }
}

// Questions people actually ask about each scheme (English); other languages use the
// translated amount / who / documents questions.
const SCHEME_QUESTIONS = [
  [/magalir|urimai/i, ['How much is Magalir Urimai Thogai?', "Can government employees' families get Magalir Urimai?", 'Is an income certificate needed for Magalir Urimai?']],
  [/kisan/i, ['How much does PM-KISAN give in a year?', 'How do I complete e-KYC for PM-KISAN?', 'Who is not eligible for PM-KISAN?']],
  [/atal|pension/i, ['How much pension does Atal Pension Yojana give?', 'What is the age limit to join Atal Pension Yojana?', 'Can income tax payers join Atal Pension Yojana?']],
  [/ujjwala/i, ['Who can get an Ujjwala gas connection?', 'What documents are needed for Ujjwala?', 'Is the Ujjwala connection free?']],
  [/breakfast/i, ["Which classes get the Chief Minister's Breakfast?", "Which schools have the Chief Minister's Breakfast Scheme?"]],
  [/pudhumai/i, ['How much does Pudhumai Penn give?', 'Who is eligible for Pudhumai Penn?']],
  [/maruthuva|insurance|cmchis|health/i, ['What is the income limit for the CM health insurance scheme?', 'How much cover does the CM health insurance give?']],
];
// Category and issuer for each scheme in sources.json (shown as a quiet label on the card).
const SCHEME_META = [
  [/magalir|urimai/i, 'women', 'tn'], [/pudhumai/i, 'education', 'tn'], [/kisan/i, 'farmers', 'central'],
  [/atal|apy|pension/i, 'pension', 'central'], [/ujjwala/i, 'gas', 'central'], [/breakfast/i, 'children', 'tn'],
  [/maruthuva|insurance|cmchis|health/i, 'health', 'tn'], [/hostel|backward|bc|mbc|scholar|graduate|student/i, 'education', 'tn'],
];
const CATEGORY_ORDER = ['women', 'farmers', 'pension', 'gas', 'children', 'health', 'education', 'welfare'];
let activeCategory = 'all';

function schemeMeta(scheme, docs) {
  const hit = SCHEME_META.find(([re]) => re.test(scheme));
  const issuer = hit ? hit[2] : (docs.some((d) => d.language === 'ta') ? 'tn' : '');
  return { category: hit ? hit[1] : 'welfare', issuer };
}

function schemeQuestions(scheme) {
  const asks = QUICK_QUESTIONS[state.language] || QUICK_QUESTIONS['en-IN'];
  const own = state.language === 'en-IN' ? SCHEME_QUESTIONS.find(([re]) => re.test(scheme))?.[1] : null;
  return own || [asks.amount(scheme), asks.who(scheme), asks.docs(scheme)];
}

function groupedSchemes() {
  const byScheme = new Map();
  (sources || []).forEach((doc) => {
    if (!byScheme.has(doc.scheme)) byScheme.set(doc.scheme, []);
    byScheme.get(doc.scheme).push(doc);
  });
  return [...byScheme.entries()].map(([scheme, docs]) => ({ scheme, docs, ...schemeMeta(scheme, docs), facts: schemeFacts[scheme] }));
}

function renderSchemeFilters(items) {
  const box = document.getElementById('scheme-filters');
  if (!box) return;
  const present = CATEGORY_ORDER.filter((c) => items.some((i) => i.category === c));
  box.replaceChildren(...['all', ...present].map((cat) => {
    const count = cat === 'all' ? items.length : items.filter((i) => i.category === cat).length;
    const button = chip('', () => {
      activeCategory = cat;
      renderSchemes(null, document.getElementById('scheme-search-input')?.value || '');
    }, `filter-tab${activeCategory === cat ? ' active' : ''}`);
    if (cat !== 'all' && ART[`cat-${cat}`]) { const mini = el('span', 'tab-art'); mini.innerHTML = ART[`cat-${cat}`]; button.append(mini); }
    button.append(document.createTextNode(t(cat === 'all' ? 'schemes.all' : `cat.${cat}`)), el('span', 'tab-count', String(count)));
    button.setAttribute('aria-pressed', String(activeCategory === cat));
    return button;
  }));
}

function renderSchemes(_unused, searchQuery = '') {
  const grid = document.getElementById('schemes-grid');
  const summary = document.getElementById('schemes-summary');
  if (!grid) return;
  grid.replaceChildren();
  if (!sources) {
    grid.append(el('p', 'empty-state', sources === null ? t('documents.offline') : t('documents.loading')));
    return;
  }
  const items = groupedSchemes();
  if (summary) summary.textContent = fill(t('schemes.summary'), { schemes: items.length, docs: sources.length });
  renderSchemeFilters(items);
  const query = searchQuery.trim().toLowerCase();
  const shown = items
    .filter((i) => activeCategory === 'all' || i.category === activeCategory)
    .filter((i) => !query || i.scheme.toLowerCase().includes(query) || i.docs.some((d) => d.title.toLowerCase().includes(query)));
  const banner = document.getElementById('scheme-banner');
  if (banner) {
    banner.hidden = activeCategory === 'all';
    if (activeCategory !== 'all') {
      const art = el('span', 'banner-art'); art.innerHTML = ART[`cat-${activeCategory}`] || '';
      const words = el('div');
      words.append(el('h2', '', t(`catline.${activeCategory}`)), el('p', '', t('catline.hint')));
      banner.replaceChildren(art, words);
    }
  }
  if (!shown.length) {
    const empty = el('div', 'empty-art');
    const art = el('span', 'empty-art-pic'); art.innerHTML = ART.empty;
    empty.append(art, el('p', '', t('schemes.emptyArt')), chip(t('home.ask'), () => showPage('assistant'), 'cta-button'));
    grid.append(empty);
    return;
  }
  const list = el('div', 'scheme-list');
  list.append(...shown.map((item) => {
    const row = el('button', 'scheme-row');
    row.type = 'button';
    const main = el('div', 'row-main');
    main.append(el('h2', 'row-name', item.scheme),
      el('p', 'row-meta', [t(`cat.${item.category}`), item.issuer ? t(`issuer.${item.issuer}`) : '', `${item.docs.length} ${t(item.docs.length === 1 ? 'schemes.docCount1' : 'schemes.docCount')}`].filter(Boolean).join(' · ')));
    if (item.facts?.who) main.append(el('p', 'row-who', item.facts.who));
    const side = el('div', 'row-side');
    const signed = item.facts?.amount_citation?.checked_by || item.facts?.who_citation?.checked_by;
    side.append(el('p', item.facts?.amount ? 'row-amount' : 'row-amount muted', item.facts?.amount || t('schemes.noAmount')));
    if (signed) { const tick = el('p', 'row-signed', `✓ ${t('schemes.verified')}`); tick.title = signed; side.append(tick); }
    row.append(main, side, el('span', 'row-chevron', '›'));
    row.addEventListener('click', () => openSchemeDrawer(item));
    return row;
  }));
  grid.append(list);
}

const WA_SVG = document.querySelector('.wa-icon')?.outerHTML || '';
/** A button with the WhatsApp mark in front of its label. */
function waChip(label, onClick, className) {
  const button = chip('', onClick, className);
  button.innerHTML = WA_SVG;
  button.append(el('span', '', splitIcon(label)[1]));
  return button;
}

function closeSchemeDrawer() { document.querySelector('.scheme-drawer')?.remove(); }

/** Everything about one scheme, in a side panel (bottom sheet on phones). */
function openSchemeDrawer(item) {
  closeSchemeDrawer();
  const shade = el('div', 'scheme-drawer');
  shade.setAttribute('role', 'dialog');
  shade.setAttribute('aria-modal', 'true');
  shade.setAttribute('aria-label', item.scheme);
  const panel = el('div', 'drawer-panel');
  const close = chip('✕', closeSchemeDrawer, 'icon-btn drawer-close');
  close.setAttribute('aria-label', t('proof.close'));
  const head = el('div', 'drawer-head');
  if (ART[`cat-${item.category}`]) { const art = el('span', 'drawer-art'); art.innerHTML = ART[`cat-${item.category}`]; head.append(art); }
  const titles = el('div');
  titles.append(el('p', 'tile-cat', [t(`cat.${item.category}`), item.issuer ? t(`issuer.${item.issuer}`) : ''].filter(Boolean).join(' · ')), el('h2', '', item.scheme));
  head.append(titles);
  panel.append(close, head);

  const facts = item.facts;
  if (facts && (facts.amount || facts.who)) {
    const box = el('dl', 'drawer-facts');
    if (facts.amount) box.append(el('dt', '', t('section.amount')), el('dd', '', facts.amount));
    if (facts.who) box.append(el('dt', '', t('section.eligibility')), el('dd', '', facts.who));
    panel.append(box);
    const checker = facts.amount_citation?.checked_by || facts.who_citation?.checked_by;
    const proofs = el('div', 'citation-pills');
    [facts.amount_citation, facts.who_citation].filter(Boolean)
      .filter((c, i, all) => all.findIndex((o) => o.doc_id === c.doc_id && o.page_start === c.page_start) === i)
      .forEach((c) => proofs.append(proofButton(c)));
    if (checker) panel.append(el('p', 'checked-tag', `✓ ${t('proof.checked')} ${checker}`));
    panel.append(proofs);
  } else {
    panel.append(el('p', 'setting-help', t('schemes.noAmount')));
  }

  panel.append(el('h3', 'drawer-label', t('schemes.documents')));
  const list = el('ul', 'doc-list');
  item.docs.forEach((doc) => {
    const li = el('li');
    const meta = [doc.language.toUpperCase(), doc.doc_date ? `${t('documents.dated')} ${doc.doc_date}` : ''].filter(Boolean).join(' · ');
    li.append(el('span', 'doc-title', doc.title), el('span', 'doc-meta', meta), linkChip(t('documents.open'), doc.source_url));
    list.append(li);
  });
  panel.append(list);

  panel.append(el('h3', 'drawer-label', t('schemes.questions')));
  const asks = el('div', 'ask-list');
  schemeQuestions(item.scheme).forEach((q) => asks.append(chip(`${q}  →`, () => { closeSchemeDrawer(); submitChatQuery(q); }, 'ask-row')));
  panel.append(asks);

  shade.append(panel);
  shade.addEventListener('click', (event) => { if (event.target === shade) closeSchemeDrawer(); });
  document.body.append(shade);
  requestAnimationFrame(() => shade.classList.add('open'));
  close.focus();
}

// Under the orb: "Speak. Hear. See the proof." and a real example question that types itself out,
// one language at a time. Tapping it asks it. Still (one example) for reduced motion and easy mode.
const SLOGAN_EXAMPLES = [
  { tag: 'தமிழ்', q: 'மகளிர் உரிமைத் தொகை எவ்வளவு?' },
  { tag: 'Tanglish', q: 'PM Kisan la varushathuku evlo?' },
  { tag: 'हिंदी', q: 'अटल पेंशन किसे मिलती है?' },
  { tag: 'English', q: 'Who gets free breakfast at school?' },
];
const slogan = { index: 0, chars: 0, timer: null, hold: false };

function showSloganExample(full) {
  const button = document.getElementById('slogan-example');
  if (!button) return;
  const item = SLOGAN_EXAMPLES[slogan.index];
  button.querySelector('.ex-tag').textContent = item.tag;
  const shown = full ? item.q : [...item.q].slice(0, slogan.chars).join('');
  // The full question sits invisibly underneath, so the box is its final size while it types.
  const box = button.querySelector('.ex-text');
  if (box.dataset.q !== item.q) { box.dataset.q = item.q; box.replaceChildren(el('span', 'ex-full', item.q), el('span', 'ex-typed')); }
  box.querySelector('.ex-typed').textContent = shown;
  button.setAttribute('aria-label', `${t('slogan.ask')}: ${item.q}`);
  button.setAttribute('lang', { 'தமிழ்': 'ta', 'हिंदी': 'hi' }[item.tag] || 'en');
}

function runSlogan() {
  clearTimeout(slogan.timer);
  const still = reduceMotion() || document.documentElement.classList.contains('easy');
  if (still) { showSloganExample(true); return; }
  const tick = () => {
    const total = [...SLOGAN_EXAMPLES[slogan.index].q].length;
    if (slogan.hold || document.hidden) { slogan.timer = setTimeout(tick, 400); return; }
    if (slogan.chars < total) { slogan.chars += 1; showSloganExample(false); slogan.timer = setTimeout(tick, 55); return; }
    slogan.timer = setTimeout(() => { slogan.index = (slogan.index + 1) % SLOGAN_EXAMPLES.length; slogan.chars = 0; tick(); }, 2600);
  };
  tick();
}

function setupSlogan() {
  const button = document.getElementById('slogan-example');
  if (!button) return;
  button.addEventListener('click', () => submitChatQuery(SLOGAN_EXAMPLES[slogan.index].q));
  ['mouseenter', 'focus'].forEach((type) => button.addEventListener(type, () => { slogan.hold = true; slogan.chars = 999; showSloganExample(true); }));
  ['mouseleave', 'blur'].forEach((type) => button.addEventListener(type, () => { slogan.hold = false; }));
  runSlogan();
}

function renderHomeExamples() {
  const box = document.getElementById('home-examples');
  if (!box) return;
  const icons = ['rupee', 'simple', 'leaf', 'flame'];
  box.replaceChildren(...(EXAMPLES[state.language] || EXAMPLES['en-IN']).map((q, index) => {
    const card = el('button', 'example-card');
    card.type = 'button';
    card.style.setProperty('--i', String(index));
    const mark = el('span', 'example-icon');
    mark.innerHTML = iconSvg(icons[index % icons.length]);
    card.append(mark, el('span', 'example-text', q), el('span', 'example-go', '→'));
    card.addEventListener('click', () => submitChatQuery(q));
    card.classList.add('reveal');
    return card;
  }));
  watchReveals(box);
}

/* ==========================================================================
   SETTINGS (this browser only)
   ========================================================================== */
const prefs = (() => {
  const read = (key, fallback) => { try { return localStorage.getItem(key) ?? fallback; } catch (_) { return fallback; } };
  return { speed: Number(read('pakkam_speed', '1')) || 1, easy: read('pakkam_easy', '0') === '1', size: Number(read('pakkam_size', '100')) || 100,
    calm: read('pakkam_calm', '0') === '1', phone: read('pakkam_phone', '0') === '1',
    bg: ['minimal', 'balanced', 'ambient'].includes(read('pakkam_bg', 'balanced')) ? read('pakkam_bg', 'balanced') : 'balanced' };
})();

function savePref(key, value) { try { localStorage.setItem(key, String(value)); } catch (_) { /* private mode */ } }

function applyPrefs() {
  const root = document.documentElement;
  root.classList.toggle('easy', prefs.easy);
  root.classList.toggle('calm', prefs.calm);
  if (root.dataset.bg !== prefs.bg) root.dataset.bg = prefs.bg;
  root.style.fontSize = `${prefs.easy ? Math.max(prefs.size, 118) : prefs.size}%`;
  if (window.PakkamRecorder) window.PakkamRecorder.phoneMode = prefs.phone;
  const mark = (selector, attr, value) => document.querySelectorAll(`${selector} [${attr}]`).forEach((b) => {
    const on = b.getAttribute(attr) === String(value);
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', String(on));
  });
  mark('#setting-speed', 'data-speed', prefs.easy ? 0.85 : prefs.speed);
  mark('#setting-size', 'data-size', prefs.size);
  mark('#setting-bg', 'data-bg-choice', prefs.bg);
  mark('#setting-theme', 'data-theme-choice', state.theme);
  mark('#setting-lang', 'data-lang', state.language);
  const set = (id, value) => { const box = document.getElementById(id); if (box) box.checked = value; };
  set('setting-easy', prefs.easy);
  set('setting-calm', prefs.calm);
  set('setting-phone', prefs.phone);
  state.autoPlayTTS = readAloud();
  set('setting-autoplay-tts', state.autoPlayTTS);
  set('read-aloud-toggle', state.autoPlayTTS);
}

function bindSettings() {
  document.querySelectorAll('#setting-speed [data-speed]').forEach((b) => b.addEventListener('click', () => { prefs.speed = Number(b.dataset.speed); savePref('pakkam_speed', prefs.speed); applyPrefs(); }));
  document.querySelectorAll('#setting-size [data-size]').forEach((b) => b.addEventListener('click', () => { prefs.size = Number(b.dataset.size); savePref('pakkam_size', prefs.size); applyPrefs(); }));
  document.querySelectorAll('#setting-bg [data-bg-choice]').forEach((b) => b.addEventListener('click', () => { prefs.bg = b.dataset.bgChoice; savePref('pakkam_bg', prefs.bg); applyPrefs(); }));
  document.querySelectorAll('#setting-theme [data-theme-choice]').forEach((b) => b.addEventListener('click', () => { applyTheme(b.dataset.themeChoice); applyPrefs(); }));
  const toggle = (id, key, onChange) => document.getElementById(id)?.addEventListener('change', (event) => { onChange(event.target.checked); savePref(key, event.target.checked ? '1' : '0'); applyPrefs(); });
  toggle('setting-easy', 'pakkam_easy', (on) => { prefs.easy = on; if (on) prefs.speed = 0.85; });
  toggle('setting-calm', 'pakkam_calm', (on) => { prefs.calm = on; });
  toggle('setting-phone', 'pakkam_phone', (on) => { prefs.phone = on; });
  ['setting-autoplay-tts', 'read-aloud-toggle'].forEach((id) => document.getElementById(id)?.addEventListener('change', (event) => {
    state.autoPlayTTS = event.target.checked;
    savePref('pakkam_tts', event.target.checked);
    applyPrefs();
  }));
  document.getElementById('composer-stop')?.addEventListener('click', stopSpeaking);
  // Clear history: a second tap confirms (pop-up confirms are blocked in some browsers).
  const clear = document.getElementById('clear-history-btn');
  clear?.addEventListener('click', () => {
    if (clear.dataset.armed !== '1') {
      clear.dataset.armed = '1';
      clear.textContent = t('set.clearConfirm');
      setTimeout(() => { clear.dataset.armed = '0'; clear.textContent = t('history.clear'); }, 4000);
      return;
    }
    clear.dataset.armed = '0';
    clear.textContent = t('history.clear');
    state.history = [];
    try { localStorage.removeItem('pakkam_history'); } catch (_) { /* private mode */ }
    renderHistory();
  });
}

/* ==========================================================================
   13. HISTORY (this browser only)
   ========================================================================== */
function saveToHistory(question, answer) {
  state.history.unshift({ id: Date.now(), date: new Date().toLocaleDateString(), question, answer });
  state.history = state.history.slice(0, 30);
  try { localStorage.setItem('pakkam_history', JSON.stringify(state.history)); } catch (_) { /* private mode */ }
  renderHistory();
}

function renderHistory() {
  const list = document.getElementById('history-list');
  if (!list) return;
  if (!state.history.length) { list.replaceChildren(el('p', 'empty-state', t('history.empty'))); return; }
  list.replaceChildren(...state.history.map((item) => {
    const article = el('article', 'history-row');
    article.append(el('time', 'history-date', item.date), el('h2', '', item.question), el('p', '', item.answer));
    article.append(chip(`↻ ${t('common.ask')}`, () => submitChatQuery(item.question)));
    return article;
  }));
}

/* ==========================================================================
   14. ABOUT: Pakkam explains itself, out loud
   ========================================================================== */
async function aboutListen() {
  const button = document.getElementById('about-listen');
  const text = document.getElementById('about-listen-text');
  const label = button.querySelector('[data-i18n="about.listen"]');
  const setLabel = (key) => { if (label) label.textContent = splitIcon(t(key))[1]; };
  if (state.currentAudio && button.dataset.playing === '1') {
    stopSpeaking();
    button.dataset.playing = '0';
    setLabel('about.listen');
    return;
  }
  const intro = t('about.intro');
  text.textContent = intro;
  text.hidden = false;
  button.dataset.playing = '1';
  setLabel('about.stop');
  await speak(intro, SPEECH_LANG[state.language] || 'en');
  button.dataset.playing = '0';
  setLabel('about.listen');
}

/* ==========================================================================
   14b. ROUND 5: offline fallback, credits, motion
   ========================================================================== */
const reduceMotion = () => document.documentElement.classList.contains('calm') || Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);

// --- Offline: never show a broken page ---------------------------------------------------
const server = { online: true };
function isOfflineError(error) {
  return error instanceof TypeError || (error instanceof ApiError && [404, 502, 503, 504, 520, 521, 522, 523, 524, 530].includes(error.status));
}
function setOffline(off) {
  server.online = !off;
  let banner = document.getElementById('offline-banner');
  if (!off) { banner?.remove(); return; }
  if (banner) return;
  banner = el('div', 'offline-banner');
  banner.id = 'offline-banner';
  banner.setAttribute('role', 'status');
  banner.append(el('span', '', t('offline.banner')), chip(t('offline.retry'), retryServer, 'chip-btn offline-retry'));
  document.body.prepend(banner);
}
async function retryServer() {
  const button = document.querySelector('.offline-retry');
  if (button) button.disabled = true;
  await loadSources();
  await loadSchemeFacts();
  renderSchemes(null, document.getElementById('scheme-search-input')?.value || '');
  if (button) button.disabled = false;
}
/** Answer from the built-in samples when the server is down. */
function renderOfflineAnswer(bubble, question) {
  const sample = sampleFor(question, SPEECH_LANG[state.language] || 'en');
  if (!sample) {
    bubble.replaceChildren(el('div', 'answer-text', t('offline.none')));
    bubble.append(chipRow(exampleChips().slice(0, 2)));
    return '';
  }
  const text = renderAnswer(bubble, sample, question);
  bubble.prepend(el('p', 'answer-flag sample-flag', t('offline.sample')));
  return text;
}

// --- Credits ---------------------------------------------------------------------------
// Names, roles and links of the people who built Pakkam. A person without a name is not shown,
// and only real links are listed.
const CREDITS = [
  { name: 'Jaswanth S S', role: 'credit.role1', photo: './assets/team/jaswanth.jpg', links: { github: 'https://github.com/mailtojaswanthss-svg', linkedin: 'https://www.linkedin.com/in/jaswanthss' } },
  { name: 'Mohit K', role: 'credit.role2', photo: './assets/team/mohit.jpg', links: { github: 'https://github.com/mxhxt010-code', linkedin: 'https://www.linkedin.com/in/mohit-k-575947371/' } },
];
function renderCredits() {
  const box = document.getElementById('credits');
  if (!box) return;
  box.replaceChildren(...CREDITS.filter((p) => p.name).map((person) => {
    const card = el('article', 'credit-card reveal in');
    const initials = person.name.split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase();
    const links = el('div', 'credit-links');
    Object.entries(person.links || {}).forEach(([kind, href]) => {
      const a = el('a', 'icon-btn credit-link');
      a.href = href; a.target = '_blank'; a.rel = 'noopener';
      a.innerHTML = iconSvg(kind);
      a.setAttribute('aria-label', `${person.name} on ${kind === 'github' ? 'GitHub' : kind === 'linkedin' ? 'LinkedIn' : kind}`);
      links.append(a);
    });
    const who = el('div', 'credit-who');
    who.append(el('h3', '', person.name), el('p', '', t(person.role)));
    const avatar = el('span', 'credit-avatar', initials);
    if (person.photo) {
      // A photo when one is set (web/assets/team/), initials if it is missing or fails to load.
      const img = document.createElement('img');
      img.src = person.photo; img.alt = person.name; img.width = 56; img.height = 56; img.loading = 'lazy'; img.decoding = 'async';
      img.addEventListener('error', () => img.remove());
      avatar.append(img);
    }
    card.append(avatar, who, links);
    return card;
  }));
}

// --- Motion ------------------------------------------------------------------------------
let revealer = null;
function watchReveals(root = document) {
  const nodes = root.querySelectorAll('.reveal:not(.in), .count:not(.counted)');
  if (reduceMotion() || !('IntersectionObserver' in window)) {
    nodes.forEach((node) => { node.classList.add('in'); if (node.classList.contains('count')) countUp(node, true); });
    return;
  }
  if (!revealer) {
    revealer = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('in');
      if (entry.target.classList.contains('count')) countUp(entry.target);
      revealer.unobserve(entry.target);
    }), { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  }
  nodes.forEach((node) => revealer.observe(node));
}

function countUp(node, instant = false) {
  if (node.classList.contains('counted')) return;
  node.classList.add('counted');
  const to = Number(node.dataset.to || 0);
  const suffix = node.dataset.suffix || '';
  if (instant || reduceMotion()) { node.textContent = `${to}${suffix}`; return; }
  const start = performance.now();
  const step = (now) => {
    const p = Math.min(1, (now - start) / 1200);
    node.textContent = `${Math.round(to * (1 - (1 - p) ** 3))}${suffix}`;
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// About: the story as a five-chapter player (one scene and its words at a time), and the rest
// of the page in four tabs. Auto-play is off by default and pauses on hover, focus or touch.
const SLIDE_MS = 12000;
const player = { index: 0, playing: false, hold: false, elapsed: 0, last: 0, tick: null };
const playerRoot = () => document.querySelector('.story-player');

function labelPlayer() {
  const root = playerRoot();
  if (!root) return;
  const slides = root.querySelectorAll('.slide');
  slides.forEach((slide, i) => slide.setAttribute('aria-label', fill(t('pl.chapter'), { n: i + 1, total: slides.length })));
  const play = root.querySelector('.player-play');
  play.setAttribute('aria-label', t(player.playing ? 'pl.pause' : 'pl.play'));
  play.setAttribute('aria-pressed', String(player.playing));
  play.classList.toggle('is-playing', player.playing);
}

function showProgress() {
  const root = playerRoot();
  if (!root) return;
  const n = root.querySelectorAll('.slide').length;
  const part = player.playing ? Math.min(1, player.elapsed / SLIDE_MS) : 1;
  root.style.setProperty('--player-progress', ((player.index + part) / n).toFixed(4));
}

function goToSlide(index, announce = true) {
  const root = playerRoot();
  if (!root) return;
  const slides = [...root.querySelectorAll('.slide')];
  const n = slides.length;
  player.index = (index + n) % n;
  player.elapsed = 0;
  slides.forEach((slide, i) => {
    const on = i === player.index;
    slide.hidden = false;
    slide.inert = !on;
    slide.setAttribute('aria-hidden', String(!on));
    slide.classList.toggle('is-active', on);
    const art = slide.querySelector('.chapter-art');
    if (!art) return;
    art.classList.remove('in');
    if (on) { void art.offsetWidth; art.classList.add('in'); }  // replay the scene
  });
  root.querySelectorAll('.player-dot').forEach((dot, i) => {
    dot.classList.toggle('is-active', i === player.index);
    dot.setAttribute('aria-current', i === player.index ? 'step' : 'false');
  });
  root.querySelector('.player-count').textContent = `${player.index + 1} / ${n}`;
  if (announce) {
    const name = slides[player.index].querySelector('.chapter-n span')?.textContent || '';
    root.querySelector('.player-live').textContent = `${fill(t('pl.chapter'), { n: player.index + 1, total: n })}: ${name}`;
  }
  showProgress();
}

function setPlaying(on) {
  player.playing = Boolean(on) && !reduceMotion();
  player.elapsed = 0;
  player.last = performance.now();
  clearInterval(player.tick);
  player.tick = null;
  if (player.playing) {
    player.tick = setInterval(() => {
      const now = performance.now();
      if (!player.hold && !document.hidden) player.elapsed += now - player.last;
      player.last = now;
      if (player.elapsed >= SLIDE_MS) {
        if (player.index === playerRoot().querySelectorAll('.slide').length - 1) { setPlaying(false); return; }
        goToSlide(player.index + 1);
      }
      showProgress();
    }, 200);
  }
  labelPlayer();
  showProgress();
}

function setupStoryPlayer() {
  const root = playerRoot();
  if (!root) return;
  root.querySelector('.player-prev').addEventListener('click', () => goToSlide(player.index - 1));
  root.querySelector('.player-next').addEventListener('click', () => goToSlide(player.index + 1));
  root.querySelector('.player-play').addEventListener('click', () => setPlaying(!player.playing));
  root.querySelectorAll('.player-dot').forEach((dot) => dot.addEventListener('click', () => goToSlide(Number(dot.dataset.go))));
  root.addEventListener('keydown', (event) => {
    if (event.target.closest('input, textarea, [role="tab"]')) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); goToSlide(player.index + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); goToSlide(player.index - 1); }
  });
  // Hovering, focusing or touching the story pauses auto-play, so nobody loses their place.
  root.addEventListener('mouseenter', () => { player.hold = true; });
  root.addEventListener('mouseleave', () => { player.hold = false; });
  root.addEventListener('focusin', (event) => { if (!event.target.closest('.player-play')) player.hold = true; });
  root.addEventListener('focusout', () => { player.hold = false; });
  const stage = root.querySelector('.player-stage');
  let startX = null;
  let startY = 0;
  stage.addEventListener('touchstart', (event) => { startX = event.touches[0].clientX; startY = event.touches[0].clientY; player.hold = true; }, { passive: true });
  stage.addEventListener('touchend', (event) => {
    player.hold = false;
    if (startX === null) return;
    const dx = event.changedTouches[0].clientX - startX;
    const dy = event.changedTouches[0].clientY - startY;
    startX = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) goToSlide(player.index + (dx < 0 ? 1 : -1));
  }, { passive: true });
  if (reduceMotion()) root.querySelector('.player-play').hidden = true;
  document.addEventListener('pakkam:page', () => setPlaying(false));
  goToSlide(0, false);
  labelPlayer();
}

function setupAboutTabs() {
  const tabs = [...document.querySelectorAll('.about-tablist [role="tab"]')];
  const select = (tab, focus = false) => {
    tabs.forEach((other) => {
      const on = other === tab;
      other.setAttribute('aria-selected', String(on));
      other.tabIndex = on ? 0 : -1;
      document.getElementById(other.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
    watchReveals();
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', (event) => {
      const to = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[event.key];
      if (to === undefined) return;
      event.preventDefault();
      select(tabs[(to + tabs.length) % tabs.length], true);
    });
  });
}

/** A skipped or timed-out transition is harmless: the page still changes. Keep its promises quiet. */
function quietTransition(transition) {
  ['ready', 'finished', 'updateCallbackDone'].forEach((key) => transition[key]?.catch?.(() => {}));
  return transition;
}

/** Page change with a soft crossfade (View Transitions where the browser has them). */
function showPage(pageKey) {
  const go = () => {
    navigateTo(pageKey);
    window.scrollTo({ top: 0, behavior: 'instant' });
    watchReveals();
  };
  if (document.startViewTransition && !reduceMotion()) quietTransition(document.startViewTransition(go));
  else go();
}

/** Theme switch: the new theme spreads in a circle from the button that was pressed. */
function switchTheme(event) {
  const swap = () => { toggleTheme(); applyPrefs(); };
  if (!document.startViewTransition || reduceMotion()) {
    const root = document.documentElement;
    if (!reduceMotion()) { root.classList.add('theme-fading'); setTimeout(() => root.classList.remove('theme-fading'), 320); }
    swap();
    return;
  }
  const box = event?.currentTarget?.getBoundingClientRect?.();
  const x = box ? box.left + box.width / 2 : window.innerWidth / 2;
  const y = box ? box.top + box.height / 2 : 0;
  const r = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
  const root = document.documentElement;
  root.dataset.vt = 'theme';
  const transition = quietTransition(document.startViewTransition(swap));
  transition.ready.then(() => {
    root.animate({ clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
      { duration: 550, easing: 'cubic-bezier(.22,1,.36,1)', pseudoElement: '::view-transition-new(root)' });
  }).catch(() => {});
  transition.finished.catch(() => {}).finally(() => { delete root.dataset.vt; });
}

// Keyboard focus stays inside an open panel (scheme details, proof card) until it closes.
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Tab') return;
  const panels = document.querySelectorAll('.scheme-drawer, .proof-overlay');
  const panel = panels[panels.length - 1];
  if (!panel) return;
  const items = [...panel.querySelectorAll('a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])')].filter((n) => n.offsetParent !== null);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  if (!panel.contains(document.activeElement)) { event.preventDefault(); first.focus(); }
  else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});

// --- The 60-second tour (for first-time visitors and judges; ?tour=1 starts it) ----------
const waitFor = (selector, ms = 9000) => new Promise((resolve) => {
  const start = performance.now();
  const check = () => {
    const node = document.querySelector(selector);
    if (node || performance.now() - start > ms) resolve(node);
    else setTimeout(check, 120);
  };
  check();
});

function startTour() {
  const tourQuestion = (EXAMPLES[state.language] || EXAMPLES['en-IN'])[0];
  runTour([
    { target: '#hero-orb-trigger', title: t('tour.1t'), body: t('tour.1'), enter: async () => { closeOverlay(); showPage('home'); } },
    { target: '#chat-messages .chat-bubble.ai:last-child', title: t('tour.2t'), body: t('tour.2'),
      enter: async () => {
        showPage('assistant');
        const before = document.querySelectorAll('#chat-messages .chat-bubble.ai:not(.thinking)').length;
        submitChatQuery(tourQuestion);
        const start = performance.now();
        while (document.querySelectorAll('#chat-messages .chat-bubble.ai:not(.thinking)').length <= before && performance.now() - start < 15000) await new Promise((r) => setTimeout(r, 150));
        stopSpeaking();
      } },
    { target: '.proof-box', title: t('tour.3t'), body: t('tour.3'),
      enter: async () => { document.querySelector('#chat-messages .chat-bubble.ai:last-child .source-pill')?.click(); await waitFor('.proof-box'); },
      leave: () => closeOverlay() },
    { target: '#shield-form', title: t('tour.4t'), body: t('tour.4'),
      enter: async () => { closeOverlay(); showPage('shield'); const box = document.getElementById('shield-input'); if (box && !box.value) box.value = SHIELD_EXAMPLE; } },
    { target: '#page-about .about-hero h1', title: t('tour.5t'), body: t('tour.5'), enter: async () => { showPage('about'); } },
  ], { next: t('tour.next'), back: t('tour.back'), skip: t('tour.skip'), done: t('tour.done'), count: t('tour.count') });
}

/** First visit in this tab: the orb, headline and boxes arrive one after another. */
function heroEntrance() {
  let seen = false;
  try { seen = sessionStorage.getItem('pakkam_intro') === '1'; sessionStorage.setItem('pakkam_intro', '1'); } catch (_) { /* private mode */ }
  if (seen || reduceMotion()) return;
  document.body.classList.add('intro');
  setTimeout(() => { document.body.classList.remove('intro'); document.dispatchEvent(new CustomEvent('pakkam:page', { detail: 'home' })); }, 2200);
}

/* ==========================================================================
   15. START-UP AND EVENTS
   ========================================================================== */
function refreshLanguageParts() {
  showHeard('');
  if (!typer.step) { typer.pos = 0; startTyping(); }
  renderWelcomeChips();
  renderVoiceChips();
  renderHomeExamples();
  renderCredits();
  setupSlogan();
  setupStoryPlayer();
  setupAboutTabs();
  applyShieldText();
  applyPrefs();
  loadSchemeFacts().then(() => renderSchemes(null, document.getElementById('scheme-search-input')?.value || ''));
}

document.addEventListener('DOMContentLoaded', () => {
  try { convo.voiceLang = localStorage.getItem('pakkam_voice'); } catch (_) { /* private mode */ }
  applyTheme(state.theme);
  applyLanguage(state.language);
  renderHistory();
  refreshLanguageParts();
  setConversationMode(convo.mode);
  bindSettings();
  applyPrefs();
  loadSources().then(() => renderSchemes(null, document.getElementById('scheme-search-input')?.value || ''));

  document.querySelectorAll('[data-nav]').forEach((node) => {
    node.addEventListener('click', (event) => { event.preventDefault(); showPage(node.dataset.nav); });
  });
  document.getElementById('theme-toggle-btn')?.addEventListener('click', switchTheme);
  document.getElementById('settings-theme-btn')?.addEventListener('click', switchTheme);
  document.querySelector('.skip-link')?.addEventListener('click', (event) => {
    event.preventDefault();
    const heading = document.querySelector('.page-section.active h1, .page-section.active h2');
    if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus(); }
  });
  document.getElementById('footer-privacy')?.addEventListener('click', () => {
    showPage('settings');
    setTimeout(() => document.querySelector('[data-i18n="set.privacyTitle"]')?.closest('.settings-card, section, div')?.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'center' }), 80);
  });
  fillArt();
  heroEntrance();
  watchReveals();
  document.getElementById('tour-start')?.addEventListener('click', startTour);
  if (new URLSearchParams(window.location.search).get('tour') === '1') setTimeout(startTour, 700);
  document.getElementById('composer-mic')?.addEventListener('click', () => orbTap('chat'));
  const messages = chatBox();
  const jump = document.getElementById('jump-latest');
  if (messages && jump) {
    messages.addEventListener('scroll', () => { jump.hidden = messages.scrollHeight - messages.scrollTop - messages.clientHeight < 220; }, { passive: true });
    jump.addEventListener('click', () => { messages.scrollTo({ top: messages.scrollHeight, behavior: reduceMotion() ? 'auto' : 'smooth' }); });
  }
  document.querySelectorAll('#setting-lang [data-lang]').forEach((button) => button.addEventListener('click', () => {
    convo.voiceLang = null;
    try { localStorage.removeItem('pakkam_voice'); } catch (_) { /* private mode */ }
    applyLanguage(button.dataset.lang);
    refreshLanguageParts();
  }));

  // Phones and tablets: the menu opens from the ☰ button.
  const capsule = document.querySelector('.navbar-capsule');
  const burger = document.getElementById('nav-toggle');
  const setMenu = (open) => { capsule?.classList.toggle('nav-open', open); burger?.setAttribute('aria-expanded', String(open)); };
  burger?.addEventListener('click', (event) => { event.stopPropagation(); setMenu(!capsule.classList.contains('nav-open')); });
  document.querySelectorAll('.nav-links [data-nav]').forEach((item) => item.addEventListener('click', () => setMenu(false)));
  document.addEventListener('click', (event) => { if (capsule && !capsule.contains(event.target)) setMenu(false); });

  document.querySelectorAll('.conv-mode-input').forEach((box) => box.addEventListener('change', () => setConversationMode(box.checked)));

  document.getElementById('cta-ask-pakkam')?.addEventListener('click', () => navigateTo('assistant'));
  const heroOrb = document.getElementById('hero-orb-trigger');
  heroOrb?.addEventListener('click', () => orbTap('home'));
  heroOrb?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); orbTap('home'); }
  });
  document.getElementById('assistant-mic-orb')?.addEventListener('click', () => orbTap('chat'));
  document.getElementById('nav-mic-btn')?.addEventListener('click', () => orbTap('chat'));

  document.getElementById('chat-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;
    input.value = '';
    await submitChatQuery(query);
  });
  document.getElementById('scheme-search-input')?.addEventListener('input', (event) => renderSchemes(null, event.target.value));
  document.getElementById('stop-audio-btn')?.addEventListener('click', stopSpeaking);
  document.getElementById('about-listen')?.addEventListener('click', aboutListen);

  document.getElementById('shield-form')?.addEventListener('submit', (event) => {
    event.preventDefault();
    const message = document.getElementById('shield-input').value.trim();
    if (message.length >= 10) checkForward(message);
  });
  document.getElementById('shield-example')?.addEventListener('click', () => { document.getElementById('shield-input').value = SHIELD_EXAMPLE; playHowChecks(); });
  const howChecks = document.querySelector('.how-checks');
  if (howChecks && 'IntersectionObserver' in window) {
    new IntersectionObserver((entries, obs) => { if (entries[0].isIntersecting) { playHowChecks(); obs.disconnect(); } }, { threshold: 0.2 }).observe(howChecks);
  } else howChecks?.classList.add('play');
  document.getElementById('shield-paste')?.addEventListener('click', async () => {
    try { const text = await navigator.clipboard.readText(); if (text) document.getElementById('shield-input').value = text.slice(0, 1500); } catch (_) { document.getElementById('shield-input').focus(); }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (document.querySelector('.proof-overlay, .scheme-drawer')) { closeOverlay(); closeSchemeDrawer(); return; }
    stopSpeaking();
  });
});
