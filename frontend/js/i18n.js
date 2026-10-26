/**
 * SmartSilageAI - Internationalization & Language Manager (SIH26111)
 * Complete English & Tamil bilingual translations for dairy farmers, extension officers, and lab personnel.
 */

const I18N = {
  currentLang: localStorage.getItem('smartsilage_lang') || 'en',

  translations: {
    en: {
      // General & Header
      topHeader: "SIH26111: Rapid Silage & Feed Quality System for Dairy Farmers",
      brandTitle: "SmartSilageAI",
      brandSub: "Silage Quality Testing",
      langSwitch: "தமிழ்",
      navHome: "🏠 Home",
      navNewTest: "🧪 Test Silage",
      navDashboard: "📊 Dashboard",
      navHistory: "📋 History",
      navLogin: "👨‍🌾 Farmer Login",
      navRegister: "📝 Register",
      navAdmin: "⚙️ Admin / Jury",
      navDocs: "📖 Docs",

      // Hero
      heroBadge: "🌱 Dairy Forage Decision Support",
      heroTitle: "Smart Silage Quality Testing System",
      heroSubtitle: "Rapid, transparent feed and silage quality screening designed for Indian dairy farmers. Choose your testing mode below:",

      // Modes
      tabFarmer: "👨‍🌾 Farmer Mode (No Lab Report)",
      tabScientific: "🔬 Scientific FQI Prediction Mode",
      farmerModeTitle: "Farmer Mode — Guided On-Farm Assessment",
      farmerModeDesc: "No laboratory report required. Answer everyday questions about your crop, harvest, storage, and silage appearance to receive immediate, practical feeding and storage guidance.",
      farmerModeBadge: "Simple Everyday Language • No Chemistry Needed",
      scientificModeTitle: "Scientific FQI Prediction Mode",
      scientificModeDesc: "Evaluates the 11-feature research Random Forest regression pipeline. Requires verified laboratory proximate measurements (DM, CP, Ash, WSC, Starch) and agronomic trial records.",
      scientificModeBadge: "For Lab Analysts & Field Officers",

      // Farmer Form - Steps
      step1Title: "1. Crop & Harvest",
      step2Title: "2. Storage & Inoculant",
      step3Title: "3. Appearance & Smell",
      step4Title: "4. Lab Check & Notes",

      // Step 1 Questions
      qCrop: "Which crop was used for silage?",
      qCropHint: "Select the primary fodder plant harvested for ensiling.",
      optCorn: "🌽 Corn / Maize",
      optSorghum: "🌾 Sorghum / Jowar",
      optNapier: "🌱 Hybrid Napier / Green Grass",
      optMixed: "🌿 Mixed Forage / Legume",
      optOtherCrop: "❓ Other / Unknown",

      qHarvestTiming: "When was the crop harvested?",
      qHarvestTimingHint: "Grain maturity at harvest directly impacts silage starch and moisture.",
      optMidHarvest: "Recommended mid-milk line (50% grain dent, optimal moisture)",
      optEarlyHarvest: "Early harvest (very watery / milky grain, high seepage)",
      optLateHarvest: "Late harvest (hard dry grain, dry brown stalks)",
      optUnknownMaturity: "I don't know",

      qDelay: "How long after cutting was it sealed?",
      qDelayHint: "Prolonged air exposure before sealing burns sugar and causes heating.",
      optDelayFast: "Sealed quickly (within 0–4 hours of chopping)",
      optDelayMed: "Same day packing (4–6 hours delay)",
      optDelayLong: "Delayed overnight / next day (>20 hours delay)",
      optDelayUnknown: "I don't know",

      // Step 2 Questions
      qStorage: "Which storage method was used?",
      qStorageHint: "The containment structure influences air exclusion and compaction.",
      optStorageBunker: "Silage Pit / Bunker Silo",
      optStorageBags: "Silage Bags / Tube Bags",
      optStorageDrums: "Drums / Barrels / Buckets",
      optStorageStack: "Open Ground Clamp / Stack",
      optStorageUnknown: "I don't know",

      qInoculant: "Was an inoculant / biological additive used?",
      qInoculantHint: "Lactic acid bacterial cultures accelerate acidification.",
      optInocNone: "No inoculant used / None added",
      optInocBacterial: "Yes, biological bacterial culture (homo/heterofermentative)",
      optInocMolasses: "Yes, molasses / salt / mineral blend",
      optInocUnknown: "I don't know",

      // Step 3 Questions
      qMould: "Is there visible mould on the silage?",
      qMouldHint: "Mould patches indicate air leaks and possible dangerous mycotoxins.",
      optMouldNone: "No mould visible / Clean forage",
      optMouldSurface: "Surface layer mould only (top 2–5 cm white crust)",
      optMouldDeep: "Extensive mould / deep pockets (green, black, or pink patches)",
      optMouldUnknown: "I don't know",

      qColor: "What is the colour of the silage?",
      qColorHint: "Healthy silage retains green/golden hues; dark brown indicates heat damage.",
      optColorNormal: "Healthy olive green to golden/light brown",
      optColorCaramel: "Dark brown / caramelized (sweet tobacco/burnt bread smell)",
      optColorBlack: "Black / slimy / wet dark (rotted)",
      optColorPale: "Pale / bleached colour",
      optColorUnknown: "I don't know",

      qOdor: "What does the silage smell like?",
      qOdorHint: "Good fermentation smells clean and pleasantly sour (lactic acid).",
      optOdorLactic: "Pleasant, mildly acidic / fruity / yogurt-like (clean lactic)",
      optOdorAcetic: "Sharp vinegar / pungent acetic smell",
      optOdorButyric: "Foul, rotting, rancid butter / pungent ammonia smell",
      optOdorMusty: "Musty, stale, mouldy cellar smell",
      optOdorUnknown: "I don't know",

      qWarmth: "How does the silage feel inside when touched?",
      qWarmthHint: "Silage should feel cool; warmth indicates ongoing aerobic spoilage.",
      optWarmthCool: "Cool or normal ambient temperature",
      optWarmthWarm: "Warm to touch (mild heating)",
      optWarmthHot: "Hot or steaming (severe aerobic heating)",
      optWarmthUnknown: "I don't know",

      // Step 4 Questions
      qLabReport: "Do you have a certified laboratory test report?",
      qLabReportHint: "Laboratory wet chemistry provides proximate numbers (CP, NDF, Ash, Starch).",
      optLabNo: "No — I do not have a laboratory report (Farmer Mode guidance)",
      optLabYes: "Yes — I have laboratory measurements",

      optionalFieldTools: "Optional Field Measurements (if you have tools):",
      phFieldLabel: "Silage pH (pocket meter or test strip)",
      moistureFieldLabel: "Moisture % (dryer or squeeze estimate)",
      tempFieldLabel: "Internal Temperature (°C with probe)",
      notesFieldLabel: "Field Notes & Observations",
      notesPlaceholder: "e.g. Silo opened last week, cow herd size 8, slight rain during packing...",
      saveToHistoryLabel: "Save this assessment to my dairy farm records (Sample History)",

      // Form Navigation Buttons
      btnNext: "Next Step ➜",
      btnPrev: "⬅ Back",
      btnStartAgain: "↺ Start Again",
      btnCancel: "✕ Cancel",
      btnGetGuidance: "🌾 Get Farmer Guidance",
      btnPredictFQI: "🔬 Run Scientific FQI Prediction",
      btnClear: "Clear Fields",
      btnFillPreset: "✨ Fill Verified Sample",

      // Scientific Mode Fields
      sciSubtitle: "Enter all 11 verified proximate and management parameters. All fields are required by the ML model.",
      groupNutritional: "1. Fresh Nutritional Traits (% Dry Matter Basis)",
      groupAgronomic: "2. Agronomic & Management Decisions",
      dmfLabel: "Fresh Dry Matter (dm.f)",
      dmfHint: "Whole-crop dry matter percentage (typical: 28% - 38%)",
      cpfLabel: "Crude Protein (cp.f)",
      cpfHint: "Total crude protein % of dry matter (typical: 6.5% - 10%)",
      ashfLabel: "Total Ash (ash.f)",
      ashfHint: "Mineral residue % of dry matter (typical: 3.5% - 6.5%)",
      wscfLabel: "Water-Soluble Carbs (wsc.f)",
      wscfHint: "Fermentable sugars % of dry matter (typical: 4% - 12%)",
      starchfLabel: "Starch Content (starch.f)",
      starchfHint: "Grain starch % of dry matter (typical: 20% - 35%)",
      methodLabel: "Silo Containment (method)",
      methodHint: "Trial containment structure (bags vs buckets)",
      inhoculantLabel: "Biological Inoculant (inhoculant)",
      inhoculantHint: "c = control/water, he = heterofermentative, ho = homofermentative",
      doseLabel: "Application Dosage (dose)",
      doseHint: "none, standard (s), half (h), double (d), Unknown",
      delayLabel: "Sealing Delay (delay)",
      delayHint: "Chopping to sealing: D0 (0-4h), D6 (6h), D20 (20-24h)",
      faoLabel: "FAO Maturity Class (fao.class)",
      faoHint: "ea = early (~200 FAO), la = late (~600-700 FAO), Unknown",
      maturityLabel: "Milk-Line Maturity (maturity)",
      maturityHint: "eh = early 1/3, mh = mid 2/3, lh = late, vlh = very late",

      // Results - Farmer Mode
      resFarmerHeading: "Farmer Silage Screening Dossier",
      resWarningTitle: "🔍 Observed Silage Warning Signs",
      resGuidanceTitle: "🚜 Practical Dairy Farm Guidance",
      resLabAdvisoryTitle: "🧪 Certified Laboratory Advisory",
      resDisclaimerHeading: "Important Health & Scientific Notice",
      resDisclaimerBody: "This preliminary guidance is based on validated dairy extension rules (ICAR-NDRI) and observable field indicators. It is NOT an ML-generated FQI prediction or a certified laboratory diagnosis. Appearance and smell alone CANNOT establish that silage is safe for animal consumption (e.g. microscopic mycotoxins or subclinical bacterial spores cannot be detected by eye or nose alone).",
      resSummaryHeading: "Summary of Your Silage Inputs",

      // Results - Scientific Mode
      resSciHeading: "Scientific FQI Regression Output",
      resFqiScoreLabel: "Predicted Fermentation Quality Index (FQI)",
      resSciDisclaimerHeading: "Model Limitations & Research Disclaimer",
      resSciDisclaimerBody: "RESEARCH PROTOTYPE: This Random Forest regression model (n_estimators=500, max_depth=10) was trained on 1,486 research trial observations from the University of Padova. Under rigorous 5-fold Leave-One-Trial-Out cross-validation (GroupKFold on ref.trial), its average out-of-trial R² remained negative (-0.580 ± 1.068, MAE = 9.51), reflecting biological domain shifts between research campaigns. The model has NOT been calibrated on Indian fodder cultivars or tropical agro-climatic zones. In compliance with scientific integrity, no artificial accuracy percentages or Good/Moderate/Poor tiers were invented. This prediction does NOT prove silage is safe for animal feeding.",
      resSciInputsHeading: "Exact 11 Verified Features Used for Inference",

      // Footer
      footerText: "SmartSilageAI • SIH26111 • Ministry of Fisheries, Animal Husbandry & Dairying",
      footerDiscl: "For research and decision support. Consult local veterinarians and accredited dairy nutritionists for clinical ration formulation.",

      // Alerts & Validation
      errFillAllML: "All 11 verified inputs are required for ML prediction. Please complete all highlighted fields.",
      errMissingNum: "Please enter a valid numeric value for",
      loadingPredict: "Calculating continuous FQI via frozen Random Forest pipeline...",
      loadingGuidance: "Analyzing silage observations against dairy agronomic rules...",
      sampleSavedSuccess: "Sample registered in database with ID:"
    },

    ta: {
      // General & Header
      topHeader: "SIH26111: பால் பண்ணையாளர்களுக்கான விரைவான சைலேஜ் மற்றும் தீவன தர பரிசோதனை அமைப்பு",
      brandTitle: "ஸ்மார்ட் சைலேஜ் AI",
      brandSub: "சைலேஜ் தர பரிசோதனை",
      langSwitch: "English",
      navHome: "🏠 முகப்பு",
      navNewTest: "🧪 புதிய பரிசோதனை",
      navDashboard: "📊 டாஷ்போர்டு",
      navHistory: "📋 முந்தைய பதிவுகள்",
      navLogin: "👨‍🌾 உழவர் உள்நுழைவு",
      navRegister: "📝 பதிவு",
      navAdmin: "⚙️ நிர்வாக பார்வை",
      navDocs: "📖 கையேடு",

      // Hero
      heroBadge: "🌱 பால்பண்ணை தீவன மேலாண்மை வழிகாட்டி",
      heroTitle: "ஸ்மார்ட் சைலேஜ் தர பரிசோதனை அமைப்பு",
      heroSubtitle: "இந்திய பால் பண்ணையாளர்களுக்கான விரைவான, வெளிப்படையான தீவன தர பரிசோதனை. கீழே உங்கள் ஆய்வு முறையைத் தேர்ந்தெடுக்கவும்:",

      // Modes
      tabFarmer: "👨‍🌾 விவசாயி முறை (ஆய்வக அறிக்கை தேவையில்லை)",
      tabScientific: "🔬 அறிவியல் FQI கணிப்பு முறை",
      farmerModeTitle: "விவசாயி முறை — எளிய வழிகாட்டுதல்",
      farmerModeDesc: "ஆய்வக அறிக்கை தேவையில்லை. உங்கள் பயிர், அறுவடை நேரம், சேமிப்பு முறை மற்றும் தீவனத்தின் தோற்றம் குறித்த எளிய கேள்விகளுக்கு பதிலளித்து நடைமுறை ஆலோசனைகளைப் பெறுங்கள்.",
      farmerModeBadge: "எளிய அன்றாட தமிழ் • ஆய்வகம் தேவையில்லை",
      scientificModeTitle: "அறிவியல் FQI கணிப்பு முறை",
      scientificModeDesc: "11 சரிபார்க்கப்பட்ட ஆய்வக அளவீடுகள் (உலர்ந்த பொருள், புரதம், சாம்பல், சர்க்கரை, ஸ்டார்ச்) மற்றும் பண்ணை பதிவுகளைக் கொண்டு ML மாதிரி மூலம் FQI குறியீட்டைக் கணிக்கவும்.",
      scientificModeBadge: "ஆய்வக தொழில்நுட்ப வல்லுநர்களுக்கு",

      // Farmer Form - Steps
      step1Title: "1. பயிர் & அறுவடை",
      step2Title: "2. சேமிப்பு & சேர்க்கைகள்",
      step3Title: "3. தோற்றம் & வாசனை",
      step4Title: "4. ஆய்வகம் & குறிப்புகள்",

      // Step 1 Questions
      qCrop: "சைலேஜிற்கு எந்த பயிர் பயன்படுத்தப்பட்டது?",
      qCropHint: "சைலேஜ் தயாரிப்பதற்காக அறுவடை செய்யப்பட்ட முதன்மை தீவனப் பயிரைத் தேர்ந்தெடுக்கவும்.",
      optCorn: "🌽 மக்காச்சோளம் (Corn / Maize)",
      optSorghum: "🌾 சோளம் (Sorghum / Jowar)",
      optNapier: "🌱 கலப்பின நேப்பியர் / பசுந்தீவனம்",
      optMixed: "🌿 கலப்பு தீவனம் / பயறு வகை",
      optOtherCrop: "❓ மற்றவை / எனக்குத் தெரியாது",

      qHarvestTiming: "பயிர் எப்போது அறுவடை செய்யப்பட்டது?",
      qHarvestTimingHint: "அறுவடையின் போது தானிய முதிர்ச்சி சைலேஜின் ஸ்டார்ச் மற்றும் ஈரப்பதத்தை நேரடியாக பாதிக்கிறது.",
      optMidHarvest: "பரிந்துரைக்கப்பட்ட பால்-வரிசை பருவம் (50% தானிய முதிர்ச்சி, சரியான ஈரப்பதம்)",
      optEarlyHarvest: "முன்கூட்டியே அறுவடை (அதிக நீர்ச்சத்து / பால் பருவம், சாறு வெளியேறும்)",
      optLateHarvest: "தாமதமான அறுவடை (காய்ந்த பயிர், கடினமான தானியம்)",
      optUnknownMaturity: "எனக்குத் தெரியாது",

      qDelay: "வெட்டிய பின் எவ்வளவு நேரத்திற்குள் அடைக்கப்பட்டது?",
      qDelayHint: "அடைப்பதில் ஏற்படும் தாமதம் இயற்கை சர்க்கரையை வீணடித்து வெப்பத்தை அதிகரிக்கும்.",
      optDelayFast: "உடனடியாக அடைக்கப்பட்டது (0–4 மணி நேரத்திற்குள்)",
      optDelayMed: "அதே நாளில் அடைக்கப்பட்டது (4–6 மணி நேரம் தாமதம்)",
      optDelayLong: "மறுநாள் வரை தாமதம் (20 மணி நேரத்திற்கு மேல் தாமதம்)",
      optDelayUnknown: "எனக்குத் தெரியாது",

      // Step 2 Questions
      qStorage: "எந்த சேமிப்பு முறை பயன்படுத்தப்பட்டது?",
      qStorageHint: "சேமிக்கும் அமைப்பு காற்று புகாமல் அழுத்துவதை தீர்மானிக்கிறது.",
      optStorageBunker: "குழி / பங்கர் சைலேஜ் (Pit / Bunker)",
      optStorageBags: "சைலேஜ் பைகள் / டியூப் பைகள் (Silage Bags)",
      optStorageDrums: "டிரம் / பீப்பாய் / வாளிகள் (Drums)",
      optStorageStack: "திறந்த தரைக்குவியல் (Open Ground Clamp)",
      optStorageUnknown: "எனக்குத் தெரியாது",

      qInoculant: "இனோகுலண்ட் அல்லது சேர்க்கை பயன்படுத்தப்பட்டதா?",
      qInoculantHint: "லாக்டிக் பாக்டீரியா வளர்ப்பு நொதித்தலை விரைவுபடுத்துகிறது.",
      optInocNone: "எந்த சேர்க்கையும் பயன்படுத்தவில்லை",
      optInocBacterial: "ஆம், பாக்டீரியா வளர்ப்பு / இனோகுலண்ட் சேர்க்கப்பட்டது",
      optInocMolasses: "ஆம், வெல்லப்பாகு / உப்பு / தாதுக்கள் சேர்க்கப்பட்டது",
      optInocUnknown: "எனக்குத் தெரியாது",

      // Step 3 Questions
      qMould: "சைலேஜில் பூஞ்சை ஏதேனும் தென்படுகிறதா?",
      qMouldHint: "பூஞ்சை காற்று உள்ளே புகுந்ததையும் நச்சுத்தன்மையையும் காட்டுகிறது.",
      optMouldNone: "பூஞ்சை எதுவும் இல்லை / சுத்தமான தீவனம்",
      optMouldSurface: "மேற்பரப்பில் மட்டும் வெள்ளை பூஞ்சை படலம் (மேல் 2–5 செ.மீ)",
      optMouldDeep: "அதிக பூஞ்சை / ஆழமான திட்டுகள் (பச்சை, கருப்பு அல்லது இளஞ்சிவப்பு)",
      optMouldUnknown: "எனக்குத் தெரியாது",

      qColor: "சைலேஜின் நிறம் என்ன?",
      qColorHint: "ஆரோக்கியமான சைலேஜ் ஆலிவ் பச்சை முதல் பொன் நிற பழுப்பாக இருக்கும்; அடர் பழுப்பு நிறம் வெப்ப பாதிப்பைக் குறிக்கும்.",
      optColorNormal: "இயற்கையான ஆலிவ் பச்சை முதல் பொன் பழுப்பு நிறம்",
      optColorCaramel: "அடர் பழுப்பு / தீய்ந்த நிறம் (இனிப்பு சுட்ட ரொட்டி வாசனை)",
      optColorBlack: "கருப்பு / பிசுபிசுப்பான அழுகிய நிறம்",
      optColorPale: "வெளிறிய நிறம்",
      optColorUnknown: "எனக்குத் தெரியாது",

      qOdor: "சைலேஜ் என்ன வாசனையாக உள்ளது?",
      qOdorHint: "சரியான நொதித்தல் நல்ல லாக்டிக் புளிப்பு மணமாக இருக்கும்.",
      optOdorLactic: "நல்ல புளிப்பு வாசனை / பழ வாசனை / தயிர் மணம் (லாக்டிக் அமிலம்)",
      optOdorAcetic: "கடுமையான வினிகர் நெடி (அசிட்டிக் அமிலம்)",
      optOdorButyric: "அழுகிய துர்நாற்றம் / அமோனியா நெடி (பியூட்ரிக் அமிலம்)",
      optOdorMusty: "பூஞ்சை வாசனை / மூடிய அறை நெடி",
      optOdorUnknown: "எனக்குத் தெரியாது",

      qWarmth: "உட்புறம் தொட்டால் எப்படி உணர்கிறது?",
      qWarmthHint: "சைலேஜ் குளிர்ந்து இருக்க வேண்டும்; சூடு காற்று படுவதால் கெட்டுப்போவதை காட்டுகிறது.",
      optWarmthCool: "சாதாரண அறை வெப்பநிலை / குளிர்ச்சி",
      optWarmthWarm: "தொட்டால் வெதுவெதுப்பான சூடு (மிதமான வெப்பம்)",
      optWarmthHot: "அதிக வெப்பம் அல்லது புகை வரும் நிலை",
      optWarmthUnknown: "எனக்குத் தெரியாது",

      // Step 4 Questions
      qLabReport: "உங்களிடம் ஆய்வக சோதனை அறிக்கை உள்ளதா?",
      qLabReportHint: "ஆய்வக ஈர வேதியியல் பரிசோதனை புரதம், சாம்பல், ஸ்டார்ச் போன்ற துல்லியமான அளவுகளைத் தருகிறது.",
      optLabNo: "இல்லை — என்னிடம் ஆய்வக அறிக்கை இல்லை (விவசாயி முறை வழிகாட்டுதல்)",
      optLabYes: "ஆம் — என்னிடம் ஆய்வக அளவீடுகள் உள்ளன",

      optionalFieldTools: "விருப்ப அளவீடுகள் (கருவிகள் இருந்தால் மட்டும் நிரப்பவும்):",
      phFieldLabel: "சைலேஜ் pH (டிஜிட்டல் கருவி அல்லது தாள்)",
      moistureFieldLabel: "ஈரப்பதம் % (அளவீடு அல்லது பிழிந்து பார்த்தல்)",
      tempFieldLabel: "உட்புற வெப்பநிலை (°C)",
      notesFieldLabel: "பண்ணைக் குறிப்புகள் & அவதானிப்புகள்",
      notesPlaceholder: "எ.கா. கடந்த வாரம் குழி திறக்கப்பட்டது, மாடுகளின் எண்ணிக்கை 8, அறுவடையில் மழை...",
      saveToHistoryLabel: "இந்த பரிசோதனையை எனது பண்ணை வரலாற்று பதிவேட்டில் சேமிக்கவும்",

      // Form Navigation Buttons
      btnNext: "அடுத்து ➜",
      btnPrev: "⬅ பின்னே",
      btnStartAgain: "↺ மீண்டும் தொடங்கு",
      btnCancel: "✕ ரத்து செய்",
      btnGetGuidance: "🌾 வழிகாட்டுதலைப் பெறுக",
      btnPredictFQI: "🔬 FQI கணிக்கவும்",
      btnClear: "அழிக்கவும்",
      btnFillPreset: "✨ மாதிரி மதிப்புகளை நிரப்பவும்",

      // Scientific Mode Fields
      sciSubtitle: "சரிபார்க்கப்பட்ட 11 ஆய்வக மற்றும் மேலாண்மை அளவுருக்களையும் உள்ளிடவும். ML மாதிரிக்கு அனைத்து புலங்களும் கட்டாயமாகும்.",
      groupNutritional: "1. புதிய ஊட்டச்சத்து பண்புகள் (% உலர்ந்த பொருள் அடிப்படையில்)",
      groupAgronomic: "2. பயிர் மேலாண்மை முடிவுகள்",
      dmfLabel: "உலர்ந்த பொருள் % (dm.f)",
      dmfHint: "முழு பயிர் உலர் சதவீத அளவு (வழக்கமான வரம்பு: 28% - 38%)",
      cpfLabel: "கச்சா புரதம் % (cp.f)",
      cpfHint: "உலர் பொருளில் மொத்த புரத சதவீதம் (வழக்கமான வரம்பு: 6.5% - 10%)",
      ashfLabel: "சாம்பல் சத்து % (ash.f)",
      ashfHint: "தாது சாம்பல் சதவீதம் (வழக்கமான வரம்பு: 3.5% - 6.5%)",
      wscfLabel: "கரையும் சர்க்கரை % (wsc.f)",
      wscfHint: "நொதிக்கும் இயற்கை சர்க்கரை அளவு (வழக்கமான வரம்பு: 4% - 12%)",
      starchfLabel: "ஸ்டார்ச் சத்து % (starch.f)",
      starchfHint: "தானிய மாவுச்சத்து சதவீதம் (வழக்கமான வரம்பு: 20% - 35%)",
      methodLabel: "சேமிப்பு கொள்கலன் (method)",
      methodHint: "bags (பைகள்) அல்லது buckets (வாளிகள்)",
      inhoculantLabel: "உயிரியல் சேர்க்கை (inhoculant)",
      inhoculantHint: "c = சேர்க்கை இல்லை/தண்ணீர், he = ஹெட்டிரோ, ho = ஹோமோ",
      doseLabel: "பயன்படுத்திய அளவு (dose)",
      doseHint: "none (இல்லை), s (வழக்கமான), h (பாதி), d (இரட்டிப்பு), Unknown",
      delayLabel: "அடைப்பு தாமதம் (delay)",
      delayHint: "D0 (0-4 மணி), D6 (6 மணி), D20 (20-24 மணி)",
      faoLabel: "FAO முதிர்ச்சி வகுப்பு (fao.class)",
      faoHint: "ea = முன்கூட்டிய (200 FAO), la = தாமதமான (600-700 FAO), Unknown",
      maturityLabel: "தானிய முதிர்ச்சி நிலை (maturity)",
      maturityHint: "eh = 1/3 பால் நிலை, mh = 2/3 பால் நிலை, lh = முழு முதிர்ச்சி, vlh = மிகத் தாமதம்",

      // Results - Farmer Mode
      resFarmerHeading: "விவசாயி சைலேஜ் பரிசோதனை அறிக்கை",
      resWarningTitle: "🔍 கண்டறியப்பட்ட எச்சரிக்கை அறிகுறிகள்",
      resGuidanceTitle: "🚜 நடைமுறை பால்பண்ணை வழிகாட்டுதல்",
      resLabAdvisoryTitle: "🧪 சான்றளிக்கப்பட்ட ஆய்வக பரிந்துரை",
      resDisclaimerHeading: "முக்கிய பாதுகாப்பு மற்றும் அறிவியல் அறிவிப்பு",
      resDisclaimerBody: "இந்த பூர்வாங்க வழிகாட்டுதல் சரிபார்க்கப்பட்ட பால்பண்ணை அறிவியல் விதிகள் (ICAR-NDRI) மற்றும் காணக்கூடிய பண்ணை அறிகுறிகளின் அடிப்படையிலானது. இது ML மாதிரி கணிப்பு அல்லது சான்றளிக்கப்பட்ட ஆய்வக நோய் கண்டறிதல் அல்ல. தோற்றம் மற்றும் வாசனை மட்டுமே தீவனம் விலங்குகளுக்கு முற்றிலும் பாதுகாப்பானது என்பதை உறுதிப்படுத்த முடியாது (கண்ணுக்குத் தெரியாத பூஞ்சை நச்சுகள் அல்லது பாக்டீரியா வித்துகள் வாசனையின்றி இருக்கலாம்).",
      resSummaryHeading: "நீங்கள் உள்ளிட்ட தகவல்களின் சுருக்கம்",

      // Results - Scientific Mode
      resSciHeading: "அறிவியல் FQI மாதிரி கணிப்பு வெளியீடு",
      resFqiScoreLabel: "கணிக்கப்பட்ட நொதித்தல் தரக் குறியீடு (FQI)",
      resSciDisclaimerHeading: "மாதிரி வரம்புகள் & ஆராய்ச்சி அறிவிப்பு",
      resSciDisclaimerBody: "ஆராய்ச்சி மாதிரி அறிவிப்பு: இந்த ரேண்டம் ஃபாரஸ்ட் மாதிரி பதுவா பல்கலைக்கழகத்தின் 1,486 ஆராய்ச்சி சோதனைகளில் பயிற்றுவிக்கப்பட்டது. 5-பிரிவு வெளி-சோதனை சரிபார்ப்பில் (Leave-One-Trial-Out GroupKFold), இதன் R² எதிர்மறையாக இருந்தது (-0.580 ± 1.068, MAE = 9.51). இது இந்தியப் பயிர்கள் மற்றும் வெப்பமண்டல காலநிலைகளில் இன்னும் சரிபார்க்கப்படவில்லை. அறிவியல் ஒருமைப்பாட்டின் படி எந்த போலி 'நன்று / நடுத்தரம் / மோசம்' லேபிள்களும் உருவாக்கப்படவில்லை. இந்த எண் மதிப்பு தீவனம் பாதுகாப்பானது என்பதை நிரூபிக்காது.",
      resSciInputsHeading: "கணிப்பிற்கு பயன்படுத்தப்பட்ட சரியான 11 அளவுருக்கள்",

      // Footer
      footerText: "ஸ்மார்ட் சைலேஜ் AI • SIH26111 • மத்திய மீன்வளம், கால்நடை பராமரிப்பு & பால்வள அமைச்சகம்",
      footerDiscl: "ஆராய்ச்சி மற்றும் வழிகாட்டுதலுக்கு மட்டுமே. மாடுகளுக்கான தீவன விகிதத்தை துல்லியமாக நிர்ணயிக்க உள்ளூர் கால்நடை மருத்துவர்களை அணுகவும்.",

      // Alerts & Validation
      errFillAllML: "அறிவியல் FQI கணிப்பிற்கு 11 அளவுருக்களும் கட்டாயமாகும். தயவுசெய்து விடுபட்ட புலங்களை நிரப்பவும்.",
      errMissingNum: "தயவுசெய்து சரியான எண்ணை உள்ளிடவும்:",
      loadingPredict: "ரேண்டம் ஃபாரஸ்ட் மாதிரி மூலம் தொடர்ச்சியான FQI கணக்கிடப்படுகிறது...",
      loadingGuidance: "பால்பண்ணை அறிவியல் விதிகளின்படி தகவல்கள் பகுப்பாய்வு செய்யப்படுகின்றன...",
      sampleSavedSuccess: "பதிவேட்டில் சேமிக்கப்பட்ட மாதிரி எண்:"
    }
  },

  t(key) {
    const lang = this.currentLang;
    if (this.translations[lang] && this.translations[lang][key] !== undefined) {
      return this.translations[lang][key];
    }
    if (this.translations.en && this.translations.en[key] !== undefined) {
      return this.translations.en[key];
    }
    return key;
  },

  setLanguage(lang) {
    if (lang !== 'en' && lang !== 'ta') lang = 'en';
    this.currentLang = lang;
    localStorage.setItem('smartsilage_lang', lang);
    document.documentElement.lang = lang;
    this.applyLanguage();
  },

  toggleLanguage() {
    const nextLang = this.currentLang === 'en' ? 'ta' : 'en';
    this.setLanguage(nextLang);
  },

  applyLanguage() {
    // Update elements with data-i18n attribute
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key) {
        el.textContent = this.t(key);
      }
    });

    // Update placeholders with data-i18n-placeholder attribute
    const inputs = document.querySelectorAll('[data-i18n-placeholder]');
    inputs.forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        el.setAttribute('placeholder', this.t(key));
      }
    });

    // Update titles with data-i18n-title attribute
    const titled = document.querySelectorAll('[data-i18n-title]');
    titled.forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (key) {
        el.setAttribute('title', this.t(key));
      }
    });

    // Update language toggle button text if exists
    const toggleBtns = document.querySelectorAll('.lang-toggle-btn');
    toggleBtns.forEach(btn => {
      btn.innerHTML = this.currentLang === 'en' 
        ? '<span>🇮🇳</span> <span>தமிழ்</span>' 
        : '<span>🇬🇧</span> <span>English</span>';
    });

    // Dispatch event for custom JS listeners
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: this.currentLang } }));
  }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  I18N.applyLanguage();
});
