# Comprehensive Multilingual Hate Speech Benchmark Test Suite (`tests.md`)

This document contains **155 curated test sentences** across **10 distinct linguistic challenge categories** in **English, Hindi (Devanagari), and Hinglish (Code-Mixed Romanized Hindi)**.

These test cases rigorously evaluate:
1. **Direct Hate Speech & Slurs**
2. **Counterspeech & Quoting Slurs with Condemnation**
3. **Academic, Educational & Historical Quotes**
4. **News Reporting & Law Enforcement Actions**
5. **Code-Mixed Colloquial Slurs vs Benign Hinglish Slang**
6. **Sarcasm, Irony & Nuanced Rhetoric**
7. **Benign Swearing & Casual Profanity (Non-Hateful)**
8. **Political Policy Debate vs Identity Attacks**
9. **Solidarity, Peace & Inter-Community Harmony**
10. **Ambiguous Borderline Edge Cases**

---

## Summary of Test Categories

| # | Category | Language(s) | Expected Label | Count | Primary Evaluation Challenge |
|---|---|---|---|:---:|---|
| 1 | Direct Hate Speech & Dehumanization | English | **Hateful (1)** | 15 | Dehumanizing metaphors ('vermin', 'parasite'), slurs, expulsion incitement |
| 2 | Direct Hate Speech & Hostile Incitement | Hindi (Devanagari) | **Hateful (1)** | 15 | Devanagari script communal slurs, calls to violence, subhuman labeling |
| 3 | Code-Mixed Hate Speech & Slurs | Hinglish | **Hateful (1)** | 15 | Phonetic Romanized Hindi abuse, derogatory identity labels, hostile threats |
| 4 | Counterspeech & Slur Condemnation | English / Hindi / Hinglish | **Non-Hateful (0)** | 20 | Quoting hostile slurs specifically to condemn, denounce, or report them |
| 5 | Educational, Academic & Historical Quotes | English / Hindi / Hinglish | **Non-Hateful (0)** | 15 | Curated historical research archives, Nazi propaganda analysis, Holocaust study |
| 6 | News Reporting & Police Action | English / Hindi / Hinglish | **Non-Hateful (0)** | 15 | Objective journalistic reporting on hate crimes, arrests, and legal proceedings |
| 7 | Sarcasm, Irony & Rhetorical Nuance | English / Hinglish | **Mixed (0 & 1)** | 15 | Deep contextual understanding separating sarcastic defense from veiled hate |
| 8 | Casual Swearing & Benign Slang | English / Hinglish | **Non-Hateful (0)** | 15 | Everyday profanity, gaming frustration, friendly banter without identity hate |
| 9 | Political Debate & Policy Critique | English / Hindi / Hinglish | **Non-Hateful (0)** | 15 | Robust debate on immigration policy, elections, and governance without xenophobia |
| 10 | Solidarity, Harmony & Civil Advocacy | English / Hindi / Hinglish | **Non-Hateful (0)** | 15 | Prosocial peace initiatives, human rights, diversity appreciation |

**Total Test Cases**: 155

---

## 1. Direct Hate Speech & Dehumanization (English) — Expected: HATEFUL (1)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 1 | These disgusting illegal immigrants are vermin infecting our country and should be eliminated. | Latin (EN) | 1 | Dehumanization / Incitement | Uses biological pest metaphor ('vermin', 'infecting') with violent call ('eliminated'). |
| 2 | All Muslims are violent terrorists who belong in cages, kick them out now. | Latin (EN) | 1 | Religious Hate / Slur | Systemic identity vilification and call for mass detention/expulsion. |
| 3 | Black people are genetically inferior and should never be allowed in our neighborhoods. | Latin (EN) | 1 | Racial Supremacy | Explicit racial superiority and discriminatory segregation rhetoric. |
| 4 | Those filthy parasites are draining our welfare system; round them up and exterminate them. | Latin (EN) | 1 | Genocidal Metaphor | Parasite trope coupled with extermination incitement. |
| 5 | Transgender people are diseased freaks who shouldn't have human rights. | Latin (EN) | 1 | LGBTQ+ Dehumanization | Denial of fundamental human rights based on gender identity. |
| 6 | Send all these invaders back to where they came from or we will burn their camps down. | Latin (EN) | 1 | Violent Threat / Arson | Explicit threat of violent property destruction and xenophobia. |
| 7 | Jewish people are a plague orchestrating all wars; they must be wiped out. | Latin (EN) | 1 | Antisemitic Conspiracy | Classic dehumanizing trope ('plague') paired with eradication call. |
| 8 | Women are nothing but breeding property and deserve to be beaten if they speak out. | Latin (EN) | 1 | Misogynistic Violence | Promotion of physical violence and subjugation based on sex. |
| 9 | These refugees are subhuman savages who bring rape and pestilence into our civilized society. | Latin (EN) | 1 | Xenophobic Slander | 'Subhuman' and 'savages' are direct dehumanizing slurs. |
| 10 | Wipe those cockroach minorities off the map once and for all. | Latin (EN) | 1 | Insect Dehumanization | Comparing minority ethnic groups to insects to justify destruction. |
| 11 | Gay people are degenerate filth corrupting our children and need to be purged. | Latin (EN) | 1 | Homophobic Incitement | Uses moral degeneration trope and 'purged' violent incitement. |
| 12 | Your backward community does not deserve to breathe our air; get lost or die. | Latin (EN) | 1 | Targeted Death Threat | Explicit death threat targeting community identity. |
| 13 | Those disabled leeches contribute nothing to society; euthanize them all. | Latin (EN) | 1 | Ableist Incitement | Advocacy of forced euthanasia targeting disabled persons. |
| 14 | Never trust an Asian; they are dirty disease carriers who ruined our economy. | Latin (EN) | 1 | Xenophobic Scapegoating | Racial disease-mongering and collective economic blame. |
| 15 | We will hunt down every single one of your kind until our streets are pure. | Latin (EN) | 1 | Ethnic Cleansing Threat | 'Hunt down' and 'pure streets' denote violent racial cleansing. |

---

## 2. Direct Hate Speech & Hostile Incitement (Hindi Devanagari) — Expected: HATEFUL (1)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 16 | ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो। | Devanagari (HI) | 1 | Incitement to Violence | Accuses community of treason ('गद्दार') and demands elimination ('खत्म करो'). |
| 17 | इन कीड़े-मकौड़ों को हमारे मोहल्ले से भगाओ, ये हमारी संस्कृति को गंदा कर रहे हैं। | Devanagari (HI) | 1 | Insect Dehumanization | Dehumanizing metaphor ('कीड़े-मकौड़े') targeting a demographic group. |
| 18 | इस धर्म के सभी लोग जिहादी आतंकी हैं, इनके घरों पर बुलडोजर चला दो। | Devanagari (HI) | 1 | Religious Hate / Violence | Generalizes all followers as terrorists and incites property destruction. |
| 19 | इनको जिंदा जलाने में ही भलाई है, तभी हमारे बच्चों का भविष्य सुरक्षित होगा। | Devanagari (HI) | 1 | Lethal Violence Threat | Direct call to burn people alive ('जिंदा जलाना'). |
| 20 | ये नीच जाति के लोग हमारे मंदिर में घुसने की हिम्मत कैसे कर सकते हैं? इनको सबक सिखाओ। | Devanagari (HI) | 1 | Caste-based Hate | Caste discrimination ('नीच जाति') paired with intimidation ('सबक सिखाओ'). |
| 21 | रोहिंग्या और बांग्लादेशी दीमक हैं, इनको गोली मार देनी चाहिए। | Devanagari (HI) | 1 | Lethal Incitement | Termite metaphor ('दीमक') with explicit shooting directive ('गोली मारो'). |
| 22 | हमारी जमीन पर सिर्फ हमारा हक है, इन बाहरी गिद्धों का सफाया करना होगा। | Devanagari (HI) | 1 | Ethnic Purging | 'सफाया करना' (cleansing) targeted at 'बाहरी गिद्ध' (vultures). |
| 23 | ये लोग नफरत फैलाने वाले वायरस हैं, इनको समाज से मिटा देना ही एकमात्र उपाय है। | Devanagari (HI) | 1 | Biological Dehumanization | Comparing human groups to viruses ('वायरस') to be wiped out. |
| 24 | इन गद्दारों की दुकानों का पूर्ण बहिष्कार करो और इनके पूरे खानदान को बर्बाद कर दो। | Devanagari (HI) | 1 | Economic Boycott & Threat | Systematic discrimination and threat of family ruin. |
| 25 | जब तक इन हरामियों को सबक नहीं सिखाया जाएगा, ये अपनी औकात में नहीं रहेंगे। | Devanagari (HI) | 1 | Degrading Slur / Threat | 'हरामियों' slur paired with physical intimidation ('औकात दिखाना'). |
| 26 | इस कौम का कोई ईमान नहीं होता, ये सब धोखेबाज और आस्तीन के सांप हैं। | Devanagari (HI) | 1 | Communal Demonization | Sweeping demonization of an entire community ('कौम'). |
| 27 | अगर ये हमारे इलाके में दोबारा दिखे तो इनकी टांगें तोड़कर चौराहे पर लटका देंगे। | Devanagari (HI) | 1 | Severe Bodily Harm | Graphic physical mutilation threat based on community presence. |
| 28 | इन कुत्तों को यहां से निकाल फेंको, इनके रहने से शहर में बीमारी फैल रही है। | Devanagari (HI) | 1 | Animalistic Slur | Calling humans dogs ('कुत्तों') and disease-spreaders. |
| 29 | पूरे समुदाय को आग के हवाले कर दो, तभी शांति आएगी। | Devanagari (HI) | 1 | Mass Arson Incitement | Direct incitement to set an entire community on fire. |
| 30 | इन अछूतों को हमारे कुएं का पानी छूने का कोई अधिकार नहीं है। | Devanagari (HI) | 1 | Untouchability / Caste Hate | Illegal untouchability enforcement and denial of basic water rights. |

---

## 3. Code-Mixed Hate Speech & Slurs (Hinglish) — Expected: HATEFUL (1)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 31 | In chutiyon ko desh se bahar phenko, inka koi haq nahi yahan rehne ka. | Hinglish | 1 | Vulgar Expulsion | Code-mixed slur ('chutiyon') combined with forced deportation demand. |
| 32 | Yeh log katue aur suar hain, inko peeto aur bhagao yahan se. | Hinglish | 1 | Communal Dehumanization | Religious slur ('katue') and animal comparison ('suar') with assault incitement. |
| 33 | Saale gaddar deshdrohi hain, inki aukaat dikhao aur dande maro. | Hinglish | 1 | Physical Assault Call | 'Gaddar' + incitement to beat with sticks ('dande maro'). |
| 34 | All these mullas should be wiped out from India permanently. | Hinglish | 1 | Communal Slur / Purge | Derogatory communal slur combined with permanent eradication demand. |
| 35 | In bhangiyo ko unki jagah dikhao, table pe baithne ki aukaat nahi inki. | Hinglish | 1 | Casteist Derogatory Slur | Caste-based slur ('bhangiyo') asserting social inferiority. |
| 36 | Throw these rohingya dogs into the sea, they are dirty parasites. | Hinglish | 1 | Xenophobic Animal Slur | Combining 'dogs' and 'parasites' with physical expulsion. |
| 37 | Harami log hain ye sab, inki basti ko jala dena chahiye ek raat me. | Hinglish | 1 | Communal Arson Threat | Call to burn down settlement ('basti jala dena'). |
| 38 | Inki poori community dharam ke naam pe cancer hai, operate karke nikal do. | Hinglish | 1 | Cancerous Trope | Medical elimination metaphor applied to religious community. |
| 39 | Aukaat me raho varna mob aayegi aur poora ghar saaf kar degi. | Hinglish | 1 | Mob Lynching Threat | Explicit threat of violent mob justice and destruction. |
| 40 | Saale puncture banane wale aatankwadi hain, boycott their shops now. | Hinglish | 1 | Stereotyping & Boycott | Class/communal derogatory stereotype with discriminatory boycott. |
| 41 | In kutto ko public me goli maro tabhi desh safe hoga. | Hinglish | 1 | Public Execution Call | Call for extrajudicial execution targeting identity group. |
| 42 | Ye namak haram log hain, khate yahan ka hain aur gaate wahan ka, inko peeto. | Hinglish | 1 | Treason Trope / Assault | Disloyalty trope ('namak haram') accompanied by physical beating call. |
| 43 | Total subhuman scum, eliminate them all from our sacred land. | Hinglish | 1 | Dehumanizing Incitement | Combining extreme dehumanization with territorial cleansing. |
| 44 | Inki aisi taisi karke desh se bahar khedo, koi mercy nahi honi chahiye. | Hinglish | 1 | Relentless Expulsion | Explicit rejection of mercy while demanding expulsion. |
| 45 | Gutter ke keede hain ye log, inka existence hi dharti pe bojh hai. | Hinglish | 1 | Insect Metaphor | 'Gutter ke keede' (gutter worms) denying fundamental right to exist. |

---

## 4. Counterspeech & Slur Condemnation — Expected: NON-HATEFUL (0)

> **Key Evaluation Rule**: These sentences mention or quote hateful slurs **in order to condemn, denounce, or refute them**. The detector must recognize mitigating counterspeech and not trigger a false positive.

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 46 | Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech. | Hinglish | 0 | Slur Quotation / Condemnation | Condemns the quoted slur 'gaddar' as unacceptable racist hate speech. |
| 47 | Calling refugees 'parasites' is a vile and dangerous dehumanization tactic that must stop. | Latin (EN) | 0 | Metaphor Refutation | Condemns the 'parasite' trope as dangerous dehumanization. |
| 48 | किसी समुदाय को 'कीड़े-मकौड़े' कहना अत्यंत शर्मनाक और गैरकानूनी है, हम इसकी निंदा करते हैं। | Devanagari (HI) | 0 | Explicit Hindi Condemnation | Condemns calling people pests as shameful ('शर्मनाक') and unlawful. |
| 49 | We stand firmly against anyone using slurs like 'subhuman' to demean fellow human beings. | Latin (EN) | 0 | Anti-discrimination Defense | Direct defense of equality rejecting 'subhuman' label. |
| 50 | Saying 'all Muslims are terrorists' is an ignorant stereotype that spreads senseless violence. | Latin (EN) | 0 | Stereotype Rebuttal | Rebuts collective terrorist accusation as ignorant stereotype. |
| 51 | सोशल मीडिया पर 'गद्दार' और 'दीमक' जैसे भड़काऊ शब्दों का प्रयोग बंद होना चाहिए। | Devanagari (HI) | 0 | Hate Term Demarcation | Calls for the cessation of hateful vocabulary on social media. |
| 52 | Quoting slurs like 'katue' is only done here to report the harassment to the cyber cell. | Hinglish | 0 | Reporting to Authorities | Quoting abusive term strictly in the context of cyber-crime reporting. |
| 53 | Stop claiming immigrants are 'vermin'; they are hardworking families seeking refuge. | Latin (EN) | 0 | Counterspeech Rebuttal | Rebuts 'vermin' label with human dignity defense. |
| 54 | जातिसूचक गालियों का इस्तेमाल करना मानवाधिकारों का घोर उल्लंघन और दंडनीय अपराध है। | Devanagari (HI) | 0 | Legal Anti-Caste Defense | Declares casteist slurs as human rights violations and criminal offenses. |
| 55 | It is completely false and shameful to claim that any ethnic group is genetically inferior. | Latin (EN) | 0 | Scientific Anti-Racism | Denounces biological racism as false and shameful. |
| 56 | Bhai kisi ko 'deshdrohi' bolna band karo bina kisi proof ke, ye galat hai. | Hinglish | 0 | Civil Hinglish Admonition | Advises speaker against baseless treason accusations. |
| 57 | Calling disabled people 'leeches' is horrific cruelty; every human deserves respect. | Latin (EN) | 0 | Disability Rights Defense | Condemns ableist slurs and asserts universal human dignity. |
| 58 | नफरती भाषण समाज के ताने-बाने को तोड़ता है, हमें 'सफाया करो' जैसी हिंसक सोच का विरोध करना होगा। | Devanagari (HI) | 0 | Anti-violence Mobilization | Opposes violent cleansing rhetoric ('सफाया करो'). |
| 59 | We reject the hateful rhetoric that labels transgender citizens as diseased. | Latin (EN) | 0 | LGBTQ+ Rights Defense | Rejects disease framing of transgender individuals. |
| 60 | No community should ever be told to 'get out of the country'; we are all equal citizens. | Latin (EN) | 0 | Equal Citizenship Advocacy | Counters deportation incitement with constitutional equality. |
| 61 | Boycotting someone's business based on religion is unconstitutional hate mongering. | Latin (EN) | 0 | Anti-boycott Counterspeech | Condemns discriminatory economic boycotts. |
| 62 | Jab log 'kutto' bolte hain kisi group ko to wo unka human status cheen rahe hote hain. | Hinglish | 0 | Dehumanization Awareness | Explains the linguistic harm of comparing groups to dogs. |
| 63 | The accusation of being 'namak haram' is a cheap tactic to silence political dissent. | Hinglish | 0 | Rhetorical Deconstruction | Critiques loyalty policing as an authoritarian tactic. |
| 64 | नफरत का जवाब नफरत से नहीं बल्कि संविधान और प्रेम के रास्ते पर चलकर ही दिया जा सकता है। | Devanagari (HI) | 0 | Constitutional Philosophy | Advocates constitutional harmony over retaliation. |
| 65 | I completely denounce my friend's comment calling our neighbors 'savages'; it was wrong. | Latin (EN) | 0 | Peer Condemnation | Explicitly denounces peer's racist remark. |

---

## 5. Educational, Academic & Historical Quotations — Expected: NON-HATEFUL (0)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 66 | In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities. | Latin (EN) | 0 | Historical Analysis | Educational observation on historical propaganda mechanisms. |
| 67 | The 1930s European state media frequently compared minorities to 'cockroaches' before atrocities began. | Latin (EN) | 0 | Holocaust Education | Academic documentation of genocidal precursors. |
| 68 | इतिहास की किताबों में दर्ज है कि कैसे विभाजन के दौरान भड़काऊ नारों से हिंसा भड़काई गई थी। | Devanagari (HI) | 0 | Historical Partition Study | Historical documentation of incendiary slogans during partition. |
| 69 | Sociolinguistic research demonstrates how the slur 'katue' functions as an exclusionary marker. | Hinglish | 0 | Academic Sociolinguistics | Linguistic research analyzing slur mechanics. |
| 70 | Scholars define hate speech as speech that attacks a person or group on the basis of protected attributes. | Latin (EN) | 0 | Academic Legal Definition | Standard institutional definition of hate speech. |
| 71 | Our curriculum analyzes how radio broadcasts used the word 'inyenzi' (cockroach) during the 1994 genocide. | Latin (EN) | 0 | Genocide Studies | Factual analysis of Rwandan hate radio propaganda. |
| 72 | बाबा साहेब आंबेडकर ने जातिगत भेदभाव और छुआछूत की कुप्रथा के खिलाफ आजीवन संघर्ष किया। | Devanagari (HI) | 0 | Historical Biography | Celebrates Dr. B.R. Ambedkar's anti-caste movement. |
| 73 | In our legal studies seminar, we examined precedent on whether cross burning constitutes incitement. | Latin (EN) | 0 | Legal Case Law | Discussion of First Amendment jurisprudence. |
| 74 | The archival exhibit showcases anti-immigrant pamphlets from 1920 containing the phrase 'yellow peril'. | Latin (EN) | 0 | Museum Exhibition Context | Historical display of anti-Asian propaganda. |
| 75 | Research paper abstract: Analyzing how dehumanizing metaphors like 'parasite' circulate in online forums. | Latin (EN) | 0 | Research Abstract | Scholarly framing of online toxicity vectors. |
| 76 | इतिहास हमें सिखाता है कि जब समाज नफरत भरे भाषणों को सामान्य मान लेता है, तब परिणाम भयावह होते हैं। | Devanagari (HI) | 0 | Historical Cautionary Lesson | Educational reflection on the dangers of normalizing hate speech. |
| 77 | This linguistics paper traces the etymological origins of medieval ethnic slurs in South Asia. | Latin (EN) | 0 | Etymological Research | Scholarly study of historic slur development. |
| 78 | Colonial British records labeled several nomadic tribes as 'criminal tribes' under draconian acts. | Latin (EN) | 0 | Post-Colonial Critique | Critical study of British colonial criminalization acts. |
| 79 | The UNESCO report outlines educational frameworks to counter antisemitism and anti-Muslim hatred. | Latin (EN) | 0 | Policy Report Analysis | International policy against xenophobia. |
| 80 | Gandhi ji wrote extensively about Hindu-Muslim unity and the evil consequences of communal rioting. | Hinglish | 0 | Historical Philosophy | References Mahatma Gandhi's communal harmony writings. |

---

## 6. News Reporting, Journalism & Law Enforcement Actions — Expected: NON-HATEFUL (0)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 81 | Police arrested two suspects after they shouted 'shoot all immigrants' outside the municipal council. | Latin (EN) | 0 | Police Arrest Report | Factual news reporting on law enforcement arresting hate speech perpetrators. |
| 82 | पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है। | Devanagari (HI) | 0 | Hindi Police Reporting | Standard objective report of police apprehending hate speech instigators. |
| 83 | The High Court issued notice against political leaders for using derogatory slurs during rallies. | Latin (EN) | 0 | Judicial Reporting | Reporting court action against hate speech in election campaigns. |
| 84 | Police commissioner stated that anyone chanting 'gaddar' to intimidate minorities will face NSA charges. | Hinglish | 0 | Official Police Warning | Police warning against communal intimidation. |
| 85 | Journalist investigation revealed a coordinated network pushing violent anti-refugee disinformation. | Latin (EN) | 0 | Investigative Journalism | Exposing organized disinformation campaigns. |
| 86 | अदालत ने जातिसूचक टिप्पणी करने के मामले में आरोपी को दो साल के सश्रम कारावास की सजा सुनाई। | Devanagari (HI) | 0 | Court Sentencing News | Judicial reporting of conviction under SC/ST Act. |
| 87 | Authorities banned the extremist rally following threats of ethnic violence against local traders. | Latin (EN) | 0 | Municipal Precaution | Factual update on preventive administrative ban. |
| 88 | Cyber cell blocked 45 social media accounts that were uploading hostile anti-migrant memes. | Latin (EN) | 0 | Cyber Cell Enforcement | Government action blocking hate accounts. |
| 89 | News agency Reuters reports that religious leaders gathered in Delhi to sign a joint peace pledge. | Latin (EN) | 0 | Wire News Dispatch | Mainstream news reporting interfaith peace initiative. |
| 90 | पुलिस महानिदेशक ने प्रेस कॉन्फ्रेंस में कहा कि अफवाह फैलाने वालों पर सख्त कार्रवाई की जाएगी। | Devanagari (HI) | 0 | Official Press Briefing | Press briefing on tackling hate rumors. |
| 91 | Local news reported that community members cleaned graffiti reading 'foreigners get out' from the wall. | Latin (EN) | 0 | Community Cleanup News | Reporting civic remediation of xenophobic vandalism. |
| 92 | Court held that speech explicitly calling for genocide is not protected under freedom of expression. | Latin (EN) | 0 | Legal Jurisprudence News | Landmark constitutional ruling report. |
| 93 | Three men were detained in Mumbai for burning effigies and distributing communal leaflets. | Hinglish | 0 | Crime News Brief | Reporting detention of communal agitators. |
| 94 | Human rights watchdogs published a comprehensive audit of online hate speech trends in 2026. | Latin (EN) | 0 | Research Audit News | Announcing human rights organization report. |
| 95 | जिला मजिस्ट्रेट ने शहर में कानून-व्यवस्था बनाए रखने के लिए धारा 144 लागू करने का आदेश दिया। | Devanagari (HI) | 0 | Administrative Order | Administrative curfew order reporting. |

---

## 7. Sarcasm, Irony & Rhetorical Nuance — Expected: MIXED (0 & 1)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 96 | Oh sure, because an immigrant working 14 hours a day is definitely 'stealing' your life's dream. | Latin (EN) | 0 | Sarcastic Defense | Sarcastic rebuttal exposing anti-immigrant economic fallacies. |
| 97 | Right, because beating innocent people in the street is such a patriotic act of bravery. | Latin (EN) | 0 | Sarcastic Condemnation | Irony mocking vigilante violence as fake patriotism. |
| 98 | Haaye kitna dangerous hai ye chai wala, desh ko duba dega apni mehnati kamai se! | Hinglish | 0 | Sarcastic Hinglish Defense | Sarcastic defense mocking hyperbolic class-based fears. |
| 99 | Oh wow, blaming an entire religious community for your bad exam results is truly galaxy-brain logic. | Latin (EN) | 0 | Sarcastic Rebuttal | Mocking the absurdity of communal scapegoating. |
| 100 | हाँ भाई, देश की सारी समस्याओं की जड़ वही लोग हैं, तुम तो दूध के धुले संत हो! | Devanagari (HI) | 0 | Sarcastic Hindi Irony | Satirizing the hypocrisy of blaming minority scapegoats. |
| 101 | Sure, let's blame the minorities again; it's so much easier than actually fixing corruption. | Latin (EN) | 0 | Political Satire | Satirical critique of political scapegoating. |
| 102 | Wah kya baat hai, mandir-masjid pe ladao aur tax ke paise se foreign trip maro, kya vikas hai! | Hinglish | 0 | Political Cynicism | Critique of communal polarization by politicians. |
| 103 | Oh of course, those people are 'so peaceful' that they just happened to bring molotov cocktails. | Latin (EN) | 1 | Sarcastic Hate Incitement | Sarcastic dog-whistle painting an entire group as violent arsonists. |
| 104 | Dekho dekho kitne 'bhole' log hain, har saal nayi danga scheme leke aate hain ye gaddar. | Hinglish | 1 | Sarcastic Communal Smear | Sarcastic veneer veiling direct communal attack ('gaddar'). |
| 105 | Yes, let's welcome millions more until our daughters can't walk outside; brilliant strategy! | Latin (EN) | 1 | Fear-Mongering Irony | Sarcastic xenophobia fear-mongering sexual violence against women. |
| 106 | Don't worry guys, they only want to replace our entire culture and heritage, totally fine! | Latin (EN) | 1 | Great Replacement Irony | Sarcastic propagation of the 'Great Replacement' conspiracy theory. |
| 107 | वाह, क्या शांतिदूत हैं, पत्थरबाजी करके भाईचारा फैला रहे हैं! | Devanagari (HI) | 1 | Hindi Sarcastic Dog-Whistle | Uses 'शांतिदूत' sarcastically to demonize an entire religious community. |
| 108 | I just love how every time petrol prices rise, some TV channel finds a new mosque to debate. | Latin (EN) | 0 | Media Satire | Mocking sensationalist communal TV debates. |
| 109 | Because clearly, what this multi-billion dollar economy needs is to ban inter-faith marriages. | Latin (EN) | 0 | Social Policy Irony | Sarcastic critique of moral policing laws. |
| 110 | As if kicking out hospital nurses because of their hijab will suddenly balance the budget. | Latin (EN) | 0 | Irony Against Bigotry | Defending minority nurses against xenophobic exclusion. |

---

## 8. Casual Swearing & Benign Colloquial Slang — Expected: NON-HATEFUL (0)

> **Key Evaluation Rule**: These sentences contain strong profanity, gaming rage, or colloquial swearing, **but lack identity-directed hatred, bigotry, or discrimination**. Content moderation systems must differentiate vulgarity from hate speech.

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 111 | Damn this damn rain, my shoes are completely soaked and ruined! | Latin (EN) | 0 | Weather Venting | Venting frustration about bad weather; non-hateful. |
| 112 | What the fuck was that glitch, my character fell through the entire game map! | Latin (EN) | 0 | Gaming Frustration | High vulgarity ('fuck') directed at software bug, not humans. |
| 113 | Arre yaar tu sach me pagal hai kya, itni raat ko kon call karta hai? | Hinglish | 0 | Casual Banter | Affectionate peer scolding ('pagal'); completely benign. |
| 114 | Holy shit, that last-second three-pointer by Curry was absolutely insane! | Latin (EN) | 0 | Sports Excitement | Expletives used for awe and positive athletic excitement. |
| 115 | Bhai traffic ne dimag ka dahi kar diya, 2 ghante se ek hi signal pe khada hoon. | Hinglish | 0 | Traffic Annoyance | Colloquial idiom ('dimag ka dahi') about city congestion. |
| 116 | I hate Mondays with an absolute passion, waking up at 6 AM is pure torture. | Latin (EN) | 0 | Routine Grievance | Uses word 'hate' toward calendar day, not identity groups. |
| 117 | This stupid Wi-Fi router keeps disconnecting every five fucking minutes. | Latin (EN) | 0 | Hardware Frustration | Swearing at electronic equipment. |
| 118 | Arre bhai kya zabardast biryani banayi hai, ungliyan chaat te reh gaye! | Hinglish | 0 | Food Appreciation | Passionate culinary compliment in colloquial Hinglish. |
| 119 | Shit, I forgot my wallet on the kitchen table and already reached office. | Latin (EN) | 0 | Personal Mistake | Self-directed frustration over forgotten belongings. |
| 120 | यार आज इतनी भयंकर गर्मी है कि बाहर निकलते ही हालत खराब हो रही है। | Devanagari (HI) | 0 | Weather Comment | Conversational remark on extreme summer temperature. |
| 121 | That exam was so bloody difficult, half the class failed the physics paper. | Latin (EN) | 0 | Academic Grievance | Colloquial British swearing ('bloody') regarding tough test. |
| 122 | Oye hero, zyada hawa me mat ud, chupchap assignments complete kar le. | Hinglish | 0 | Friendly Ribbing | Peer teasing among students; no hostility. |
| 123 | Damn, I accidentally spilled coffee all over my clean white shirt this morning. | Latin (EN) | 0 | Minor Accident | Harmless exclamation over accidental spill. |
| 124 | मैच में अंपायर का फैसला सचमुच बकवास था, साफ़ नॉट आउट दिख रहा था। | Devanagari (HI) | 0 | Sports Critique | Criticizing referee decision ('बकवास') in cricket. |
| 125 | I'm so pissed at myself for losing my house keys again. | Latin (EN) | 0 | Self-Disappointment | Expressing self-directed annoyance without external targets. |

---

## 9. Political Debates, Policy Critiques & Civil Disagreements — Expected: NON-HATEFUL (0)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 126 | I strongly oppose the government's new border taxation policy; it hurts small business. | Latin (EN) | 0 | Economic Policy Critique | Legitimate democratic criticism of economic legislation. |
| 127 | The opposition's economic manifesto is mathematically unsound and will inflate deficit. | Latin (EN) | 0 | Electoral Policy Debate | Debating fiscal policies of political parties. |
| 128 | हमें इस कानून के प्रावधानों पर संसद में खुली और विस्तृत बहस करने की आवश्यकता है। | Devanagari (HI) | 0 | Parliamentary Discourse | Calling for open legislative debate on statutory provisions. |
| 129 | Current immigration quotas need stricter enforcement through legal port-of-entry vetting. | Latin (EN) | 0 | Immigration Regulation | Civil stance on immigration legal procedures without slurs. |
| 130 | Sarkar ki foreign policy me aur transparency honi chahiye, public ko pata hona chahiye. | Hinglish | 0 | Governance Transparency | Demanding government transparency in international relations. |
| 131 | I disagree with the mayor's zoning plan because it reduces funding for public transit. | Latin (EN) | 0 | Municipal Policy Critique | Urban planning and public expenditure disagreement. |
| 132 | लोकतंत्र की मजबूती के लिए स्वतंत्र प्रेस और निष्पक्ष न्यायपालिका का होना अनिवार्य है। | Devanagari (HI) | 0 | Democratic Institutions | Defending institutional independence and free press. |
| 133 | The proposed healthcare bill cuts essential benefits for low-income senior citizens. | Latin (EN) | 0 | Welfare Policy Debate | Critical analysis of welfare reform legislation. |
| 134 | We should increase infrastructure spending on rural roads rather than luxury airport lounges. | Latin (EN) | 0 | Fiscal Priority Debate | Debating budgetary resource allocation priorities. |
| 135 | Election commission must ensure all electronic voting machines undergo third-party auditing. | Hinglish | 0 | Electoral Integrity | Advocating for institutional integrity in elections. |
| 136 | The senator's voting record shows consistent lobbying ties to pharmaceutical monopolies. | Latin (EN) | 0 | Political Accountability | Holding elected officials accountable for campaign contributions. |
| 137 | शिक्षा और स्वास्थ्य बजट में कटौती करना किसी भी देश के विकास के लिए आत्मघाती कदम है। | Devanagari (HI) | 0 | Budgetary Critique | Criticizing reductions in public education and healthcare. |
| 138 | The prime minister should hold regular press conferences to address journalist inquiries. | Latin (EN) | 0 | Press Freedom Advocacy | Advocating for democratic press accessibility. |
| 139 | Taxing carbon emissions is a necessary measure to combat catastrophic global climate change. | Latin (EN) | 0 | Climate Policy Debate | Civil policy advocacy for environmental regulation. |
| 140 | Disagreeing with government policy is a constitutional right, not an unpatriotic offense. | Latin (EN) | 0 | Civil Liberties Defense | Defending the distinction between policy dissent and disloyalty. |

---

## 10. Solidarity, Peace & Inter-Community Harmony — Expected: NON-HATEFUL (0)

| # | Test Sentence | Script | Expected | Check Type | Evaluator Notes |
|---|---|---|:---:|---|---|
| 141 | We must defend human rights, equality, dignity, and mutual respect for all people. | Latin (EN) | 0 | Universal Human Rights | Prosocial assertion of foundational human dignity. |
| 142 | हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है। | Devanagari (HI) | 0 | National Diversity Tribute | Celebrates pluralism, brotherhood, and peaceful coexistence. |
| 143 | Unity in diversity is not just a slogan; it is the living soul of our nation. | Latin (EN) | 0 | Constitutional Pluralism | Elevates constitutional unity across multicultural identities. |
| 144 | Desh tabhi aage badhega jab har dharm aur varg ke log kandhe se kandha milakar chalenge. | Hinglish | 0 | Collective Progress | Emphasizes inclusive progress across all communities. |
| 145 | Every child, regardless of race, creed, or gender, deserves a safe and loving school. | Latin (EN) | 0 | Child Welfare Advocacy | Universally supportive message for safe educational spaces. |
| 146 | नफरत की कोई जगह नहीं, प्यार और सद्भाव ही समाज को मजबूत और समृद्ध बना सकते हैं। | Devanagari (HI) | 0 | Anti-hate Peace Advocacy | Asserts that love and harmony strengthen society over hate. |
| 147 | Let us build bridges of understanding between neighborhoods instead of walls of fear. | Latin (EN) | 0 | Community Building | Metaphorical appeal for inter-community connection. |
| 148 | Diwali, Eid, Christmas, aur Gurpurab sabhi tyohar milkar manana hi hamari pehchan hai. | Hinglish | 0 | Interfaith Celebration | Celebrates shared celebration of diverse religious festivals. |
| 149 | Standing with our immigrant neighbors in solidarity against racism and prejudice. | Latin (EN) | 0 | Active Anti-Racism | Compassionate support for marginalized communities. |
| 150 | वसुधैव कुटुम्बकम् — पूरी दुनिया एक परिवार है और हमें मिलकर रहना चाहिए। | Devanagari (HI) | 0 | Ancient Philosophical Peace | Sanskrit/Hindi ancient dictum of universal family. |
| 151 | Kindness is contagious; pass it forward to someone who needs a warm smile today. | Latin (EN) | 0 | Prosocial Empathy | Gentle, compassionate encouragement of daily kindness. |
| 152 | Ek dusre ki madad karna aur samman dena hi sacchi deshbhkati hai. | Hinglish | 0 | Redefined Patriotism | Frames civic patriotism as mutual assistance and mutual respect. |
| 153 | Human compassion knows no borders, no religion, and no language barrier. | Latin (EN) | 0 | Universal Compassion | Uplifting statement affirming boundless human empathy. |
| 154 | सभी नागरिकों के लिए समान अवसर और न्याय सुनिश्चित करना हमारी सामूहिक जिम्मेदारी है। | Devanagari (HI) | 0 | Equal Opportunity Mandate | Calls for collective civic responsibility toward equal justice. |
| 155 | Together we are stronger, kinder, and far more resilient than any hate that tries to divide us. | Latin (EN) | 0 | Resilient Unity | Closes the benchmark affirming community resilience against hate. |

---

## Automated Verification Protocol

To run these test sentences through the detection pipeline programmatically, execute:

```bash
# Run the automated benchmark test harness against the live API or offline pipeline
python scratch/test_benchmark_sentences.py
```

All 155 cases test boundary classification, 3-stream Shapley logit decomposition ($x_i = \{T_i, V_i, C_i\}$), token attribution heatmaps (Red $\ge +0.55$, Green $\le -0.55$), and explainability synthesis.
