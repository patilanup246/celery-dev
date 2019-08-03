SNS_NAME_INS = 'ins'
NO_FACE = -1
NO_IMG = -2

# Pipes
PIPE_CONST = {
    'True': True,
    'False': False,
    '-1': -1,
    'dg': 'dg'
}

# Demographics
DG_FACE_MIN_SIZE = 13  # if field face octet_length >= 13 bytes than there is a face
DG_FOLLOWER_SET_LIMIT = 150000
DG_PRIORITIZING_THRESHOLD = 1500
DG_ANALYZING_GAP_PERCENTAGE = 0.05
DG_LARGE_SAMPLE_FOLLOWER_THRESHOLD = 100000
DG_LARGE_SAMPLE_PERCENTAGE = 0.1
DB_TASK_COUNTDOWN = 120

# Updates
PROFILE_UPDATE_GAP = 3600 * 24 * 7    # 7 days of second
SP_PROFILE_UPDATE_GAP = 3600 * 24     # daily update
# PROFILE_UPDATE_GAP = 3600


# time series
POST_METRICS = [
    'likes_count',
    'replies_count',
    'reach',
    'engagement',
    'engagement_rate',
    'published_at',
]

POST_T0_METRICS = [     # based on first achieved reach
    'reach_t0',
    'engagement_rate_t0',
]

# Sponsored post update
HOURLY_UPDATE_WINDOW = 72 * 3600   # 72 hours in second


# Post Enrichment
POST_ENRICHMENT_TYPE = {
    'purchase_intent': 'purchase_intent',
    'fake_engagement': 'fake_engagement',
}


VERTICALS = {
    "1": "Accessories", "2": "Acting", "3": "Adult Entertainment", "4": "Adventure Travel", "5": "Airlines",
    "6": "Alcohol", "7": "Alternative medicine", "8": "Alternative/Indie rock", "9": "Americana",
    "10": "Amusement/Theme Parks", "11": "Animals (not pet)", "12": "Anime", "13": "Apartments and Home Rentals",
    "14": "Apparel", "15": "Appliances", "16": "Applied Art", "17": "Apps", "18": "Architecture", "19": "Art",
    "20": "Auction House", "21": "Audiobooks", "22": "Auto Racing", "23": "Avant-garde", "24": "Bakery", "25": "Bars",
    "26": "Baseball", "27": "Basketball", "28": "Beauty", "29": "Bed & Breakfasts", "30": "Beers", "31": "Beverage",
    "32": "Bicycles", "33": "Biology", "34": "Bird", "35": "Blues", "36": "BMX", "37": "Body Piercing",
    "38": "Bodybuilding", "39": "Books", "40": "Bookstores", "41": "Botany", "42": "Bridal Dresses",
    "43": "British show", "44": "Busline", "46": "Cakes", "47": "Cameras/Camcorders", "48": "Candy and Sweets",
    "49": "Cannabis", "50": "Careers advice", "51": "Cars", "53": "Causes", "54": "Cello", "55": "Charity",
    "56": "Chemistry", "57": "Children & Family", "58": "Children Product", "59": "Children's music", "60": "Chocolate",
    "61": "Christian & gospel", "62": "Cinema/movie theatre", "63": "Cinematography", "64": "Circuits",
    "65": "Clarinet", "66": "Classical music", "67": "Climatology", "68": "Club/Dance", "69": "Coffee",
    "70": "Coffeehouse", "71": "College/University", "72": "Consumer Electronics", "73": "Cooking",
    "74": "Cooking Sauces", "75": "Country music", "76": "Crime show", "77": "Cruise ship", "78": "Dance",
    "79": "Dance music", "80": "Dance-Pop", "81": "Dating/romance", "82": "Delivery Services", "83": "Dental Care",
    "84": "Dermatology", "85": "Design", "86": "Desserts/Baking", "87": "Dieting", "89": "Documentary", "91": "Dramas",
    "92": "Drawing & sketching", "93": "Drum", "94": "E-commerce", "95": "Easy listening", "96": "Education",
    "97": "Elderly care", "98": "Electric & hybrid cars", "99": "Electronic music", "100": "Elementary school",
    "101": "Energy drinks", "102": "Entertainment", "103": "Entrepreneurship", "104": "Event", "105": "Exercise",
    "106": "Eye Health", "107": "Eyewear", "108": "Family life", "109": "Fashion", "110": "Fatherhood",
    "111": "Festival", "112": "Fiction books", "113": "Finance", "114": "Fine dining", "115": "Fitness",
    "116": "Fitness Equipment", "117": "Flutes", "118": "Folk music", "119": "Food", "120": "Footwear", "121": "Fruit",
    "122": "Furniture", "123": "Gallery", "124": "Gaming", "125": "Gardening", "126": "Gay life", "127": "Geography",
    "128": "Geology", "129": "Gift Cards", "130": "Gifts", "131": "Gluten-Free Food", "132": "Golf",
    "133": "Government & Politics", "134": "Grocery store", "135": "Guitar & bass", "136": "Gym", "137": "Gymnastics",
    "138": "Hair Care", "139": "Handbags/Wallets", "140": "Hard rock", "141": "Hardware", "142": "Hats",
    "143": "Healthcare", "144": "Healthy Food", "145": "High school", "146": "Hiking", "147": "Home & Garden",
    "148": "Home Entertainment", "149": "Home improvement", "150": "Home stay", "151": "Horror",
    "152": "Hospitality service", "153": "Hotels", "154": "House music", "155": "Household Products",
    "156": "Independent movies", "157": "Insurance", "158": "Interior decorating", "159": "International movies",
    "160": "J-Pop", "161": "Jazz", "162": "Jewelry", "163": "Job search", "164": "Jogging & running", "165": "Journal",
    "166": "Juices", "167": "K-Pop", "168": "Kids Clothing", "169": "Kindergarten", "170": "Korean show",
    "171": "Language learning", "172": "Latin music", "173": "LGBTQ", "174": "Lifestyle", "175": "Live music",
    "176": "Luxury Beauty", "177": "Magazine", "178": "Makeup", "179": "Marketing", "180": "Marriage",
    "181": "Martial Arts", "182": "Maternity Clothing", "183": "Maths & Stats", "184": "Medicine",
    "185": "Men's grooming", "186": "Men's health", "187": "Mental illness", "188": "Milkshakes",
    "189": "Mixed martial arts", "190": "Mixed-media", "191": "Motherhood", "192": "Motorcycles", "193": "Motorsport",
    "194": "Movies", "195": "Museum", "196": "Music", "197": "Music composing", "198": "Musical",
    "199": "Musical instrument", "200": "Nail care", "201": "National park", "202": "Natural beauty products",
    "203": "New age music", "204": "New Media", "205": "News", "206": "Newspaper", "207": "Nightlife/partying",
    "208": "Non-fiction books", "209": "Non-Profit Organization", "210": "Nutrition/Weight loss",
    "211": "Online courses", "212": "Opera", "213": "Organic Food", "214": "Other pet", "215": "Outdoor activity",
    "216": "Outdoor life", "217": "Paintings", "218": "Parenthood", "219": "Parenting", "220": "Parks",
    "221": "Parks and Recreation", "222": "Party Decorations", "223": "Pasta", "224": "Pediatrics",
    "225": "Performance Art", "226": "Perfume/Cologne", "227": "Personal care", "228": "Pets", "229": "Philosophy",
    "230": "Photography", "231": "Physical therapy", "232": "Physics", "233": "Piano & keyboard", "234": "Pilates",
    "235": "Plastic surgery", "236": "Plus-size", "238": "Psychological therapy", "239": "Psychology",
    "240": "Public transportation", "241": "Publication", "242": "Punk", "243": "R&B", "244": "Radio",
    "245": "Rap & hip hop", "246": "Real estate", "247": "Reality TV", "248": "Recycling", "249": "Reggae",
    "250": "Relationships", "251": "Resorts", "252": "Restaurants", "253": "Retail", "254": "Rock & heavy metal",
    "255": "Rock & roll", "256": "Romance", "257": "Salons", "258": "Saxophone", "259": "Scholarships/Financial aid",
    "260": "Sci-fi & Fantasy", "261": "Science", "262": "Science & nature show", "263": "Sculpture", "264": "Seafood",
    "265": "Senior health", "266": "Shopping", "267": "Shopping mall", "268": "Skateboarding", "269": "Skin care",
    "270": "Smartphones", "271": "Snacks", "272": "Soccer", "273": "Social Justice", "274": "Social networks",
    "275": "Social sciences", "276": "Soft drinks", "277": "Software", "278": "Soul music", "279": "Sound engineering",
    "280": "Space/Astronomy", "281": "Spirits", "282": "Sport nutrition", "283": "Sport show", "284": "Sports",
    "285": "Sportswear", "286": "Standup comedy", "287": "Startups", "288": "Stock market", "289": "Suitcase",
    "290": "Sunglasses", "291": "Supermarket", "292": "Surfing", "293": "Swimming", "294": "Swimwear", "295": "Tablets",
    "296": "Talk show", "297": "Tattoos", "298": "Tea", "300": "Technology", "301": "Teen pop", "302": "Teen show",
    "303": "Theatre", "304": "Thrillers", "305": "Tourism board", "306": "Toys", "307": "Trains", "309": "Transport",
    "310": "Travel", "311": "Travel agency & booking services", "312": "Traveling With Kids", "313": "Trombone",
    "314": "Trucks", "315": "Trumpet", "316": "TV show", "317": "Underwear & Lingerie", "318": "Vegan",
    "319": "Videography", "320": "Violin", "322": "Volleyball", "324": "Watches", "325": "Wearable Tech",
    "326": "Weddings", "327": "Western movies", "328": "Wines", "329": "Women's health", "330": "World music",
    "331": "Writing", "332": "Yoga", "333": "Automotive parts", "334": "Backpack", "335": "Badminton",
    "336": "Beauty Tools", "337": "Blogging", "338": "Boats", "339": "Cigarette", "340": "Cosplay",
    "341": "Cryotherapy", "342": "Detox", "343": "DIY", "344": "Firearm", "345": "Flower", "346": "Football",
    "347": "Helmets", "348": "Horse racing", "349": "Ice hockey", "350": "Modeling", "351": "Outdoor gear",
    "352": "Pharmacy", "353": "Skiing", "354": "Snowboarding", "355": "Spas", "356": "Stadium", "357": "Stationery",
    "358": "Television network",
    "359": "Naturalista",
    "360": "Animation",
    "361": "ASMR",
    "362": "Bullet Journal",
    "363": "Calligraphy",
    "364": "Comic Book",
    "365": "Concept Art",
    "366": "Digital Art",
    "367": "Illustration",
    "368": "Manga",
    "369": "Traditional Art"
}

VERTICAL_IDS = {str.lower(v): int(k) for k, v in VERTICALS.items()}

FEED_QUALITIES = {0: "Bad",5: "Okay",10: "Good"}
FEED_QUALITY_IDS = {str.lower(v): int(k) for k, v in FEED_QUALITIES.items()}