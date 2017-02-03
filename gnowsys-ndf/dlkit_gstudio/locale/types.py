# -*- coding: utf-8 -*-
from dlkit.abstract_osid.osid.errors import NotFound

class Language:

    iso_major_language_types = {
        'AAR': 'Afar',
        'ABK': 'Abkhazian',
        'ACE': 'Achinese',
        'ACH': 'Acoli',
        'ADA': 'Adangme',
        'ADY': 'Adyghe, Adygei',
        'AFR': 'Afrikaans',
        'AIN': 'Ainu',
        'ALE': 'Aleut',
        'ALT': 'Southern Altai',
        'AMH': 'Amharic',
        'ANP': 'Angika',
        'ARA': 'Arabic',
        'ARG': 'Aragonese',
        'ARM': 'Armenian',
        'ARN': 'Mapudungun, Mapuche',
        'ARP': 'Arapaho',
        'ARW': 'Arawak',
        'ASM': 'Assamese',
        'AST': 'Asturian, Bable, Leonese, Asturleonese',
        'AVA': 'Avaric',
        'AWA': 'Awadhi',
        'BAK': 'Bashkir',
        'BAL': 'Baluchi',
        'BAM': 'Bambara',
        'BAN': 'Balinese',
        'BAQ': 'Basque',
        'BAS': 'Basa',
        'BEJ': 'Beja, Bedawiyet',
        'BEL': 'Belarusian',
        'BEM': 'Bemba',
        'BEN': 'Bengali',
        'BHO': 'Bhojpuri',
        'BIN': 'Bini, Edo',
        'BIS': 'Bislama',
        'BLA': 'Siksika',
        'BNT': 'Bantu (Other)',
        'BOS': 'Bosnian',
        'BRA': 'Braj',
        'BRE': 'Breton',
        'BUG': 'Buginese',
        'BUL': 'Bulgarian',
        'BUR': 'Burmese',
        'BYN': 'Blin, Bilin',
        'CAD': 'Caddo',
        'CAR': 'Galibi Carib',
        'CAT': 'Catalan, Valencian',
        'CEB': 'Cebuano',
        'CHA': 'Chamorro',
        'CHE': 'Chechen',
        'CHI': 'Chinese',
        'CHK': 'Chuukese',
        'CHM': 'Mari',
        'CHN': 'Chinook jargon',
        'CHO': 'Choctaw',
        'CHP': 'Chipewyan, Dene Suline',
        'CHR': 'Cherokee',
        'CHV': 'Chuvash',
        'CHY': 'Cheyenne',
        'COR': 'Cornish',
        'COS': 'Corsican',
        'CPE': 'Creoles and pidgins, English based',
        'CPF': 'Creoles and pidgins, French-based',
        'CPP': 'Creoles and pidgins, Portuguese-based',
        'CRH': 'Crimean Tatar, Crimean Turkish',
        'CRP': 'Creoles and pidgins',
        'CSB': 'Kashubian',
        'CZE': 'Czech',
        'DAK': 'Dakota',
        'DAN': 'Danish',
        'DAR': 'Dargwa',
        'DGR': 'Dogrib',
        'DIV': 'Divehi, Dhivehi, Maldivian',
        'DOI': 'Dogri',
        'DSB': 'Lower Sorbian',
        'DUA': 'Duala',
        'DUT': 'Dutch, Flemish',
        'DYU': 'Dyula',
        'DZO': 'Dzongkha',
        'EFI': 'Efik',
        'EKA': 'Ekajuk',
        'ENG': 'English',
        'EPO': 'Esperanto',
        'EWE': 'Ewe',
        'EWO': 'Ewondo',
        'FAN': 'Fang',
        'FAO': 'Faroese',
        'FAT': 'Fanti',
        'FIJ': 'Fijian',
        'FIL': 'Filipino, Pilipino',
        'FIN': 'Finnish',
        'FON': 'Fon',
        'FRE': 'French',
        'FRR': 'Northern Frisian',
        'FRS': 'Eastern Frisian',
        'FRY': 'Western Frisian',
        'FUR': 'Friulian',
        'GAA': 'Ga',
        'GAY': 'Gayo',
        'GEO': 'Georgian',
        'GER': 'German',
        'GIL': 'Gilbertese',
        'GLA': 'Gaelic, Scottish Gaelic',
        'GLE': 'Irish',
        'GLG': 'Galician',
        'GLV': 'Manx',
        'GOR': 'Gorontalo',
        'GRC': 'Greek, Ancient (to 1453)',
        'GRE': 'Greek, Modern (1453-)',
        'GSW': 'Swiss German, Alemannic, Alsatian',
        'GUJ': 'Gujarati',
        'GWI': 'Gwich\'in',
        'HAT': 'Haitian, Haitian Creole',
        'HAU': 'Hausa',
        'HAW': 'Hawaiian',
        'HEB': 'Hebrew',
        'HER': 'Herero',
        'HIL': 'Hiligaynon',
        'HIN': 'Hindi',
        'HMO': 'Hiri Motu',
        'HRV': 'Croatian',
        'HSB': 'Upper Sorbian',
        'HUN': 'Hungarian',
        'HUP': 'Hupa',
        'IBA': 'Iban',
        'IBO': 'Igbo',
        'ICE': 'Icelandic',
        'III': 'Sichuan Yi, Nuosu',
        'ILO': 'Iloko',
        'IND': 'Indonesian',
        'INH': 'Ingush',
        'ITA': 'Italian',
        'JAV': 'Javanese',
        'JPN': 'Japanese',
        'JPR': 'Judeo-Persian',
        'KAA': 'Kara-Kalpak',
        'KAB': 'Kabyle',
        'KAC': 'Kachin, Jingpho',
        'KAL': 'Kalaallisut, Greenlandic',
        'KAM': 'Kamba',
        'KAN': 'Kannada',
        'KAS': 'Kashmiri',
        'KAZ': 'Kazakh',
        'KBD': 'Kabardian',
        'KHA': 'Khasi',
        'KHM': 'Central Khmer',
        'KHO': 'Khotanese, Sakan',
        'KIK': 'Kikuyu, Gikuyu',
        'KIN': 'Kinyarwanda',
        'KIR': 'Kirghiz, Kyrgyz',
        'KMB': 'Kimbundu',
        'KOR': 'Korean',
        'KOS': 'Kosraean',
        'KRC': 'Karachay-Balkar',
        'KRL': 'Karelian',
        'KRU': 'Kurukh',
        'KUA': 'Kuanyama, Kwanyama',
        'KUM': 'Kumyk',
        'KUT': 'Kutenai',
        'LAD': 'Ladino',
        'LAM': 'Lamba',
        'LAO': 'Lao',
        'LAV': 'Latvian',
        'LEZ': 'Lezghian',
        'LIM': 'Limburgan, Limburger, Limburgish',
        'LIN': 'Lingala',
        'LIT': 'Lithuanian',
        'LOL': 'Mongo',
        'LOZ': 'Lozi',
        'LTZ': 'Luxembourgish, Letzeburgesch',
        'LUA': 'Luba-Lulua',
        'LUB': 'Luba-Katanga',
        'LUG': 'Ganda',
        'LUI': 'Luiseno',
        'LUN': 'Lunda',
        'LUO': 'Luo (Kenya and Tanzania)',
        'LUS': 'Lushai',
        'MAC': 'Macedonian',
        'MAD': 'Madurese',
        'MAG': 'Magahi',
        'MAH': 'Marshallese',
        'MAI': 'Maithili',
        'MAK': 'Makasar',
        'MAL': 'Malayalam',
        'MAO': 'Maori',
        'MAR': 'Marathi',
        'MAS': 'Masai',
        'MDF': 'Moksha',
        'MDR': 'Mandar',
        'MEN': 'Mende',
        'MIC': 'Mi\'kmaq, Micmac',
        'MIN': 'Minangkabau',
        'MLT': 'Maltese',
        'MNC': 'Manchu',
        'MNI': 'Manipuri',
        'MOH': 'Mohawk',
        'MOS': 'Mossi',
        'MUS': 'Creek',
        'MWL': 'Mirandese',
        'MYV': 'Erzya',
        'NAP': 'Neapolitan',
        'NAU': 'Nauru',
        'NAV': 'Navajo, Navaho',
        'NBL': 'Ndebele, South, South Ndebele',
        'NDE': 'Ndebele, North, North Ndebele',
        'NDO': 'Ndonga',
        'NDS': 'Low German, Low Saxon, German, Low, Saxon, Low',
        'NEP': 'Nepali',
        'NEW': 'Nepal Bhasa, Newari',
        'NIA': 'Nias',
        'NIU': 'Niuean',
        'NNO': 'Norwegian Nynorsk, Nynorsk, Norwegian',
        'NOB': 'Bokmål, Norwegian, Norwegian Bokmål',
        'NOG': 'Nogai',
        'NQO': 'N\'Ko',
        'NSO': 'Pedi, Sepedi, Northern Sotho',
        'NWC': 'Classical Newari, Old Newari, Classical Nepal Bhasa',
        'NYA': 'Chichewa, Chewa, Nyanja',
        'NYM': 'Nyamwezi',
        'NYN': 'Nyankole',
        'NYO': 'Nyoro',
        'NZI': 'Nzima',
        'OCI': 'Occitan (post 1500), Provençal',
        'ORI': 'Oriya',
        'OSA': 'Osage',
        'OSS': 'Ossetian, Ossetic',
        'PAG': 'Pangasinan',
        'PAM': 'Pampanga, Kapampangan',
        'PAN': 'Panjabi, Punjabi',
        'PAP': 'Papiamento',
        'PAU': 'Palauan',
        'PER': 'Persian',
        'POL': 'Polish',
        'PON': 'Pohnpeian',
        'POR': 'Portuguese',
        'PUS': 'Pushto, Pashto',
        'RAP': 'Rapanui',
        'RAR': 'Rarotongan, Cook Islands Maori',
        'ROH': 'Romansh',
        'RUM': 'Romanian, Moldavian, Moldovan',
        'RUN': 'Rundi',
        'RUP': 'Aromanian, Arumanian, Macedo-Romanian',
        'RUS': 'Russian',
        'SAD': 'Sandawe',
        'SAG': 'Sango',
        'SAH': 'Yakut',
        'SAI': 'South American Indian (Other)',
        'SAS': 'Sasak',
        'SAT': 'Santali',
        'SCN': 'Sicilian',
        'SCO': 'Scots',
        'SEL': 'Selkup',
        'SHN': 'Shan',
        'SID': 'Sidamo',
        'SIN': 'Sinhala, Sinhalese',
        'SLO': 'Slovak',
        'SLV': 'Slovenian',
        'SMA': 'Southern Sami',
        'SME': 'Northern Sami',
        'SMJ': 'Lule Sami',
        'SMN': 'Inari Sami',
        'SMO': 'Samoan',
        'SMS': 'Skolt Sami',
        'SNA': 'Shona',
        'SND': 'Sindhi',
        'SNK': 'Soninke',
        'SOM': 'Somali',
        'SOT': 'Sotho, Southern',
        'SPA': 'Spanish, Castilian',
        'SRN': 'Sranan Tongo',
        'SRP': 'Serbian',
        'SRR': 'Serer',
        'SSW': 'Swati',
        'SUK': 'Sukuma',
        'SUN': 'Sundanese',
        'SUS': 'Susu',
        'SWE': 'Swedish',
        'TAH': 'Tahitian',
        'TAM': 'Tamil',
        'TAT': 'Tatar',
        'TEL': 'Telugu',
        'TEM': 'Timne',
        'TER': 'Tereno',
        'TET': 'Tetum',
        'TGK': 'Tajik',
        'TGL': 'Tagalog',
        'THA': 'Thai',
        'TIB': 'Tibetan',
        'TIG': 'Tigre',
        'TIR': 'Tigrinya',
        'TIV': 'Tiv',
        'TKL': 'Tokelau',
        'TLI': 'Tlingit',
        'TOG': 'Tonga (Nyasa)',
        'TON': 'Tonga (Tonga Islands)',
        'TPI': 'Tok Pisin',
        'TSI': 'Tsimshian',
        'TSN': 'Tswana',
        'TSO': 'Tsonga',
        'TUK': 'Turkmen',
        'TUM': 'Tumbuka',
        'TUR': 'Turkish',
        'TVL': 'Tuvalu',
        'TWI': 'Twi',
        'TYV': 'Tuvinian',
        'UDM': 'Udmurt',
        'UIG': 'Uighur, Uyghur',
        'UKR': 'Ukrainian',
        'UMB': 'Umbundu',
        'UND': 'Undetermined',
        'URD': 'Urdu',
        'VAI': 'Vai',
        'VEN': 'Venda',
        'VIE': 'Vietnamese',
        'VOT': 'Votic',
        'WAL': 'Walamo',
        'WAR': 'Waray',
        'WAS': 'Washo',
        'WEL': 'Welsh',
        'WLN': 'Walloon',
        'WOL': 'Wolof',
        'XAL': 'Kalmyk, Oirat',
        'XHO': 'Xhosa',
        'YAO': 'Yao',
        'YAP': 'Yapese',
        'YOR': 'Yoruba',
        'ZAP': 'Zapotec',
        'ZEN': 'Zenaga',
        'ZUL': 'Zulu',
        'ZUN': 'Zuni'
        }

    iso_other_language_types = {
        # ISO Ancient Language Types
        'AKK': 'Akkadian',
        'ARC': 'Official Aramaic (700-300 BCE)',
        'AVE': 'Avestan',
        'CHU': 'Church Slavi',
        'CMS': 'Messapic',
        'ECR': 'Eteocretan',
        'ECY': 'Eteocypriot',
        'EGY': 'Egyptian (Ancient)',
        'ELX': 'Elamite',
        'ETT': 'Etruscan',
        'GEZ': 'Geez',
        'GMY': 'Mycenaean Greek',
        'GOT': 'Gothic',
        'HIT': 'Hittite',
        'HLU': 'Hieroglyphic Luwian',
        'HTX': 'Middle Hittite',
        'IMS': 'Marsian',
        'IMY': 'Milyan',
        'INM': 'Minaean',
        'KAW': 'Kawi',
        'KHO': 'Khotanese',
        'LAB': 'Linear A',
        'LAT': 'Lati',
        'LNG': 'Langobardic',
        'NEI': 'Neo-Hittite',
        'NRC': 'Nori',
        'NRP': 'North Picene',
        'NXM': 'Numidian',
        'OAR': 'Old Aramaic (up to 700 BCE)',
        'OBM': 'Moabite',
        'OCH': 'Old Chinese',
        'OHT': 'Old Hittite',
        'OMN': 'Minoan',
        'OOS': 'Old Ossetic',
        'OSC': 'Osca',
        'OTY': 'Old Tamil',
        'PAL': 'Pahlavi',
        'PGL': 'Primitive Irish',
        'PGN': 'Paelignian',
        'PHN': 'Phoenician',
        'PLI': 'Pali',
        'PLQ': 'Palaic',
        'PYX': 'Pyu (Myanmar',
        'SAN': 'Sanskrit',
        'SBV': 'Sabine',
        'SCX': 'Sice',
        'SOG': 'Sogdian',
        'SPX': 'South Picene',
        'SUX': 'Sumerian',
        'SXC': 'Sicanian',
        'SXO': 'Sorothaptic',
        'TXB': 'Tokharian B',
        'TXG': 'Tangut',
        'TXH': 'Thracian',
        'TXR': 'Tartessian',
        'UGA': 'Ugaritic',
        'UMC': 'Marrucinian',
        'XAE': 'Aequian',
        'XAQ': 'Aquitanian',
        'XBC': 'Bactrian',
        'XCC': 'Camunic',
        'XCE': 'Celtiberian',
        'XCG': 'Cisalpine Gaulish',
        'XCO': 'Chorasmian',
        'XCR': 'Carian',
        'XDC': 'Dacian',
        'XDM': 'Edomite',
        'XEB': 'Ebla',
        'XEP': 'Epi-Olmec',
        'XFA': 'Faliscan',
        'XHA': 'Harami',
        'XHD': 'Hadrami',
        'XHR': 'Hernican',
        'XHT': 'Hattic',
        'XHU': 'Hurrian',
        'XIB': 'Iberian',
        'XIL': 'Illyrian',
        'XIV': 'Indus Valley Languag',
        'XLC': 'Lycian',
        'XLD': 'Lydian',
        'XLE': 'Lemnian',
        'XLG': 'Ligurian (Ancient)',
        'XLI': 'Liburnian',
        'XLN': 'Alanic',
        'XLP': 'Lepontic',
        'XLS': 'Lusitanian',
        'XLU': 'Cuneiform Luwian',
        'XLY': 'Elymian',
        'XME': 'Median',
        'XMK': 'Ancient Macedonian',
        'XMR': 'Meroitic',
        'XNA': 'Ancient North Arabia',
        'XPG': 'Phrygian',
        'XPR': 'Parthian',
        'XPU': 'Puni',
        'XQT': 'Qatabanian',
        'XRR': 'Raetic',
        'XSA': 'Sabaean',
        'XSC': 'Scythian',
        'XSD': 'Sidetic',
        'XTG': 'Transalpine Gaulish',
        'XTO': 'Tokharian A',
        'XTR': 'Early Tripur',
        'XUM': 'Umbrian',
        'XUR': 'Urartian',
        'XVE': 'Venetic',
        'XVN': 'Vandalic',
        'XVO': 'Volscian',
        'XVS': 'Vestinian',
        'XZH': 'Zhang-Zhung',
        'YMS': 'Mysian',
        'ZSK': 'Kaskean',
        # ISO Constructed Language Types
        'AFH': 'Afrihili',
        'AVK': 'Kotava',
        'BZT': 'Brithenig',
        'DWS': 'Dutton World Speedwords',
        'EPO': 'Esperanto',
        'IDO': 'Ido',
        'IGS': 'Interglossa',
        'ILE': 'Interlingue',
        'INA': 'Interlingua (International Auxiliary Language Association)',
        'JBO': 'Lojban',
        'LDN': 'Láadan',
        'LFN': 'Lingua Franca Nova',
        'NEU': 'Neo',
        'NOV': 'Novial',
        'QYA': 'Quenya',
        'RMV': 'Romanova',
        'SJN': 'Sindarin',
        'TLH': 'Klingon',
        'VOL': 'Volapük',
        'ZBL': 'Blissymbols',
        # ISO Extinct Language Types
        'AAQ': 'Eastern Abnaki',
        'ABE': 'Western Abnaki',
        'ABJ': 'Aka-Bea',
        'ACI': 'Aka-Cari',
        'ACK': 'Aka-Kora',
        'ACL': 'Akar-Bale',
        'ACS': 'Acro',
        'AEA': 'Areb',
        'AES': 'Alse',
        'AGA': 'Aguano',
        'AHO': 'Ahom',
        'AID': 'Alngith',
        'AIT': 'Arikem',
        'AJW': 'Ajaw',
        'AKJ': 'Aka-Jeru',
        'AKM': 'Aka-Bo',
        'AKX': 'Aka-Kede',
        'AKY': 'Aka-Kol',
        'AMA': 'Amanayé',
        'AMZ': 'Atampaya',
        'ANA': 'Andaqui',
        'ANB': 'Ando',
        'ANS': 'Anserma',
        'AOH': 'Arma',
        'AOR': 'Aore',
        'APV': 'Alapmunte',
        'AQP': 'Atakapa',
        'ARD': 'Arabana',
        'ARJ': 'Arapaso',
        'ARU': 'Aruá (Amazonas State',
        'ASH': 'Abishira',
        'ATC': 'Atsahuaca',
        'AUO': 'Auyokawa',
        'AUX': 'Aurá',
        'AVM': 'Angkamuthi',
        'AVO': 'Agavotaguerr',
        'AVS': 'Aushiri',
        'AWG': 'Anguthimri',
        'AWK': 'Awabakal',
        'AXB': 'Abipon',
        'AXE': 'Ayerrerenge',
        'AXG': 'Mato Grosso Arára',
        'AYD': 'Ayabadhu',
        'AYY': 'Tayabas Ayta',
        'BAE': 'Baré',
        'BJB': 'Banggarla',
        'BJY': 'Bayali',
        'BLL': 'Biloxi',
        'BMN': 'Bina (Papua New Guinea)',
        'BOI': 'Barbareño',
        'BOW': 'Rema',
        'BPB': 'Barbacoas',
        'BPT': 'Barrow Point',
        'BQF': 'Baga Kaloum',
        'BRC': 'Berbice Creole Dutch',
        'BRK': 'Birked',
        'BSL': 'Basa-Gumna',
        'BSV': 'Baga Sobané',
        'BTE': 'Gamo-Ningi',
        'BUE': 'Beothuk',
        'BVV': 'Baniva',
        'BXI': 'Pirlatapa',
        'BYG': 'Bayg',
        'BYQ': 'Basa',
        'BYT': 'Bert',
        'BZR': 'Biri',
        'CAJ': 'Chan',
        'CAZ': 'Canichana',
        'CBE': 'Chipiajes',
        'CBH': 'Cagu',
        'CCA': 'Cauc',
        'CCR': 'Cacaopera',
        'CEA': 'Lower Chehalis',
        'CHB': 'Chibcha',
        'CHC': 'Catawba',
        'CHG': 'Chagatai',
        'CHT': 'Cholón',
        'CID': 'Chimariko',
        'CJH': 'Upper Chehalis',
        'CMM': 'Michigamea',
        'COB': 'Chicomucelte',
        'COJ': 'Cochimi',
        'COP': 'Coptic',
        'COQ': 'Coquille',
        'COW': 'Cowlitz',
        'COY': 'Coyaima',
        'CPG': 'Cappadocian Greek',
        'CRB': 'Island Carib',
        'CRF': 'Caramanta',
        'CRR': 'Carolina Algonquian',
        'CRZ': 'Cruzeño',
        'CSI': 'Coast Miwok',
        'CSS': 'Southern Ohlone',
        'CTM': 'Chitimacha',
        'CUM': 'Cumeral',
        'CUO': 'Cumanagoto',
        'CUP': 'Cupeño',
        'CYB': 'Cayubaba',
        'CZK': 'Knaanic',
        'DCR': 'Negerholland',
        'DDA': 'Dadi Dadi',
        'DDR': 'Dhudhuroa',
        'DEP': 'Pidgin Delaware',
        'DGN': 'Dagoman',
        'DGT': 'Ndrag\'ngith',
        'DGW': 'Daungwurrung',
        'DHU': 'Dhurga',
        'DIF': 'Dier',
        'DIT': 'Dirari',
        'DJA': 'Djadjawurrun',
        'DJF': 'Djangun',
        'DJL': 'Djiwarli',
        'DJW': 'Djaw',
        'DLM': 'Dalmatian',
        'DMD': 'Madhi Madhi',
        'DRQ': 'Dura',
        'DRR': 'Dororo',
        'DTH': 'Adithinngithigh',
        'DUY': 'Dicamay Agta',
        'DUZ': 'Duli',
        'DYB': 'Dyaberdyaber',
        'DYD': 'Dyugun',
        'DYG': 'Villa Viciosa Agta',
        'EEE': 'E',
        'ELI': 'Ndin',
        'EMM': 'Mamulique',
        'EMO': 'Emok',
        'EMY': 'Epigraphic Mayan',
        'ERR': 'Erre',
        'ESM': 'Esum',
        'ESQ': 'Esselen',
        'ETC': 'Etchemin',
        'EYA': 'Eyak',
        'FLN': 'Flinders Island',
        'FOS': 'Siraya',
        'FRK': 'Frankish',
        'GCD': 'Ganggalida',
        'GCE': 'Galice',
        'GDC': 'Gugu Badhun',
        'GFT': 'Gafa',
        'GGD': 'Gugadj',
        'GGK': 'Kungarakany',
        'GGR': 'Aghu Tharnggalu',
        'GHC': 'Hiberno-Scottish Gaelic',
        'GHO': 'Ghomara',
        'GKO': 'Kok-Nar',
        'GLI': 'Guliguli',
        'GLY': 'Gule',
        'GMA': 'Gambera',
        'GNC': 'Guanche',
        'GNL': 'Gangulu',
        'GNR': 'Gureng Guren',
        'GQN': 'Guana (Brazil)',
        'GUV': 'Gey',
        'GVY': 'Guyani',
        'GWM': 'Awngthim',
        'GWU': 'Guwamu',
        'GYF': 'Gungabula',
        'GYY': 'Guny',
        'HIB': 'Hibito',
        'HMK': 'Maek',
        'HOD': 'Holm',
        'HOM': 'Homa',
        'HOR': 'Horo',
        'HUW': 'Hukumina',
        'IFF': 'Ifo',
        'IHW': 'Bidhawal',
        'ILG': 'Garig-Ilgar',
        'IML': 'Milu',
        'INZ': 'Ineseño',
        'IOW': 'Iowa-Oto',
        'ITE': 'Iten',
        'JAN': 'Jandai',
        'JBW': 'Yawijibaya',
        'JGB': 'Ngbe',
        'JNG': 'Yangman',
        'JOR': 'Jorá',
        'JUC': 'Jurchen',
        'JUI': 'Ngadjuri',
        'JVD': 'Javindo',
        'KAE': 'Ketangalan',
        'KBA': 'Kalarko',
        'KBB': 'Kaxuiâna',
        'KBF': 'Kakauhua',
        'KDA': 'Worimi',
        'KGL': 'Kunggari',
        'KGM': 'Karipúna',
        'KII': 'Kitsai',
        'KLA': 'Klamath-Modo',
        'KOC': 'Kpat',
        'KOF': 'Kubi',
        'KOX': 'Coxima',
        'KPN': 'Kepkiriwát',
        'KQU': 'Sero',
        'KQZ': 'Korana',
        'KRB': 'Karkin',
        'KRK': 'Kere',
        'KTG': 'Kalkutung',
        'KTK': 'Kaniet',
        'KTQ': 'Katabaga',
        'KTW': 'Kato',
        'KUZ': 'Kunz',
        'KWZ': 'Kwad',
        'KXO': 'Kano',
        'KZK': 'Kazukuru',
        'KZW': 'Karirí-Xocó',
        'LAZ': 'Aribwatsa',
        'LBA': 'Lui',
        'LBY': 'Lamu-Lamu',
        'LEN': 'Lenc',
        'LHS': 'Mlahsö',
        'LLF': 'Hermit',
        'LLJ': 'Ladji Ladji',
        'LLK': 'Lela',
        'LMC': 'Limilngan',
        'LMZ': 'Lumbee',
        'LNJ': 'Leningitij',
        'LRE': 'Laurentian',
        'LRG': 'Laragia',
        'MBE': 'Molale',
        'MCL': 'Macaguaje',
        'MEM': 'Mangala',
        'MFW': 'Mulaha',
        'MJE': 'Muskum',
        'MJQ': 'Malaryan',
        'MJY': 'Mahican',
        'MKQ': 'Bay Miwok',
        'MMV': 'Miriti',
        'MNT': 'Maykulan',
        'MOD': 'Mobilian',
        'MOM': 'Mangue',
        'MRE': 'Martha\'s Vineyard Sign Language',
        'MSP': 'Maritsauá',
        'MTM': 'Mato',
        'MTN': 'Matagalpa',
        'MVB': 'Mattole',
        'MVL': 'Mbara (Australia)',
        'MWU': 'Mitt',
        'MXI': 'Mozarabic',
        'MYS': 'Mesmes',
        'MZO': 'Matipuhy',
        'NAY': 'Narrinyeri',
        'NBX': 'Ngur',
        'NCZ': 'Natchez',
        'NDF': 'Nadruvian',
        'NGV': 'Nagumi',
        'NHC': 'Tabasco Nahuatl',
        'NID': 'Ngandi',
        'NIG': 'Ngalakan',
        'NKP': 'Niuatoputapu',
        'NMP': 'Nimanbur',
        'NMR': 'Nimbari',
        'NMV': 'Ngamini',
        'NNR': 'Narungga',
        'NNT': 'Nanticoke',
        'NNV': 'Nugunu (Australia)',
        'NNY': 'Nyangga',
        'NOK': 'Nooksack',
        'NOM': 'Nocamán',
        'NRN': 'Norn',
        'NRT': 'Northern Kalapuya',
        'NRX': 'Ngurmbur',
        'NTS': 'Natagaimas',
        'NTW': 'Nottoway',
        'NUC': 'Nukuini',
        'NUG': 'Nungali',
        'NWA': 'Nawathinehen',
        'NWG': 'Ngayawung',
        'NWO': 'Nauo',
        'NWY': 'Nottoway-Meherrin',
        'NXN': 'Ngawun',
        'NXU': 'Nara',
        'NYP': 'Nyang\'i',
        'NYT': 'Nyawaygi',
        'NYV': 'Nyulnyul',
        'NYX': 'Nganyaywana',
        'OBI': 'Obispeño',
        'OFO': 'Ofo',
        'OKG': 'Koko Babangk',
        'OKJ': 'Oko-Juwoi',
        'OKL': 'Old Kentish Sign Language',
        'OMC': 'Mochica',
        'OME': 'Omejes',
        'OMK': 'Omok',
        'OMU': 'Omurano',
        'OPT': 'Opat',
        'OTI': 'Oti',
        'OTU': 'Otuk',
        'OUM': 'Ouma',
        'PAF': 'Paranawát',
        'PAX': 'Pankararé',
        'PAZ': 'Pankararú',
        'PBG': 'Paraujano',
        'PEB': 'Eastern Pomo',
        'PEF': 'Northeastern Pomo',
        'PEJ': 'Northern Pom',
        'PIE': 'Piro',
        'PIJ': 'Pija',
        'PIM': 'Powhatan',
        'PIT': 'Pitta Pitta',
        'PKC': 'Paekche',
        'PMC': 'Palumata',
        'PMD': 'Pallanganmiddang',
        'PMK': 'Pamlico',
        'PML': 'Lingua Franc',
        'PMZ': 'Southern Pam',
        'PNO': 'Panobo',
        'POD': 'Ponares',
        'POG': 'Potiguára',
        'POX': 'Polabian',
        'PPU': 'Papora',
        'PRR': 'Puri',
        'PSM': 'Pauserna',
        'PSY': 'Piscataway',
        'PTH': 'Pataxó Hã-Ha-Hãe',
        'PTW': 'Pentlatch',
        'PUQ': 'Puquina',
        'PUY': 'Purisimeño',
        'QUN': 'Quinault',
        'QWM': 'Kuman (Russia)',
        'QWT': 'Kwalhioqua-Tlatskana',
        'QYP': 'Quiripi',
        'RBP': 'Barababaraba',
        'REM': 'Remo',
        'RER': 'Rer Bare',
        'RGK': 'Rangkas',
        'RMD': 'Traveller Danish',
        'RNA': 'Runa',
        'RNR': 'NariNari',
        'RRT': 'Arritinngithigh',
        'SAM': 'Samaritan Aramaic',
        'SAR': 'Saraveca',
        'SDS': 'Sene',
        'SDT': 'Shuadit',
        'SGM': 'Sing',
        'SHT': 'Shasta',
        'SIA': 'Akkala Sami',
        'SIS': 'Siuslaw',
        'SJK': 'Kemi Sami',
        'SJS': 'Senhaja De Srair',
        'SKW': 'Skepi Creole Dutch',
        'SLN': 'Salinan',
        'SMC': 'Som',
        'SMP': 'Samaritan',
        'SMU': 'Somray',
        'SNH': 'Shinabo',
        'SNI': 'Sens',
        'SQN': 'Susquehannoc',
        'SUT': 'Subtiaba',
        'SVX': 'Skalvian',
        'SWW': 'Sowa',
        'SXK': 'Southern Kalapuya',
        'SXL': 'Selian',
        'SZD': 'Seru',
        'TAS': 'Tay Boi',
        'TBB': 'Tapeba',
        'TBH': 'Thurawal',
        'TBU': 'Tuba',
        'TCL': 'Taman (Myanmar)',
        'TEB': 'Tetete',
        'TEN': 'Tama (Colombia)',
        'TEP': 'Tepecano',
        'TGV': 'Tingui-Boto',
        'TGY': 'Togoyo',
        'TGZ': 'Tagalaka',
        'TIL': 'Tillamook',
        'TJM': 'Timucua',
        'TJN': 'Tonjon',
        'TJU': 'Tjurruru',
        'TKA': 'Truk',
        'TKF': 'Tukumanféd',
        'TKM': 'Takelma',
        'TME': 'Tremembé',
        'TMG': 'Ternateño',
        'TMR': 'Jewish Babylonian Aramaic (ca. 200-1200 CE)',
        'TMZ': 'Tamanaku',
        'TNQ': 'Tain',
        'TOE': 'Tomedes',
        'TPK': 'Tupinikin',
        'TPN': 'Tupinambá',
        'TPW': 'Tupí',
        'TQR': 'Torona',
        'TQW': 'Tonkawa',
        'TRY': 'Turung',
        'TRZ': 'Torá',
        'TTA': 'Tutelo',
        'TUD': 'Tuxá',
        'TUN': 'Tunica',
        'TUX': 'Tuxináwa',
        'TVY': 'Timor Pidgin',
        'TWA': 'Twan',
        'TWC': 'Teshenawa',
        'TWT': 'Turiwára',
        'TXC': 'Tsetsaut',
        'TYP': 'Thaypan',
        'UAM': 'Uamu',
        'UBY': 'Ubyk',
        'UGB': 'Kuku-Ugbanh',
        'UKY': 'Kuuk-Yak',
        'UMD': 'Umbindhamu',
        'UMG': 'Umbuygamu',
        'UMO': 'Umotína',
        'UMR': 'Umbugarla',
        'UNM': 'Unam',
        'URC': 'Urningangg',
        'URF': 'Uradhi',
        'URU': 'Urum',
        'URV': 'Uruava',
        'VEO': 'Ventureño',
        'VKA': 'Kariyarra',
        'VKM': 'Kamakan',
        'VMB': 'Mbabaram',
        'VMI': 'Miwa',
        'VML': 'Malgana',
        'VMS': 'Moksela',
        'VMU': 'Muluridyi',
        'VMV': 'Valley Maidu',
        'WAF': 'Wakoná',
        'WAM': 'Wampanoag',
        'WAO': 'Wapp',
        'WDU': 'Wadjigu',
        'WEA': 'Wewa',
        'WGA': 'Wagaya',
        'WGG': 'Wangganguru',
        'WGU': 'Wirangu',
        'WIE': 'Wik-Epa',
        'WIF': 'Wik-Keyangan',
        'WIL': 'Wilawila',
        'WIR': 'Wiraféd',
        'WIY': 'Wiyo',
        'WKA': 'Kw\'adza',
        'WKW': 'Wakawaka',
        'WLK': 'Wailaki',
        'WLU': 'Wuliwuli',
        'WLY': 'Waling',
        'WMA': 'Mawa (Nigeria)',
        'WMI': 'Wami',
        'WMN': 'Waamwang',
        'WND': 'Wandarang',
        'WNM': 'Wanggamala',
        'WOY': 'Weyt',
        'WRB': 'Warluwara',
        'WRG': 'Warungu',
        'WRH': 'Wiradhuri',
        'WRI': 'Wariyangga',
        'WRO': 'Worrorra',
        'WRW': 'Gugu Warra',
        'WRZ': 'Waray (Australia)',
        'WSU': 'Wasu',
        'WSV': 'Wotapuri-Katarqalai',
        'WUR': 'Wurrugu',
        'WWB': 'Wakabunga',
        'WWR': 'Warrwa',
        'XAD': 'Adai',
        'XAG': 'Aghwan',
        'XAI': 'Kaimbé',
        'XAM': '/Xam',
        'XAP': 'Apalachee',
        'XAR': 'Karami',
        'XAS': 'Kama',
        'XBA': 'Kamba (Brazil)',
        'XBB': 'Lower Burdekin',
        'XBN': 'Kenaboi',
        'XBO': 'Bolgarian',
        'XBW': 'Kambiwá',
        'XBX': 'Kabixí',
        'XCB': 'Cumbric',
        'XCH': 'Chemakum',
        'XCM': 'Comecrudo',
        'XCN': 'Cotoname',
        'XCU': 'Curonian',
        'XCV': 'Chuvantsy',
        'XCW': 'Coahuilteco',
        'XCY': 'Cayuse',
        'XEG': '//Xegwi',
        'XGB': 'Gbin',
        'XGF': 'Gabrielino-Fernandeñ',
        'XGL': 'Galindan',
        'XGR': 'Garz',
        'XHC': 'Hunnic',
        'XIN': 'Xinc',
        'XIP': 'Xipináwa',
        'XIR': 'Xiriâna',
        'XKR': 'Xakriabá',
        'XLB': 'Loup B',
        'XLO': 'Loup A',
        'XMP': 'Kuku-Mu\'inh',
        'XMQ': 'Kuku-Mangk',
        'XMU': 'Kamu',
        'XNT': 'Narragansett',
        'XOC': 'O\'chi\'chi\'',
        'XOO': 'Xukurú',
        'XPC': 'Pecheneg',
        'XPI': 'Pictish',
        'XPJ': 'Mpalitjanh',
        'XPM': 'Pumpokol',
        'XPN': 'Kapinawá',
        'XPO': 'Pochutec',
        'XPP': 'Puyo-Paekche',
        'XPQ': 'Mohegan-Pequot',
        'XPS': 'Pisidian',
        'XPY': 'Puyo',
        'XRM': 'Armazic',
        'XRN': 'Arin',
        'XRT': 'Aranama-Tamique',
        'XSO': 'Solano',
        'XSS': 'Assa',
        'XSV': 'Sudovian',
        'XTZ': 'Tasmanian',
        'XUD': 'Umiida',
        'XUN': 'Unggarranggu',
        'XUP': 'Upper Umpqua',
        'XUT': 'Kuthant',
        'XWC': 'Woccon',
        'XWO': 'Written Oira',
        'XXB': 'Boro (Ghana)',
        'XXR': 'Koropó',
        'XXT': 'Tambora',
        'XYL': 'Yalakalore',
        'XZM': 'Zemgalian',
        'YBN': 'Yabaâna',
        'YEI': 'Yeni',
        'YGA': 'Malyangapa',
        'YIL': 'Yindjilandji',
        'YLR': 'Yalarnnga',
        'YME': 'Yame',
        'YMT': 'Mator-Taygi-Karagas',
        'YND': 'Yandruwandha',
        'YNN': 'Yana',
        'YNU': 'Yahuna',
        'YOB': 'Yoba',
        'YOL': 'Yola',
        'YSC': 'Yassic',
        'YSR': 'Sirenik Yupi',
        'YUB': 'Yugambal',
        'YUG': 'Yug',
        'YUK': 'Yuki',
        'YVT': 'Yavitero',
        'YWW': 'Yawarawarga',
        'YXG': 'Yagara',
        'YXY': 'Yabula Yabul',
        'ZIR': 'Ziriya',
        'ZKB': 'Koibal',
        'ZKG': 'Koguryo',
        'ZKH': 'Khorezmian',
        'ZKK': 'Karankawa',
        'ZKO': 'Kott',
        'ZKP': 'São Paulo Kaingáng',
        'ZKT': 'Kita',
        'ZKU': 'Kaurna',
        'ZKV': 'Krevinian',
        'ZKZ': 'Khazar',
        'ZMC': 'Margany',
        'ZME': 'Mangerr',
        'ZMH': 'Makolkol',
        'ZMK': 'Mandandanyi',
        'ZMU': 'Muruwari',
        'ZMV': 'Mbariman-Gudhinma',
        'ZNK': 'Manangkari',
        'ZRA': 'Kara (Korea)',
        'ZRP': 'Zarphatic'
        }

    type_set = {
        'ISOMLT': iso_major_language_types,
        'ISOOLT': iso_other_language_types
        }

    def get_type_data(self, name):
        if name in self.iso_major_language_types:
            namespace = '639-2'
            lang_name = self.iso_major_language_types[name]
        elif name in self.iso_other_language_types:
            namespace = '639-3'
            lang_name = self.iso_other_language_types[name]
        else:
            raise NotFound('Language Type: ' + name)

        return {
            'authority': 'ISO',
            'namespace': namespace,
            'identifier': name,
            'domain': 'DisplayText Languages',
            'display_name': lang_name + ' Language Type',
            'display_label': lang_name,
            'description': ('The display text language type for the ' +
                                                    lang_name + ' language.')
            }

class Script:

    iso_script_types = {
        'AFAK': 'Afak',
        'ARAB': 'Arabic',
        'ARMI': 'ImperialAramaic, Imperial Aramaic',
        'ARMN': 'Armenian',
        'AVST': 'Avestan',
        'BALI': 'Balinese',
        'BAMU': 'Bamum',
        'BASS': 'BassaVah, Bassa Vah',
        'BATK': 'Batak',
        'BENG': 'Bengali',
        'BLIS': 'Bissymbols',
        'BOPO': 'Bopomofo',
        'BRAH': 'Brahmi',
        'BUGI': 'Buginese',
        'BUHD': 'Buhid',
        'CAKM': 'Chakma',
        'CANS': 'UCAS, Unified Canadian Aboriginal Syllabics',
        'CARI': 'Carian',
        'CHAM': 'Cham',
        'CHER': 'Cherokee',
        'CIRT': 'Cirth',
        'COPT': 'Coptic',
        'CPRT': 'Cypriot',
        'CYRL': 'Cyrillic',
        'DEVA': 'Devanagari',
        'DSRT': 'Deseret',
        'DUPL': 'Duployan',
        'EGYD': 'EgyptianDemotic, Egyptian Demotic',
        'EGYH': 'EgyptianHieratic, Egyptian Hieratic',
        'EGYP': 'EgyptianHieroglyphs, Egyptian Hieroglyphs',
        'ELBA': 'Elbasan',
        'ETHI': 'Ethopic',
        'GEOK': 'Khutsuri',
        'GEOR': 'Georgian',
        'GLAG': 'Glagolotic',
        'GOTH': 'Gothic',
        'GRAN': 'Grantha',
        'GREK': 'Greek',
        'GUJR': 'Gujarati',
        'GURU': 'Gurmukhi',
        'HANG': 'Hangul',
        'HANI': 'Han',
        'HANS': 'HanSimple, Han Simplified',
        'HANT': 'HanTraditional, Han Traditional',
        'HEBR': 'Hebrew',
        'HIRA': 'Hiragana',
        'HLUW': 'AnatolianHieroglyphs, Anatolian, Luwian, Hittite Hieroglyphs',
        'HMNG': 'PahawhHmong, Pahawh Hmong',
        'HRKT': 'HiraganaKatakana, Japanese Hiragana and Katakana',
        'HUNG': 'OldHungarian, Old Hungarian',
        'INDS': 'Indus',
        'Ital': 'OldItalic, Old Italic',
        'JAVA': 'Javanese',
        'JPAN': 'Japanese, Japanese Han, Hiragana, and Katakana',
        'JURC': 'Jurchen',
        'KALI': 'KayahLi, Kayah Li',
        'KANA': 'Katakana',
        'KHAR': 'Kharoshthi',
        'KHMR': 'Khmer',
        'KHOJ': 'Khojki',
        'KNDA': 'Kannada',
        'KORE': 'Korean, Koran Hangul and Han',
        'KPEL': 'Kpelle',
        'KTHI': 'Kaithi',
        'LANA': 'TaiTham, Tai Tham',
        'LAOO': 'Lao',
        'LATF': 'LatinFraktur, Latin Fra',
        'LATG': 'LatinGaelic, Latin Gaelic',
        'LATN': 'Latin',
        'LEPC': 'Lepcha',
        'LIMB': 'Limbu',
        'LINA': 'LinearA, Linear A',
        'LINB': 'LinearB, Linear B',
        'LISU': 'Lisu',
        'LOMA': 'Loma',
        'LYCI': 'Lycian',
        'LYDI': 'Lydian',
        'MAND': 'Mandaic',
        'MANI': 'Manichaean',
        'MAYA': 'Mayan, Mayan Hieroglyphs',
        'MEND': 'Mende',
        'MERC': 'MeroiticCursive, Meroitic Cursive',
        'MERO': 'MeroiticHieroglyphs, Meroitic Hieroglyphs',
        'MLYM': 'Malayalam',
        'MONG': 'Mongolian',
        'MOON': 'Moon',
        'MROO': 'Mro',
        'MTEI': 'MeiteiMayek, Meitei Mayek',
        'MYMR': 'Myanmar',
        'NARB': 'OldNorthArabian, Old North Arabian',
        'NBAT': 'Nabataean',
        'NKGB': 'NakhiGeba, Nakhi Geba',
        'NKOO': 'N\’Ko, N\'Ko',
        'NSHU': 'Nüshu",  "NüshuO',
        'OGAM': 'Ogham',
        'OLCK': 'OlChiki, Ol Chiki',
        'ORKH': 'OldTurkic, Old Turkic',
        'ORYA': 'Oriya',
        'OSMA': 'Osmanya',
        'PALM': 'Palmyrene',
        'PERM': 'OldPermic, OldPermic',
        'PHAG': 'Phags-pa',
        'PHLI': 'InscriptionalPahlavi, Inscriptional Pahlavi',
        'PHLP': 'Psalter Pahlavi, Psalter Pahlavi',
        'PHLV': 'Book Pahlavi, Book Pahlavi',
        'PHNX': 'Phoenician',
        'PLRD': 'Miao',
        'PRTI': 'InscriptionalParthian, Inscriptional Parthian',
        'RJNG': 'Rejang',
        'RORO': 'Rongorongo',
        'RUNR': 'Runic',
        'SAMR': 'Samaritan',
        'SARA': 'Sarati',
        'SARB': 'OldSouthArabian, Old South Arabian',
        'SAUR': 'Saurashtra',
        'SGNW': 'SignWriting',
        'SHAW': 'Shavian',
        'SHRD': 'Sharada',
        'SIND': 'Khudawadi',
        'SINH': 'Sinhala',
        'SORA': 'SoraSompeng, Sora Sompeng',
        'SUND': 'Sundanese',
        'SYLO': 'SylotiNagri, Syloti Nagri',
        'SYRC': 'Syriac',
        'SYRE': 'SyriacEstrangelo, Syriac Estrangelo',
        'SYRJ': 'SyriacWestern, Syriac Western',
        'SYRN': 'SyriacEastern, Syriac Eastern',
        'TAGB': 'Tagbanwa',
        'TAKR': 'Takri',
        'TALE': 'TaiLe, Tai Le',
        'TALU': 'NewTaiLue, New Tai Lue',
        'TAML': 'Tamil',
        'TANG': 'Tangut',
        'TAVT': 'TaiViet, Tai Viet',
        'TELU': 'Telugu',
        'TENG': 'Tengwar',
        'TFNG': 'Tifinagh',
        'TGLG': 'Tagalog',
        'THAA': 'Thaana',
        'THAI': 'Thai',
        'TIBT': 'Tibetan',
        'TIRH': 'Tirhuta',
        'UGAR': 'Ugaritic',
        'VAII': 'Vai',
        'VISP': 'VisibleSpeech, Visible Speech',
        'WARA': 'WarangCiti, Warang Citi',
        'WOLE': 'Woleai',
        'XPEO': 'OldPersian, Old Persian',
        'XSUX': 'Cuneiform',
        'YIII': 'Yi',
        'ZMTH': 'Mathematical, Mathematical Notation',
        'ZSYM': 'Symbols',
        'ZYYY': 'Undetermined, Undetermined Script',
        'ZZZZ': 'Uncoded, Uncoded Script'
    }

    type_set = {
        'ISOST': iso_script_types
        }

    def get_type_data(self, name):
        return {
            'authority': 'ISO',
            'namespace': '15924',
            'identifier': name,
            'domain': 'ISO Script Types',
            'display_name': self.iso_script_types[name] + ' Script Type',
            'display_label': self.iso_script_types[name],
            'description': ('The display text script type for the ' +
                                    self.iso_script_types[name] + ' script.')
            }

class Format:

    format_types = {
        'ASCIIDOC': 'AsciiDoc',
        'CREOLE': 'Creole',
        'DOCBOOK': 'DocBook',
        'GROFF': 'Groff',
        'HTML': 'HTML',
        'LATEX': 'LaTeX',
        'MARKDOWN': 'Markdown',
        'MMD': 'MultiMarkdown',
        'NROFF': 'nroff',
        'PLAIN': 'plain',
        'REST': 'reStricturedText',
        'RUNOFF': 'RUNOFF',
        'SCRIBE': 'Scribe',
        'TEX': 'TeX',
        'TEXINFO': 'Texinfo',
        'TEXTILE': 'Textile',
        'TROFF': 'troff',
        'Z': 'ZFormat'
        }

    type_set = {
        'FT': format_types
        }

    def get_type_data(self, name):
        try:
            return {
                'authority': 'okapia.net',
                'namespace': 'TextFormats',
                'identifier': name,
                'domain': 'DisplayText Formats',
                'display_name': self.format_types[name] + ' Format Type',
                'display_label': self.format_types[name],
                'description': ('The display text format type for the ' +
                                        self.format_types[name] + ' format.')
                }
        except IndexError:
            raise NotFound('Format Type:' + name)

class Time:

    celestial_time_types = {
        # Ephemeris Time #
        'ET': 'Ephemeris',

        # Barycentric Coordinate Time #
        'TCB': 'Barycentric Coordinate',

        # Barycentric Dynamic Time #
        'TDB': 'Barycentric Dynamic',

        # Geocentric Coordinate Time #
        'TCG': 'Geocentric Coordinate',

        # Terrestrial Dynamic Time #
        'TDT': 'Terrestrial Dynamic'
    }

    earth_time_types = {
        # GPS Time #
        'GPS': 'GPS',

        # Metric Time #
        'METRIC': 'Metric',

        # International Atomic Time #
        'TAI': 'International Atomic',

        # Universal Time #
        'UT0': 'Universal (UT0)',

        # Universal Time #
        'UT1': 'Universal (UT1)',

        # Universal Time #
        'UT1R': 'Universal (UT1R)',

        # Universal Time #
        'UT2': 'Universal (UT2)',

        # Universal Time #
        'UT2R': 'Universal (UT2R)',

        # Coordinated Universal Time #
        'UTC': 'Coordinate Universal'
    }

    super_fun_time_types = {
    # Frakkin' Centon Time #
    'COLONIAL': 'Colonial, Battlestar Galactica',

    # New Earth Time #
    'NET': 'NewEarth, New Earth',

    # Swatch Internet Time #
    'SWATCH': 'Swatch, Swatch Internet'
    }

    type_set = {
        'CTT': celestial_time_types,
        'ETT': earth_time_types,
        'SFTT': super_fun_time_types
        }

    def get_type_data(self, name):
        if name in self.celestial_time_types:
            namespace = 'time'
            domain = 'Celestial Time Systems'
            time_name = self.celestial_time_types[name]
        elif name in self.earth_time_types:
            namespace = 'time'
            domain = 'Earth Time Systems'
            time_name = self.earth_time_types[name]
        elif name in self.superfun_time_types:
            namespace = 'time'
            domain = 'Alternative Time Systems'
            time_name = self.superfun_time_types[name]
        else:
            raise NotFound('Time Type: ' + name)

        return {
            'authority': 'okapia.net',
            'namespace': namespace,
            'identifier': name,
            'domain': domain,
            'display_name': time_name + ' Time Type',
            'display_label': time_name,
            'description': ('The time type for ' + time_name + ' time.')
            }

class Calendar:

    calendar_types = {
        # Akan Calendar #
        'AKAN': 'Akan',

        # Bahai Calendar #
        'BAHAI': 'Bahai, Bahá\'í',

        # Bengali Calendar #
        'BENGALI': 'Bengali',

        # Berber Calendar #
        'BERBER': 'Berber',

        # Buddhist Calendar #
        'BUDDHIST': 'Buddhist',

        # Chinese Calendar #
        'CHINESE': 'Chinese',

        # Coptic Calendar #
        'COPTIC': 'Coptic',

        # Discordian Calendar #
        'DISCORDIAN': 'Discordian',

        # Ethiopian Calendar #
        'ETHIOPIAN': 'Ethiopian',

        # Gregorian Calendar #
        'GREGORIAN': 'Gregorian',

        # Hebrew Calendar #
        'HEBREW': 'Hebrew',

        # Hellenic Calendar #
        'HELLENIC': 'Hellenic',

        # Igbo Calendar #
        'IGBO': 'Igbo',

        # Indian Calendar #
        'INDIAN': 'Indian, Indian National',

        # ISO8601 Calendar #
        'ISO_8601': 'ISO8601, ISO 8601',

        # ISOWeekdate Calendar #
        'ISO_WEEKDATE': 'ISOWeekdate, ISO Week Date',

        # Islamic Calendar #
        'ISLAMIC': 'Islamic',

        # Japanese Calendar #
        'JAPANESE': 'Japanese',

        # Javanese Calendar #
        'JAVANESE': 'Javanese',

        # Juche Calendar #
        'JUCHE': 'Juche, Juche Era',

        # Jualian Calendar #
        'JULIAN': 'Jualian',

        # Kurdish Calendar #
        'KURDISH': 'Kurdish',

        # Malayalam Calendar #
        'MALAYALAM': 'Malayalam',

        # Nanakshahi Calendar #
        'NANAKSHAHI': 'Nanakshahi',

        # Nepali Calendar #
        'NEPALI': 'Nepali',

        # NepalSambat Calendar #
        'NEPAL_SAMBAT': 'NepalSambat, Nepal Sambat',

        # RevisedJulian Calendar #
        'REVISED_JULIAN': 'RevisedJulian, Revised Julian',

        # Romanian Calendar #
        'ROMANIAN': 'Romanian',

        # Rumi Calendar #
        'RUMI': 'Rumi',

        # Runic Calendar #
        'RUNIC': 'Runic',

        # Tamil Calendar #
        'TAMIL': 'Tamil',

        # ThaiLunar Calendar #
        'THAI_LUNAR': 'ThaiLunar, Thai Lunar',

        # ThaiSolar Calendar #
        'THAI_SOLAR': 'ThaiSolar, Thai Solar',

        # Tibetan Calendar #
        'TIBETAN': 'Tibetan',

        # Zoroastrian Calendar #
        'ZOROASTRIAN': 'Zoroastrian',

        # Xhosa Calendar #
        'XHOSA': 'Xhosa',

        # Yoruba Calendar #
        'YORUBA': 'Yoruba'
    }

    ancient_calendar_types = {
        # Armenian Calendar #
        'ARMENIAN': 'Armenian',

        # Assyrian Calendar #
        'ASSYRIAN': 'Assyrian',

        # Attic Calendar #
        'ATTIC': 'Attic',

        # Aztec Calendar #
        'AZTEC': 'Aztec',

        # Babylonian Calendar #
        'BABYLONIAN': 'Babylonian',

        # Boeotian Calendar #
        'BOEOTIAN': 'Boeotian',

        # Bulgar Calendar #
        'BULGAR': 'Bulgar',

        # Byzantine Calendar #
        'BYZANTINE': 'Byzantine',

        # Coligny Calendar #
        'COLIGNY': 'Coligny',

        # Cretan Calendar #
        'CRETAN': 'Cretan',

        # Delphic Calendar #
        'DELPHIC': 'Delphic',

        # Egyptian Calendar #
        'EGYPTIAN': 'Egyptian',

        # Epirotic Calendar #
        'EPIROTIC': 'Epirotic',

        # Enoch Calendar #
        'ENOCH': 'Enoch',

        # Florentine Calendar #
        'FLORENTINE': 'Florentine',

        # FrenchRepublican Calendar #
        'FRENCH_REPUBLICAN': 'FrenchRepublican, French Republican',

        # Germanic Calendar #
        'GERMANIC': 'Germanic',

        # Gaelic Calendar #
        'GAELIC': 'Gaelic',

        # Laconian Calendar #
        'LACONIAN': 'Laconian',

        # Lithuanian Calendar #
        'LITHUANIAN': 'Lithuanian',

        # Macedonian Calendar #
        'MACEDONIAN': 'Macedonian, Ancient Macedonian',

        # Maya Calendar #
        'MAYA': 'Maya',

        # Minguo Calendar #
        'MINGUO': 'Minguo',

        # Pentecontad Calendar #
        'PENTECONTAD': 'Pentecontad',

        # RapaNui Calendar #
        'RAPA_NUI': 'RapaNui, Rapa Nui',

        # Rhodian Calendar #
        'RHODIAN': 'Rhodian',

        # Roman Calendar #
        'ROMAN': 'Roman',

        # Runic Calendar #
        'RUNIC': 'Runic',

        # Sicilian Calendar #
        'SICILIAN': 'Sicilian',

        # Soviet Calendar #
        'SOVIET': 'Soviet',

        # Swedish Calendar #
        'SWEDISH': 'Swedish'
        }

    alternate_calendar_types = {
            # 360-day Calendar #
        'C360': '360-day',

        # Astronomical Calendar #
        'ASTRONOMICAL': 'Astronomical',

        # Colonial Calendar #
        'COLONIAL': 'Colonial, Battlestar Galactica',

        # Common-Civil-Calendar-and-Time #
        'COMMON_CIVIL': 'CommonCivil, Common-Civil-Calendar-and-Time',

        # Darian Calendar #
        'DARIAN': 'Darian',

        # Discworld Calendar #
        'DISCWORLD': 'Discworld',

        # Hanke-Henry Permanent Calendar #
        'HANKE_HENRY': 'Hanke-Henry, Hanke-Henry Permanent',

        # holocene Calendar #
        'HOLOCENE': 'holocene',

        # InternationalFixed Calendar #
        'INTERNATIONAL_FIXED': 'InternationalFixed, International Fixed',

        # MiddleEarth Calendar #
        'MIDDLE_EARTH': 'MiddleEarth, Middle-earth',

        # Pax Calendar #
        'PAX': 'Pax',

        # Positivist Calendar #
        'POSITIVIST': 'Positivist',

        # Stardate Calendar #
        'STARDATE': 'Stardate',

        # Symmetry454 Calendar #
        'SYMMETRY454': 'Symmetry454',

        # Tranquility Calendar #
        'TRANQUILITY': 'Tranquility',

        # World Calendar #
        'WORLD': 'World',

        # WorldSeason Calendar #
        'WORLD_SEASON': 'WorldSeason, World Season'
    }

    type_set = {
        'CT': calendar_types,
        'ACT': ancient_calendar_types,
        'ALTCT': alternate_calendar_types
        }

    def get_type_data(self, name):
        if name in self.calendar_types:
            domain = 'Calendar Types'
            calendar_name = self.calendar_types[name]
        elif name in self.ancient_calendar_types:
            domain = 'Ancient Calendar Types'
            calendar_name = self.ancient_calendar_types[name]
        elif name in self.alternate_calendar_types:
            domain = 'Alternative Calendar Types'
            calendar_name = self.alternate_calendar_types[name]
        else:
            raise NotFound('Calendar Type: ' + name)

        return {
            'authority': 'okapia.net',
            'namespace': 'calendar',
            'identifier': name,
            'domain': domain,
            'display_name': calendar_name + ' Calendar Type',
            'display_label': calendar_name,
            'description': ('The time type for the ' + calendar_name + ' calendar.')
            }

class Coordinate:

    celestial_coordinate_types = {
        # Ecliptic Coordinate System #
        'ECLIPTIC': 'Ecliptic',

        # Equatorial Coordinate System #
        'EQUATORIAL': 'Equatorial',

        # Galactic Coordinate System #
        'GCS': 'Galactic',

        # Horizontal Altitude-Azimuth Coordinate System #
        'HORIZON': 'Horizon',

        # Supergalactic Coordinate System #
        'SUPERGALACTIC': 'Supergalactic'
    }

    geographic_coordinate_types = {
        # Earth Gravitational Model 1996 #
        'EGM96': 'EGM96, Geodetic Earth Gravitational Model 1996 Coordinate',

        # Geocentric #
        'GEOCENTRIC': 'Geocentric',

        # Geodetic Reference System 1980 #
        'GRS80': 'GRS80, Geodetic Reference System 80 Coordinate',

        # North American Datum of 1927 #
        'NAD27': 'NAD27, Geodetic North American Datum of 1927 Coordinate',

        # North American Datum of 1983 #
        'NAD83': 'NAD83, Geodetic North American Datum of 1983 Coordinate',

        # Maidenhead Locator System  #
        'MAIDENHEAD': 'Maidenhead, Maidenhead Locator',

        # Military Grid Reference System  #
        'MGRS': 'MGRS, Military Grid Reference',

        # World Geodetic System 1960  #
        'WGS60': 'WGS60, World Geodetic System of 1960 Coordinate',

        # World Geodetic System 1966  #
        'WGS66': 'WGS66, World Geodetic System of 1966 Coordinate',

        # World Geodetic System 1972  #
        'WGS72': 'WGS72, World Geodetic System of 1972 Coordinate',

        # World Geodetic System 1984 (used by GPS) #
        'WGS84': 'WGS84, World Geodetic System of 1984 Coordinate',

        # US Zip Codes  #
        'USPOSTAL': 'USPostal, United States Postal Code',

        # Universal Polar Stereographic System  #
        'UPS': 'UPS, Universal Polar Stereographic Coordinate',

        # Universal Transverse Mercator  System #
        'UTM': 'UTM, Universal Transverse Mercator Coordinate',

        # AT&T V and H System #
        'VH': 'V&H, AT&T V and H Coordinate',

        # VOR-DME System #
        'VOR': 'VOR-DME, VOR-DME Coordinate'
    }

    type_set = {
        'CCT': celestial_coordinate_types,
        'GCT': geographic_coordinate_types
        }

    def get_type_data(self, name):
        if name in self.celestial_coordinate_types:
            domain = 'Celestial Coordinate Systems'
            coordinate_name = self.celestial_coordinate_types[name]
        elif name in self.geographic_coordinate_types:
            domain = 'Geographic Coordinate Systems'
            coordinate_name = self.geographic_coordinate_types[name]
        else:
            raise NotFound('Coordinate Type' + name)

        return {
            'authority': 'okapia.net',
            'namespace': 'coordinate',
            'identifier': name,
            'domain': domain,
            'display_name': coordinate_name + ' Type',
            'display_label': coordinate_name,
            'description': ('The type for the ' + coordinate_name + ' System.')
            }

class Currency:

    iso_currency_types = {
        # UAE Dirham #
        'AED': 'UAE Dirham',

        # Afghani #
        'AFN': 'Afghani',

        # Lek #
        'ALL': 'Lek',

        # Armenian Dram #
        'AMD': 'Armenian Dram',

        # Netherlands Antillean Guilder #
        'ANG': 'Netherlands Antillean Guilder',

        # Kwanza #
        'AOA': 'Kwanza',

        # Argentine Peso #
        'ARS': 'Argentine Peso',

        # Australian Dollar #
        'AUD': 'Australian Dollar',

        # Aruban Florin #
        'AWG': 'Aruban Florin',

        # Azerbaijanian Manat #
        'AZN': 'Azerbaijanian Manat',

        # Convertible Mark #
        'BAM': 'Convertible Mark',

        # Barbados Dollar #
        'BBD': 'Barbados Dollar',

        # Taka #
        'BDT': 'Taka',

        # Bulgarian Lev #
        'BGN': 'Bulgarian Lev',

        # Bahraini Dinar #
        'BHD': 'Bahraini Dinar',

        # Burundi Franc #
        'BIF': 'Burundi Franc',

        # Bermudian Dollar #
        'BMD': 'Bermudian Dollar',

        # Brunei Dollar #
        'BND': 'Brunei Dollar',

        # Boliviano #
        'BOB': 'Boliviano',

        # Mvdol #
        'BOV': 'Mvdol',

        # Brazilian Real #
        'BRL': 'Brazilian Real',

        # Bahamian Dollar #
        'BSD': 'Bahamian Dollar',

        # Ngultrum #
        'BTN': 'Ngultrum',

        # Pula #
        'BWP': 'Pula',

        # Belarussian Ruble #
        'BYR': 'Belarussian Ruble',

        # Belize Dollar #
        'BZD': 'Belize Dollar',

        # Canadian Dollar #
        'CAD': 'Canadian Dollar',

        # Congolese Franc #
        'CDF': 'Congolese Franc',

        # WIR Euro #
        'CHE': 'WIR Euro',

        # Swiss Franc #
        'CHF': 'Swiss Franc',

        # WIR Franc #
        'CHW': 'WIR Franc',

        # Unidades de fomento #
        'CLF': 'Unidades de fomento',

        # Chilean Peso #
        'CLP': 'Chilean Peso',

        # Yuan Renminbi #
        'CNY': 'Yuan Renminbi',

        # Colombian Peso #
        'COP': 'Colombian Peso',

        # Unidad de Valor Real #
        'COU': 'Unidad de Valor Real',

        # Costa Rican Colon #
        'CRC': 'Costa Rican Colon',

        # Peso Convertible #
        'CUC': 'Peso Convertible',

        # Cuban Peso #
        'CUP': 'Cuban Peso',

        # Cape Verde Escudo #
        'CVE': 'Cape Verde Escudo',

        # Czech Koruna #
        'CZK': 'Czech Koruna',

        # Djibouti Franc #
        'DJF': 'Djibouti Franc',

        # Danish Krone #
        'DKK': 'Danish Krone',

        # Dominican Peso #
        'DOP': 'Dominican Peso',

        # Algerian Dinar #
        'DZD': 'Algerian Dinar',

        # Egyptian Pound #
        'EGP': 'Egyptian Pound',

        # Nakfa #
        'ERN': 'Nakfa',

        # Ethiopian Birr #
        'ETB': 'Ethiopian Birr',

        # Euro #
        'EUR': 'Euro',

        # Fiji Dollar #
        'FJD': 'Fiji Dollar',

        # Falkland Islands Pound #
        'FKP': 'Falkland Islands Pound',

        # Pound Sterling #
        'GBP': 'Pound Sterling',

        # Lari #
        'GEL': 'Lari',

        # Ghana Cedi #
        'GHS': 'Ghana Cedi',

        # Gibraltar Pound #
        'GIP': 'Gibraltar Pound',

        # Dalasi #
        'GMD': 'Dalasi',

        # Guinea Franc #
        'GNF': 'Guinea Franc',

        # Quetzal #
        'GTQ': 'Quetzal',

        # Guyana Dollar #
        'GYD': 'Guyana Dollar',

        # Hong Kong Dollar #
        'HKD': 'Hong Kong Dollar',

        # Lempira #
        'HNL': 'Lempira',

        # Croatian Kuna #
        'HRK': 'Croatian Kuna',

        # Gourde #
        'HTG': 'Gourde',

        # Forint #
        'HUF': 'Forint',

        # Rupiah #
        'IDR': 'Rupiah',

        # New Israeli Sheqel #
        'ILS': 'New Israeli Sheqel',

        # Indian Rupee #
        'INR': 'Indian Rupee',

        # Iraqi Dinar #
        'IQD': 'Iraqi Dinar',

        # Iranian Rial #
        'IRR': 'Iranian Rial',

        # Iceland Krona #
        'ISK': 'Iceland Krona',

        # Jamaican Dollar #
        'JMD': 'Jamaican Dollar',

        # Jordanian Dinar #
        'JOD': 'Jordanian Dinar',

        # Yen #
        'JPY': 'Yen',

        # Kenyan Shilling #
        'KES': 'Kenyan Shilling',

        # Som #
        'KGS': 'Som',

        # Riel #
        'KHR': 'Riel',

        # Comoro Franc #
        'KMF': 'Comoro Franc',

        # North Korean Won #
        'KPW': 'North Korean Won',

        # Won #
        'KRW': 'Won',

        # Kuwaiti Dinar #
        'KWD': 'Kuwaiti Dinar',

        # Cayman Islands Dollar #
        'KYD': 'Cayman Islands Dollar',

        # Tenge #
        'KZT': 'Tenge',

        # Kip #
        'LAK': 'Kip',

        # Lebanese Pound #
        'LBP': 'Lebanese Pound',

        # Sri Lanka Rupee #
        'LKR': 'Sri Lanka Rupee',

        # Liberian Dollar #
        'LRD': 'Liberian Dollar',

        # Loti #
        'LSL': 'Loti',

        # Lithuanian Litas #
        'LTL': 'Lithuanian Litas',

        # Latvian Lats #
        'LVL': 'Latvian Lats',

        # Libyan Dinar #
        'LYD': 'Libyan Dinar',

        # Moroccan Dirham #
        'MAD': 'Moroccan Dirham',

        # Moldovan Leu #
        'MDL': 'Moldovan Leu',

        # Malagasy Ariary #
        'MGA': 'Malagasy Ariary',

        # Denar #
        'MKD': 'Denar',

        # Kyat #
        'MMK': 'Kyat',

        # Tugrik #
        'MNT': 'Tugrik',

        # Pataca #
        'MOP': 'Pataca',

        # Ouguiya #
        'MRO': 'Ouguiya',

        # Mauritius Rupee #
        'MUR': 'Mauritius Rupee',

        # Rufiyaa #
        'MVR': 'Rufiyaa',

        # Kwacha #
        'MWK': 'Kwacha',

        # Malaysian Ringgit #
        'MYR': 'Malaysian Ringgit',

        # Mozambique Metical #
        'MZN': 'Mozambique Metical',

        # Namibia Dollar #
        'NAD': 'Namibia Dollar',

        # Naira #
        'NGN': 'Naira',

        # Cordoba Oro #
        'NIO': 'Cordoba Oro',

        # Norwegian Krone #
        'NOK': 'Norwegian Krone',

        # Nepalese Rupee #
        'NPR': 'Nepalese Rupee',

        # New Zealand Dollar #
        'NZD': 'New Zealand Dollar',

        # Rial Omani #
        'OMR': 'Rial Omani',

        # Balboa #
        'PAB': 'Balboa',

        # Nuevo Sol #
        'PEN': 'Nuevo Sol',

        # Kina #
        'PGK': 'Kina',

        # Philippine Peso #
        'PHP': 'Philippine Peso',

        # Pakistan Rupee #
        'PKR': 'Pakistan Rupee',

        # Guarani #
        'PYG': 'Guarani',

        # Qatari Rial #
        'QAR': 'Qatari Rial',

        # New Romanian Leu #
        'RON': 'New Romanian Leu',

        # Serbian Dinar #
        'RSD': 'Serbian Dinar',

        # Russian Ruble #
        'RUB': 'Russian Ruble',

        # Rwanda Franc #
        'RWF': 'Rwanda Franc',

        # Saudi Riyal #
        'SAR': 'Saudi Riyal',

        # Seychelles Rupee #
        'SCR': 'Seychelles Rupee',

        # Sudanese Pound #
        'SDG': 'Sudanese Pound',

        # Swedish Krona #
        'SEK': 'Swedish Krona',

        # Singapore Dollar #
        'SGD': 'Singapore Dollar',

        # Saint Helena Pound #
        'SHP': 'Saint Helena Pound',

        # Leone #
        'SLL': 'Leone',

        # Somali Shilling #
        'SOS': 'Somali Shilling',

        # Surinam Dollar #
        'SRD': 'Surinam Dollar',

        # South Sudanese Pound #
        'SSP': 'South Sudanese Pound',

        # Dobra #
        'STD': 'Dobra',

        # El Salvador Colon #
        'SVC': 'El Salvador Colon',

        # Syrian Pound #
        'SYP': 'Syrian Pound',

        # Lilangeni #
        'SZL': 'Lilangeni',

        # Baht #
        'THB': 'Baht',

        # Somoni #
        'TJS': 'Somoni',

        # Turkmenistan New Manat #
        'TMT': 'Turkmenistan New Manat',

        # Tunisian Dinar #
        'TND': 'Tunisian Dinar',

        # Pa’anga #
        'TOP': 'Pa’anga',

        # Turkish Lira #
        'TRY': 'Turkish Lira',

        # Trinidad and Tobago Dollar #
        'TTD': 'Trinidad and Tobago Dollar',

        # New Taiwan Dollar #
        'TWD': 'New Taiwan Dollar',

        # Tanzanian Shilling #
        'TZS': 'Tanzanian Shilling',

        # Hryvnia #
        'UAH': 'Hryvnia',

        # Uganda Shilling #
        'UGX': 'Uganda Shilling',

        # US Dollar #
        'USD': 'US Dollar',

        # US Dollar (Next day) #
        'USN': 'US Dollar (Next day)',

        # US Dollar (Same day) #
        'USS': 'US Dollar (Same day)',

        # Uruguay Peso en Unidades Indexadas (URUIURUI) #
        'UYI': 'Uruguay Peso en Unidades Indexadas (URUIURUI)',

        # Peso Uruguayo #
        'UYU': 'Peso Uruguayo',

        # Uzbekistan Sum #
        'UZS': 'Uzbekistan Sum',

        # Bolivar Fuerte #
        'VEF': 'Bolivar Fuerte',

        # Dong #
        'VND': 'Dong',

        # Vatu #
        'VUV': 'Vatu',

        # Tala #
        'WST': 'Tala',

        # CFA Franc BEAC #
        'XAF': 'CFA Franc BEAC',

        # East Caribbean Dollar #
        'XCD': 'East Caribbean Dollar',

        # SDR (Special Drawing Right) #
        'XDR': 'SDR (Special Drawing Right)',

        # UIC-Franc #
        'XFU': 'UIC-Franc',

        # CFA Franc BCEAO #
        'XOF': 'CFA Franc BCEAO',

        # CFP Franc #
        'XPF': 'CFP Franc',

        # Yemeni Rial #
        'YER': 'Yemeni Rial',

        # Rand #
        'ZAR': 'Rand',

        # Zambian Kwacha #
        'ZMK': 'Zambian Kwacha',

        # Zimbabwe Dollar #
        'ZWL': 'Zimbabwe Dollar'
        }

    iso_currency_element_types = {
        # Platinum #
        'XPT': 'Platinum',

        # Testing #
        'XTS': 'Testing',

        # Palladium #
        'XPD': 'Palladium',

         # Silver #
        'XAG': 'Silver',

        # Gold #
        'XAU': 'Gold',
    }

    type_set = {
        'ISOCT': iso_currency_types,
        'ISOCET': iso_currency_element_types
        }

    def get_type_data(self, name):

        if name in self.iso_currency_types:
            article = 'the '
            type_name = self.iso_currency_types[name]
        elif name in self.iso_currency_element_types:
            article = ''
            type_name = self.iso_currency_element_types[name]
        else:
            raise NotFound('Currency Type: ' + name)

        return {
            'authority': 'ISO',
            'namespace': '4217',
            'identifier': name,
            'domain': 'ISO Currency Types',
            'display_name': type_name + ' Currency Type',
            'display_label': type_name,
            'description': ('The ISO currency type for ' +  article +
                                    type_name + '.')
            }

class Heading:

    heading_types = {
    'DEGREE': 'Degree'
    }

    type_set = {
        'HT': heading_types
        }

    def get_type_data(self, name):

        if name not in self.heading_types:
            raise NotFound('Heading Type: ' + name)

        return {
            'authority': 'okapia.net',
            'namespace': 'heading',
            'identifier': name,
            'domain': 'Headings',
            'display_name': self.heading_types[name] + ' Heading Type',
            'display_label': self.heading_types[name],
            'description': ('The heading type for the ' +
                                    self.heading_types[name] + ' heading.')
            }

class String:

    string_match_types = {
        'EXACT': 'Exact',
        'IGNORECASE': 'Ignore Case',
        'WORD': 'Word',
        'WORDIGNORECASE': 'Word Ignore Case',
        'WILDCARD': 'Wildcard',
        'REGEX': 'Regular Expression',
        'SOUND': 'Sound',
        'SOUNDEX': 'Soundex',
        'METAPHONE': 'Metaphone',
        'DMETAPHONE': 'Dmetaphone',
        'LEVENSHTEIN': 'Levenshtein'
    }

    type_set = {
        'SMT': string_match_types
        }

    def get_type_data(self, name):

        if name not in self.string_match_types:
            raise NotFound('String Type: ' + name)

        return {
            'authority': 'okapia.net',
            'namespace': 'string match types',
            'identifier': name,
            'domain': 'String Match Types',
            'display_name': self.string_match_types[name] + ' String Match Type',
            'display_label': self.string_match_types[name],
            'description': ('The string match type for the ' +
                                    self.string_match_types[name])
            }

class UnitSystem:

    jeffs_unit_system_types = {
        'METRIC': 'Metric',
        'ENGLISH': 'English'
        }

    type_set = {
        'JUST': jeffs_unit_system_types
        }

    def get_type_data(self, name):

        if name not in self.jeffs_unit_system_types:
            raise NotFound('UnitSystem Type: ' + name)

        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'unit system',
            'identifier': name,
            'domain': 'Unit System Types',
            'display_name': self.jeffs_unit_system_types[name] + ' Unit System Type',
            'display_label': self.jeffs_unit_system_types[name],
            'description': ('The unit system type for the ' +
                                    self.jeffs_unit_system_types[name] + ' System')
            }

class CalendarFormat:

    jeffs_calendar_format_types = {
        'MMDDYYYY': 'MM/DD/YYYY'
        }

    type_set = {
        'JCALFT': jeffs_calendar_format_types
        }

    def get_type_data(self, name):

        if name not in self.jeffs_calendar_format_types:
            raise NotFound('CalendarFormat Type: ' + name)

        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'calendar format',
            'identifier': name,
            'domain': 'Calendar Format Types',
            'display_name': self.jeffs_calendar_format_types[name] + ' Calendar Format Type',
            'display_label': self.jeffs_calendar_format_types[name],
            'description': ('The calendar format type for ' +
                                    self.jeffs_calendar_format_types[name])
            }

class TimeFormat:

    jeffs_time_format_types = {
        'HHMMSS': '24 Hour Clock (hh:mm:ss)',
        'HHMMSSAMPM': '12 Hour Clock (hh:mm:ss am/pm)'
        }

    type_set = {
        'JTIMEFT': jeffs_time_format_types
        }

    def get_type_data(self, name):

        if name not in self.jeffs_time_format_types:
            raise NotFound('TimeFormat Type: ' + name)

        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'time format',
            'identifier': name,
            'domain': 'Time Format Types',
            'display_name': self.jeffs_time_format_types[name] + ' Time Format Type',
            'display_label': self.jeffs_time_format_types[name],
            'description': ('The time format type for ' +
                                    self.jeffs_time_format_types[name])
            }


class CurrencyFormat:

    jeffs_currency_format_types = {
        'US': 'US ($1,234.56)'
        }

    type_set = {
        'JCURFT': jeffs_currency_format_types
        }

    def get_type_data(self, name):

        if name not in self.jeffs_currency_format_types:
            raise NotFound('CurrencyFormat Type: ' + name)

        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'currency format',
            'identifier': name,
            'domain': 'Currency Format Types',
            'display_name': self.jeffs_currency_format_types[name] + ' Currency Format Type',
            'display_label': self.jeffs_currency_format_types[name],
            'description': ('The format type for the ' +
                                    self.jeffs_currency_format_types[name] + ' currency')
            }

class CoordinateFormat:

    jeffs_coordinate_format_types = {
        'DMS': 'Degree/Minute/Second'
        }

    type_set = {
        'JCRDFT': jeffs_coordinate_format_types
        }

    def get_type_data(self, name):

        if name not in self.jeffs_coordinate_format_types:
            raise NotFound('CoordinateFormat Type: ' + name)

        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'coordinate format',
            'identifier': name,
            'domain': 'Currency Format Types',
            'display_name': self.jeffs_coordinate_format_types[name] + ' Coordinate Format Type',
            'display_label': self.jeffs_coordinate_format_types[name],
            'description': ('The type for the ' +
                                    self.jeffs_coordinate_format_types[name] +
                                    ' Geographic coordinate format.')
            }

class NumericFormat:

    # THIS NEEDS WORK!!!  in gnu format the #.# specifies places
    # Can this NumericFormat class take place argument?
    gnu_basic_numeric_format_types = {
        'F8.2': 'F8.2 (3141.59, -3141.59)',
        'COMMA9.2': 'COMMA9.2 (3,141.59, -3,141.59)',
        'DOT9.2': 'DOT9.2 (3.141,59, -3.141,59)',
        'DOLLAR10.2': 'DOLLAR10.2 ($3,141.59, -$3,141.59)',
        'PCT9.2': 'PCT9.2 (3141.59%, -3141.59%)',
        'E8.1': 'E8.1, (3.1E+003, -3.1E+003)'
        }

    type_set = {
        'GNUBNFT': gnu_basic_numeric_format_types
        }

    def get_type_data(self, name):
        try:
            return {
                'authority': 'gnu.org',
                'namespace': 'Basic Numeric Formats',
                'identifier': name,
                'domain': 'Numeric Format Types',
                'display_name': self.jeffs_numeric_format_types[name] + ' Numeric Format Type',
                'display_label': self.jeffs_numeric_format_types[name],
                'description': ('The type for the ' +
                                        self.jeffs_numeric_format_types[name] +
                                        ' numeric format.')
                }
        except IndexError:
            raise NotFound('NumericFormat Type: ' + name)
