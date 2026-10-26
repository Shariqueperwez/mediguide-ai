"""
Synthetic Dataset Generator for MediGuide AI.
Creates a comprehensive, high-quality labeled synthetic dataset for
care navigation, triage urgency classification, and analytics demonstration.
"""

import csv
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "synthetic_demo_data.csv"

SAMPLES = [
    # EMERGENCY - Cardiovascular & Stroke & Airway
    ("Crushing chest pain radiating down my left arm with heavy sweating and nausea", "EMERGENCY", "Cardiology", "Adult (18-64)", 10),
    ("Sudden numbness on the left side of my face and my speech has become slurred", "EMERGENCY", "Neurology", "Senior (65+)", 10),
    ("Severe shortness of breath, gasping for air, and my lips are turning blue", "EMERGENCY", "Pulmonology", "Adult (18-64)", 10),
    ("Coughing up large amounts of bright red blood and feeling very faint", "EMERGENCY", "Pulmonology", "Adult (18-64)", 9),
    ("Severe allergic reaction, my tongue and throat are swelling rapidly and I cannot swallow", "EMERGENCY", "Emergency Medicine", "Young Adult (18-25)", 10),
    ("My father passed out suddenly, fell to the floor, and won't wake up", "EMERGENCY", "Emergency Medicine", "Senior (65+)", 10),
    ("Sudden loss of vision in one eye accompanied by massive weakness in my right leg", "EMERGENCY", "Neurology", "Senior (65+)", 10),
    ("Intense crushing chest tightness like an elephant is sitting on my chest", "EMERGENCY", "Cardiology", "Adult (18-64)", 9),
    ("High fever of 104 with sudden severe stiff neck and purplish spots on skin", "EMERGENCY", "Infectious Disease", "Child (2-12)", 10),
    ("Uncontrolled heavy bleeding from a deep laceration on the thigh after an accident", "EMERGENCY", "Emergency Medicine", "Adult (18-64)", 10),
    ("Severe sudden difficulty breathing with loud whistling stridor sound", "EMERGENCY", "Pulmonology", "Child (2-12)", 10),
    ("Sudden worst headache of my life like a thunderclap with vomiting and confusion", "EMERGENCY", "Neurology", "Adult (18-64)", 10),
    ("Vomiting dark blood and passing black tarry stools with extreme dizziness", "EMERGENCY", "Gastroenterology", "Adult (18-64)", 9),
    ("Baby is 6 weeks old with 102 fever and completely lethargic refusing to nurse", "EMERGENCY", "Pediatrics", "Infant (0-1)", 9),
    ("Severe chest pain accompanied by cold clammy skin and shortness of breath", "EMERGENCY", "Cardiology", "Senior (65+)", 10),

    # URGENT - Needs evaluation within 12-24h
    ("Excruciating sharp pain in the right lower abdomen with nausea and moderate fever", "URGENT", "Gastroenterology", "Young Adult (18-25)", 8),
    ("Deep cut on my finger with rusty metal, bleeding has slowed but edges are gaping open", "URGENT", "Emergency Medicine", "Adult (18-64)", 7),
    ("High fever of 103 for three days that won't come down with medication and body is shaking", "URGENT", "General Physician", "Adult (18-64)", 8),
    ("Severe pain and swelling in right calf after long flight, warm and red to touch", "URGENT", "Cardiology", "Adult (18-64)", 7),
    ("Painful urination with flank pain on my back and chills", "URGENT", "Urology", "Adult (18-64)", 8),
    ("Severe sudden eye pain with blurred vision and halos around lights", "URGENT", "Ophthalmology", "Senior (65+)", 8),
    ("Asthma flare-up, my rescue inhaler is giving less relief than usual and wheezing is persistent", "URGENT", "Pulmonology", "Teen (13-17)", 7),
    ("Pregnant in first trimester with sharp cramping and moderate vaginal spotting", "URGENT", "Obstetrics & Gynecology", "Adult (18-64)", 8),
    ("Fell down the stairs, heard a pop in my ankle, severe swelling and cannot put weight on foot", "URGENT", "Orthopedics", "Adult (18-64)", 8),
    ("Severe toothache with swollen cheek and difficulty opening mouth", "URGENT", "Dentistry", "Adult (18-64)", 8),
    ("Persistent severe vomiting for 24 hours unable to keep any water down, feeling severely dehydrated", "URGENT", "General Physician", "Adult (18-64)", 8),
    ("Dog bite on forearm that punctured skin and is beginning to look red and warm", "URGENT", "General Physician", "Adult (18-64)", 7),
    ("Sharp pain in kidney area radiating down groin, unbearable waves of pain", "URGENT", "Urology", "Adult (18-64)", 9),
    ("Rapid heart flutter lasting over 2 hours without chest pain but feeling dizzy", "URGENT", "Cardiology", "Adult (18-64)", 7),
    ("Deep ear pain with thick discharge and hearing reduction after swimming", "URGENT", "Otolaryngology (ENT)", "Child (2-12)", 7),

    # ROUTINE - Standard specialist or GP visit
    ("Red itchy bumpy rash on both forearms after hiking, seems like poison ivy", "ROUTINE", "Dermatology", "Adult (18-64)", 4),
    ("Persistent dry cough lasting for over 3 weeks with no fever", "ROUTINE", "Pulmonology", "Adult (18-64)", 4),
    ("Dull aching pain in both knees especially when walking down stairs for the past month", "ROUTINE", "Orthopedics", "Senior (65+)", 5),
    ("Frequent heartburn and acid regurgitation into throat after eating spicy food", "ROUTINE", "Gastroenterology", "Adult (18-64)", 4),
    ("Severe throbbing headache on right side with sensitivity to light once a week", "ROUTINE", "Neurology", "Young Adult (18-25)", 6),
    ("Itchy red eyes with gritty feeling and crusty eyelids in the morning", "ROUTINE", "Ophthalmology", "Adult (18-64)", 3),
    ("Sensitivity to hot and cold drinks in my lower molar with mild throbbing", "ROUTINE", "Dentistry", "Adult (18-64)", 4),
    ("Persistent sinus pressure and yellow nasal discharge for the past 10 days", "ROUTINE", "Otolaryngology (ENT)", "Adult (18-64)", 4),
    ("Irregular periods for the last 6 months along with sudden facial acne and weight gain", "ROUTINE", "Obstetrics & Gynecology", "Young Adult (18-25)", 4),
    ("Feeling overwhelmed with constant worry, racing thoughts, and difficulty falling asleep", "ROUTINE", "Psychiatry / Mental Health", "Young Adult (18-25)", 5),
    ("Persistent fatigue, general weakness, and feeling cold all the time for 2 months", "ROUTINE", "General Physician", "Adult (18-64)", 4),
    ("Dry scaly patches of skin on elbows that flake and itch intensely", "ROUTINE", "Dermatology", "Adult (18-64)", 4),
    ("Lower back stiffness every morning that takes an hour to loosen up", "ROUTINE", "Orthopedics", "Adult (18-64)", 5),
    ("Intermittent ringing sound in both ears without any pain or dizziness", "ROUTINE", "Otolaryngology (ENT)", "Senior (65+)", 3),
    ("Burning sensation during urination for the past 2 days with increased frequency", "ROUTINE", "Urology", "Adult (18-64)", 5),
    ("Bloating and alternating diarrhea with constipation for several months", "ROUTINE", "Gastroenterology", "Adult (18-64)", 4),
    ("Mild tremor in right hand when resting that started recently", "ROUTINE", "Neurology", "Senior (65+)", 4),
    ("Gradual loss of distance vision needing squinting to read road signs", "ROUTINE", "Ophthalmology", "Adult (18-64)", 2),
    ("Child has recurring sore throats every few weeks throughout the winter", "ROUTINE", "Pediatrics", "Child (2-12)", 4),
    ("Mild depression and lack of interest in daily hobbies for several weeks", "ROUTINE", "Psychiatry / Mental Health", "Adult (18-64)", 5),

    # SELF_CARE - Mild, self-limiting
    ("Mild headache after staring at computer screen all afternoon, goes away when resting", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
    ("Slight runny nose and sneezing since yesterday morning, feeling normal otherwise", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
    ("Minor paper cut on index finger, washed with soap and water, slight sting", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
    ("Mild soreness in shoulder muscles after lifting weights yesterday at gym", "SELF_CARE", "Orthopedics", "Young Adult (18-25)", 2),
    ("Slight stomach discomfort after eating a very heavy dinner last night", "SELF_CARE", "Gastroenterology", "Adult (18-64)", 2),
    ("Dry lips and mild dehydration headache on a hot summer afternoon", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
    ("Small localized mosquito bite that is mildly itchy, no spreading redness", "SELF_CARE", "Dermatology", "Child (2-12)", 1),
    ("Mild throat scratchiness in the morning that cleared after drinking warm tea", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
    ("Minor bruise on shin from bumping into the coffee table, no deformity", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
    ("Felt a bit groggy and tired this morning due to sleeping only 4 hours last night", "SELF_CARE", "General Physician", "Adult (18-64)", 1)
]


def generate_dataset():
    """Write the dataset to CSV format."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symptoms_text", "triage_level", "specialty_category", "age_group", "severity"])
        
        # Write primary samples
        for row in SAMPLES:
            writer.writerow(row)
            
        # Write augmented variants to ensure balanced distribution
        variants = [
            ("Sudden crushing chest tightness radiating to the jaw with cold sweats", "EMERGENCY", "Cardiology", "Senior (65+)", 10),
            ("Face dropped on right side and right arm cannot be lifted", "EMERGENCY", "Neurology", "Adult (18-64)", 10),
            ("Gasping for breath, wheezing uncontrollably and turning pale", "EMERGENCY", "Pulmonology", "Adult (18-64)", 10),
            ("Massive arterial spurting wound on leg from glass cut", "EMERGENCY", "Emergency Medicine", "Adult (18-64)", 10),
            ("Sudden unresponsiveness, eyes rolled back and seizing", "EMERGENCY", "Emergency Medicine", "Adult (18-64)", 10),
            ("High fever with rigid stiff neck and violent vomiting", "EMERGENCY", "Infectious Disease", "Adult (18-64)", 10),
            
            ("Severe right iliac fossa belly pain with chills and nausea", "URGENT", "Gastroenterology", "Young Adult (18-25)", 8),
            ("Fell off bicycle and heard cracking sound in wrist, swelling quickly", "URGENT", "Orthopedics", "Teen (13-17)", 8),
            ("Blood in urine accompanied by sudden acute flank back spasms", "URGENT", "Urology", "Adult (18-64)", 8),
            ("Swollen painful red eye with cloudy cornea and photophobia", "URGENT", "Ophthalmology", "Adult (18-64)", 8),
            ("Persistent high temperature of 103F for 4 consecutive days", "URGENT", "General Physician", "Adult (18-64)", 8),

            ("Scaly red itchy patches on cheeks and forehead for 3 weeks", "ROUTINE", "Dermatology", "Adult (18-64)", 4),
            ("Chronic lower back dull ache worse after sitting for hours", "ROUTINE", "Orthopedics", "Adult (18-64)", 4),
            ("Bloating and indigestion after every meal for the last month", "ROUTINE", "Gastroenterology", "Adult (18-64)", 3),
            ("Severe one-sided throbbing headache with nausea twice a month", "ROUTINE", "Neurology", "Adult (18-64)", 6),
            ("Feeling anxious and panicked in social situations with poor sleep", "ROUTINE", "Psychiatry / Mental Health", "Young Adult (18-25)", 5),
            ("Tooth pain when eating sweets or cold ice cream", "ROUTINE", "Dentistry", "Adult (18-64)", 3),
            ("Persistent ear buzzing and blocked ear feeling", "ROUTINE", "Otolaryngology (ENT)", "Adult (18-64)", 3),

            ("Slight stiffness in neck after sleeping on an awkward pillow", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
            ("Minor scrape on knee while jogging, cleaned and bandaged", "SELF_CARE", "General Physician", "Young Adult (18-25)", 1),
            ("Tired eyes after 8 hours of coding on laptop", "SELF_CARE", "General Physician", "Adult (18-64)", 2),
            ("Occasional sneeze and clear nasal fluid after walking past flowers", "SELF_CARE", "General Physician", "Adult (18-64)", 1),

            # Additional Multi-Domain Samples for Enhanced ML Generalization
            ("Skin breaking out with red itchy hives after eating shellfish", "URGENT", "Dermatology", "Young Adult (18-25)", 7),
            ("Persistent redness, swelling, and pus around toenail for 5 days", "ROUTINE", "Dermatology", "Adult (18-64)", 4),
            ("Severe pain in ear with fever and reduced hearing in 5-year-old child", "URGENT", "Pediatrics", "Child (2-12)", 7),
            ("Sudden severe dizziness with room spinning and inability to stand", "URGENT", "Neurology", "Senior (65+)", 8),
            ("Difficulty sleeping and intense dread every evening before work", "ROUTINE", "Psychiatry / Mental Health", "Adult (18-64)", 5),
            ("Mild dry cough after standing outside in cold air", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
            ("Sharp chest pain that gets worse when taking a deep breath and coughing", "URGENT", "Pulmonology", "Adult (18-64)", 7),
            ("Dark urine and yellowing of the whites of my eyes", "URGENT", "Gastroenterology", "Adult (18-64)", 8),
            ("Severe menstrual cramps accompanied by heavy clotting and faintness", "URGENT", "Obstetrics & Gynecology", "Young Adult (18-25)", 7),
            ("Swollen ankle with bruising after twisting it on uneven pavement", "ROUTINE", "Orthopedics", "Adult (18-64)", 5),
            ("Burning sensation in chest behind breastbone after drinking coffee", "ROUTINE", "Gastroenterology", "Adult (18-64)", 3),
            ("Mild muscle soreness in legs after 5km walk", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
            ("Tooth feeling loose and painful when biting on hard bread", "ROUTINE", "Dentistry", "Senior (65+)", 4),
            ("Sudden double vision and difficulty keeping eyes focused", "URGENT", "Ophthalmology", "Senior (65+)", 8),
            ("Crushing sensation in chest with cold sweat and pain in left shoulder", "EMERGENCY", "Cardiology", "Adult (18-64)", 10),
            ("Inability to move right arm and slurred incomprehensible words", "EMERGENCY", "Neurology", "Senior (65+)", 10),
            ("Stridor, inability to take in air, and blue nail beds", "EMERGENCY", "Pulmonology", "Adult (18-64)", 10),
            ("Large volume of blood vomited into sink with extreme weakness", "EMERGENCY", "Gastroenterology", "Adult (18-64)", 10),
            ("Infant under 2 months with rectal temperature of 101.5 and crying weakly", "EMERGENCY", "Pediatrics", "Infant (0-1)", 9),
            ("Severe throbbing headache after head trauma with repeated vomiting", "EMERGENCY", "Neurology", "Teen (13-17)", 10),
            ("Feeling slightly bloated after carbonated soda", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
            ("Mild dry skin patches during winter cold weather", "SELF_CARE", "Dermatology", "Adult (18-64)", 1),
            ("Single episode of loose stool after eating street food, feeling fine now", "SELF_CARE", "General Physician", "Young Adult (18-25)", 2),
            ("Mild paper cut on thumb", "SELF_CARE", "General Physician", "Adult (18-64)", 1),
            ("Persistent joint pain and morning stiffness in both wrists for 6 weeks", "ROUTINE", "Orthopedics", "Adult (18-64)", 5),
            ("Dry cough with tickle in throat for a week", "ROUTINE", "Pulmonology", "Adult (18-64)", 3),
            ("Psoriasis flare up on knees with thick silvery scales", "ROUTINE", "Dermatology", "Adult (18-64)", 4),
            ("Chronic low back pain radiating to glutes when sitting at desk", "ROUTINE", "Orthopedics", "Adult (18-64)", 4),
            ("Cloudy vision in right eye like looking through frosted glass", "ROUTINE", "Ophthalmology", "Senior (65+)", 4),
            ("Cavity ache in lower molar when drinking sweet juice", "ROUTINE", "Dentistry", "Teen (13-17)", 3),
            ("Frequent urination and increased thirst with unexplained weight loss", "ROUTINE", "General Physician", "Adult (18-64)", 5)
        ]
        for row in variants:
            writer.writerow(row)

    print(f"Generated synthetic dataset at {DATA_PATH} with {len(SAMPLES) + len(variants)} records.")


if __name__ == "__main__":
    generate_dataset()
