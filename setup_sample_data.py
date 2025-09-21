#!/usr/bin/env python3
"""
Setup script to add sample documents for testing the Deep Researcher Agent
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_sample_data():
    """Add sample documents to the system for testing."""

    print("🚀 Setting up Deep Researcher Agent with sample data...")
    print("=" * 60)

    try:
        from src.main import DeepResearcherAgent

        # Initialize agent
        agent = DeepResearcherAgent()
        print("✅ Agent initialized successfully")

        # Sample documents
        documents = [
            {
                "title": "Artificial Intelligence Overview",
                "content": """
Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines.
It has become an essential part of the technology industry.

Key areas of AI include:
• Machine Learning: Algorithms that improve through experience and data
• Natural Language Processing: Understanding and generating human language
• Computer Vision: Interpreting and understanding visual information
• Robotics: AI systems that can interact with the physical world
• Expert Systems: AI systems that mimic human decision-making

AI has applications in:
• Healthcare: Medical diagnosis, drug discovery, personalized treatment
• Finance: Fraud detection, algorithmic trading, risk assessment
• Transportation: Autonomous vehicles, traffic optimization
• Education: Personalized learning, intelligent tutoring systems
• Entertainment: Content recommendation, game AI, creative tools

The field continues to evolve rapidly with new breakthroughs occurring regularly.
"""
            },
            {
                "title": "Machine Learning Fundamentals",
                "content": """
Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

Types of Machine Learning:
1. Supervised Learning: Learning from labeled training data
   - Classification: Predicting categorical labels
   - Regression: Predicting continuous values

2. Unsupervised Learning: Finding patterns in unlabeled data
   - Clustering: Grouping similar data points
   - Dimensionality Reduction: Simplifying complex data

3. Reinforcement Learning: Learning through trial and error
   - Agent learns by interacting with environment
   - Receives rewards or penalties for actions

Popular algorithms:
• Linear Regression
• Decision Trees
• Neural Networks
• Support Vector Machines
• Random Forests
• Gradient Boosting

Applications include image recognition, natural language processing, recommendation systems, and predictive analytics.
"""
            },
            {
                "title": "Data Science and Analytics",
                "content": """
Data Science combines statistics, programming, and domain expertise to extract insights from data.

The data science process:
1. Problem Definition: Understanding the business question
2. Data Collection: Gathering relevant data from various sources
3. Data Cleaning: Handling missing values, outliers, and inconsistencies
4. Exploratory Data Analysis: Understanding data patterns and relationships
5. Feature Engineering: Creating meaningful features for modeling
6. Model Building: Selecting and training appropriate algorithms
7. Model Evaluation: Assessing model performance and accuracy
8. Deployment: Implementing the model in production systems

Tools and technologies:
• Programming: Python, R, SQL
• Libraries: Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch
• Visualization: Matplotlib, Seaborn, Tableau, Power BI
• Big Data: Hadoop, Spark, Kafka
• Cloud Platforms: AWS, Google Cloud, Azure

Data scientists help organizations make data-driven decisions, identify trends, and solve complex problems.
"""
            },
            {
                "title": "Web Development Technologies",
                "content": """
Web development involves creating websites and web applications using various technologies and programming languages.

Frontend Technologies:
• HTML: Structure and content of web pages
• CSS: Styling and visual presentation
• JavaScript: Interactive functionality and behavior
• React: Component-based UI library
• Vue.js: Progressive framework for building user interfaces
• Angular: Platform for building mobile and desktop web applications

Backend Technologies:
• Node.js: JavaScript runtime for server-side development
• Python: Django, Flask for web frameworks
• PHP: Popular server-side scripting language
• Ruby: Ruby on Rails framework
• Java: Spring Boot, enterprise applications
• C#: ASP.NET framework

Database Technologies:
• SQL: MySQL, PostgreSQL, SQL Server
• NoSQL: MongoDB, Redis, Cassandra
• Cloud Databases: AWS RDS, Google Cloud SQL

DevOps and Deployment:
• Docker: Containerization platform
• Kubernetes: Container orchestration
• AWS, Google Cloud, Azure: Cloud platforms
• Git: Version control system
• CI/CD: Continuous integration and deployment

Modern web development focuses on responsive design, performance optimization, security, and user experience.
"""
            },
            {
                "title": "Climate Change and Environment",
                "content": """
Climate change refers to long-term shifts in temperature and weather patterns, primarily caused by human activities.

Causes of Climate Change:
1. Greenhouse Gas Emissions: Carbon dioxide, methane, nitrous oxide
2. Deforestation: Reduces carbon absorption capacity
3. Industrial Activities: Manufacturing, energy production
4. Transportation: Fossil fuel consumption
5. Agriculture: Livestock farming, rice cultivation

Effects of Climate Change:
• Rising global temperatures
• Extreme weather events (hurricanes, droughts, floods)
• Sea level rise due to melting ice caps
• Ocean acidification affecting marine life
• Biodiversity loss and species extinction
• Food and water security challenges
• Health impacts from heat waves and air pollution

Solutions and Mitigation:
• Transition to renewable energy sources
• Energy efficiency improvements
• Sustainable transportation systems
• Forest conservation and reforestation
• Carbon capture and storage technologies
• International agreements like Paris Accord
• Individual lifestyle changes

The scientific consensus is clear: climate change is real, human-caused, and requires immediate global action to prevent catastrophic consequences.
"""
            },
            {
                "title": "Space Exploration and Technology",
                "content": """
Space exploration involves the discovery and study of celestial structures in outer space using advanced technology.

Major Space Agencies:
• NASA (United States)
• ESA (European Space Agency)
• Roscosmos (Russia)
• CNSA (China)
• ISRO (India)
• JAXA (Japan)

Key Space Missions:
1. Apollo Program: First human moon landings (1969-1972)
2. Space Shuttle Program: Reusable spacecraft (1981-2011)
3. International Space Station: Continuous human presence in space
4. Mars Exploration: Rovers, landers, and orbiters
5. Hubble Space Telescope: Deep space observations
6. James Webb Space Telescope: Infrared astronomy

Current and Future Developments:
• Artemis Program: Return to the Moon by 2024
• Mars Sample Return Mission: Collect and return Martian samples
• Commercial Space Travel: SpaceX, Blue Origin, Virgin Galactic
• Satellite Constellations: Starlink, OneWeb for global internet
• Space Tourism: Orbital and suborbital flights
• Deep Space Exploration: Jupiter, Saturn, and beyond

Technological Advances:
• Reusable rocket technology
• Advanced propulsion systems
• Life support systems for long-duration missions
• Autonomous spacecraft operations
• Radiation protection for deep space travel

Space exploration drives technological innovation, inspires scientific discovery, and expands human understanding of the universe.
"""
            },
            {
                "title": "Psychology and Human Behavior",
                "content": """
Psychology is the scientific study of the human mind and behavior, encompassing various subfields and theoretical perspectives.

Major Branches of Psychology:
1. Clinical Psychology: Diagnosis and treatment of mental disorders
2. Cognitive Psychology: Mental processes like thinking, memory, perception
3. Developmental Psychology: Human growth and development across lifespan
4. Social Psychology: How individuals influence and are influenced by others
5. Forensic Psychology: Application of psychology in legal contexts
6. Industrial-Organizational Psychology: Workplace behavior and performance

Key Psychological Theories:
• Behaviorism: Focus on observable behaviors (Skinner, Pavlov)
• Cognitive Theory: Mental processes and information processing
• Psychodynamic Theory: Unconscious drives and early experiences (Freud)
• Humanistic Theory: Personal growth and self-actualization (Maslow, Rogers)
• Evolutionary Psychology: Adaptive behaviors from evolutionary perspective

Research Methods in Psychology:
• Experimental Research: Controlled studies to test hypotheses
• Observational Studies: Naturalistic observation of behavior
• Surveys and Questionnaires: Self-report data collection
• Case Studies: In-depth analysis of individual cases
• Neuroimaging: Brain scans to study neural activity
• Longitudinal Studies: Following subjects over extended periods

Mental Health and Wellness:
• Common Disorders: Depression, anxiety, PTSD, ADHD
• Treatment Approaches: Psychotherapy, medication, lifestyle interventions
• Prevention Strategies: Stress management, social support, healthy habits
• Stigma Reduction: Promoting mental health awareness

Psychology contributes to understanding human behavior, improving mental health treatment, and enhancing quality of life.
"""
            },
            {
                "title": "Renewable Energy Systems",
                "content": """
Renewable energy sources provide sustainable alternatives to fossil fuels, helping combat climate change and energy security.

Types of Renewable Energy:
1. Solar Energy: Photovoltaic panels, solar thermal systems
2. Wind Energy: Onshore and offshore wind turbines
3. Hydroelectric Power: Dams, run-of-river systems
4. Geothermal Energy: Heat from Earth's interior
5. Biomass Energy: Organic materials, biofuels
6. Tidal and Wave Energy: Ocean-based power generation

Advantages of Renewable Energy:
• Environmentally friendly with low carbon emissions
• Inexhaustible energy sources
• Energy independence and security
• Job creation in green technology sector
• Cost reductions through technological improvements
• Distributed generation capabilities

Challenges and Solutions:
• Intermittency: Energy storage solutions (batteries, pumped hydro)
• High initial costs: Government incentives, subsidies
• Land use requirements: Offshore installations, dual-use land
• Grid integration: Smart grid technology, demand response
• Material sourcing: Recycling programs, alternative materials

Global Energy Transition:
• International agreements (Paris Accord)
• National renewable energy targets
• Corporate sustainability commitments
• Investment in research and development
• Public awareness and education

The transition to renewable energy is essential for sustainable development and requires coordinated efforts from governments, businesses, and individuals.
"""
            },
            {
                "title": "Cybersecurity Fundamentals",
                "content": """
Cybersecurity involves protecting computer systems, networks, and data from digital attacks, theft, and damage.

Key Cybersecurity Concepts:
1. Confidentiality: Ensuring information is only accessible to authorized users
2. Integrity: Protecting data from unauthorized modification
3. Availability: Ensuring systems and data are accessible when needed

Common Cyber Threats:
• Malware: Viruses, ransomware, spyware, trojans
• Phishing: Social engineering attacks via email or websites
• DDoS Attacks: Distributed denial of service to overwhelm systems
• SQL Injection: Database attacks through web applications
• Man-in-the-Middle Attacks: Intercepting communications
• Zero-Day Exploits: Attacks on unknown vulnerabilities

Security Best Practices:
• Multi-Factor Authentication (MFA)
• Regular software updates and patches
• Strong password policies
• Employee security training
• Network segmentation and firewalls
• Data encryption at rest and in transit
• Regular security audits and penetration testing

Cybersecurity Frameworks:
• NIST Cybersecurity Framework
• ISO 27001 Information Security Management
• CIS Controls (Center for Internet Security)
• MITRE ATT&CK Framework for threat modeling

Emerging Technologies:
• Artificial Intelligence in threat detection
• Blockchain for secure transactions
• Quantum-resistant encryption
• Zero Trust Architecture
• Cloud security solutions

Cybersecurity is a critical concern for individuals, businesses, and governments, requiring constant vigilance and adaptation to evolving threats.
"""
            },
            {
                "title": "Blockchain Technology",
                "content": """
Blockchain is a distributed ledger technology that maintains a continuously growing list of records called blocks, secured using cryptography.

Core Blockchain Concepts:
1. Decentralization: No central authority controls the network
2. Transparency: All transactions are visible to network participants
3. Immutability: Once recorded, data cannot be altered
4. Consensus Mechanisms: Agreement on transaction validity

Types of Blockchains:
• Public Blockchains: Open to anyone (Bitcoin, Ethereum)
• Private Blockchains: Restricted access, single organization control
• Consortium Blockchains: Controlled by group of organizations
• Hybrid Blockchains: Combination of public and private features

Cryptocurrency Applications:
• Bitcoin: Digital currency and store of value
• Ethereum: Smart contracts and decentralized applications
• DeFi: Decentralized finance platforms
• NFTs: Non-fungible tokens for digital ownership
• Stablecoins: Cryptocurrencies pegged to traditional assets

Blockchain Use Cases:
• Supply Chain Management: Product traceability and authenticity
• Healthcare: Secure medical record sharing
• Voting Systems: Transparent and tamper-proof elections
• Real Estate: Property title management
• Identity Management: Digital identity verification
• Intellectual Property: Copyright and patent management

Challenges and Considerations:
• Scalability: Transaction speed and network congestion
• Energy Consumption: Proof-of-work mining environmental impact
• Regulatory Uncertainty: Legal and compliance frameworks
• Interoperability: Different blockchain networks working together
• Security Concerns: Smart contract vulnerabilities, exchange hacks

Blockchain technology has the potential to revolutionize various industries by providing trust, transparency, and efficiency in digital transactions.
"""
            {
                "title": "Healthcare and Medical Technology",
                "content": """
Healthcare encompasses a wide range of services and technologies aimed at maintaining and improving human health and well-being.

Major Areas of Healthcare:
1. Primary Care: Routine check-ups, preventive care, basic treatment
2. Emergency Medicine: Acute care for life-threatening conditions
3. Surgery: Operative procedures for treatment and diagnosis
4. Pediatrics: Medical care for infants, children, and adolescents
5. Geriatrics: Healthcare for elderly populations
6. Mental Health: Psychological and psychiatric care
7. Rehabilitation: Physical and occupational therapy

Medical Technologies:
• Diagnostic Imaging: X-rays, MRI, CT scans, ultrasound
• Electronic Health Records: Digital patient data management
• Telemedicine: Remote healthcare delivery
• Robotic Surgery: Computer-assisted surgical procedures
• Wearable Health Devices: Fitness trackers, smartwatches
• Artificial Intelligence: Medical diagnosis and treatment planning

Healthcare Challenges:
• Rising costs and insurance complexities
• Aging population and chronic diseases
• Healthcare accessibility and equity
• Medical data privacy and security
• Shortage of healthcare professionals
• Integration of new technologies

Healthcare Systems:
• Universal Healthcare: Government-funded systems
• Private Insurance: Employer-sponsored or individual plans
• Mixed Systems: Combination of public and private funding
• Digital Health: Technology-driven healthcare delivery

The healthcare industry continues to evolve with advances in medical research, technology integration, and changing demographics.
"""
            },
            {
                "title": "Financial Markets and Investment",
                "content": """
Financial markets facilitate the buying and selling of financial instruments, enabling capital allocation and economic growth.

Types of Financial Markets:
1. Stock Markets: Trading of company shares and equities
2. Bond Markets: Government and corporate debt instruments
3. Commodity Markets: Raw materials and natural resources
4. Foreign Exchange: Currency trading and exchange rates
5. Derivatives: Futures, options, and complex financial instruments
6. Cryptocurrency: Digital assets and blockchain-based trading

Investment Strategies:
• Value Investing: Buying undervalued assets for long-term growth
• Growth Investing: Investing in companies with high growth potential
• Dividend Investing: Focus on companies paying regular dividends
• Index Investing: Passive investment in market indices
• Alternative Investments: Real estate, private equity, hedge funds

Financial Instruments:
• Stocks: Ownership shares in publicly traded companies
• Bonds: Debt securities with fixed interest payments
• Mutual Funds: Pooled investments managed by professionals
• ETFs: Exchange-traded funds tracking indices or sectors
• Options: Contracts for buying/selling assets at predetermined prices
• Futures: Agreements to buy/sell assets at future dates

Risk Management:
• Diversification: Spreading investments across asset classes
• Asset Allocation: Balancing risk and return based on goals
• Dollar-Cost Averaging: Regular investment regardless of price
• Stop-Loss Orders: Automatic selling to limit losses
• Hedging: Protecting against adverse price movements

Market Analysis:
• Fundamental Analysis: Evaluating company financials and economics
• Technical Analysis: Studying price patterns and trading volumes
• Sentiment Analysis: Gauging market psychology and investor behavior
• Economic Indicators: GDP, inflation, employment data

Financial markets play a crucial role in economic development, capital formation, and wealth creation.
"""
            },
            {
                "title": "Modern Education Systems",
                "content": """
Education systems worldwide are evolving to meet the demands of the 21st century knowledge economy and changing workforce requirements.

Educational Levels:
1. Early Childhood Education: Preschool and kindergarten programs
2. Primary Education: Elementary school (ages 5-11)
3. Secondary Education: Middle and high school (ages 12-18)
4. Higher Education: Colleges, universities, and vocational training
5. Continuing Education: Lifelong learning and professional development

Teaching Methodologies:
• Traditional Learning: Lecture-based instruction and textbooks
• Active Learning: Student-centered, hands-on activities
• Blended Learning: Combination of online and in-person instruction
• Flipped Classroom: Students learn content at home, practice in class
• Project-Based Learning: Learning through real-world projects
• Personalized Learning: Individualized instruction based on student needs

Technology in Education:
• Learning Management Systems: Canvas, Moodle, Blackboard
• Educational Apps: Duolingo, Khan Academy, Coursera
• Virtual Reality: Immersive learning experiences
• Artificial Intelligence: Personalized tutoring and assessment
• Online Learning Platforms: MOOCs, webinars, virtual classrooms
• Adaptive Learning Software: Adjusts difficulty based on performance

Educational Challenges:
• Digital Divide: Access to technology and internet connectivity
• Learning Loss: Educational setbacks due to external factors
• Student Mental Health: Increasing rates of anxiety and depression
• Teacher Shortages: Recruitment and retention of qualified educators
• Standardized Testing: Balancing assessment with actual learning
• Inclusive Education: Meeting diverse learning needs

Future of Education:
• Micro-Credentials: Short, focused skill certifications
• Competency-Based Education: Learning at individual pace
• Global Education: International collaboration and exchange programs
• Lifelong Learning: Continuous skill development for career changes
• STEM Education: Science, technology, engineering, and mathematics focus

Education is the foundation of personal development, economic growth, and social progress.
"""
            },
            {
                "title": "Sports Science and Performance",
                "content": """
Sports science combines physiology, psychology, biomechanics, and nutrition to optimize athletic performance and prevent injuries.

Sports Physiology:
• Cardiovascular Endurance: Heart and lung efficiency
• Muscular Strength: Force generation and power output
• Flexibility: Range of motion and injury prevention
• Body Composition: Optimal muscle-to-fat ratios for different sports
• Energy Systems: Aerobic and anaerobic metabolism

Training Methods:
• Periodization: Structured training cycles for peak performance
• High-Intensity Interval Training: Short bursts of intense exercise
• Strength Training: Resistance exercises for power development
• Endurance Training: Sustained aerobic activities
• Speed and Agility Training: Quick movements and directional changes
• Recovery Training: Rest and regeneration techniques

Nutrition for Athletes:
• Macronutrients: Proteins, carbohydrates, and fats
• Micronutrients: Vitamins and minerals for performance
• Hydration: Fluid balance and electrolyte management
• Timing: Pre, during, and post-exercise nutrition
• Supplementation: Legal performance-enhancing substances
• Sports-Specific Diets: Tailored nutrition for different sports

Injury Prevention and Treatment:
• Biomechanical Analysis: Movement pattern assessment
• Strength Imbalances: Identifying and correcting weaknesses
• Recovery Protocols: Ice, compression, elevation, rest
• Rehabilitation Programs: Progressive return to activity
• Equipment Technology: Protective gear and performance tools
• Medical Interventions: Surgery, therapy, and medication

Sports Psychology:
• Mental Preparation: Visualization and goal setting
• Performance Anxiety: Managing pressure and stress
• Motivation: Intrinsic and extrinsic motivational factors
• Team Dynamics: Leadership and communication
• Focus and Concentration: Attention control techniques

Performance Analytics:
• Wearable Technology: GPS tracking, heart rate monitors
• Video Analysis: Technique assessment and improvement
• Statistical Analysis: Performance metrics and trends
• Predictive Modeling: Injury risk and performance forecasting

Sports science has revolutionized athletic training, making elite performance more accessible and sustainable.
"""
            },
            {
                "title": "World History and Civilizations",
                "content": """
World history encompasses the collective human experience, from ancient civilizations to modern global interactions.

Ancient Civilizations:
• Mesopotamia: Cradle of civilization, writing, and law codes
• Ancient Egypt: Pyramids, pharaohs, and Nile River culture
• Indus Valley: Advanced urban planning and sanitation systems
• Ancient China: Great Wall, silk road, and technological innovations
• Ancient Greece: Democracy, philosophy, and Olympic Games
• Roman Empire: Law, engineering, and vast territorial expansion

Medieval Period:
• Feudal System: Social hierarchy and land-based economy
• Crusades: Religious wars between Christians and Muslims
• Mongol Empire: Largest contiguous land empire in history
• Renaissance: Rebirth of art, science, and humanism in Europe
• Age of Exploration: Discovery of new continents and trade routes
• Ottoman Empire: Islamic caliphate and military expansion

Modern History:
• Industrial Revolution: Mechanization and urbanization
• World Wars: Global conflicts reshaping international relations
• Cold War: Ideological struggle between capitalism and communism
• Decolonization: Independence movements across Asia and Africa
• Information Age: Digital revolution and global connectivity
• Globalization: International trade and cultural exchange

Major Historical Events:
• Fall of Constantinople (1453): End of Byzantine Empire
• American Revolution (1776): Birth of democratic republic
• French Revolution (1789): Overthrow of absolute monarchy
• World War I (1914-1918): Trench warfare and chemical weapons
• World War II (1939-1945): Holocaust and atomic bombings
• Moon Landing (1969): Human achievement in space exploration

Historical Themes:
• Rise and Fall of Empires: Cycles of growth and decline
• Technological Progress: From stone tools to artificial intelligence
• Social Movements: Civil rights, women's suffrage, labor rights
• Economic Systems: From barter to cryptocurrency
• Cultural Exchange: Silk Road, colonialism, globalization

History provides context for understanding contemporary issues and informs future decision-making.
"""
            },
            {
                "title": "Literature and Creative Writing",
                "content": """
Literature encompasses written works of artistic and intellectual value, reflecting human experiences and imagination.

Literary Genres:
1. Fiction: Novels, short stories, and imaginative narratives
2. Poetry: Rhythmic language expressing emotions and ideas
3. Drama: Plays and theatrical works for performance
4. Non-Fiction: Essays, biographies, and factual accounts
5. Fantasy: Magical and supernatural elements
6. Science Fiction: Speculative fiction about future technologies
7. Mystery: Crime, detective, and suspense stories
8. Romance: Love stories and relationship narratives

Literary Movements:
• Romanticism: Emotion, nature, and individualism
• Realism: Accurate depiction of ordinary life
• Modernism: Experimental forms and psychological depth
• Postmodernism: Metafiction and cultural critique
• Magical Realism: Blend of reality and fantasy
• Beat Generation: Counterculture and spontaneous expression

Writing Techniques:
• Character Development: Creating believable and complex characters
• Plot Structure: Beginning, middle, end with rising action
• Setting: Time and place establishing context
• Point of View: First-person, third-person, omniscient
• Dialogue: Realistic conversations advancing plot
• Symbolism: Objects representing deeper meanings
• Foreshadowing: Hints about future events
• Theme: Central ideas or messages

Famous Literary Works:
• Shakespeare: Hamlet, Romeo and Juliet, Macbeth
• Jane Austen: Pride and Prejudice, Sense and Sensibility
• Mark Twain: The Adventures of Huckleberry Finn
• Charles Dickens: Great Expectations, A Tale of Two Cities
• Virginia Woolf: Mrs. Dalloway, To the Lighthouse
• Gabriel García Márquez: One Hundred Years of Solitude
• Toni Morrison: Beloved, The Bluest Eye

Creative Writing Process:
1. Brainstorming: Generating ideas and concepts
2. Outlining: Structuring the narrative
3. Drafting: Writing the first version
4. Revising: Improving content and structure
5. Editing: Correcting grammar and style
6. Publishing: Sharing work with readers

Literary Analysis:
• Close Reading: Detailed examination of text
• Historical Context: Understanding time period influences
• Author Biography: Writer's background and influences
• Cultural Significance: Social and political impact
• Stylistic Elements: Language use and literary devices

Literature serves as a mirror to society, preserving cultural heritage and inspiring future generations.
"""
            },
            {
                "title": "Transportation and Mobility",
                "content": """
Transportation systems enable movement of people and goods, connecting communities and driving economic development.

Modes of Transportation:
1. Road Transport: Cars, trucks, buses, motorcycles
2. Rail Transport: Trains, subways, high-speed rail
3. Air Transport: Commercial airlines, cargo planes, helicopters
4. Maritime Transport: Ships, cargo vessels, ferries
5. Pipeline Transport: Oil, gas, and liquid transport
6. Space Transport: Rockets, satellites, space stations

Urban Transportation:
• Public Transit: Buses, subways, light rail, trams
• Ride-Sharing: Uber, Lyft, and similar services
• Micro-Mobility: Electric scooters, bike-sharing
• Autonomous Vehicles: Self-driving cars and trucks
• Smart Cities: Integrated transportation systems
• Traffic Management: Intelligent transportation systems

Sustainable Transportation:
• Electric Vehicles: Battery-powered cars and buses
• Hydrogen Fuel Cells: Alternative clean energy source
• Public Transportation: Reduced individual car usage
• Active Transportation: Walking and cycling infrastructure
• Carpooling: Shared rides to reduce congestion
• Telecommuting: Working from home to reduce travel

Aviation Industry:
• Commercial Airlines: Passenger and cargo services
• Airport Operations: Ground handling and air traffic control
• Aircraft Manufacturing: Boeing, Airbus, and emerging companies
• Air Traffic Management: Radar, navigation, and communication
• Aviation Safety: Regulations and accident prevention
• Space Tourism: Commercial space travel

Maritime and Shipping:
• Container Shipping: Standardized cargo containers
• Port Operations: Loading, unloading, and logistics
• Cruise Industry: Passenger ships and entertainment
• Fishing Fleet: Commercial and recreational fishing
• Naval Operations: Military maritime activities
• Offshore Industries: Oil rigs and wind farms

Future Transportation:
• Hyperloop: High-speed ground transportation
• Flying Cars: Urban air mobility solutions
• Maglev Trains: Magnetic levitation rail systems
• Autonomous Shipping: Self-navigating cargo vessels
• Drone Delivery: Unmanned aerial vehicle logistics
• Space Travel: Commercial and tourist spaceflight

Transportation infrastructure forms the backbone of modern economies and global connectivity.
"""
            },
            {
                "title": "Agriculture and Food Systems",
                "content": """
Agriculture provides food, fiber, and fuel for human populations, evolving from traditional farming to modern agribusiness.

Types of Agriculture:
1. Subsistence Farming: Small-scale, family-based food production
2. Commercial Agriculture: Large-scale, profit-driven farming
3. Organic Farming: Chemical-free, sustainable practices
4. Precision Agriculture: Technology-driven farming methods
5. Vertical Farming: Indoor, multi-level crop production
6. Aquaculture: Fish and seafood farming

Crop Production:
• Cereals: Wheat, rice, corn, barley, oats
• Vegetables: Tomatoes, potatoes, onions, carrots, lettuce
• Fruits: Apples, oranges, bananas, grapes, berries
• Oilseeds: Soybeans, canola, sunflower, peanuts
• Legumes: Beans, lentils, chickpeas, peas
• Specialty Crops: Coffee, tea, cocoa, spices, herbs

Livestock Production:
• Cattle: Beef and dairy production
• Poultry: Chicken, turkey, duck farming
• Swine: Pork production and processing
• Sheep and Goats: Wool, milk, and meat production
• Aquaculture: Fish, shrimp, and shellfish farming
• Beekeeping: Honey production and pollination services

Agricultural Technology:
• Tractors and Machinery: Automated farming equipment
• Irrigation Systems: Drip irrigation, sprinklers, center pivots
• GPS and GIS: Precision mapping and field navigation
• Drones: Crop monitoring and field analysis
• Sensors: Soil moisture, weather, and crop health monitoring
• Biotechnology: Genetically modified crops and seeds

Food Processing and Distribution:
• Processing: Canning, freezing, drying, milling
• Packaging: Food preservation and marketing
• Cold Chain: Temperature-controlled storage and transport
• Supply Chain: From farm to consumer logistics
• Food Safety: Quality control and contamination prevention
• Traceability: Product tracking from origin to consumption

Sustainable Agriculture:
• Conservation Tillage: Reduced soil erosion practices
• Crop Rotation: Soil health and pest management
• Integrated Pest Management: Natural pest control methods
• Water Conservation: Efficient irrigation techniques
• Biodiversity: Multiple crop varieties and wildlife habitats
• Carbon Sequestration: Soil carbon storage practices

Global Food Security:
• Population Growth: Feeding 8+ billion people
• Climate Change: Adaptation to changing weather patterns
• Food Waste: Reducing loss throughout supply chain
• Nutrition: Ensuring access to healthy, diverse diets
• Trade: International food distribution and markets

Agriculture is fundamental to human survival and economic development worldwide.
"""
            },
            {
                "title": "Government and Political Systems",
                "content": """
Political systems organize societies, establish laws, and provide governance structures for collective decision-making.

Types of Government:
1. Democracy: Government by the people, for the people
2. Monarchy: Rule by a king, queen, or emperor
3. Dictatorship: Absolute rule by a single individual
4. Oligarchy: Rule by a small group of people
5. Theocracy: Government based on religious principles
6. Anarchy: Absence of formal government structure

Democratic Systems:
• Presidential Democracy: Separation of executive and legislative powers
• Parliamentary Democracy: Executive power derived from legislature
• Direct Democracy: Citizens vote directly on policy decisions
• Representative Democracy: Citizens elect representatives to make decisions
• Constitutional Democracy: Government limited by fundamental law
• Federal Democracy: Power divided between national and regional governments

Political Institutions:
• Executive Branch: President, prime minister, cabinet
• Legislative Branch: Congress, parliament, assembly
• Judicial Branch: Courts, supreme court, legal system
• Political Parties: Organizations competing for political power
• Civil Service: Bureaucratic administration of government
• Local Government: Municipal and regional administration

Electoral Systems:
• First-Past-The-Post: Winner takes all voting
• Proportional Representation: Seats allocated by vote percentage
• Ranked Choice Voting: Voters rank candidates by preference
• Mixed Systems: Combination of different voting methods
• Compulsory Voting: Mandatory participation in elections
• Absentee Voting: Mail-in and early voting options

Public Policy Areas:
• Economic Policy: Taxation, spending, and regulation
• Social Policy: Healthcare, education, and welfare
• Foreign Policy: International relations and diplomacy
• Environmental Policy: Conservation and climate action
• Defense Policy: Military and national security
• Immigration Policy: Border control and citizenship

Political Participation:
• Voting: Participation in elections and referendums
• Political Parties: Membership and campaign involvement
• Interest Groups: Lobbying and advocacy organizations
• Social Movements: Grassroots political activism
• Media: Journalism and political communication
• Civic Education: Understanding political processes

International Relations:
• Diplomacy: Negotiation between nations
• International Organizations: UN, NATO, EU, WTO
• Trade Agreements: Bilateral and multilateral treaties
• Conflict Resolution: Peacekeeping and mediation
• Global Governance: International law and cooperation

Political systems shape the organization and functioning of human societies.
"""
            },
            {
                "title": "Entertainment and Media Industry",
                "content": """
The entertainment industry encompasses various forms of media and cultural expression, providing recreation and information to global audiences.

Traditional Media:
1. Television: Broadcast, cable, and streaming content
2. Film: Movies, documentaries, and animated features
3. Music: Recording, live performance, and streaming
4. Publishing: Books, magazines, newspapers, and digital content
5. Radio: Broadcast radio, podcasts, and audio streaming
6. Theater: Live performances, musicals, and stage productions

Digital Media and Technology:
• Streaming Platforms: Netflix, Disney+, Amazon Prime Video
• Social Media: Facebook, Instagram, TikTok, YouTube
• Gaming: Video games, esports, and interactive entertainment
• Virtual Reality: Immersive digital experiences
• Augmented Reality: Enhanced real-world interactions
• Artificial Intelligence: Content creation and personalization

Content Creation:
• Film Production: Screenwriting, directing, cinematography
• Music Production: Composition, recording, mixing, mastering
• Game Development: Programming, design, art, sound design
• Publishing: Writing, editing, graphic design, marketing
• Digital Content: Blogging, vlogging, podcasting, streaming
• Live Entertainment: Concerts, theater, comedy, sports events

Entertainment Business:
• Talent Agencies: Representation for actors, musicians, athletes
• Production Companies: Content creation and development
• Distribution Networks: Getting content to audiences
• Marketing and Promotion: Advertising and public relations
• Merchandising: Branded products and tie-ins
• Licensing: Intellectual property rights management

Cultural Impact:
• Social Influence: Shaping public opinion and trends
• Educational Value: Documentaries and informative content
• Economic Impact: Job creation and revenue generation
• Global Reach: Cross-cultural exchange and understanding
• Technological Innovation: Driving new media technologies
• Artistic Expression: Platform for creative storytelling

Industry Challenges:
• Digital Disruption: Changing consumption patterns
• Copyright Protection: Piracy and intellectual property issues
• Content Moderation: Balancing free speech and safety
• Diversity and Inclusion: Representation in media
• Mental Health: Impact of fame and public scrutiny
• Sustainability: Environmental impact of production

Future Trends:
• Interactive Entertainment: Choose-your-own-adventure experiences
• Personalized Content: AI-curated recommendations
• Virtual Events: Digital concerts and conferences
• Cross-Platform Experiences: Seamless media consumption
• User-Generated Content: Creator economy growth
• Immersive Technologies: VR, AR, and mixed reality

Entertainment shapes culture, provides escape, and connects people across the globe.
"""
            }
        ]

    try:
        # Add documents to the system
        print(f"📝 Adding {len(documents)} sample documents...")

        for i, doc in enumerate(documents, 1):
            doc_id = agent.ingest_text(doc["content"])
            print(f"  ✅ Document {i}: {doc['title']} (ID: {doc_id})")

        # Test the system with various queries
        print("\n🧪 Testing the system with different queries...")
        test_queries = [
            "What is artificial intelligence?",
            "How does climate change affect the environment?",
            "What are the benefits of renewable energy?",
            "How does blockchain technology work?",
            "What is cybersecurity?",
            "How do financial markets work?",
            "What is modern education?",
            "How does sports science work?",
            "What is world history?",
            "What are literary genres?"
        ]

        for query in test_queries:
            result = agent.query(query)
            print(f"  ✅ {query}")
            print(f"  💡 Answer: {result.get('answer', 'No answer')[:100]}...")
            if result.get('retrieved_documents'):
                doc_titles = [doc.get('id', f'Doc {i+1}') for i, doc in enumerate(result['retrieved_documents'])]
                print(f"  📚 Sources: {', '.join(doc_titles[:3])}")
            print()

        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("✅ 20 diverse sample documents added successfully")
        print("✅ System ready for testing with varied topics")
        print("✅ Start the web interface with: python src/web_app.py")
        print("✅ Ask questions about AI, climate, finance, education, sports, history, literature, etc.")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_sample_data()
