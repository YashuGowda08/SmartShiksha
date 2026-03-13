"""Seed script to populate the database with real Karnataka PU Board / CBSE curriculum data.
Supports SQLite, PostgreSQL (via SQLAlchemy), and MongoDB (via Motor).
"""
import asyncio
from datetime import datetime
from app.config import get_settings
from app.models import Base, Subject, Chapter, Topic, Question, MockTest, TestQuestion, User

settings = get_settings()


# ── Real Karnataka State / CBSE Syllabus ──
CURRICULUM = {
    # ── Class 8 (CBSE / Karnataka State Board) ──
    ("Mathematics", "8"): [
        "Rational Numbers",
        "Linear Equations in One Variable",
        "Understanding Quadrilaterals",
        "Data Handling",
        "Squares and Square Roots",
        "Cubes and Cube Roots",
        "Comparing Quantities",
        "Algebraic Expressions and Identities",
        "Mensuration",
        "Exponents and Powers",
        "Direct and Inverse Proportions",
        "Factorisation",
        "Introduction to Graphs",
        "Playing with Numbers",
    ],
    ("Science", "8"): [
        "Crop Production and Management",
        "Microorganisms: Friend and Foe",
        "Synthetic Fibres and Plastics",
        "Materials: Metals and Non-Metals",
        "Coal and Petroleum",
        "Combustion and Flame",
        "Conservation of Plants and Animals",
        "Cell: Structure and Functions",
        "Reproduction in Animals",
        "Force and Pressure",
        "Friction",
        "Sound",
        "Chemical Effects of Electric Current",
        "Some Natural Phenomena",
        "Light",
        "Stars and the Solar System",
        "Pollution of Air and Water",
    ],
    ("Social Science", "8"): [
        "How, When and Where (History)",
        "From Trade to Territory (History)",
        "Ruling the Countryside (History)",
        "Resources (Geography)",
        "Land, Soil, Water (Geography)",
        "The Indian Constitution (Civics)",
        "Understanding Secularism (Civics)",
        "Parliament and Making of Laws (Civics)",
    ],
    ("English", "8"): [
        "Prose — The Best Christmas Present",
        "Poetry — The Ant and the Cricket",
        "Grammar — Tenses",
        "Grammar — Active and Passive Voice",
        "Writing — Letter Writing",
        "Writing — Essay Writing",
        "Comprehension Passages",
    ],
    ("Computer Science", "8"): [
        "Introduction to Computers",
        "Operating Systems",
        "MS Word Basics",
        "Internet and Email",
        "Introduction to HTML",
    ],

    # ── Class 9 (CBSE / Karnataka State Board) ──
    ("Mathematics", "9"): [
        "Number Systems",
        "Polynomials",
        "Coordinate Geometry",
        "Linear Equations in Two Variables",
        "Introduction to Euclid's Geometry",
        "Lines and Angles",
        "Triangles",
        "Quadrilaterals",
        "Areas of Parallelograms and Triangles",
        "Circles",
        "Constructions",
        "Heron's Formula",
        "Surface Areas and Volumes",
        "Statistics",
        "Probability",
    ],
    ("Science", "9"): [
        "Matter in Our Surroundings",
        "Is Matter Around Us Pure?",
        "Atoms and Molecules",
        "Structure of the Atom",
        "The Fundamental Unit of Life",
        "Tissues",
        "Motion",
        "Force and Laws of Motion",
        "Gravitation",
        "Work and Energy",
        "Sound",
        "Improvement in Food Resources",
    ],
    ("Social Science", "9"): [
        "The French Revolution",
        "Socialism in Europe and the Russian Revolution",
        "India – Size and Location",
        "Physical Features of India",
        "Drainage",
        "Climate",
        "Democracy in the Contemporary World",
        "Constitutional Design",
        "Electoral Politics",
        "The Story of Village Palampur",
        "People as Resource",
    ],
    ("English", "9"): [
        "Prose — The Fun They Had",
        "Prose — The Sound of Music",
        "Poetry — The Road Not Taken",
        "Poetry — Wind",
        "Grammar — Reported Speech",
        "Grammar — Modals",
        "Writing — Diary Entry",
        "Comprehension — Unseen Passages",
    ],

    # ── Class 10 (CBSE / Karnataka SSLC) ──
    ("Mathematics", "10"): [
        "Real Numbers",
        "Polynomials",
        "Pair of Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Introduction to Trigonometry",
        "Applications of Trigonometry",
        "Circles",
        "Constructions",
        "Areas Related to Circles",
        "Surface Areas and Volumes",
        "Statistics",
        "Probability",
    ],
    ("Science", "10"): [
        "Chemical Reactions and Equations",
        "Acids, Bases and Salts",
        "Metals and Non-metals",
        "Carbon and Its Compounds",
        "Periodic Classification of Elements",
        "Life Processes",
        "Control and Coordination",
        "How Do Organisms Reproduce?",
        "Heredity and Evolution",
        "Light – Reflection and Refraction",
        "Human Eye and the Colourful World",
        "Electricity",
        "Magnetic Effects of Electric Current",
        "Sources of Energy",
        "Our Environment",
    ],
    ("Social Science", "10"): [
        "The Rise of Nationalism in Europe",
        "Nationalism in India",
        "The Making of a Global World",
        "Resources and Development",
        "Forest and Wildlife Resources",
        "Water Resources",
        "Agriculture",
        "Power Sharing",
        "Federalism",
        "Gender, Religion and Caste",
        "Money and Credit",
        "Globalisation and the Indian Economy",
        "Consumer Rights",
    ],
    ("English", "10"): [
        "Prose — A Letter to God",
        "Prose — Nelson Mandela",
        "Poetry — Dust of Snow",
        "Poetry — Fire and Ice",
        "Grammar — Tenses (Advanced)",
        "Grammar — Subject-Verb Agreement",
        "Writing — Formal Letter",
        "Writing — Analytical Paragraph",
        "Comprehension — Unseen Passages",
    ],
    ("Computer Science", "10"): [
        "Computer Networks",
        "Internet Services",
        "HTML Advanced",
        "Introduction to Python",
        "Python Data Types",
        "Cyber Safety",
    ],

    # ── Class 11 (Karnataka 1st PUC / CBSE) ──
    ("Physics", "11"): [
        "Physical World",
        "Units and Measurements",
        "Motion in a Straight Line",
        "Motion in a Plane",
        "Laws of Motion",
        "Work, Energy and Power",
        "System of Particles and Rotational Motion",
        "Gravitation",
        "Mechanical Properties of Solids",
        "Mechanical Properties of Fluids",
        "Thermal Properties of Matter",
        "Thermodynamics",
        "Kinetic Theory",
        "Oscillations",
        "Waves",
    ],
    ("Chemistry", "11"): [
        "Some Basic Concepts of Chemistry",
        "Structure of Atom",
        "Classification of Elements and Periodicity",
        "Chemical Bonding and Molecular Structure",
        "States of Matter",
        "Thermodynamics",
        "Equilibrium",
        "Redox Reactions",
        "Hydrogen",
        "The s-Block Elements",
        "The p-Block Elements",
        "Organic Chemistry – Basic Principles",
        "Hydrocarbons",
        "Environmental Chemistry",
    ],
    ("Biology", "11"): [
        "The Living World",
        "Biological Classification",
        "Plant Kingdom",
        "Animal Kingdom",
        "Morphology of Flowering Plants",
        "Anatomy of Flowering Plants",
        "Structural Organisation in Animals",
        "Cell: The Unit of Life",
        "Biomolecules",
        "Cell Cycle and Cell Division",
        "Transport in Plants",
        "Mineral Nutrition",
        "Photosynthesis in Higher Plants",
        "Respiration in Plants",
        "Plant Growth and Development",
        "Digestion and Absorption",
        "Breathing and Exchange of Gases",
        "Body Fluids and Circulation",
        "Excretory Products and Their Elimination",
        "Locomotion and Movement",
        "Neural Control and Coordination",
        "Chemical Coordination and Integration",
    ],
    ("Mathematics", "11"): [
        "Sets",
        "Relations and Functions",
        "Trigonometric Functions",
        "Principle of Mathematical Induction",
        "Complex Numbers and Quadratic Equations",
        "Linear Inequalities",
        "Permutations and Combinations",
        "Binomial Theorem",
        "Sequences and Series",
        "Straight Lines",
        "Conic Sections",
        "Introduction to Three Dimensional Geometry",
        "Limits and Derivatives",
        "Mathematical Reasoning",
        "Statistics",
        "Probability",
    ],
    ("Computer Science", "11"): [
        "Computer Systems and Organisation",
        "Encoding Schemes and Number Systems",
        "Emerging Trends in Computing",
        "Problem Solving Methodology",
        "Getting Started with Python",
        "Python Fundamentals",
        "Data Handling in Python",
        "Conditional and Iterative Statements",
        "Strings in Python",
        "Lists and Tuples",
        "Dictionaries",
        "Society, Law and Ethics",
    ],

    # ── Class 12 (Karnataka 2nd PUC / CBSE) ──
    ("Physics", "12"): [
        "Electric Charges and Fields",
        "Electrostatic Potential and Capacitance",
        "Current Electricity",
        "Moving Charges and Magnetism",
        "Magnetism and Matter",
        "Electromagnetic Induction",
        "Alternating Current",
        "Electromagnetic Waves",
        "Ray Optics and Optical Instruments",
        "Wave Optics",
        "Dual Nature of Radiation and Matter",
        "Atoms",
        "Nuclei",
        "Semiconductor Electronics",
    ],
    ("Chemistry", "12"): [
        "The Solid State",
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "Surface Chemistry",
        "General Principles of Isolation of Elements",
        "The p-Block Elements",
        "The d- and f-Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Amines",
        "Biomolecules",
        "Polymers",
        "Chemistry in Everyday Life",
    ],
    ("Biology", "12"): [
        "Reproduction in Organisms",
        "Sexual Reproduction in Flowering Plants",
        "Human Reproduction",
        "Reproductive Health",
        "Principles of Inheritance and Variation",
        "Molecular Basis of Inheritance",
        "Evolution",
        "Human Health and Disease",
        "Strategies for Enhancement in Food Production",
        "Microbes in Human Welfare",
        "Biotechnology: Principles and Processes",
        "Biotechnology and Its Applications",
        "Organisms and Populations",
        "Ecosystem",
        "Biodiversity and Conservation",
        "Environmental Issues",
    ],
    ("Mathematics", "12"): [
        "Relations and Functions",
        "Inverse Trigonometric Functions",
        "Matrices",
        "Determinants",
        "Continuity and Differentiability",
        "Applications of Derivatives",
        "Integrals",
        "Applications of Integrals",
        "Differential Equations",
        "Vectors",
        "Three Dimensional Geometry",
        "Linear Programming",
        "Probability",
    ],
    ("Computer Science", "12"): [
        "Python Revision Tour – I",
        "Python Revision Tour – II",
        "Working with Functions in Python",
        "Using Python Libraries",
        "File Handling in Python",
        "Data Structures – Stack and Queue",
        "Database Concepts and SQL",
        "SQL Commands (DDL, DML)",
        "Interface Python with SQL",
        "Computer Networks",
        "Network Security Concepts",
        "Society, Law and Ethics – II",
    ],
}

# ── Shared constants ──
BOARDS = [
    "CBSE", "ICSE", "Karnataka Board", "Tamil Nadu Board", "Kerala Board",
    "Andhra Pradesh Board", "Telangana Board", "UP Board",
    "Maharashtra Board", "Bihar Board", "Rajasthan Board",
]

BASE_SUBJECTS_CONFIG = [
    {"name": "Mathematics",      "icon": "Math",      "color": "#6366f1", "classes": ["8","9","10"],      "desc": "Numbers, algebra, geometry, trigonometry"},
    {"name": "Science",          "icon": "Science",    "color": "#10b981", "classes": ["8","9","10"],      "desc": "Physics, Chemistry, Biology combined"},
    {"name": "Social Science",   "icon": "Globe",      "color": "#f59e0b", "classes": ["8","9","10"],      "desc": "History, Geography, Civics, Economics"},
    {"name": "English",          "icon": "Book",       "color": "#ef4444", "classes": ["8","9","10"],      "desc": "Grammar, comprehension, literature"},
    {"name": "Computer Science", "icon": "Web",        "color": "#8b5cf6", "classes": ["8","10","11","12"], "desc": "Python, SQL, networking, HTML"},
    {"name": "Physics",          "icon": "Physics",    "color": "#3b82f6", "classes": ["11","12"],         "desc": "Mechanics, electromagnetism, optics, modern physics"},
    {"name": "Chemistry",        "icon": "Chemistry",  "color": "#22c55e", "classes": ["11","12"],         "desc": "Organic, inorganic, physical chemistry"},
    {"name": "Biology",          "icon": "Biology",    "color": "#ec4899", "classes": ["11","12"],         "desc": "Botany, zoology, genetics, ecology"},
    {"name": "Mathematics",      "icon": "Math",       "color": "#6366f1", "classes": ["11","12"],         "desc": "Calculus, vectors, 3D, probability"},
]

TESTS_METADATA = [
    {"title": "Class 8 Maths — Algebra & Numbers", "subject": "Mathematics", "class": "8", "type": "Chapter Test", "duration": 30, "marks": 40},
    {"title": "Class 8 Science — Matter & Forces", "subject": "Science", "class": "8", "type": "Chapter Test", "duration": 25, "marks": 30},
    {"title": "Class 8 Social Science Quiz", "subject": "Social Science", "class": "8", "type": "Chapter Test", "duration": 20, "marks": 25},
    {"title": "Class 8 English Grammar Test", "subject": "English", "class": "8", "type": "Chapter Test", "duration": 20, "marks": 25},
    {"title": "Class 9 Maths — Polynomials & Geometry", "subject": "Mathematics", "class": "9", "type": "Chapter Test", "duration": 30, "marks": 40},
    {"title": "Class 9 Science — Atoms & Motion", "subject": "Science", "class": "9", "type": "Chapter Test", "duration": 30, "marks": 40},
    {"title": "Class 9 Social — French Revolution", "subject": "Social Science", "class": "9", "type": "Chapter Test", "duration": 25, "marks": 30},
    {"title": "Class 9 Full Mock", "subject": "Mathematics", "class": "9", "type": "Mock Test", "duration": 120, "marks": 80},
    {"title": "Class 10 Maths — Trigonometry", "subject": "Mathematics", "class": "10", "type": "Chapter Test", "duration": 30, "marks": 40},
    {"title": "Class 10 Maths — Full SSLC Mock", "subject": "Mathematics", "class": "10", "type": "Mock Test", "duration": 180, "marks": 100},
    {"title": "Class 10 Science — Chemical Reactions", "subject": "Science", "class": "10", "type": "Chapter Test", "duration": 30, "marks": 40},
    {"title": "Class 10 Science — Full SSLC Mock", "subject": "Science", "class": "10", "type": "Mock Test", "duration": 180, "marks": 100},
    {"title": "Class 10 Social — Nationalism", "subject": "Social Science", "class": "10", "type": "Chapter Test", "duration": 25, "marks": 30},
    {"title": "Class 10 English — Reading & Writing", "subject": "English", "class": "10", "type": "Chapter Test", "duration": 20, "marks": 25},
    {"title": "Class 10 Computer Practice", "subject": "Computer Science", "class": "10", "type": "Chapter Test", "duration": 30, "marks": 30},
    {"title": "1st PUC Physics — Mechanics", "subject": "Physics", "class": "11", "type": "Chapter Test", "duration": 45, "marks": 50},
    {"title": "1st PUC Chemistry — Basic Concepts", "subject": "Chemistry", "class": "11", "type": "Chapter Test", "duration": 40, "marks": 50},
    {"title": "1st PUC Biology — Diversity of Life", "subject": "Biology", "class": "11", "type": "Chapter Test", "duration": 40, "marks": 50},
    {"title": "1st PUC Maths — Sets & Functions", "subject": "Mathematics", "class": "11", "type": "Chapter Test", "duration": 45, "marks": 50},
    {"title": "1st PUC Full Mock Test", "subject": "Physics", "class": "11", "type": "Mock Test", "duration": 180, "marks": 100},
    {"title": "2nd PUC Physics — Electrostatics", "subject": "Physics", "class": "12", "type": "Chapter Test", "duration": 45, "marks": 50},
    {"title": "2nd PUC Chemistry — Electrochemistry", "subject": "Chemistry", "class": "12", "type": "Chapter Test", "duration": 40, "marks": 50},
    {"title": "2nd PUC Biology — Genetics", "subject": "Biology", "class": "12", "type": "Chapter Test", "duration": 40, "marks": 50},
    {"title": "2nd PUC Maths — Vectors & 3D Geometry", "subject": "Mathematics", "class": "12", "type": "Chapter Test", "duration": 45, "marks": 50},
    {"title": "2nd PUC Maths — Integrals & Calculus", "subject": "Mathematics", "class": "12", "type": "Chapter Test", "duration": 45, "marks": 50},
    {"title": "2nd PUC Full Mock Test", "subject": "Chemistry", "class": "12", "type": "Mock Test", "duration": 180, "marks": 100},
    {"title": "JEE Main — Full Mock Test 1", "subject": "Physics", "class": "12", "type": "JEE", "duration": 180, "marks": 300},
    {"title": "JEE Main — Physics Practice", "subject": "Physics", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "JEE Main — Chemistry Practice", "subject": "Chemistry", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "JEE Main — Mathematics Practice", "subject": "Mathematics", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "JEE Advanced — Physics", "subject": "Physics", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "JEE Advanced — Chemistry", "subject": "Chemistry", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "JEE Advanced — Mathematics", "subject": "Mathematics", "class": "12", "type": "JEE", "duration": 60, "marks": 100},
    {"title": "NEET — Full Mock Test 1", "subject": "Biology", "class": "12", "type": "NEET", "duration": 200, "marks": 720},
    {"title": "NEET — Physics Practice", "subject": "Physics", "class": "12", "type": "NEET", "duration": 45, "marks": 180},
    {"title": "NEET — Chemistry Practice", "subject": "Chemistry", "class": "12", "type": "NEET", "duration": 45, "marks": 180},
    {"title": "NEET — Biology Practice", "subject": "Biology", "class": "12", "type": "NEET", "duration": 90, "marks": 360},
    {"title": "NEET — Botany Chapter Test", "subject": "Biology", "class": "12", "type": "NEET", "duration": 30, "marks": 120},
    {"title": "NEET — Zoology Chapter Test", "subject": "Biology", "class": "12", "type": "NEET", "duration": 30, "marks": 120},
]

REAL_QUESTION_BANK = {
    "Mathematics": [
        {"q": "What is the derivative of x^2?", "options": ["x", "2x", "x^2", "2"], "ans": "2x"},
        {"q": "Solve for x: 2x + 5 = 15", "options": ["5", "10", "4", "2"], "ans": "5"},
        {"q": "What is the value of sin(90°)?", "options": ["0", "1", "-1", "undefined"], "ans": "1"},
        {"q": "Find the integral of 2x dx.", "options": ["x^2 + C", "x^2", "2x^2 + C", "x + C"], "ans": "x^2 + C"},
        {"q": "What is the probability of rolling a 6 on a fair die?", "options": ["1/6", "1/2", "1/3", "1"], "ans": "1/6"},
        {"q": "What is the sum of angles in a triangle?", "options": ["90°", "180°", "360°", "270°"], "ans": "180°"},
        {"q": "Calculate 15% of 200.", "options": ["30", "15", "45", "50"], "ans": "30"},
        {"q": "Find the roots of x^2 - 5x + 6 = 0.", "options": ["2, 3", "-2, -3", "1, 6", "-1, -6"], "ans": "2, 3"},
        {"q": "What is the value of log10(100)?", "options": ["1", "2", "10", "100"], "ans": "2"},
        {"q": "What is the area of a circle with radius r?", "options": ["πr", "2πr", "πr^2", "2πr^2"], "ans": "πr^2"},
    ],
    "Physics": [
        {"q": "What is the SI unit of force?", "options": ["Joule", "Newton", "Pascal", "Watt"], "ans": "Newton"},
        {"q": "What is the speed of light in vacuum?", "options": ["3x10^8 m/s", "3x10^5 m/s", "3x10^6 m/s", "3x10^10 m/s"], "ans": "3x10^8 m/s"},
        {"q": "Which law states F = ma?", "options": ["Newton's 1st Law", "Newton's 2nd Law", "Newton's 3rd Law", "Law of Gravitation"], "ans": "Newton's 2nd Law"},
        {"q": "What is the acceleration due to gravity on Earth?", "options": ["9.8 m/s^2", "8.9 m/s^2", "10.8 m/s^2", "9.0 m/s^2"], "ans": "9.8 m/s^2"},
        {"q": "Energy of a photon is given by?", "options": ["E = mc^2", "E = hv", "E = 1/2mv^2", "E = mgh"], "ans": "E = hv"},
        {"q": "What is the unit of electric current?", "options": ["Volt", "Ampere", "Ohm", "Coulomb"], "ans": "Ampere"},
        {"q": "What does a voltmeter measure?", "options": ["Current", "Voltage", "Resistance", "Power"], "ans": "Voltage"},
        {"q": "What is the work done if displacement is zero?", "options": ["Infinity", "Maximum", "Zero", "Negative"], "ans": "Zero"},
        {"q": "What type of lens is used in a magnifying glass?", "options": ["Concave", "Convex", "Plano-concave", "Cylindrical"], "ans": "Convex"},
        {"q": "What is the phenomenon of splitting of white light?", "options": ["Reflection", "Refraction", "Dispersion", "Diffraction"], "ans": "Dispersion"},
    ],
    "Chemistry": [
        {"q": "Atomic number represents the number of?", "options": ["Protons", "Neutrons", "Electrons", "Nucleons"], "ans": "Protons"},
        {"q": "Which is the lightest element?", "options": ["Helium", "Hydrogen", "Lithium", "Carbon"], "ans": "Hydrogen"},
        {"q": "What is the pH of pure water?", "options": ["7", "0", "14", "1"], "ans": "7"},
        {"q": "Which gas is known as laughing gas?", "options": ["NO2", "N2O", "NH3", "NO"], "ans": "N2O"},
        {"q": "Chemical formula for water?", "options": ["HO", "H2O2", "H2O", "O2H"], "ans": "H2O"},
        {"q": "Which metal is liquid at room temperature?", "options": ["Iron", "Mercury", "Gold", "Silver"], "ans": "Mercury"},
        {"q": "What is the common name for NaCl?", "options": ["Baking Soda", "Washing Soda", "Common Salt", "Bleaching Powder"], "ans": "Common Salt"},
        {"q": "Most abundant gas in Earth's atmosphere?", "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Argon"], "ans": "Nitrogen"},
        {"q": "What type of bond involves sharing of electrons?", "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "ans": "Covalent"},
        {"q": "Which acid is present in lemon?", "options": ["Acetic Acid", "Citric Acid", "Lactic Acid", "Hydrochloric Acid"], "ans": "Citric Acid"},
    ],
    "Biology": [
        {"q": "Powerhouse of the cell?", "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi Body"], "ans": "Mitochondria"},
        {"q": "Process by which plants make food?", "options": ["Respiration", "Photosynthesis", "Transpiration", "Digestion"], "ans": "Photosynthesis"},
        {"q": "Basic unit of life?", "options": ["Tissue", "Organ", "Cell", "System"], "ans": "Cell"},
        {"q": "Which part of the brain controls balance?", "options": ["Cerebrum", "Cerebellum", "Medulla", "Pons"], "ans": "Cerebellum"},
        {"q": "Which blood cells carry oxygen?", "options": ["WBC", "RBC", "Platelets", "Plasma"], "ans": "RBC"},
        {"q": "Number of chromosomes in human cell?", "options": ["46", "23", "48", "44"], "ans": "46"},
        {"q": "Enzyme in saliva that breaks down starch?", "options": ["Lipase", "Amylase", "Pepsin", "Trypsin"], "ans": "Amylase"},
        {"q": "Largest organ in the human body?", "options": ["Liver", "Heart", "Skin", "Lungs"], "ans": "Skin"},
        {"q": "What hormone is responsible for blood sugar regulation?", "options": ["Adrenaline", "Insulin", "Thyroxine", "Testosterone"], "ans": "Insulin"},
        {"q": "DNA stands for?", "options": ["Deoxyribonucleic Acid", "Diribonucleic Acid", "Dioxy Acid", "Deoxynucleic Acid"], "ans": "Deoxyribonucleic Acid"},
    ],
    "Science": [
        {"q": "Water boils at what temperature (Celsius)?", "options": ["100", "0", "50", "90"], "ans": "100"},
        {"q": "What planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "ans": "Mars"},
        {"q": "What is the hardest natural substance on Earth?", "options": ["Gold", "Iron", "Diamond", "Platinum"], "ans": "Diamond"},
        {"q": "Electric resistance is measured in?", "options": ["Volts", "Amperes", "Ohms", "Watts"], "ans": "Ohms"},
        {"q": "What force pulls objects toward the center of the Earth?", "options": ["Friction", "Gravity", "Magnetism", "Tension"], "ans": "Gravity"},
        {"q": "What is the chemical symbol for Iron?", "options": ["Ir", "Fe", "In", "I"], "ans": "Fe"},
        {"q": "Animals that eat both plants and meat are called?", "options": ["Herbivores", "Carnivores", "Omnivores", "Insectivores"], "ans": "Omnivores"},
        {"q": "What travels fastest in the universe?", "options": ["Sound", "Light", "Rocket", "Electricity"], "ans": "Light"},
        {"q": "What is the freezing point of water?", "options": ["0 °C", "32 °C", "100 °C", "10 °C"], "ans": "0 °C"},
        {"q": "Which sense uses the olfactory nerve?", "options": ["Sight", "Hearing", "Smell", "Taste"], "ans": "Smell"},
    ],
    "Social Science": [
        {"q": "Who is known as the Father of the Nation in India?", "options": ["Bose", "Gandhi", "Nehru", "Patel"], "ans": "Gandhi"},
        {"q": "Capital of France?", "options": ["Rome", "Berlin", "Paris", "Madrid"], "ans": "Paris"},
        {"q": "Which continent is known as the Dark Continent?", "options": ["Asia", "Africa", "Europe", "South America"], "ans": "Africa"},
        {"q": "Who wrote the Indian Constitution?", "options": ["Gandhi", "Ambedkar", "Nehru", "Prasad"], "ans": "Ambedkar"},
        {"q": "Longest river in the world?", "options": ["Amazon", "Nile", "Ganga", "Yangtze"], "ans": "Nile"},
        {"q": "Mount Everest is located in which mountain range?", "options": ["Alps", "Rockies", "Andes", "Himalayas"], "ans": "Himalayas"},
        {"q": "Who discovered America?", "options": ["Columbus", "Vasco da Gama", "Magellan", "Cook"], "ans": "Columbus"},
        {"q": "What is the currency of Japan?", "options": ["Yuan", "Yen", "Won", "Rupee"], "ans": "Yen"},
        {"q": "Which ocean is the largest?", "options": ["Atlantic", "Indian", "Pacific", "Arctic"], "ans": "Pacific"},
        {"q": "First War of Indian Independence happened in?", "options": ["1857", "1947", "1914", "1885"], "ans": "1857"},
    ],
    "English": [
        {"q": "Which word is an antonym for 'Happy'?", "options": ["Joyful", "Sad", "Angry", "Excited"], "ans": "Sad"},
        {"q": "Find the synonym for 'Quick':", "options": ["Slow", "Fast", "Lazy", "Dull"], "ans": "Fast"},
        {"q": "Identify the noun in: 'The dog barked loudly.'", "options": ["The", "dog", "barked", "loudly"], "ans": "dog"},
        {"q": "Choose the correct spelling:", "options": ["Recieve", "Receive", "Receeve", "Receieve"], "ans": "Receive"},
        {"q": "What is the past tense of 'Go'?", "options": ["Goes", "Gone", "Went", "Going"], "ans": "Went"},
        {"q": "Select the correct article: '___ apple a day'", "options": ["A", "An", "The", "No article"], "ans": "An"},
        {"q": "What type of word describes an action?", "options": ["Noun", "Adjective", "Verb", "Adverb"], "ans": "Verb"},
        {"q": "Complete the idiom: 'Break a ___'", "options": ["Hand", "Leg", "Glass", "Stick"], "ans": "Leg"},
        {"q": "Plural form of 'Child'?", "options": ["Childs", "Childrens", "Children", "Childes"], "ans": "Children"},
        {"q": "What refers to words that sound the same but have different meanings?", "options": ["Synonyms", "Antonyms", "Homophones", "Acronyms"], "ans": "Homophones"},
    ],
    "Computer Science": [
        {"q": "What does CPU stand for?", "options": ["Central Process Unit", "Computer Personal Unit", "Central Processing Unit", "Central Processor Unit"], "ans": "Central Processing Unit"},
        {"q": "Which of these is a programming language?", "options": ["HTML", "Python", "HTTP", "FTP"], "ans": "Python"},
        {"q": "What does RAM stand for?", "options": ["Random Access Memory", "Read Access Memory", "Run Accept Memory", "Rate Access Memory"], "ans": "Random Access Memory"},
        {"q": "Brain of the computer?", "options": ["Monitor", "Keyboard", "CPU", "Mouse"], "ans": "CPU"},
        {"q": "What does WWW stand for?", "options": ["World Wide Web", "World Web Wide", "Wide World Web", "Web World Wide"], "ans": "World Wide Web"},
        {"q": "1 Byte = __ Bits?", "options": ["4", "8", "16", "32"], "ans": "8"},
        {"q": "Which is an Output Device?", "options": ["Keyboard", "Mouse", "Monitor", "Scanner"], "ans": "Monitor"},
        {"q": "Short cut for Copy?", "options": ["Ctrl + V", "Ctrl + C", "Ctrl + X", "Ctrl + P"], "ans": "Ctrl + C"},
        {"q": "Which symbol is used for comments in Python?", "options": ["//", "/*", "#", "--"], "ans": "#"},
        {"q": "Who is known as the father of computers?", "options": ["Bill Gates", "Charles Babbage", "Steve Jobs", "Alan Turing"], "ans": "Charles Babbage"},
    ],
}


async def seed_data():
    """Seed the database with real Karnataka PU Board / CBSE curriculum data."""

    if settings.DB_TYPE == "mongodb":
        await _seed_mongodb()
    else:
        await _seed_sql()


async def _seed_sql():
    """Seed via SQLAlchemy (SQLite / PostgreSQL)."""
    from sqlalchemy import delete, select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.database import engine

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        print("Clearing existing curriculum data...")
        for tbl in [TestQuestion, MockTest, Question, Topic, Chapter, Subject]:
            await db.execute(delete(tbl))
        await db.commit()

        print("Seeding Smart Shiksha database with real CBSE & State Board syllabus...")
        now = datetime.utcnow()

        # ── Subjects ──
        subject_objs = []
        for board in BOARDS:
            for s in BASE_SUBJECTS_CONFIG:
                obj = Subject(
                    name=s["name"], description=f"{s['desc']} ({board})", icon=s["icon"],
                    color=s["color"], classes=s["classes"], board=board, created_at=now,
                )
                db.add(obj)
                subject_objs.append((obj, s["classes"], board))
        await db.flush()

        subject_map = {}
        for obj, classes, board in subject_objs:
            for cls in classes:
                subject_map[(obj.name, cls, board)] = obj.id

        print(f"  [OK] {len(subject_objs)} subject entries created across boards")

        # ── Chapters ──
        chapter_count = 0
        for board in BOARDS:
            for (subj_name, cls), chapters in CURRICULUM.items():
                key = (subj_name, cls, board)
                if key not in subject_map:
                    continue
                subj_id = subject_map[key]
                for i, ch_name in enumerate(chapters):
                    display_name = ch_name if board in ["CBSE", "ICSE"] else f"{ch_name} ({board} Pattern)"
                    db.add(Chapter(
                        subject_id=subj_id,
                        name=display_name,
                        description=f"{display_name} — {subj_name} Class {cls} {board}",
                        order_index=i, student_class=cls, board=board, created_at=now,
                    ))
                    chapter_count += 1
        await db.flush()
        print(f"  [OK] {chapter_count} real chapters seeded across boards and classes")

        # ── Mock Tests + Questions ──
        test_objs = _create_mock_tests(db, now)
        await db.flush()
        print(f"  [OK] {len(test_objs)} mock tests created")

        q_count = _create_test_questions(db, test_objs, now)
        await db.flush()
        print(f"  [OK] {q_count} mock test questions created")

        # Admin user
        result = await db.execute(select(User).where(User.role == "admin"))
        if not result.scalar_one_or_none():
            db.add(User(
                clerk_id="admin_dev", name="Admin", email="admin@smartshiksha.com",
                student_class="12", board="Karnataka PU Board", language="English",
                role="admin", onboarding_complete=True,
                created_at=now, updated_at=now,
            ))
            print("  [OK] Admin user created")

        await db.commit()
        print(f"\nDONE: Seeding complete! ({len(test_objs)} tests, {chapter_count} chapters)")


async def _seed_mongodb():
    """Seed via Motor (MongoDB)."""
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]

    print("Clearing existing curriculum data (MongoDB)...")
    for coll in ["test_questions", "mock_tests", "questions", "topics", "chapters", "subjects"]:
        await db[coll].delete_many({})
    # Reset counters
    await db["_counters"].delete_many({})

    print("Seeding Smart Shiksha MongoDB with real CBSE & State Board syllabus...")
    now = datetime.utcnow()
    next_id_cache: dict[str, int] = {}

    def get_id(collection: str) -> int:
        next_id_cache.setdefault(collection, 0)
        next_id_cache[collection] += 1
        return next_id_cache[collection]

    # ── Subjects ──
    subject_docs = []
    subject_map: dict[tuple, int] = {}
    for board in BOARDS:
        for s in BASE_SUBJECTS_CONFIG:
            sid = get_id("subjects")
            doc = {
                "id": sid, "name": s["name"], "description": f"{s['desc']} ({board})",
                "icon": s["icon"], "color": s["color"], "classes": s["classes"],
                "board": board, "created_at": now,
            }
            subject_docs.append(doc)
            for cls in s["classes"]:
                subject_map[(s["name"], cls, board)] = sid
    if subject_docs:
        await db.subjects.insert_many(subject_docs)
    print(f"  [OK] {len(subject_docs)} subject entries created across boards")

    # ── Chapters ──
    chapter_docs = []
    for board in BOARDS:
        for (subj_name, cls), chapters in CURRICULUM.items():
            key = (subj_name, cls, board)
            if key not in subject_map:
                continue
            subj_id = subject_map[key]
            for i, ch_name in enumerate(chapters):
                display_name = ch_name if board in ["CBSE", "ICSE"] else f"{ch_name} ({board} Pattern)"
                chapter_docs.append({
                    "id": get_id("chapters"), "subject_id": subj_id,
                    "name": display_name,
                    "description": f"{display_name} — {subj_name} Class {cls} {board}",
                    "order_index": i, "student_class": cls, "board": board, "created_at": now,
                })
    if chapter_docs:
        await db.chapters.insert_many(chapter_docs)
    print(f"  [OK] {len(chapter_docs)} real chapters seeded across boards and classes")

    # ── Mock Tests ──
    test_docs = []
    for t in TESTS_METADATA:
        tid = get_id("mock_tests")
        test_docs.append({
            "id": tid, "title": t["title"],
            "description": f"Comprehensive {t['type']} for {t['subject']}",
            "test_type": t["type"], "student_class": t["class"],
            "subject_name": t["subject"], "duration_minutes": t["duration"],
            "total_marks": t["marks"], "question_count": 10,
            "is_active": True, "created_at": now,
        })
    if test_docs:
        await db.mock_tests.insert_many(test_docs)
    print(f"  [OK] {len(test_docs)} mock tests created")

    # ── Test Questions ──
    tq_docs = []
    for tdoc, t_meta in zip(test_docs, TESTS_METADATA):
        pool = REAL_QUESTION_BANK.get(t_meta["subject"], REAL_QUESTION_BANK["Science"])
        marks_per_q = max(1, t_meta["marks"] // 10)
        for i in range(10):
            q = pool[i % len(pool)]
            tq_docs.append({
                "id": get_id("test_questions"), "test_id": tdoc["id"],
                "question_text": q["q"], "question_type": "MCQ",
                "options": q["options"], "correct_answer": q["ans"],
                "marks": marks_per_q, "order_index": i, "created_at": now,
            })
    if tq_docs:
        await db.test_questions.insert_many(tq_docs)
    print(f"  [OK] {len(tq_docs)} mock test questions created")

    # ── Admin user ──
    existing = await db.users.find_one({"role": "admin"})
    if not existing:
        await db.users.insert_one({
            "id": get_id("users"),
            "clerk_id": "admin_dev", "name": "Admin", "email": "admin@smartshiksha.com",
            "student_class": "12", "board": "Karnataka PU Board", "language": "English",
            "role": "admin", "onboarding_complete": True,
            "created_at": now, "updated_at": now,
        })
        print("  [OK] Admin user created")

    # Sync counters collection
    for coll_name, seq in next_id_cache.items():
        await db["_counters"].update_one(
            {"_id": coll_name}, {"$set": {"seq": seq}}, upsert=True
        )

    client.close()
    print(f"\nDONE: Seeding complete! ({len(test_docs)} tests, {len(chapter_docs)} chapters)")


def _create_mock_tests(db, now):
    """Add MockTest objects to the session. Returns list of (obj, meta) tuples."""
    pairs = []
    for t in TESTS_METADATA:
        obj = MockTest(
            title=t["title"],
            description=f"Comprehensive {t['type']} for {t['subject']}",
            test_type=t["type"], student_class=t["class"],
            subject_name=t["subject"], duration_minutes=t["duration"],
            total_marks=t["marks"], question_count=10,
            is_active=True, created_at=now,
        )
        db.add(obj)
        pairs.append((obj, t))
    return pairs


def _create_test_questions(db, test_objs, now) -> int:
    count = 0
    for test_obj, t_meta in test_objs:
        pool = REAL_QUESTION_BANK.get(t_meta["subject"], REAL_QUESTION_BANK["Science"])
        marks_per_q = max(1, t_meta["marks"] // 10)
        for i in range(10):
            q = pool[i % len(pool)]
            db.add(TestQuestion(
                test_id=test_obj.id, question_text=q["q"],
                question_type="MCQ", options=q["options"],
                correct_answer=q["ans"], marks=marks_per_q,
                order_index=i, created_at=now,
            ))
            count += 1
    return count


if __name__ == "__main__":
    asyncio.run(seed_data())
