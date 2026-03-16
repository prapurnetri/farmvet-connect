"""
FarmVet Connect - Symptom Questionnaire Definitions
10 categories with specific questions per category
Includes auto severity scoring
"""

CATEGORIES = [
    'Respiratory',
    'Digestive',
    'Musculoskeletal',
    'Reproductive',
    'Neurological',
    'Skin & External',
    'Eye & Ear',
    'Fever & General',
    'Poisoning / Toxic',
    'Neonatal'
]

QUESTIONS = {
    'Respiratory': [
        {'id': 'r1', 'text': 'Is the animal coughing?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'r2', 'text': 'Is there nasal discharge? If yes, what colour?', 'type': 'text', 'severity_weight': 1},
        {'id': 'r3', 'text': 'Is breathing laboured or rapid?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'r4', 'text': 'Is the animal open-mouth breathing?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'r5', 'text': 'How long have symptoms been present?', 'type': 'text', 'severity_weight': 1},
        {'id': 'r6', 'text': 'Is the animal still eating and drinking?', 'type': 'yesno', 'severity_weight': 1},
    ],
    'Digestive': [
        {'id': 'd1', 'text': 'Is the animal bloated or has a distended abdomen?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'd2', 'text': 'Does the animal have diarrhea? Is there blood?', 'type': 'text', 'severity_weight': 2},
        {'id': 'd3', 'text': 'Has the animal stopped eating?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'd4', 'text': 'Is the animal grinding its teeth?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'd5', 'text': 'Are rumen sounds present (cattle/goats)?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'd6', 'text': 'Has the animal vomited or attempted to vomit?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'd7', 'text': 'How long since last normal bowel movement?', 'type': 'text', 'severity_weight': 1},
    ],
    'Musculoskeletal': [
        {'id': 'm1', 'text': 'Which limb(s) are affected?', 'type': 'text', 'severity_weight': 1},
        {'id': 'm2', 'text': 'Is the animal unable to stand or walk?', 'type': 'yesno', 'severity_weight': 3},
        {'id': 'm3', 'text': 'Is there visible swelling or heat in the joint?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'm4', 'text': 'Was there a recent injury or trauma?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'm5', 'text': 'How severe is the lameness? (Mild/Moderate/Severe)', 'type': 'text', 'severity_weight': 2},
    ],
    'Reproductive': [
        {'id': 'rep1', 'text': 'Is the animal pregnant or recently gave birth?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'rep2', 'text': 'Is there abnormal discharge? Describe colour and smell.', 'type': 'text', 'severity_weight': 2},
        {'id': 'rep3', 'text': 'Has the placenta been retained after birth?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'rep4', 'text': 'Is the animal straining without producing offspring?', 'type': 'yesno', 'severity_weight': 3},
        {'id': 'rep5', 'text': 'How long has labour been ongoing?', 'type': 'text', 'severity_weight': 2},
    ],
    'Neurological': [
        {'id': 'n1', 'text': 'Is the animal having seizures or convulsions?', 'type': 'yesno', 'severity_weight': 3},
        {'id': 'n2', 'text': 'Is the animal walking in circles or pressing its head against walls?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'n3', 'text': 'Does the animal appear blind?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'n4', 'text': 'Is the animal uncoordinated or falling over?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'n5', 'text': 'Is the animal responsive to stimulation?', 'type': 'yesno', 'severity_weight': 2},
    ],
    'Skin & External': [
        {'id': 's1', 'text': 'Describe the skin lesion (size, colour, location)', 'type': 'text', 'severity_weight': 1},
        {'id': 's2', 'text': 'Is the animal scratching or rubbing excessively?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 's3', 'text': 'Is there hair/wool loss?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 's4', 'text': 'Are there open wounds or abscesses?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 's5', 'text': 'Are multiple animals affected?', 'type': 'yesno', 'severity_weight': 2},
    ],
    'Eye & Ear': [
        {'id': 'e1', 'text': 'Which eye/ear is affected?', 'type': 'text', 'severity_weight': 1},
        {'id': 'e2', 'text': 'Is there discharge? Describe colour and amount.', 'type': 'text', 'severity_weight': 1},
        {'id': 'e3', 'text': 'Is the eye cloudy or does it appear painful?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'e4', 'text': 'Is the animal shaking its head or holding it tilted?', 'type': 'yesno', 'severity_weight': 1},
    ],
    'Fever & General': [
        {'id': 'f1', 'text': 'What is the animal\'s temperature (°C)?', 'type': 'text', 'severity_weight': 2},
        {'id': 'f2', 'text': 'Is the animal lethargic or depressed?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'f3', 'text': 'Has the animal lost significant weight recently?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'f4', 'text': 'Is the animal isolating itself from the herd?', 'type': 'yesno', 'severity_weight': 1},
        {'id': 'f5', 'text': 'How many days has this been going on?', 'type': 'text', 'severity_weight': 1},
    ],
    'Poisoning / Toxic': [
        {'id': 'p1', 'text': 'What plants or substances may the animal have eaten?', 'type': 'text', 'severity_weight': 2},
        {'id': 'p2', 'text': 'Did symptoms appear suddenly?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'p3', 'text': 'Is the animal salivating excessively?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'p4', 'text': 'Are multiple animals showing the same symptoms?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'p5', 'text': 'Has the animal collapsed or lost consciousness?', 'type': 'yesno', 'severity_weight': 3},
    ],
    'Neonatal': [
        {'id': 'nb1', 'text': 'How old is the newborn (hours/days)?', 'type': 'text', 'severity_weight': 1},
        {'id': 'nb2', 'text': 'Is the newborn able to stand?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'nb3', 'text': 'Has the newborn suckled or been fed colostrum?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'nb4', 'text': 'Is the umbilical area swollen or infected?', 'type': 'yesno', 'severity_weight': 2},
        {'id': 'nb5', 'text': 'Is the newborn breathing normally?', 'type': 'yesno', 'severity_weight': 3},
    ],
}


def get_questions(category):
    """Return questions for a given category."""
    return QUESTIONS.get(category, [])


def calculate_severity(answers):
    """
    Auto-calculate severity score 1-5 based on answers.
    'yes' answers to high-weight questions increase severity.
    """
    score = 1
    for question, answer in answers.items():
        if answer.lower() in ('yes', 'y', 'severe', 'unable'):
            score += 1
    return min(score, 5)
