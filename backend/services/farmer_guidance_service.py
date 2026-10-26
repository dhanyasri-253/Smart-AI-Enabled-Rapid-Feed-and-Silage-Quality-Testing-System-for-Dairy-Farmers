"""
Farmer Guidance Service for SmartSilageAI (SIH26111)
Provides transparent, rule-based agronomic and sensory screening guidance for dairy farmers
WITHOUT requiring laboratory reports or scientific terminology.
Follows ICAR-NDRI (National Dairy Research Institute) forage conservation benchmarks.
Explicitly separate from the 11-feature ML Random Forest regression pipeline.
"""
from typing import Dict, Any, List, Optional


def evaluate_farmer_mode(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates ordinary dairy farmer observations (crop, harvest stage, delay, storage,
    inoculant, mould, colour, smell, warmth, lab report availability).
    Produces an actionable, honest guidance dossier in both English and Tamil.
    NEVER fabricates an ML FQI score or synthetic quality tiers.
    """
    crop = str(data.get("crop", "Corn / Maize"))
    harvest_timing = str(data.get("harvest_timing", "Unknown"))
    sealing_delay = str(data.get("sealing_delay", "Unknown"))
    storage_method = str(data.get("storage_method", "Unknown"))
    inoculant_used = str(data.get("inoculant_used", "Unknown"))
    visible_mould = str(data.get("visible_mould", "None"))
    silage_color = str(data.get("silage_color", "Normal"))
    silage_odor = str(data.get("silage_odor", "Clean"))
    temperature_feeling = str(data.get("temperature_feeling", "Cool"))
    has_lab_report = bool(data.get("lab_report_available", False))
    ph = data.get("ph")
    moisture = data.get("moisture")
    temp_c = data.get("temperature")

    warning_signs: List[Dict[str, Any]] = []
    guidance_en: List[str] = []
    guidance_ta: List[str] = []
    lab_reasons_en: List[str] = []
    lab_reasons_ta: List[str] = []
    requires_lab_attention = False

    # 1. MOULD EVALUATION
    if "Deep" in visible_mould or "extensive" in visible_mould.lower() or "green" in visible_mould.lower() or "black" in visible_mould.lower():
        requires_lab_attention = True
        warning_signs.append({
            "category": "Mould / Fungal Risk",
            "category_ta": "பூஞ்சை நச்சு ஆபத்து",
            "severity": "danger",
            "title": "Severe Fungal Contamination Detected",
            "title_ta": "அதிக பூஞ்சை வளர்ச்சி கண்டறியப்பட்டுள்ளது",
            "description": "Green, black, or pink mould patches produce hazardous mycotoxins (Aflatoxin B1, Zearalenone, DON, T-2). These toxins cause liver damage, milk yield drop, reproductive failure, and immunosuppression in dairy cattle.",
            "description_ta": "பச்சை அல்லது கருப்பு நிற பூஞ்சைகள் ஆபத்தான பூஞ்சை நச்சுகளை (Mycotoxins) உருவாக்குகின்றன. இது பாலின் அளவை குறைத்து, மாடுகளுக்கு கருச்சிதைவு மற்றும் கல்லீரல் பாதிப்பை ஏற்படுத்தும்."
        })
        guidance_en.append("CRITICAL: Discard heavily mouldy portions completely. NEVER mix mouldy silage into feed or Total Mixed Ration (TMR).")
        guidance_ta.append("அவசர எச்சரிக்கை: பூஞ்சை பிடித்த பகுதிகளை முழுமையாக அப்புறப்படுத்தவும். இதனை ஒருபோதும் மாடுகளின் தீவனத்துடன் கலக்க வேண்டாம்.")
        lab_reasons_en.append("Visible fungal growth requires certified laboratory ELISA/HPLC mycotoxin testing to ensure milk safety.")
        lab_reasons_ta.append("பூஞ்சை வளர்ச்சி உள்ளதால், பாலின் பாதுகாப்பை உறுதிப்படுத்த ஆய்வக மைக்கோடாக்சின் சோதனை அவசியம்.")
    elif "Surface" in visible_mould or "white" in visible_mould.lower():
        requires_lab_attention = True
        warning_signs.append({
            "category": "Mould / Fungal Risk",
            "category_ta": "மேற்பரப்பு பூஞ்சை",
            "severity": "warning",
            "title": "Surface Yeast / Aerobic Crust",
            "title_ta": "மேற்பரப்பில் வெள்ளை பூஞ்சை படலம்",
            "description": "White surface mould (usually yeasts like Candida/Pichia) indicates air penetration through torn polythene or loose top compaction. Spores cause respiratory irritation.",
            "description_ta": "மேற்பரப்பில் உள்ள வெள்ளை பூஞ்சை காற்று உட்புகுந்ததால் ஏற்படுகிறது. இது தீவனத்தின் ஊட்டச்சத்தை குறைக்கும்."
        })
        guidance_en.append("Skim off and discard the top 5–10 cm spoilt surface layer. Do not feed this layer to heifers or milch cows.")
        guidance_ta.append("மேல்புறத்தில் கெட்டுப்போன 5-10 செ.மீ அடுக்கை வெட்டி அப்புறப்படுத்தவும். இதனை கறவை மாடுகளுக்கு கொடுக்க வேண்டாம்.")
        guidance_en.append("Inspect plastic covering for punctures, tears, or rodent damage, and weigh down edges tightly with tyres or sandbags.")
        guidance_ta.append("தார்ப்பாயில் கிழிசல்கள் உள்ளதா என சரிபார்த்து, ஓரங்களை மணல் மூட்டைகள் கொண்டு காற்று புகாதவாறு இறுக்கமாக மூடவும்.")
    else:
        warning_signs.append({
            "category": "Mould / Fungal Risk",
            "category_ta": "பூஞ்சை நிலை",
            "severity": "success",
            "title": "No Visible Mould Patches",
            "title_ta": "வெளிப்படையான பூஞ்சை இல்லை",
            "description": "No visible fungal mycelium observed. Note that microscopic spores or odorless toxins cannot be ruled out by eye alone.",
            "description_ta": "பூஞ்சை எதுவும் தென்படவில்லை. எனினும் நுண் பூஞ்சை நச்சுகளை வெறும் கண்ணால் மட்டுமே முழுமையாக உறுதிப்படுத்த முடியாது."
        })

    # 2. ODOUR / SMELL EVALUATION
    if "Foul" in silage_odor or "rancid" in silage_odor.lower() or "ammonia" in silage_odor.lower():
        requires_lab_attention = True
        warning_signs.append({
            "category": "Fermentation Odour",
            "category_ta": "நொதித்தல் வாசனை",
            "severity": "danger",
            "title": "Clostridial Putrefaction / Butyric Odour",
            "title_ta": "அழுகிய துர்நாற்றம் (பியூட்ரிக் அமிலம்)",
            "description": "A foul rancid butter or sharp ammonia smell indicates secondary fermentation by Clostridium bacteria. Plant proteins have been broken down into amines and ammonia, causing severe palatability drop and risk of ketosis.",
            "description_ta": "அழுகிய துர்நாற்றம் அல்லது அமோனியா நெடி குளோஸ்ட்ரிடியல் பாக்டீரியாக்களால் புரதங்கள் சிதைந்து பியூட்ரிக் அமிலம் உருவானதைக் குறிக்கிறது. இதனால் மாடுகள் தீவனத்தை உட்கொள்ளாது மற்றும் கீட்டோசிஸ் நோய் ஏற்படும்."
        })
        guidance_en.append("Do NOT feed foul or rancid silage to high-producing fresh cows or pregnant heifers. It can trigger metabolic ketosis and unpalatability.")
        guidance_ta.append("துர்நாற்றம் வீசும் சைலேஜை சினை மாடுகளுக்கோ அல்லது அதிக பால் கறக்கும் மாடுகளுக்கோ கொடுக்க வேண்டாம்.")
        lab_reasons_en.append("Butyric fermentation indicates severe protein loss and potential spore contamination in milk.")
        lab_reasons_ta.append("பியூட்ரிக் நொதித்தல் தீவிர புரத இழப்பையும், பாலில் பாக்டீரியா வித்துகள் பரவும் அபாயத்தையும் குறிக்கிறது.")
    elif "Vinegar" in silage_odor or "acetic" in silage_odor.lower():
        warning_signs.append({
            "category": "Fermentation Odour",
            "category_ta": "நொதித்தல் வாசனை",
            "severity": "warning",
            "title": "Excess Acetic Acid / Prolonged Fermentation",
            "title_ta": "அதிக வினிகர் நெடி (அசிட்டிக் அமிலம்)",
            "description": "Sharp vinegar smell indicates prolonged heterolactic fermentation or ensiling of very wet forage. While preserved, high acetic acid can depress daily dry matter intake.",
            "description_ta": "கடுமையான வினிகர் நெடி அதிகப்படியான ஈரப்பதத்தால் நொதித்தல் தாமதமானதைக் குறிக்கிறது. இது தீவன உட்கொள்ளும் அளவைக் குறைக்கலாம்."
        })
        guidance_en.append("Aerate the required daily portion for 30–60 minutes before feeding, or blend with dry hay to improve intake.")
        guidance_ta.append("தீவனம் கொடுப்பதற்கு முன் 30 நிமிடங்கள் காற்றில் உலர வைக்கவும் அல்லது உலர் தீவனத்துடன் கலந்து வழங்கவும்.")
    elif "Musty" in silage_odor or "mould" in silage_odor.lower():
        requires_lab_attention = True
        warning_signs.append({
            "category": "Fermentation Odour",
            "category_ta": "நொதித்தல் வாசனை",
            "severity": "danger",
            "title": "Musty Aerobic Deterioration",
            "title_ta": "பூஞ்சை மற்றும் மக்கல் வாசனை",
            "description": "Musty basement or rotting smell indicates active aerobic spoilage by yeasts, molds, and bacillus bacteria.",
            "description_ta": "பூஞ்சை வாசனை காற்று உள்ளே சென்று தீவனம் கெட்டுப்போவதை உறுதிப்படுத்துகிறது."
        })
        guidance_en.append("Accelerate face removal to at least 20 cm daily to get ahead of the spoilage front.")
        guidance_ta.append("தினமும் 20 செ.மீ ஆழத்திற்கு தீவனத்தை விரைவாக வெட்டி எடுத்து பயன்படுத்தவும்.")
    else:
        warning_signs.append({
            "category": "Fermentation Odour",
            "category_ta": "நொதித்தல் வாசனை",
            "severity": "success",
            "title": "Desirable Lactic / Acidic Aroma",
            "title_ta": "சிறந்த லாக்டிக் புளிப்பு மணம்",
            "description": "Pleasant, clean, mildly acidic fruity or yogurt-like aroma typical of sound lactic acid preservation.",
            "description_ta": "நல்ல புளிப்பு அல்லது தயிர் போன்ற மணம் லாக்டிக் அமிலம் சரியான முறையில் உருவாகியுள்ளதைக் காட்டுகிறது."
        })

    # 3. COLOUR EVALUATION
    if "Black" in silage_color or "slimy" in silage_color.lower():
        requires_lab_attention = True
        warning_signs.append({
            "category": "Silage Colour & Physical Integrity",
            "category_ta": "தீவனத்தின் நிறம்",
            "severity": "danger",
            "title": "Slimy Black Rotting / Anaerobic Breakdown",
            "title_ta": "பிசுபிசுப்பான கருப்பு நிற அழுகல்",
            "description": "Black, slimy, or water-soaked silage is completely rotted by enterobacteria and clostridia. Contains toxic degradation products.",
            "description_ta": "கருப்பாக பிசுபிசுப்புடன் கூடிய தீவனம் முற்றிலும் அழுகிவிட்டது. இதில் நச்சுப் பொருட்கள் உருவாகியிருக்கும்."
        })
        guidance_en.append("Immediately discard black and slimy silage. It is toxic and unfit for any animal feeding.")
        guidance_ta.append("கருப்பு நிற அழுகிய தீவனத்தை உடனடியாக குப்பையில் அப்புறப்படுத்தவும். இதனை மாடுகளுக்கு எக்காரணம் கொண்டும் உணவாக வழங்கக் கூடாது.")
    elif "Dark brown" in silage_color or "caramel" in silage_color.lower():
        warning_signs.append({
            "category": "Silage Colour & Physical Integrity",
            "category_ta": "தீவனத்தின் நிறம்",
            "severity": "warning",
            "title": "Caramelized / Heat-Damaged Forage (Maillard Reaction)",
            "title_ta": "தீய்ந்த அடர் பழுப்பு நிறம் (வெப்ப பாதிப்பு)",
            "description": "Dark brown or tobacco-brown colour with a sweet, baked-bread smell indicates internal overheating (>45°C). Sugars and amino acids have caramelized, rendering crude protein largely indigestible.",
            "description_ta": "அடர் பழுப்பு நிறம் சைலேஜ் உள்ளே அதிக வெப்பமடைந்ததைக் குறிக்கிறது. இதனால் புரதச் சத்து வீணாகி மாடுகளால் செரிக்க முடியாமல் போகும்."
        })
        guidance_en.append("Protein digestibility is reduced in dark caramelized silage. Supplement with oilcake or bypass protein concentrates in the ration.")
        guidance_ta.append("தீய்ந்த நிற சைலேஜில் புரதச்சத்து குறைவாகவே உறிஞ்சப்படும். இதற்கு ஈடாக மாடுகளுக்கு பிண்ணாக்கு அல்லது கலப்பு தீவனம் அதிகமாக வழங்கவும்.")
    elif "Pale" in silage_color or "bleached" in silage_color.lower():
        warning_signs.append({
            "category": "Silage Colour & Physical Integrity",
            "category_ta": "தீவனத்தின் நிறம்",
            "severity": "warning",
            "title": "Bleached / Overmature Forage",
            "title_ta": "வெளிறிய நிறம்",
            "description": "Very pale or bleached silage indicates the crop was harvested too late when stems were fully dried and lignified.",
            "description_ta": "வெளிறிய நிறம் பயிர் மிகவும் முதிர்ந்து காய்ந்த பின் அறுவடை செய்யப்பட்டதைக் காட்டுகிறது."
        })
    else:
        warning_signs.append({
            "category": "Silage Colour & Physical Integrity",
            "category_ta": "தீவனத்தின் நிறம்",
            "severity": "success",
            "title": "Healthy Olive Green to Golden Brown",
            "title_ta": "இயற்கையான ஆலிவ் பச்சை / பொன் பழுப்பு நிறம்",
            "description": "Normal colour preservation indicating chlorophyll integrity and minimal heating during anaerobic consolidation.",
            "description_ta": "சரியான பச்சையம் மற்றும் நிறம் பேணப்பட்டுள்ளது, வெப்ப சேதம் ஏற்படவில்லை என்பதை காட்டுகிறது."
        })

    # 4. WARMTH & INTERNAL TEMPERATURE EVALUATION
    if "Hot" in temperature_feeling or "steaming" in temperature_feeling.lower() or (temp_c is not None and temp_c > 40.0):
        requires_lab_attention = True
        warning_signs.append({
            "category": "Internal Temperature / Aerobic Heat",
            "category_ta": "சைலேஜ் உட்புற வெப்பநிலை",
            "severity": "danger",
            "title": "Active High-Temperature Heating (>40°C)",
            "title_ta": "அதிக வெப்பம் / புகை வரும் நிலை (>40°C)",
            "description": "Silage is actively heating upon air exposure. Oxygen has reactivated aerobic yeasts and molds, burning digestible nutrients (carbohydrates and sugars) into carbon dioxide and heat.",
            "description_ta": "தீவனத்தில் காற்று படுவதால் ஈஸ்ட்கள் செயல்பட்டு சத்துக்களை எரித்து அதிக வெப்பத்தை உருவாக்குகின்றன."
        })
        guidance_en.append("Never feed hot or steaming silage directly. Discard the hot outer layer and feed only cool, interior silage.")
        guidance_ta.append("சூடாக இருக்கும் சைலேஜை நேரடியாக போட வேண்டாம். சூடான மேல் பகுதியை அகற்றிவிட்டு, குளிர்ந்த உட்பகுதியை மட்டும் வழங்கவும்.")
    elif "Warm" in temperature_feeling or (temp_c is not None and temp_c > 32.0):
        warning_signs.append({
            "category": "Internal Temperature / Aerobic Heat",
            "category_ta": "சைலேஜ் உட்புற வெப்பநிலை",
            "severity": "warning",
            "title": "Mild Heating / Aerobic Instability",
            "title_ta": "மிதமான வெப்பம் (காற்று உட்புகுதல்)",
            "description": "Slightly elevated temperature indicates trapped air or slow feed-out rate at the pit face.",
            "description_ta": "வெதுவெதுப்பான சூடு உள்ளே காற்று தங்கியுள்ளதை அல்லது தீவனம் மெதுவாக எடுக்கப்படுவதை குறிக்கிறது."
        })
        guidance_en.append("Increase daily feed-out rate to at least 15–20 cm depth straight across the entire silo face to prevent heating advancing inward.")
        guidance_ta.append("குழியின் முகப்பு பகுதி முழுவதும் தினமும் குறைந்தது 15–20 செ.மீ ஆழத்திற்கு நேராக வெட்டி எடுத்து பயன்படுத்தவும்.")
    else:
        warning_signs.append({
            "category": "Internal Temperature / Aerobic Heat",
            "category_ta": "சைலேஜ் உட்புற வெப்பநிலை",
            "severity": "success",
            "title": "Cool / Stable Anaerobic Mass",
            "title_ta": "குளிர்ந்த நிலையான நிலை",
            "description": "Internal temperature matches ambient conditions, confirming sound anaerobic dormancy.",
            "description_ta": "தீவனம் வெப்பமடையாமல் நிலையாக குளிர்ந்து உள்ளது."
        })

    # 5. HARVEST TIMING & MATURITY
    if "Early" in harvest_timing:
        warning_signs.append({
            "category": "Harvest Agronomy",
            "category_ta": "அறுவடை பருவம்",
            "severity": "warning",
            "title": "Early / Watery Harvest",
            "title_ta": "முன்கூட்டியே அறுவடை (அதிக நீர்ச்சத்து)",
            "description": "Harvesting at early milky stage leads to low starch content, high effluent (seepage) runoff, and risk of prolonged fermentation.",
            "description_ta": "பால் பருவத்தில் முன்கூட்டியே அறுவடை செய்தால் நீர்ச்சத்து அதிகமாகி சாறு வெளியேறி சத்துக்கள் வீணாகும்."
        })
        guidance_en.append("Ensure drainage channels around the pit carry silage seepage away so it is not re-absorbed into the lower bales.")
        guidance_ta.append("சைலேஜ் சாறு தேங்காமல் வெளியேற வடிகால் வசதியை உறுதி செய்யவும்.")
    elif "Late" in harvest_timing:
        warning_signs.append({
            "category": "Harvest Agronomy",
            "category_ta": "அறுவடை பருவம்",
            "severity": "warning",
            "title": "Late / Dry Harvest",
            "title_ta": "தாமதமான அறுவடை (அதிக நார் / காய்ந்த பயிர்)",
            "description": "Harvesting overmature, dry corn or sorghum makes compaction difficult. Trapped oxygen causes mold pockets. Grains may pass undigested in cow dung unless crushed.",
            "description_ta": "பயிர் காய்ந்த பின் அறுவடை செய்தால் காற்றை வெளியேற்றி அழுத்துவது கடினம். தானியங்கள் சரியாக அரைக்கப்படாவிட்டால் சாணத்தில் செரிக்காமல் வெளியேறும்."
        })
        guidance_en.append("Check dairy cow dung. If whole uncracked corn grains appear, kernel processing was insufficient during chopping.")
        guidance_ta.append("சாணத்தில் முழு சோள தானியங்கள் தென்படுகிறதா என கவனிக்கவும்; தானியங்கள் நன்றாக உடைக்கப்பட வேண்டும்.")
    elif "Recommended" in harvest_timing or "mid" in harvest_timing.lower():
        warning_signs.append({
            "category": "Harvest Agronomy",
            "category_ta": "அறுவடை பருவம்",
            "severity": "success",
            "title": "Optimal Harvest Stage (1/2 to 2/3 Milk-Line)",
            "title_ta": "சரியான அறுவடை பருவம் (50% தானிய முதிர்ச்சி)",
            "description": "Harvested at ideal grain dent and 32–35% whole-crop dry matter for maximum digestible energy.",
            "description_ta": "சரியான ஈரப்பதம் மற்றும் தானிய முதிர்ச்சியில் அறுவடை செய்யப்பட்டுள்ளது."
        })

    # 6. SEALING DELAY
    if "Delayed" in sealing_delay or ">20" in sealing_delay:
        warning_signs.append({
            "category": "Packing & Sealing Delay",
            "category_ta": "அடைப்பதில் தாமதம்",
            "severity": "warning",
            "title": "Extended Packing Delay (>20 Hours)",
            "title_ta": "நீண்ட நேர தாமதம் (20 மணி நேரத்திற்கு மேல்)",
            "description": "Leaving chopped forage uncompacted overnight causes plant cellular respiration to consume natural sugars, leading to nutrient loss and heating before anaerobic fermentation can begin.",
            "description_ta": "அறுவடை செய்து நீண்ட நேரம் கழித்து அடைப்பதால் இயற்கை சர்க்கரை வீணாகி வெப்பம் அதிகரிக்கிறது."
        })
        guidance_en.append("In future ensiling, seal within 4 hours of chopping. Rapid packing is the single most critical factor for silage success.")
        guidance_ta.append("அடுத்த முறை பயிரை வெட்டிய 4 மணி நேரத்திற்குள் காற்று புகாமல் அழுத்தி அடைத்து விடவும்.")
    elif "Immediate" in sealing_delay or "0" in sealing_delay:
        warning_signs.append({
            "category": "Packing & Sealing Delay",
            "category_ta": "அடைப்பதில் தாமதம்",
            "severity": "success",
            "title": "Rapid Packing (Within 0–4 Hours)",
            "title_ta": "விரைவான அடைப்பு (4 மணி நேரத்திற்குள்)",
            "description": "Swift packing quickly halted aerobic respiration, preserving water-soluble sugars for lactic bacteria.",
            "description_ta": "விரைவாக அடைக்கப்பட்டதால் சர்க்கரை சத்துக்கள் சேமிக்கப்பட்டு சிறந்த தரம் கிடைக்கிறது."
        })

    # 7. STORAGE METHOD
    if "Stack" in storage_method or "clamp" in storage_method.lower():
        warning_signs.append({
            "category": "Storage Structure",
            "category_ta": "சேமிப்பு முறை",
            "severity": "warning",
            "title": "Unwalled Open Clamp / Stack",
            "title_ta": "திறந்த தரைக்குவியல்",
            "description": "Unwalled silage clamps experience higher surface spoilage (20–40% losses) along sloped shoulders compared to concrete bunkers or silage bags.",
            "description_ta": "சுவர்கள் இல்லாத திறந்த குவியல்களில் விளிம்பு பகுதிகளில் 20-40% தீவனம் கெட்டுப்போக வாய்ப்புள்ளது."
        })
        guidance_en.append("Keep plastic tightly weighted on slopes with soil, tyres, or gravel bags to minimize shoulder spoilage.")
        guidance_ta.append("குவியலின் சாய்வான பக்கங்களில் காற்று புகாதவாறு மண் அல்லது டயர்களை வைத்து பலமாக அழுத்தவும்.")

    # 8. FIELD MEASUREMENTS (IF ENTERED)
    if ph is not None:
        try:
            f_ph = float(ph)
            if 3.7 <= f_ph <= 4.2:
                warning_signs.append({
                    "category": "Measured Silage Acidity (pH)",
                    "category_ta": "அளவிடப்பட்ட pH (புளிப்புத் தன்மை)",
                    "severity": "success",
                    "title": f"Optimal Silage pH ({f_ph:.1f})",
                    "title_ta": f"சிறந்த pH அளவு ({f_ph:.1f})",
                    "description": f"pH {f_ph:.1f} is in the ideal preservation range (3.7–4.2), thoroughly inhibiting pathogenic bacteria.",
                    "description_ta": f"pH {f_ph:.1f} என்பது தீவனத்தை பாதுகாப்பாக வைக்கும் சரியான அமில அளவாகும்."
                })
            elif f_ph > 4.6:
                requires_lab_attention = True
                warning_signs.append({
                    "category": "Measured Silage Acidity (pH)",
                    "category_ta": "அளவிடப்பட்ட pH (புளிப்புத் தன்மை)",
                    "severity": "danger",
                    "title": f"Elevated Silage pH ({f_ph:.1f})",
                    "title_ta": f"அபாயகரமான உயர் pH அளவு ({f_ph:.1f})",
                    "description": f"pH {f_ph:.1f} is significantly above the safe silage threshold (4.2). Silage may be unstable with high risk of clostridial degradation.",
                    "description_ta": f"pH {f_ph:.1f} என்பது பாதுகாப்பான அளவை (4.2) விட மிக அதிகம். தீவனம் கெட்டுப்போக வாய்ப்புள்ளது."
                })
                lab_reasons_en.append(f"Silage pH ({f_ph:.1f}) exceeds safe benchmark. Laboratory testing is advised to check volatile fatty acid ratios.")
                lab_reasons_ta.append(f"pH அளவு ({f_ph:.1f}) அதிகமாக உள்ளதால் விரிவான ஆய்வகப் பரிசோதனை தேவை.")
        except (ValueError, TypeError):
            pass

    # DEFAULT PRACTICAL GUIDANCE IF NOT ALREADY POPULATED
    if not guidance_en:
        guidance_en.append("Continue current daily feed-out rate (minimum 15–20 cm straight face removal daily).")
        guidance_ta.append("தற்போது எடுக்கும் தீவன அளவை (தினமும் 15-20 செ.மீ நேராக) தொடர்ந்து பராமரிக்கவும்.")
        guidance_en.append("Keep edges of plastic sheeting weighed down tightly after every feeding to prevent secondary air ingress.")
        guidance_ta.append("தீவனம் எடுத்த பிறகு தார்ப்பாயை காற்று புகாதவாறு உடனடியாக மூடி வைக்கவும்.")
        guidance_en.append("Introduce silage gradually over 7–10 days into cow diet to allow rumen microbes to adapt smoothly.")
        guidance_ta.append("புதிய சைலேஜை மாடுகளுக்கு கொடுக்கும்போது 7-10 நாட்கள் படிப்படியாக பழக்கப்படுத்தவும்.")

    # LAB TESTING RECOMMENDATIONS
    if requires_lab_attention or has_lab_report:
        lab_reasons_en.append("Periodic testing is recommended for high-yielding milch cattle (>15 L/day) to accurately balance dietary protein and energy.")
        lab_reasons_ta.append("அதிக பால் கறக்கும் மாடுகளுக்கு (>15 லிட்டர்/நாள்) சரியான தீவன விகிதத்தை நிர்ணயிக்க ஆய்வக பரிசோதனை உதவும்.")
    else:
        lab_reasons_en.append("Routine laboratory proximate analysis (CP, NDF, ADF, Starch) once per silo opening helps dairy farmers adjust concentrate rations.")
        lab_reasons_ta.append("ஒவ்வொரு சைலேஜ் குழி திறக்கும் போதும் ஒருமுறை ஆய்வக பரிசோதனை செய்வது தீவன செலவை குறைக்க உதவும்.")

    # SUMMARY OF PROVIDED ANSWERS
    summary = {
        "crop": crop,
        "harvest_timing": harvest_timing,
        "sealing_delay": sealing_delay,
        "storage_method": storage_method,
        "inoculant_used": inoculant_used,
        "visible_mould": visible_mould,
        "silage_color": silage_color,
        "silage_odor": silage_odor,
        "temperature_feeling": temperature_feeling,
        "lab_report_available": "Yes" if has_lab_report else "No (Farmer Mode)",
    }

    return {
        "mode": "farmer_guided",
        "is_ml_prediction": False,
        "disclaimer_en": (
            "NOTICE: This preliminary guidance is based on validated dairy extension benchmarks (ICAR-NDRI) "
            "and observable on-farm indicators. It is NOT an ML-generated FQI prediction or a certified laboratory diagnosis. "
            "Appearance and smell alone CANNOT establish that silage is completely safe for animal consumption (e.g. microscopic mycotoxins "
            "or subclinical bacterial spores cannot be detected by eye or nose alone)."
        ),
        "disclaimer_ta": (
            "முக்கிய அறிவிப்பு: இந்த பூர்வாங்க வழிகாட்டுதல் சரிபார்க்கப்பட்ட பால்பண்ணை அறிவியல் விதிகள் (ICAR-NDRI) "
            "மற்றும் காணக்கூடிய பண்ணை அறிகுறிகளின் அடிப்படையிலானது. இது ML மாதிரி கணிப்பு அல்லது சான்றளிக்கப்பட்ட ஆய்வக நோய் கண்டறிதல் அல்ல. "
            "தோற்றம் மற்றும் வாசனை மட்டுமே தீவனம் விலங்குகளுக்கு முற்றிலும் பாதுகாப்பானது என்பதை உறுதிப்படுத்த முடியாது (கண்ணுக்குத் தெரியாத பூஞ்சை நச்சுகள் வாசனை இன்றியும் இருக்கலாம்)."
        ),
        "summary": summary,
        "warning_signs": warning_signs,
        "guidance_en": guidance_en,
        "guidance_ta": guidance_ta,
        "lab_recommended": requires_lab_attention,
        "lab_reasons_en": lab_reasons_en,
        "lab_reasons_ta": lab_reasons_ta,
        "referral_contacts_en": "District Veterinary Polyclinic, State Animal Husbandry Diagnostic Lab, or Krishi Vigyan Kendra (KVK)",
        "referral_contacts_ta": "மாவட்ட கால்நடை மருத்துவமனை, மாநில கால்நடை நோய் கண்டறியும் ஆய்வகம், அல்லது வேளாண் அறிவியல் மையம் (KVK)",
    }
