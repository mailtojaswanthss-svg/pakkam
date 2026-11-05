// frontend/js/app.js

const API_BASE = window.PAKKAM_API_BASE || '';

const ASSETS = {
  darkOrb: './assets/images/Dark theme orb.png',
  lightOrb: './assets/images/Light theme orb.png',
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
  language: localStorage.getItem('pakkam_lang') || 'en-IN',
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
  'home.step2Title': 'See the official page', 'home.step2Body': 'Every answer shows the government document and page it comes from.',
  'home.step3Title': 'No page, no answer', 'home.step3Body': 'When the documents do not say it, Pakkam says so instead of guessing.',
  'feature.01': 'See the Proof', 'feature.01body': 'Each answer opens the exact page of the official document.',
  'feature.02body': 'Ask in Tamil, Tanglish, Hindi or English.',
  'assistant.languages': 'Supports Tamil, Tanglish, Hindi & English',
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
  'answer.refused': 'Not in the documents', 'answer.call': 'Helpline', 'answer.didYouMean': 'Which scheme do you mean?',
  'status.tooMany': 'Pakkam is getting a lot of questions. Wait a minute, then ask again.',
  'status.timeout': 'Pakkam took too long to answer. Ask again in a moment.',
  'status.noSpeech': 'I did not hear anything. Tap the orb and try again.',
  'footer.line': 'A student project, not a government service. Always check the official source before you act.',
});
Object.assign(MESSAGES['ta-IN'], {
  'home.title': 'அரசு திட்டங்கள், அதிகாரப்பூர்வ பக்கத்திலிருந்தே.',
  'home.step2Title': 'அரசு பக்கத்தைப் பாருங்கள்', 'home.step2Body': 'ஒவ்வொரு பதிலும் அது வந்த அரசு ஆவணத்தையும் பக்கத்தையும் காட்டும்.',
  'home.step3Title': 'பக்கம் இல்லையேல் பதில் இல்லை', 'home.step3Body': 'ஆவணங்களில் இல்லாததை ஊகிக்காமல், இல்லை என்று நேர்மையாகச் சொல்லும்.',
  'feature.01': 'ஆதாரத்தைப் பாருங்கள்', 'feature.01body': 'ஒவ்வொரு பதிலும் அதிகாரப்பூர்வ ஆவணத்தின் சரியான பக்கத்தைத் திறக்கும்.',
  'feature.02body': 'தமிழ், Tanglish, இந்தி அல்லது ஆங்கிலத்தில் கேளுங்கள்.',
  'assistant.languages': 'தமிழ், Tanglish, இந்தி, ஆங்கிலம்',
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
  'answer.refused': 'ஆவணங்களில் இல்லை', 'answer.call': 'உதவி எண்', 'answer.didYouMean': 'எந்தத் திட்டத்தைக் கேட்கிறீர்கள்?',
  'status.tooMany': 'நிறைய கேள்விகள் வருகின்றன. ஒரு நிமிடம் கழித்துக் கேளுங்கள்.',
  'status.timeout': 'பதில் வர நேரமாகிவிட்டது. மீண்டும் கேளுங்கள்.',
  'status.noSpeech': 'எதுவும் கேட்கவில்லை. உருண்டையைத் தொட்டு மீண்டும் பேசுங்கள்.',
  'footer.line': 'இது ஒரு மாணவர் திட்டம், அரசு சேவை அல்ல. முடிவெடுக்கும் முன் அதிகாரப்பூர்வ ஆதாரத்தைச் சரிபாருங்கள்.',
});
Object.assign(MESSAGES['hi-IN'], {
  'home.title': 'सरकारी योजनाएँ, आधिकारिक पन्ने से समझें।',
  'home.step2Title': 'आधिकारिक पन्ना देखें', 'home.step2Body': 'हर जवाब दिखाता है कि वह किस सरकारी दस्तावेज़ के किस पन्ने से है।',
  'home.step3Title': 'पन्ना नहीं, तो जवाब नहीं', 'home.step3Body': 'दस्तावेज़ों में न हो तो पक्कम अंदाज़ा नहीं लगाता, साफ़ बता देता है।',
  'feature.01': 'सबूत देखें', 'feature.01body': 'हर जवाब आधिकारिक दस्तावेज़ का सही पन्ना खोलता है।',
  'feature.02body': 'तमिल, Tanglish, हिंदी या अंग्रेज़ी में पूछें।',
  'assistant.languages': 'तमिल, Tanglish, हिंदी और अंग्रेज़ी',
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
  'answer.refused': 'दस्तावेज़ों में नहीं', 'answer.call': 'हेल्पलाइन', 'answer.didYouMean': 'आप किस योजना के बारे में पूछ रहे हैं?',
  'status.tooMany': 'बहुत सवाल आ रहे हैं। एक मिनट बाद फिर पूछें।',
  'status.timeout': 'जवाब में देर हो गई। फिर से पूछें।',
  'status.noSpeech': 'कुछ सुनाई नहीं दिया। ऑर्ब टैप करके फिर बोलें।',
  'footer.line': 'यह एक छात्र प्रोजेक्ट है, सरकारी सेवा नहीं। फ़ैसले से पहले आधिकारिक स्रोत देखें।',
});

/* ==========================================================================
   3. TALKING TO THE PAKKAM BACKEND (FastAPI: /ask, /transcribe, /speak, /page, /sources)
   ========================================================================== */
const ASK_TIMEOUT_MS = 120000;
const MAX_VOICE_SECONDS = 30;
// The site's language codes, and the codes the backend takes for speech.
const VOICE_LANG = { 'en-IN': 'en', 'ta-IN': 'ta', 'hi-IN': 'hi' };
const CITATION_MARKER = /\s*\[\d+(?:,\s*\d+)*\]/g;

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

function errorText(error) {
  if (error instanceof ApiError && error.status === 429) return t('status.tooMany');
  if (error instanceof ApiError && error.status === 0) return t('status.timeout');
  // Messages the server writes for people (e.g. "Please remove Aadhaar numbers").
  if (error instanceof ApiError && [400, 413, 422].includes(error.status) && error.message) return error.message;
  return t('status.chatError');
}

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
};

/* ==========================================================================
   4. VOICE: record (WAV, assets from recorder.js) -> /transcribe -> /ask -> /speak
   ========================================================================== */
let recording = null;
let recordingTimer = null;

function setStatus(text) {
  const label = document.getElementById('voice-status-label');
  if (label) label.textContent = text;
}

function showHeard(text) {
  const preview = document.getElementById('live-transcript-preview');
  if (preview) preview.textContent = text;
}

function setBars(level) {
  document.querySelectorAll('.orb-waveform-assembly').forEach((assembly) => {
    assembly.classList.add('audio-reactive');
    assembly.querySelectorAll('.wave-bar').forEach((bar, index) => {
      const shape = [0.38, 0.62, 0.9, 0.72, 0.48][index % 5];
      bar.style.setProperty('--bar-level', String(0.3 + level * shape * 1.5));
    });
  });
}

async function toggleVoiceRecording() {
  if (recording) { await finishRecording(); return; }
  if (!window.PakkamRecorder || !navigator.mediaDevices?.getUserMedia) {
    setOrbState('error');
    setStatus(t('status.voiceError'));
    return;
  }
  stopPlayback();
  navigateTo('assistant');
  try {
    recording = await window.PakkamRecorder.start({
      onLevel: setBars,
      onSilence: () => finishRecording(),
      noSpeechMs: 8000,
    });
  } catch (_) {
    recording = null;
    setOrbState('error');
    setStatus(t('status.micError'));
    return;
  }
  setOrbState('listening');
  setStatus(t('status.listening'));
  showHeard('');
  recordingTimer = setTimeout(() => finishRecording(), MAX_VOICE_SECONDS * 1000);
}

async function finishRecording() {
  if (!recording) return;
  const current = recording;
  recording = null;
  clearTimeout(recordingTimer);
  stopWaveformMeter();
  setOrbState('processing');
  setStatus(t('status.processing'));
  let wav;
  try { wav = await current.stop(); } catch (_) { wav = null; }
  if (!wav || wav.size < 2000) {
    setOrbState('idle');
    setStatus(t('assistant.tap'));
    showHeard(t('status.noSpeech'));
    return;
  }
  const form = new FormData();
  form.append('audio', wav, 'question.wav');
  form.append('language', VOICE_LANG[state.language] || 'ta');
  try {
    const data = await (await api('/transcribe', { method: 'POST', body: form }, 60000)).json();
    const heard = (data.transcript || '').trim();
    if (!heard) {
      setOrbState('idle');
      setStatus(t('assistant.tap'));
      showHeard(t('status.noSpeech'));
      return;
    }
    showHeard(`"${heard}"`);
    setStatus(t('assistant.tap'));
    await submitChatQuery(heard, { voice: true });
  } catch (error) {
    setOrbState('error');
    setStatus(t('assistant.tap'));
    showHeard(error instanceof ApiError && [400, 413, 415, 422].includes(error.status) && error.message
      ? error.message : t('status.voiceError'));
  }
}

function stopPlayback() {
  if (state.currentAudio) {
    state.currentAudio.pause();
    URL.revokeObjectURL(state.currentAudio.src);
  }
  state.currentAudio = null;
  const stopBtn = document.getElementById('stop-audio-btn');
  if (stopBtn) stopBtn.style.display = 'none';
}

// The answer read aloud by Gnani Timbre (/speak returns the WAV itself).
async function playGnaniTTS(text, language) {
  if (!state.autoPlayTTS || !text) return;
  const spoken = text.replace(CITATION_MARKER, '').trim();
  if (!spoken) return;
  try {
    const res = await api('/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: spoken.slice(0, 1200), language: language === 'unknown' ? 'en' : language }),
    }, 60000);
    const url = URL.createObjectURL(await res.blob());
    stopPlayback();
    const audio = new Audio(url);
    state.currentAudio = audio;
    const stopBtn = document.getElementById('stop-audio-btn');
    if (stopBtn) stopBtn.style.display = 'inline-block';
    audio.onended = () => { stopPlayback(); stopWaveformMeter(); setOrbState('idle'); };
    await audio.play();
    setOrbState('speaking');
    try {
      state.audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
      await state.audioContext.resume();
      startWaveformMeter(state.audioContext.createMediaElementSource(audio), true);
    } catch (_) { /* playback still works without the waveform */ }
  } catch (_) {
    // Speech is optional: the written answer is already on screen.
    setOrbState('idle');
  }
}

/* ==========================================================================
   5. ANSWERS WITH PROOF (/ask -> sentences + citations; the page image from /page)
   ========================================================================== */
function citationLabel(c) {
  const pages = c.page_end && c.page_end !== c.page_start ? `${c.page_start}-${c.page_end}` : c.page_start;
  return `${c.document} · ${t('proof.page')} ${pages}`;
}

function openProof(c) {
  closeProof();
  const overlay = el('div', 'proof-overlay');
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', t('proof.title'));
  const box = el('div', 'proof-box glass-panel');
  const close = el('button', 'icon-btn proof-close', '✕');
  close.type = 'button';
  close.setAttribute('aria-label', t('proof.close'));
  close.addEventListener('click', closeProof);
  box.append(close, el('p', 'hero-eyebrow', t('proof.title')), el('h2', 'proof-doc', c.document));
  box.append(el('p', 'proof-meta', `${c.scheme} · ${t('proof.page')} ${c.page_start}${c.document_date ? ` · ${t('documents.dated')} ${c.document_date}` : ''}`));
  box.append(c.checked_by
    ? el('p', 'proof-checked', `✓ ${t('proof.checked')} ${c.checked_by}${c.checked_on ? ` (${c.checked_on})` : ''}`)
    : el('p', 'proof-note', t('proof.unchecked')));
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
    const link = el('a', 'chip-btn', t('proof.source'));
    link.href = c.source_url;
    link.target = '_blank';
    link.rel = 'noopener';
    box.append(link);
  }
  overlay.append(box);
  overlay.addEventListener('click', (event) => { if (event.target === overlay) closeProof(); });
  document.body.append(overlay);
  close.focus();
}

function closeProof() {
  document.querySelector('.proof-overlay')?.remove();
}

function appendChatBubble(role, text, extra = {}) {
  const container = document.getElementById('chat-messages');
  if (!container) return null;
  const bubble = el('div', `chat-bubble ${role}`);
  if (extra.refused) bubble.append(el('p', 'answer-flag', t('answer.refused')));
  bubble.append(el('div', 'answer-text', text));
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
  return bubble;
}

function renderAnswer(data, question) {
  const text = (data.sentences && data.sentences.length)
    ? data.sentences.map((s) => s.text).join(' ')
    : (data.answer || '').replace(CITATION_MARKER, '');
  const bubble = appendChatBubble('ai', text, { refused: data.refused });
  if (!bubble) return text;

  // Proof: each cited page is a button that opens the page itself.
  if (data.citations && data.citations.length) {
    const wrap = el('div', 'citation-pills');
    data.citations.forEach((c) => {
      const pill = el('button', 'citation-tag', `📄 ${citationLabel(c)}${c.checked_by ? ' ✓' : ''}`);
      pill.type = 'button';
      pill.title = t('proof.open');
      pill.addEventListener('click', () => openProof(c));
      wrap.append(pill);
    });
    bubble.append(wrap);
  }

  // "What can I get?": signed amounts per scheme.
  (data.scheme_facts || []).forEach((fact) => {
    const row = el('p', 'answer-fact');
    row.append(el('strong', '', fact.scheme));
    if (fact.amount) row.append(document.createTextNode(` — ${fact.amount}`));
    bubble.append(row);
  });

  // Unclear question: let the person pick the scheme.
  if (data.status === 'needs_clarification' && data.candidate_schemes?.length) {
    bubble.append(el('p', 'answer-flag', t('answer.didYouMean')));
    const chips = el('div', 'citation-pills');
    data.candidate_schemes.slice(0, 4).forEach((scheme) => {
      const chip = el('button', 'chip-btn', scheme);
      chip.type = 'button';
      chip.addEventListener('click', () => submitChatQuery(`${question} (${scheme})`));
      chips.append(chip);
    });
    bubble.append(chips);
  }

  // Refused about a known scheme: its official helpline.
  if (data.refused && data.contact?.helpline) {
    const call = el('a', 'chip-btn', `📞 ${t('answer.call')}: ${data.contact.helpline}`);
    call.href = `tel:${data.contact.helpline.replace(/[^\d+]/g, '')}`;
    bubble.append(call);
  }
  return text;
}

async function submitChatQuery(queryText, options = {}) {
  const question = queryText.trim();
  if (!question) return;
  navigateTo('assistant');
  appendChatBubble('user', question);
  setOrbState('processing');
  setStatus(t('status.processing'));
  try {
    const res = await api('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question.slice(0, 500), voice_mode: Boolean(options.voice) }),
    });
    const data = await res.json();
    const text = renderAnswer(data, question);
    saveToHistory(question, text);
    setStatus(t('assistant.tap'));
    await playGnaniTTS(text, data.language);
    if (!state.currentAudio) setOrbState('idle');
  } catch (error) {
    appendChatBubble('ai', errorText(error));
    setOrbState('error');
    setStatus(t('assistant.tap'));
  }
}

/* ==========================================================================
   6. SCHEMES AND OFFICIAL DOCUMENTS (both from GET /sources: nothing typed in by hand)
   ========================================================================== */
let sources = null;

async function loadSources() {
  if (sources) return sources;
  try {
    sources = await (await api('/sources', {}, 30000)).json();
  } catch (_) {
    sources = null;
  }
  return sources;
}

const QUICK_QUESTIONS = {
  'en-IN': { amount: (s) => `How much money does ${s} give?`, who: (s) => `Who is eligible for ${s}?`, docs: (s) => `What documents are needed for ${s}?` },
  'ta-IN': { amount: (s) => `${s} திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?`, who: (s) => `${s} திட்டத்திற்கு யார் தகுதியானவர்கள்?`, docs: (s) => `${s} திட்டத்திற்கு என்ன ஆவணங்கள் தேவை?` },
  'hi-IN': { amount: (s) => `${s} में कितना पैसा मिलता है?`, who: (s) => `${s} के लिए कौन पात्र है?`, docs: (s) => `${s} के लिए कौन से दस्तावेज़ चाहिए?` },
};

function renderSchemes(_unused, searchQuery = '') {
  const grid = document.getElementById('schemes-grid');
  if (!grid) return;
  grid.replaceChildren();
  if (!sources) {
    grid.append(el('p', 'empty-state', sources === null ? t('documents.offline') : t('documents.loading')));
    return;
  }
  const byScheme = new Map();
  sources.forEach((doc) => {
    if (!byScheme.has(doc.scheme)) byScheme.set(doc.scheme, []);
    byScheme.get(doc.scheme).push(doc);
  });
  const query = searchQuery.trim().toLowerCase();
  const asks = QUICK_QUESTIONS[state.language] || QUICK_QUESTIONS['en-IN'];
  const rows = [...byScheme.entries()]
    .filter(([scheme, docs]) => !query || scheme.toLowerCase().includes(query)
      || docs.some((d) => d.title.toLowerCase().includes(query)))
    .map(([scheme, docs]) => {
      const row = el('article', 'scheme-row');
      const main = el('div', 'scheme-main');
      main.append(el('p', 'scheme-category', `${docs.length} ${t('schemes.docCount')}`), el('h2', '', scheme));
      const chips = el('div', 'citation-pills');
      [['amount', 'schemes.askAmount'], ['who', 'schemes.askWho'], ['docs', 'schemes.askDocs']].forEach(([kind, label]) => {
        const chip = el('button', 'chip-btn', t(label));
        chip.type = 'button';
        chip.addEventListener('click', () => submitChatQuery(asks[kind](scheme)));
        chips.append(chip);
      });
      main.append(chips);
      row.append(main);
      return row;
    });
  if (!rows.length) grid.append(el('p', 'empty-state', t('schemes.empty')));
  else grid.append(...rows);
}

function renderDocuments() {
  const list = document.getElementById('documents-list');
  if (!list) return;
  list.replaceChildren();
  if (!sources) {
    list.append(el('p', 'empty-state', t('documents.offline')));
    return;
  }
  sources.forEach((doc) => {
    const row = el('article', 'scheme-row');
    const main = el('div', 'scheme-main');
    main.append(el('p', 'scheme-category', doc.scheme), el('h2', '', doc.title));
    const meta = [doc.language.toUpperCase(), doc.doc_date ? `${t('documents.dated')} ${doc.doc_date}` : ''].filter(Boolean).join(' · ');
    main.append(el('p', 'scheme-benefit', meta));
    const link = el('a', 'chip-btn', t('documents.open'));
    link.href = doc.source_url;
    link.target = '_blank';
    link.rel = 'noopener';
    main.append(link);
    row.append(main);
    list.append(row);
  });
}

/* ==========================================================================
   7. CONVERSATION HISTORY (this browser only)
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
  if (!state.history.length) {
    list.replaceChildren(el('p', 'empty-state', t('history.empty')));
    return;
  }
  list.replaceChildren(...state.history.map((item) => {
    const article = el('article', 'history-row');
    article.append(el('time', 'history-date', item.date), el('h2', '', item.question), el('p', '', item.answer));
    return article;
  }));
}

/* ==========================================================================
   8. START-UP AND EVENTS
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(state.theme);
  applyLanguage(state.language);
  renderHistory();
  sources = undefined;  // "loading"
  renderSchemes();
  loadSources().then(() => { renderSchemes(null, document.getElementById('scheme-search-input')?.value || ''); renderDocuments(); });

  document.querySelectorAll('[data-nav]').forEach((node) => {
    node.addEventListener('click', (event) => {
      event.preventDefault();
      navigateTo(node.dataset.nav);
    });
  });

  document.getElementById('theme-toggle-btn')?.addEventListener('click', toggleTheme);
  document.getElementById('settings-theme-btn')?.addEventListener('click', toggleTheme);
  document.getElementById('global-lang-select')?.addEventListener('change', (event) => {
    applyLanguage(event.target.value);
    renderDocuments();
  });

  const autoplay = document.getElementById('setting-autoplay-tts');
  if (autoplay) {
    autoplay.checked = state.autoPlayTTS;
    autoplay.addEventListener('change', () => {
      state.autoPlayTTS = autoplay.checked;
      try { localStorage.setItem('pakkam_tts', String(autoplay.checked)); } catch (_) { /* private mode */ }
    });
  }

  document.getElementById('cta-ask-pakkam')?.addEventListener('click', () => navigateTo('assistant'));
  document.getElementById('hero-orb-trigger')?.addEventListener('click', toggleVoiceRecording);
  document.getElementById('assistant-mic-orb')?.addEventListener('click', toggleVoiceRecording);
  document.getElementById('hero-orb-trigger')?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggleVoiceRecording(); }
  });
  document.getElementById('nav-mic-btn')?.addEventListener('click', () => { navigateTo('assistant'); toggleVoiceRecording(); });

  document.getElementById('chat-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;
    input.value = '';
    await submitChatQuery(query);
  });

  document.getElementById('scheme-search-input')?.addEventListener('input', (event) => renderSchemes(null, event.target.value));

  document.getElementById('clear-history-btn')?.addEventListener('click', () => {
    if (!window.confirm(t('history.confirm'))) return;
    state.history = [];
    try { localStorage.removeItem('pakkam_history'); } catch (_) { /* private mode */ }
    renderHistory();
  });

  document.getElementById('stop-audio-btn')?.addEventListener('click', () => {
    stopPlayback();
    stopWaveformMeter();
    setOrbState('idle');
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeProof(); });
});
