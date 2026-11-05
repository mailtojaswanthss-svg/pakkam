// web/js/app.js
import { detectTalk, replyLanguage, TALK, EXAMPLES } from './talk.js';

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
    if (value) element.textContent = value;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((element) => {
    element.setAttribute('aria-label', t(element.dataset.i18nAria));
  });
  document.querySelectorAll('[data-i18n-title]').forEach((element) => {
    const translated = t(element.dataset.i18nTitle);
    if (element.tagName === 'TITLE') document.title = translated;
    else element.title = translated;
  });
  renderSchemes(activeSchemeCategory, document.getElementById('scheme-search-input')?.value || '');
  renderHistory();
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

  document.querySelectorAll('.nav-item[data-nav]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.nav === pageKey);
  });
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

// Rumour Shield and appeal texts (from the earlier chat page, web-backup/assets/chat.js).
const SHIELD = {
  'en-IN': {
    eyebrow: 'RUMOUR SHIELD', title: 'Is this WhatsApp forward true?', intro: 'Paste the message. Pakkam checks every claim against the official government documents and points out scam signs.',
    placeholder: 'Paste the WhatsApp message here', example: 'Try an example', check: 'Check it',
    checking: 'Checking each claim against the government orders…', failed: 'Pakkam could not check this now. Try again in a minute.',
    overall: { wrong: '❌ This forward is wrong', partly_wrong: '⚠️ Partly wrong', looks_right: '✅ Matches the official documents',
      not_in_documents: '⚠️ Not in any official document. Be careful.', no_claims: 'No scheme claim found in this message.' },
    verdict: { supported: '✅ True', contradicted: '❌ Wrong', not_in_documents: '⚠️ Not in the documents' },
    signs: { unofficial_link: 'The link is not a government website (.gov.in). Do not open it or enter details.',
      official_link: 'The link is a government website (.gov.in).',
      otp: 'It asks for an OTP. Government schemes never ask for your OTP. Never share it.',
      payment: 'It asks for money. Applying for these schemes does not need payment to anyone in a message.',
      personal_data: 'It asks for Aadhaar or bank details. Do not send them to unknown people.',
      urgency: '"Today only" pressure is a common trick. Check first.' },
    warnings: 'Warning signs', share: '📤 Send the correction on WhatsApp',
    correction: 'Fact-check by Pakkam (from the official government documents):',
  },
  'ta-IN': {
    eyebrow: 'வதந்தி கவசம்', title: 'இந்த வாட்ஸ்அப் செய்தி உண்மையா?', intro: 'செய்தியை ஒட்டுங்கள். ஒவ்வொரு கூற்றையும் அதிகாரப்பூர்வ அரசு ஆவணங்களுடன் சரிபார்த்து, மோசடி அறிகுறிகளையும் பக்கம் காட்டும்.',
    placeholder: 'வாட்ஸ்அப் செய்தியை இங்கே ஒட்டுங்கள்', example: 'ஒரு எடுத்துக்காட்டு', check: 'சரிபார்',
    checking: 'ஒவ்வொரு கூற்றும் அரசாணையுடன் சரிபார்க்கப்படுகிறது…', failed: 'இப்போது சரிபார்க்க முடியவில்லை. ஒரு நிமிடம் கழித்து முயற்சிக்கவும்.',
    overall: { wrong: '❌ இந்தச் செய்தி தவறு', partly_wrong: '⚠️ ஓரளவு தவறு', looks_right: '✅ அதிகாரப்பூர்வ ஆவணங்களுடன் பொருந்துகிறது',
      not_in_documents: '⚠️ எந்த அதிகாரப்பூர்வ ஆவணத்திலும் இல்லை. கவனம்.', no_claims: 'இந்தச் செய்தியில் திட்டம் பற்றிய கூற்று இல்லை.' },
    verdict: { supported: '✅ உண்மை', contradicted: '❌ தவறு', not_in_documents: '⚠️ ஆவணங்களில் இல்லை' },
    signs: { unofficial_link: 'இந்த இணைப்பு அரசு இணையதளம் (.gov.in) அல்ல. திறக்க வேண்டாம், விவரங்களைக் கொடுக்க வேண்டாம்.',
      official_link: 'இந்த இணைப்பு அரசு இணையதளம் (.gov.in).',
      otp: 'OTP கேட்கிறது. அரசுத் திட்டங்கள் ஒருபோதும் OTP கேட்பதில்லை. பகிர வேண்டாம்.',
      payment: 'பணம் கேட்கிறது. இந்தத் திட்டங்களுக்கு செய்தி மூலம் யாருக்கும் பணம் கட்டத் தேவையில்லை.',
      personal_data: 'ஆதார் அல்லது வங்கி விவரங்களைக் கேட்கிறது. தெரியாதவர்களுக்கு அனுப்ப வேண்டாம்.',
      urgency: '"இன்று மட்டும்" என்ற அவசரம் ஒரு வழக்கமான ஏமாற்று. முதலில் சரிபாருங்கள்.' },
    warnings: 'எச்சரிக்கை அறிகுறிகள்', share: '📤 திருத்தத்தை வாட்ஸ்அப்பில் அனுப்பு',
    correction: 'பக்கம் சரிபார்ப்பு (அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து):',
  },
  'hi-IN': {
    eyebrow: 'अफ़वाह कवच', title: 'क्या यह व्हाट्सऐप संदेश सच है?', intro: 'संदेश चिपकाएँ। पक्कम हर दावे को आधिकारिक सरकारी दस्तावेज़ों से जाँचता है और धोखाधड़ी के संकेत बताता है।',
    placeholder: 'व्हाट्सऐप संदेश यहाँ चिपकाएँ', example: 'एक उदाहरण', check: 'जाँचें',
    checking: 'हर दावे को सरकारी आदेश से जाँचा जा रहा है…', failed: 'अभी जाँच नहीं हो सकी। एक मिनट बाद कोशिश करें।',
    overall: { wrong: '❌ यह संदेश गलत है', partly_wrong: '⚠️ आंशिक रूप से गलत', looks_right: '✅ आधिकारिक दस्तावेज़ों से मेल खाता है',
      not_in_documents: '⚠️ किसी आधिकारिक दस्तावेज़ में नहीं। सावधान रहें।', no_claims: 'इस संदेश में योजना का कोई दावा नहीं मिला।' },
    verdict: { supported: '✅ सही', contradicted: '❌ गलत', not_in_documents: '⚠️ दस्तावेज़ों में नहीं' },
    signs: { unofficial_link: 'यह लिंक सरकारी वेबसाइट (.gov.in) नहीं है। इसे न खोलें।',
      official_link: 'यह लिंक सरकारी वेबसाइट (.gov.in) है।',
      otp: 'यह OTP माँगता है। सरकारी योजनाएँ कभी OTP नहीं माँगतीं। इसे साझा न करें।',
      payment: 'यह पैसे माँगता है। इन योजनाओं के लिए संदेश से किसी को भुगतान नहीं करना होता।',
      personal_data: 'यह आधार या बैंक विवरण माँगता है। अनजान लोगों को न भेजें।',
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
  const button = el('button', className, label);
  button.type = 'button';
  button.addEventListener('click', onClick);
  return button;
}

function linkChip(label, href) {
  const link = el('a', 'chip-btn', label);
  link.href = href;
  link.target = '_blank';
  link.rel = 'noopener';
  return link;
}

/* ==========================================================================
   4. ORB STATE, STATUS AND SPEECH
   ========================================================================== */
let orbErrorTimer = null;
function orb(name) {
  setOrbState(name);
  clearTimeout(orbErrorTimer);
  // An error ring never stays on: back to idle after 3 s.
  if (name === 'error') orbErrorTimer = setTimeout(() => { setOrbState('idle'); }, 3000);
}

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
    const call = el('a', 'chip-btn', `📞 ${t('answer.call')}: ${helpline}`);
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
  if (c.source_url) box.append(linkChip(t('proof.source'), c.source_url));
}

function renderSections(bubble, data) {
  const sections = sectionsOf(data);
  const named = sections.filter(([key]) => key !== 'other');
  if (named.length < 2) {
    bubble.append(el('div', 'answer-text', data.sentences.map((s) => s.text).join(' ')));
    return;
  }
  sections.forEach(([key, sentences]) => {
    const block = el('div', 'answer-section');
    if (key !== 'other') block.append(el('h4', '', t(`section.${key}`)));
    block.append(el('p', '', sentences.map((s) => s.text).join(' ')));
    bubble.append(block);
  });
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

  if (data.sentences && data.sentences.length) renderSections(bubble, data);
  else bubble.append(el('div', 'answer-text', text));

  if (data.citations && data.citations.length) bubble.append(citationRow(data.citations));

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
      const call = el('a', 'chip-btn', `📞 ${t('answer.call')}: ${data.contact.helpline}`);
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
    if (data.scheme) actions.push(chip(t('answer.docs'), () => showChecklist(data.scheme)));
    actions.push(chip(t('answer.share'), () => shareAnswer(question, text, data.citations?.[0])));
    actions.push(chip(t('answer.print'), () => printAnswer(question, data)));
    if (data.scheme && schemeNames().includes(data.scheme)) actions.push(chip(t('answer.appeal'), () => openAppeal(data.scheme)));
    bubble.append(chipRow(actions));
    const check = chipRow([
      chip(t('answer.yes'), (event) => { event.currentTarget.closest('.answer-row')?.remove(); handleTalk('ack', 'ok', {}); }),
      chip(t('answer.notClear'), (event) => { event.currentTarget.closest('.answer-row')?.remove(); handleTalk('notClear', 'puriyala', {}); }),
    ], t('answer.understood'));
    const feedback = chipRow([
      chip('👍', (event) => sendFeedback(event, data, 'up')),
      chip('👎', (event) => sendFeedback(event, data, 'down')),
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
    if (top && bubble.classList.contains('thinking')) progress.textContent = fill(t('progress.found'), { doc: top.document, page: top.page });
  }).catch(() => {});
  const slow = setTimeout(() => { if (bubble.classList.contains('thinking')) bubble.append(el('p', 'answer-progress', t('progress.slow'))); }, SLOW_MS);

  replyLoading = true;
  const turnGen = speechGen;  // a stop while the answer loads cancels its speech
  try {
    const data = await (await postJson('/ask', body)).json();
    replyLoading = false;
    clearTimeout(slow);
    bubble.classList.remove('thinking');
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
  if (options.voice || options.force || state.autoPlayTTS) await speak(text, language, { rate: options.rate });
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
    return;
  }
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
  set('#page-shield h1', w.title);
  set('#page-shield .page-intro', w.intro);
  set('#shield-input', w.placeholder, 'placeholder');
  set('#shield-example', w.example);
  set('#shield-check', w.check);
}

async function checkForward(message) {
  const w = shieldWords();
  const status = document.getElementById('shield-status');
  const result = document.getElementById('shield-result');
  const button = document.getElementById('shield-check');
  result.replaceChildren();
  status.textContent = w.checking;
  button.disabled = true;
  try {
    const data = await (await postJson('/check-forward', { message: message.slice(0, 1500) }, 180000)).json();
    status.textContent = '';
    result.append(el('h2', `shield-overall shield-${data.overall}`, w.overall[data.overall] || data.overall));
    const correction = [w.correction];
    data.claims.forEach((claim) => {
      const card = el('article', 'shield-claim');
      card.append(el('p', 'shield-verdict', w.verdict[claim.verdict] || claim.verdict), el('h3', '', claim.claim), el('p', '', claim.explanation));
      const cite = claim.answer?.citations?.[0];
      if (cite) card.append(proofButton(cite));
      result.append(card);
      correction.push(`${w.verdict[claim.verdict] || ''} ${claim.claim}: ${claim.explanation}${cite ? ` (${cite.document}, ${t('proof.page')} ${cite.page_start})` : ''}`);
    });
    const signs = data.scam_signs.filter((sign) => sign !== 'official_link');
    if (signs.length) {
      const box = el('div', 'shield-signs');
      box.append(el('h3', '', `⚠️ ${w.warnings}`));
      const list = el('ul');
      signs.forEach((sign) => { list.append(el('li', '', w.signs[sign] || sign)); correction.push(`⚠️ ${w.signs[sign] || sign}`); });
      box.append(list);
      result.append(box);
    }
    if (data.scam_signs.includes('official_link')) result.append(el('p', 'proof-note', w.signs.official_link));
    correction.push('— Pakkam (பக்கம்)');
    result.append(chip(w.share, () => window.open(`https://wa.me/?text=${encodeURIComponent(correction.join('\n'))}`, '_blank', 'noopener'), 'cta-button shield-share'));
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
      const share = chip(t('answer.share'), () => window.open(`https://wa.me/?text=${encodeURIComponent(note.value)}`, '_blank', 'noopener'));
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
  try { sources = await (await api('/sources', {}, 30000)).json(); } catch (_) { sources = null; }
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
    schemeFacts = {};
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
// Thin line icons (24px grid), drawn with currentColor.
const CATEGORY_ICON = {
  women: '<circle cx="12" cy="7" r="3.5"/><path d="M5 21c.8-4 3.6-6.5 7-6.5s6.2 2.5 7 6.5"/>',
  farmers: '<path d="M12 21V10"/><path d="M12 13c-4 0-6-2.5-6-6 3.5 0 6 2 6 6Z"/><path d="M12 11c0-4 2.5-6.5 6-6.5 0 3.8-2.4 6.5-6 6.5Z"/>',
  pension: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  gas: '<path d="M12 21c-3.6 0-6-2.4-6-5.6 0-3.4 2.6-5 3.6-8.4 1.6 1.4 2.4 3 2.4 4.6 1-.8 1.6-2 1.8-3.4 2.2 1.8 4.2 4.2 4.2 7.2C18 18.6 15.6 21 12 21Z"/>',
  children: '<path d="M4 12h16a8 8 0 0 1-16 0Z"/><path d="M9 4c0 1.5 1 1.5 1 3M13 4c0 1.5 1 1.5 1 3"/>',
  health: '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M12 8.5v7M8.5 12h7"/>',
  education: '<path d="M2.5 9 12 4.5 21.5 9 12 13.5Z"/><path d="M6.5 11v4.5c1.5 1.3 3.4 2 5.5 2s4-.7 5.5-2V11"/>',
  welfare: '<path d="M7 3.5h7l4 4v13H7Z"/><path d="M14 3.5v4h4M9.5 12h6M9.5 15.5h4"/>',
};
let activeCategory = 'all';

function schemeMeta(scheme, docs) {
  const hit = SCHEME_META.find(([re]) => re.test(scheme));
  const issuer = hit ? hit[2] : (docs.some((d) => d.language === 'ta') ? 'tn' : '');
  return { category: hit ? hit[1] : 'welfare', issuer };
}

function categoryIcon(category) {
  const span = el('span', 'cat-icon');
  span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${CATEGORY_ICON[category] || CATEGORY_ICON.welfare}</svg>`;
  return span;
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
    const button = chip(`${t(cat === 'all' ? 'schemes.all' : `cat.${cat}`)} · ${count}`, () => {
      activeCategory = cat;
      renderSchemes(null, document.getElementById('scheme-search-input')?.value || '');
    }, `chip-btn filter-chip${activeCategory === cat ? ' active' : ''}`);
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
  if (!shown.length) { grid.append(el('p', 'empty-state', t('schemes.empty'))); return; }
  grid.append(...shown.map((item, index) => {
    const card = el('button', 'scheme-tile');
    card.type = 'button';
    card.style.setProperty('--i', String(index));
    const top = el('div', 'tile-top');
    top.append(categoryIcon(item.category), el('span', 'tile-cat', [t(`cat.${item.category}`), item.issuer ? t(`issuer.${item.issuer}`) : ''].filter(Boolean).join(' · ')));
    card.append(top, el('h2', 'tile-name', item.scheme));
    card.append(el('p', item.facts?.amount ? 'tile-amount' : 'tile-amount muted', item.facts?.amount || t('schemes.noAmount')));
    if (item.facts?.who) card.append(el('p', 'tile-who', item.facts.who));
    const signed = item.facts?.amount_citation?.checked_by || item.facts?.who_citation?.checked_by;
    const foot = el('div', 'tile-foot');
    foot.append(el('span', '', [signed ? `✓ ${t('schemes.verified')}` : '', `${item.docs.length} ${t('schemes.docCount')}`].filter(Boolean).join(' · ')), el('span', 'tile-more', `${t('schemes.details')} →`));
    card.append(foot);
    card.addEventListener('click', () => openSchemeDrawer(item));
    return card;
  }));
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
  head.append(categoryIcon(item.category));
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

function renderHomeExamples() {
  const box = document.getElementById('home-examples');
  if (!box) return;
  const icons = ['💰', '🗣️', '🌾', '🔥'];
  box.replaceChildren(...(EXAMPLES[state.language] || EXAMPLES['en-IN']).map((q, index) => {
    const card = el('button', 'example-card');
    card.type = 'button';
    card.style.setProperty('--i', String(index));
    card.append(el('span', 'example-icon', icons[index % icons.length]), el('span', 'example-text', q), el('span', 'example-go', '→'));
    card.addEventListener('click', () => submitChatQuery(q));
    return card;
  }));
}

/* ==========================================================================
   SETTINGS (this browser only)
   ========================================================================== */
const prefs = (() => {
  const read = (key, fallback) => { try { return localStorage.getItem(key) ?? fallback; } catch (_) { return fallback; } };
  return { speed: Number(read('pakkam_speed', '1')) || 1, easy: read('pakkam_easy', '0') === '1', size: Number(read('pakkam_size', '100')) || 100,
    calm: read('pakkam_calm', '0') === '1', phone: read('pakkam_phone', '0') === '1' };
})();

function savePref(key, value) { try { localStorage.setItem(key, String(value)); } catch (_) { /* private mode */ } }

function applyPrefs() {
  const root = document.documentElement;
  root.classList.toggle('easy', prefs.easy);
  root.classList.toggle('calm', prefs.calm);
  root.style.fontSize = `${prefs.easy ? Math.max(prefs.size, 118) : prefs.size}%`;
  if (window.PakkamRecorder) window.PakkamRecorder.phoneMode = prefs.phone;
  const mark = (selector, attr, value) => document.querySelectorAll(`${selector} [${attr}]`).forEach((b) => {
    const on = b.getAttribute(attr) === String(value);
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', String(on));
  });
  mark('#setting-speed', 'data-speed', prefs.easy ? 0.85 : prefs.speed);
  mark('#setting-size', 'data-size', prefs.size);
  mark('#setting-theme', 'data-theme-choice', state.theme);
  mark('#setting-lang', 'data-lang', state.language);
  const set = (id, value) => { const box = document.getElementById(id); if (box) box.checked = value; };
  set('setting-easy', prefs.easy);
  set('setting-calm', prefs.calm);
  set('setting-phone', prefs.phone);
  set('setting-autoplay-tts', state.autoPlayTTS);
}

function bindSettings() {
  document.querySelectorAll('#setting-speed [data-speed]').forEach((b) => b.addEventListener('click', () => { prefs.speed = Number(b.dataset.speed); savePref('pakkam_speed', prefs.speed); applyPrefs(); }));
  document.querySelectorAll('#setting-size [data-size]').forEach((b) => b.addEventListener('click', () => { prefs.size = Number(b.dataset.size); savePref('pakkam_size', prefs.size); applyPrefs(); }));
  document.querySelectorAll('#setting-theme [data-theme-choice]').forEach((b) => b.addEventListener('click', () => { applyTheme(b.dataset.themeChoice); applyPrefs(); }));
  const toggle = (id, key, onChange) => document.getElementById(id)?.addEventListener('change', (event) => { onChange(event.target.checked); savePref(key, event.target.checked ? '1' : '0'); applyPrefs(); });
  toggle('setting-easy', 'pakkam_easy', (on) => { prefs.easy = on; if (on) prefs.speed = 0.85; });
  toggle('setting-calm', 'pakkam_calm', (on) => { prefs.calm = on; });
  toggle('setting-phone', 'pakkam_phone', (on) => { prefs.phone = on; });
  document.getElementById('setting-autoplay-tts')?.addEventListener('change', (event) => {
    state.autoPlayTTS = event.target.checked;
    savePref('pakkam_tts', event.target.checked);
  });
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
  if (state.currentAudio && button.dataset.playing === '1') {
    stopSpeaking();
    button.dataset.playing = '0';
    button.firstElementChild.textContent = t('about.listen');
    return;
  }
  const intro = t('about.intro');
  text.textContent = intro;
  text.hidden = false;
  button.dataset.playing = '1';
  button.firstElementChild.textContent = t('about.stop');
  await speak(intro, SPEECH_LANG[state.language] || 'en');
  button.dataset.playing = '0';
  button.firstElementChild.textContent = t('about.listen');
}

/* ==========================================================================
   15. START-UP AND EVENTS
   ========================================================================== */
function refreshLanguageParts() {
  showHeard('');
  renderWelcomeChips();
  renderVoiceChips();
  renderHomeExamples();
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
    node.addEventListener('click', (event) => { event.preventDefault(); navigateTo(node.dataset.nav); });
  });
  document.getElementById('theme-toggle-btn')?.addEventListener('click', () => { toggleTheme(); applyPrefs(); });
  document.getElementById('settings-theme-btn')?.addEventListener('click', toggleTheme);
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
  document.getElementById('shield-example')?.addEventListener('click', () => { document.getElementById('shield-input').value = SHIELD_EXAMPLE; });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (document.querySelector('.proof-overlay, .scheme-drawer')) { closeOverlay(); closeSchemeDrawer(); return; }
    stopSpeaking();
  });
});
