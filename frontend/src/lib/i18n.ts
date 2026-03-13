export type Language = "English" | "Hindi" | "Kannada" | "Telugu" | "Tamil";

const translations: Record<string, Record<Language, string>> = {
  dashboard:        { English: "Dashboard",        Hindi: "डैशबोर्ड",           Kannada: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",       Telugu: "డాష్‌బోర్డ్",          Tamil: "டாஷ்போர்ட்" },
  subjects:         { English: "Subjects",         Hindi: "विषय",               Kannada: "ವಿಷಯಗಳು",           Telugu: "విషయాలు",             Tamil: "பாடங்கள்" },
  ai_tutor:         { English: "AI Tutor",         Hindi: "AI ट्यूटर",          Kannada: "AI ಟ್ಯೂಟರ್",         Telugu: "AI ట్యూటర్",           Tamil: "AI டியூட்டர்" },
  mock_tests:       { English: "Mock Tests",       Hindi: "मॉक टेस्ट",          Kannada: "ಅಭ್ಯಾಸ ಪರೀಕ್ಷೆ",       Telugu: "మాక్ టెస్ట్‌లు",        Tamil: "போலி தேர்வுகள்" },
  exam_generator:   { English: "Exam Generator",   Hindi: "परीक्षा जनरेटर",     Kannada: "ಪರೀಕ್ಷೆ ಜನರೇಟರ್",     Telugu: "పరీక్ష జనరేటర్",       Tamil: "தேர்வு ஜெனரேட்டர்" },
  jee_neet:         { English: "JEE / NEET",       Hindi: "JEE / NEET",        Kannada: "JEE / NEET",        Telugu: "JEE / NEET",          Tamil: "JEE / NEET" },
  textbooks:        { English: "Textbooks",        Hindi: "पाठ्यपुस्तक",        Kannada: "ಪಠ್ಯಪುಸ್ತಕಗಳು",      Telugu: "పాఠ్యపుస్తకాలు",       Tamil: "பாடநூல்கள்" },
  admin:            { English: "Admin",            Hindi: "व्यवस्थापक",         Kannada: "ನಿರ್ವಾಹಕ",           Telugu: "అడ్మిన్",              Tamil: "நிர்வாகி" },
  community:        { English: "Community",        Hindi: "समुदाय",             Kannada: "ಸಮುದಾಯ",            Telugu: "కమ్యూనిటీ",           Tamil: "சமூகம்" },
  offline:          { English: "Offline",          Hindi: "ऑफलाइन",            Kannada: "ಆಫ್‌ಲೈನ್",           Telugu: "ఆఫ్‌లైన్",             Tamil: "ஆஃப்லைன்" },
  profile:          { English: "Profile",          Hindi: "प्रोफाइल",           Kannada: "ಪ್ರೊಫೈಲ್",           Telugu: "ప్రొఫైల్",            Tamil: "சுயவிவரம்" },
  loading:          { English: "Loading...",       Hindi: "लोड हो रहा है...",    Kannada: "ಲೋಡ್ ಆಗುತ್ತಿದೆ...",    Telugu: "లోడ్ అవుతోంది...",      Tamil: "ஏற்றுகிறது..." },
  topics_completed: { English: "Topics Completed", Hindi: "पूर्ण विषय",          Kannada: "ಪೂರ್ಣ ವಿಷಯಗಳು",      Telugu: "పూర్తి టాపిక్‌లు",      Tamil: "முடிந்த தலைப்புகள்" },
  tests_taken:      { English: "Tests Taken",      Hindi: "दिए गए टेस्ट",       Kannada: "ತೆಗೆದ ಪರೀಕ್ಷೆಗಳು",    Telugu: "రాసిన పరీక్షలు",       Tamil: "எடுத்த தேர்வுகள்" },
  average_score:    { English: "Average Score",    Hindi: "औसत अंक",            Kannada: "ಸರಾಸರಿ ಅಂಕ",         Telugu: "సగటు స్కోరు",          Tamil: "சராசரி மதிப்பெண்" },
  study_hours:      { English: "Study Hours",      Hindi: "पढ़ाई के घंटे",       Kannada: "ಅಧ್ಯಯನ ಗಂಟೆಗಳು",     Telugu: "అధ్యయన గంటలు",        Tamil: "படிப்பு மணிநேரம்" },
  progress:         { English: "Progress",         Hindi: "प्रगति",              Kannada: "ಪ್ರಗತಿ",              Telugu: "పురోగతి",              Tamil: "முன்னேற்றம்" },
  performance:      { English: "Performance",      Hindi: "प्रदर्शन",            Kannada: "ಪ್ರದರ್ಶನ",            Telugu: "పనితీరు",              Tamil: "செயல்திறன்" },
  recommended:      { English: "Recommended",      Hindi: "अनुशंसित",            Kannada: "ಶಿಫಾರಸು",            Telugu: "సిఫారసు",              Tamil: "பரிந்துரைக்கப்பட்டது" },
  explanation:      { English: "Explanation",      Hindi: "व्याख्या",            Kannada: "ವಿವರಣೆ",             Telugu: "వివరణ",               Tamil: "விளக்கம்" },
  examples:         { English: "Examples",         Hindi: "उदाहरण",             Kannada: "ಉದಾಹರಣೆಗಳು",        Telugu: "ఉదాహరణలు",           Tamil: "எடுத்துக்காட்டுகள்" },
  practice:         { English: "Practice",         Hindi: "अभ्यास",              Kannada: "ಅಭ್ಯಾಸ",              Telugu: "అభ్యాసం",              Tamil: "பயிற்சி" },
  ask_tutor:        { English: "Ask AI Tutor",     Hindi: "AI ट्यूटर से पूछें",   Kannada: "AI ಟ್ಯೂಟರ್ ಕೇಳಿ",     Telugu: "AI ట్యూటర్ అడగండి",    Tamil: "AI ஆசிரியரிடம் கேளுங்கள்" },
  type_message:     { English: "Type a message...",Hindi: "संदेश लिखें...",       Kannada: "ಸಂದೇಶ ಬರೆಯಿರಿ...",    Telugu: "సందేశం టైప్ చేయండి...", Tamil: "செய்தியை தட்டச்சு செய்யுங்கள்..." },
  start_test:       { English: "Start Test",       Hindi: "टेस्ट शुरू करें",      Kannada: "ಪರೀಕ್ಷೆ ಪ್ರಾರಂಭಿಸಿ",   Telugu: "పరీక్ష ప్రారంభించండి",  Tamil: "தேர்வைத் தொடங்கு" },
  language_name:    { English: "English",          Hindi: "हिन्दी",              Kannada: "ಕನ್ನಡ",               Telugu: "తెలుగు",               Tamil: "தமிழ்" },
};

export function t(key: string, language: Language): string {
  const entry = translations[key];
  if (!entry) return key;
  return entry[language] ?? entry["English"] ?? key;
}
