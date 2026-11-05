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
  history: JSON.parse(localStorage.getItem('pakkam_history') || '[]'),
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
   3. VOICE RECORDING (GNANI PRISMA STT) & AUDIO PLAYBACK (GNANI TIMBRE TTS)
   ========================================================================== */
async function toggleVoiceRecording() {
  const statusLabel = document.getElementById('voice-status-label');
  const preview = document.getElementById('live-transcript-preview');

  if (state.isRecording && state.mediaRecorder) {
    state.mediaRecorder.stop();
    state.isRecording = false;
    stopWaveformMeter();
    state.micStream?.getTracks().forEach((track) => track.stop());
    state.micStream = null;
    setOrbState('processing');
    if (statusLabel) statusLabel.textContent = t('status.processing');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.micStream = stream;
    state.audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
    await state.audioContext.resume();
    startWaveformMeter(state.audioContext.createMediaStreamSource(stream));
    state.audioChunks = [];
    state.mediaRecorder = new MediaRecorder(stream);

    state.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) state.audioChunks.push(e.data);
    };

    state.mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      const audioBlob = new Blob(state.audioChunks, { type: 'audio/webm' });
      await sendAudioToGnaniSTT(audioBlob);
    };

    state.mediaRecorder.start();
    state.isRecording = true;
    navigateTo('assistant');
    setOrbState('listening');
    if (statusLabel) statusLabel.textContent = t('status.listening');
    if (preview) preview.textContent = `Listening in ${state.language}...`;
  } catch (err) {
    stopWaveformMeter();
    setOrbState('error');
    if (statusLabel) statusLabel.textContent = t('status.micError');
  }
}

async function sendAudioToGnaniSTT(audioBlob) {
  const statusLabel = document.getElementById('voice-status-label');
  const preview = document.getElementById('live-transcript-preview');

  const formData = new FormData();
  formData.append('audio', audioBlob, 'voice_query.webm');
  formData.append('language', state.language);

  try {
    const res = await fetch(`${API_BASE}/api/v1/voice/stt`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('STT endpoint returned non-200');
    const data = await res.json();
    const transcript = data.transcript || data.text || '';

    if (preview) preview.textContent = `"${transcript}"`;
    if (statusLabel) statusLabel.textContent = t('assistant.tap');
    if (transcript.trim()) {
      await submitChatQuery(transcript);
    } else {
      setOrbState('idle');
    }
  } catch (err) {
    setOrbState('error');
    if (statusLabel) statusLabel.textContent = t('assistant.tap');
    if (preview) preview.textContent = t('status.voiceError');
  }
}

async function playGnaniTTS(text) {
  if (!state.autoPlayTTS || !text) return;
  const stopBtn = document.getElementById('stop-audio-btn');

  try {
    const res = await fetch(`${API_BASE}/api/v1/voice/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: state.language }),
    });
    if (!res.ok) return;

    const data = await res.json();
    const audioSrc = data.audio_url || (data.audio_base64 ? `data:audio/wav;base64,${data.audio_base64}` : null);
    if (!audioSrc) return;

    if (state.currentAudio) state.currentAudio.pause();
    state.currentAudio = new Audio(audioSrc);
    if (stopBtn) stopBtn.style.display = 'inline-block';

    state.currentAudio.onended = () => {
      if (stopBtn) stopBtn.style.display = 'none';
      stopWaveformMeter();
      setOrbState('idle');
    };
    await state.currentAudio.play();
    setOrbState('speaking');
    try {
      const audioUrl = new URL(audioSrc, window.location.href);
      if (audioSrc.startsWith('data:') || audioUrl.origin === window.location.origin) {
        state.audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
        await state.audioContext.resume();
        startWaveformMeter(state.audioContext.createMediaElementSource(state.currentAudio), true);
      }
    } catch (_) {
      // Audio playback remains available if waveform access is restricted.
    }
  } catch (_) {
    // Fail gracefully if TTS stream is unavailable
  }
}

/* ==========================================================================
   4. RAG CHAT (BGE-M3 + QDRANT + BGE RERANKER + CLAUDE/GEMINI)
   ========================================================================== */
function appendChatBubble(role, text, citations = [], containerId = 'chat-messages') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;

  const content = document.createElement('div');
  content.textContent = text;
  bubble.appendChild(content);

  if (citations && citations.length > 0) {
    const citeWrap = document.createElement('div');
    citeWrap.className = 'citation-pills';
    citations.forEach((cite) => {
      const pill = document.createElement('span');
      pill.className = 'citation-tag';
      pill.textContent = `${cite.source || cite.title || 'Official Gazette'}${cite.page ? ` • p.${cite.page}` : ''}`;
      citeWrap.appendChild(pill);
    });
    bubble.appendChild(citeWrap);
  }

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

async function submitChatQuery(queryText, containerId = 'chat-messages') {
  const container = document.getElementById(containerId);
  if (container && containerId !== 'chat-messages' && container.querySelector('[data-empty-hint]')) {
    container.replaceChildren();
  }
  appendChatBubble('user', queryText, [], containerId);
  setOrbState('processing');
  const statusLabel = document.getElementById('voice-status-label');
  if (statusLabel) statusLabel.textContent = t('status.processing');

  try {
    const res = await fetch(`${API_BASE}/api/v1/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: queryText,
        language: state.language,
        document_id: state.activeDocumentId,
      }),
    });

    if (!res.ok) throw new Error('RAG query failed');
    const data = await res.json();
    const answer = data.answer || data.response || 'No response returned.';
    const citations = data.citations || data.sources || [];

    appendChatBubble('ai', answer, citations, containerId);
    saveToHistory(queryText, answer);
    await playGnaniTTS(answer);
    if (!state.currentAudio || state.currentAudio.ended) {
      setOrbState('idle');
      if (statusLabel) statusLabel.textContent = t('assistant.tap');
    }
  } catch (err) {
    appendChatBubble('ai', t('status.chatError'), [], containerId);
    setOrbState('error');
    if (statusLabel) statusLabel.textContent = t('assistant.tap');
  }
}

/* ==========================================================================
   5. DOCUMENT ASSISTANT (PYMUPDF + TESSERACT OCR)
   ========================================================================== */
async function handleDocumentUpload(file) {
  const statusBanner = document.getElementById('ocr-status-banner');
  const summaryBox = document.getElementById('doc-summary-box');
  const selectedFile = document.getElementById('selected-file');
  const progress = document.getElementById('upload-progress');
  const preview = document.getElementById('pdf-preview');
  if (!file) return;
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    statusBanner.textContent = t('documents.invalid');
    return;
  }

  if (state.documentPreviewUrl) URL.revokeObjectURL(state.documentPreviewUrl);
  state.documentPreviewUrl = URL.createObjectURL(file);
  selectedFile.hidden = false;
  selectedFile.textContent = `${t('documents.selected')}: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
  preview.hidden = false;
  preview.replaceChildren();
  const frame = document.createElement('iframe');
  frame.src = state.documentPreviewUrl;
  frame.title = t('documents.preview');
  preview.appendChild(frame);
  statusBanner.textContent = t('documents.uploading');
  summaryBox.textContent = '';
  progress.hidden = false;
  progress.value = 0;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', state.language);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${API_BASE}/api/v1/documents/upload`);
  xhr.upload.addEventListener('progress', (event) => {
    if (event.lengthComputable) progress.value = Math.round((event.loaded / event.total) * 100);
  });
  xhr.addEventListener('load', () => {
    progress.hidden = true;
    if (xhr.status < 200 || xhr.status >= 300) {
      statusBanner.textContent = t('documents.error');
      setOrbState('error');
      return;
    }
    try {
      const data = JSON.parse(xhr.responseText);
      state.activeDocumentId = data.document_id || data.id || null;
      statusBanner.textContent = data.status || t('documents.ready');
      summaryBox.textContent = data.summary || '';
      setOrbState('idle');
    } catch (_) {
      statusBanner.textContent = t('documents.error');
    }
  });
  xhr.addEventListener('error', () => {
    progress.hidden = true;
    statusBanner.textContent = t('documents.error');
    setOrbState('error');
  });
  xhr.send(formData);
}

/* ==========================================================================
   6. GOVERNMENT SCHEME EXPLORER & CONVERSATION HISTORY
   ========================================================================== */
const INITIAL_SCHEMES = [
  {
    title: 'PM-KISAN Samman Nidhi',
    category: 'agriculture',
    eligibility: 'Small and marginal farmer families with cultivable land.',
    benefits: '₹6,000 per year in three equal installments via Direct Benefit Transfer.',
    docs: 'Aadhaar Card, Land Holding Papers, Bank Account Details.',
  },
  {
    title: 'Ayushman Bharat (PM-JAY)',
    category: 'healthcare',
    eligibility: 'Low-income households listed in SECC database.',
    benefits: 'Health insurance cover up to ₹5 Lakh per family per year for secondary and tertiary care.',
    docs: 'Aadhaar Card, Ration Card / PM-JAY Family ID.',
  },
  {
    title: 'Pradhan Mantri Awas Yojana (PMAY)',
    category: 'housing',
    eligibility: 'EWS, LIG, and MIG households without a pucca house.',
    benefits: 'Interest subsidy on housing loans and direct financial assistance for construction.',
    docs: 'Aadhaar, Income Certificate, Proof of No Pucca House.',
  },
  {
    title: 'Pudhumai Penn / Higher Education Scholarship',
    category: 'education',
    eligibility: 'Students enrolled in undergraduate degree/diploma programs from government schools.',
    benefits: '₹1,000 monthly financial assistance directly to student bank account.',
    docs: 'School Transfer Certificate, College Bonafide, Aadhaar-linked Bank Passbook.',
  },
];

function renderSchemes(filterCategory = 'all', searchQuery = '') {
  const grid = document.getElementById('schemes-grid');
  if (!grid) return;

  const filtered = INITIAL_SCHEMES.filter((item) => {
    const matchesCategory = filterCategory === 'all' || item.category === filterCategory;
    const query = searchQuery.toLowerCase();
    const matchesQuery = [item.title, item.benefits, item.eligibility, item.docs]
      .some((value) => value.toLowerCase().includes(query));
    return matchesCategory && matchesQuery;
  });

  if (!filtered.length) {
    grid.innerHTML = `<p class="empty-state">${t('schemes.empty')}</p>`;
    return;
  }
  const categoryNames = {
    agriculture: t('category.agriculture'), education: t('category.education'),
    healthcare: t('category.healthcare'), housing: t('category.housing'),
  };
  grid.innerHTML = filtered.map((scheme) => `
    <article class="scheme-row">
      <div class="scheme-main">
        <p class="scheme-category">${categoryNames[scheme.category] || scheme.category}</p>
        <h2>${scheme.title}</h2>
        <p class="scheme-benefit"><span>${t('schemes.benefits')}</span> ${scheme.benefits}</p>
      </div>
      <details class="scheme-details">
        <summary>${t('schemes.details')}</summary>
        <dl>
          <div><dt>${t('schemes.eligibility')}</dt><dd>${scheme.eligibility}</dd></div>
          <div><dt>${t('schemes.documents')}</dt><dd>${scheme.docs}</dd></div>
        </dl>
      </details>
    </article>
  `).join('');
}

function saveToHistory(question, answer) {
  state.history.unshift({
    id: Date.now(),
    date: new Date().toLocaleDateString(),
    question,
    answer,
  });
  localStorage.setItem('pakkam_history', JSON.stringify(state.history.slice(0, 30)));
  renderHistory();
}

function renderHistory() {
  const list = document.getElementById('history-list');
  if (!list) return;
  if (state.history.length === 0) {
    list.replaceChildren();
    const empty = document.createElement('p');
    empty.className = 'empty-state';
    empty.textContent = t('history.empty');
    list.appendChild(empty);
    return;
  }
  list.replaceChildren(...state.history.map((item) => {
    const article = document.createElement('article');
    article.className = 'history-row';
    const date = document.createElement('time');
    date.className = 'history-date';
    date.textContent = item.date;
    const question = document.createElement('h2');
    question.textContent = item.question;
    const answer = document.createElement('p');
    answer.textContent = item.answer;
    article.append(date, question, answer);
    return article;
  }));
}

/* ==========================================================================
   7. INITIALIZATION & EVENT LISTENERS
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(state.theme);
  applyLanguage(state.language);
  renderSchemes();
  renderHistory();

  // Navbar page navigation
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(el.dataset.nav);
    });
  });

  // Theme toggles
  document.getElementById('theme-toggle-btn')?.addEventListener('click', toggleTheme);
  document.getElementById('settings-theme-btn')?.addEventListener('click', toggleTheme);

  // Language switcher
  const langSelect = document.getElementById('global-lang-select');
  if (langSelect) {
    langSelect.addEventListener('change', (e) => applyLanguage(e.target.value));
  }

  // Homepage CTA & Orb triggers
  document.getElementById('cta-ask-pakkam')?.addEventListener('click', () => navigateTo('assistant'));
  document.getElementById('hero-orb-trigger')?.addEventListener('click', toggleVoiceRecording);
  document.getElementById('assistant-mic-orb')?.addEventListener('click', toggleVoiceRecording);
  document.getElementById('hero-orb-trigger')?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleVoiceRecording();
    }
  });
  document.getElementById('nav-mic-btn')?.addEventListener('click', () => {
    navigateTo('assistant');
    toggleVoiceRecording();
  });

  // Chat submission
  document.getElementById('chat-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;
    input.value = '';
    await submitChatQuery(query);
  });

  // Document upload & contextual Q&A
  document.getElementById('pdf-upload-input')?.addEventListener('change', (e) => {
    handleDocumentUpload(e.target.files[0]);
  });
  const dropzone = document.getElementById('pdf-dropzone');
  const fileInput = document.getElementById('pdf-upload-input');
  document.getElementById('browse-pdf-btn')?.addEventListener('click', () => fileInput?.click());
  dropzone?.addEventListener('click', (event) => {
    if (event.target.closest('#browse-pdf-btn')) return;
    fileInput?.click();
  });
  dropzone?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      fileInput?.click();
    }
  });
  ['dragenter', 'dragover'].forEach((eventName) => dropzone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add('is-dragging');
  }));
  ['dragleave', 'drop'].forEach((eventName) => dropzone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove('is-dragging');
  }));
  dropzone?.addEventListener('drop', (event) => handleDocumentUpload(event.dataTransfer.files[0]));

  document.getElementById('doc-qa-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('doc-qa-input');
    const query = input.value.trim();
    if (!query) return;
    if (!state.activeDocumentId) {
      document.getElementById('ocr-status-banner').textContent = t('documents.askHint');
      return;
    }
    input.value = '';
    await submitChatQuery(query, 'doc-qa-thread');
  });

  // Scheme category filtering & search
  document.querySelectorAll('#scheme-category-bar .filter-tab').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#scheme-category-bar .filter-tab').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeSchemeCategory = btn.dataset.category;
      const q = document.getElementById('scheme-search-input')?.value || '';
      renderSchemes(activeSchemeCategory, q);
    });
  });

  document.getElementById('scheme-search-input')?.addEventListener('input', (e) => {
    renderSchemes(activeCategory, e.target.value);
  });

  // Clear history
  document.getElementById('clear-history-btn')?.addEventListener('click', () => {
    if (!window.confirm(t('history.confirm'))) return;
    state.history = [];
    localStorage.removeItem('pakkam_history');
    renderHistory();
  });

  document.getElementById('stop-audio-btn')?.addEventListener('click', () => {
    state.currentAudio?.pause();
    state.currentAudio = null;
    stopWaveformMeter();
    setOrbState('idle');
    document.getElementById('stop-audio-btn').style.display = 'none';
  });
});
