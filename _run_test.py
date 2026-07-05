import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models.fake_news_detector import FakeNewsDetector
det = FakeNewsDetector()

real_news = [
    ("RN-01", "WHO declares mpox a global health emergency for second time", "The World Health Organization has declared mpox a public health emergency of international concern following a surge of cases in the Democratic Republic of Congo and neighboring countries. The declaration marks the second time mpox has received this designation. Health officials warn of a new, more severe strain spreading rapidly, prompting urgent calls for vaccine distribution to affected regions."),
    ("RN-02", "OpenAI launches GPT-4o with real-time voice and vision capabilities", "OpenAI unveiled GPT-4o, a new flagship model capable of handling text, audio, and images in real time. The model can detect emotions from voice tone and engage in natural conversations with response times comparable to a human. The company demonstrated the model performing live translation, tutoring, and coding assistance, marking a significant leap in multimodal AI capability."),
    ("RN-03", "Scientists confirm Voyager 1 resumes sending usable data from interstellar space", "NASA announced that the Voyager 1 spacecraft has resumed transmitting usable science data after months of sending back corrupted signals. Engineers discovered that a faulty chip in one of the spacecraft computers was corrupting data and found a workaround by relocating the affected code. Voyager 1, launched in 1977, remains the most distant human-made object in space."),
    ("RN-04", "Indias Chandrayaan-3 successfully lands near Moons south pole", "India became the fourth country to achieve a soft landing on the Moon and the first to land near its south pole, as its Chandrayaan-3 mission touched down successfully. The Vikram lander deployed the Pragyan rover, which began exploring the lunar surface. Scientists are particularly interested in the region for its water ice deposits that could support future human missions."),
    ("RN-05", "EU passes worlds first comprehensive AI regulation", "The European Parliament formally approved the Artificial Intelligence Act, the worlds first comprehensive legal framework for artificial intelligence. The law categorizes AI applications by risk level and bans certain uses entirely, including real-time facial recognition in public spaces. Tech companies now face significant compliance requirements, with large fines for violations."),
    ("RN-06", "Sam Altman ousted as OpenAI CEO, reinstated days later after board reversal", "OpenAIs board of directors abruptly fired CEO Sam Altman, citing a lack of consistent candor in communications. The move triggered an immediate crisis as hundreds of OpenAI employees threatened to resign and join Microsoft. Within five days the board reversed course, reinstating Altman and announcing new board members, in one of the most turbulent leadership crises in Silicon Valley history."),
    ("RN-07", "Gaza ceasefire deal reached after months of negotiations", "A ceasefire agreement between Israel and Hamas was brokered following months of intensive negotiations involving Qatar, Egypt, and the United States. The deal includes a phased release of hostages held in Gaza in exchange for Palestinian prisoners and humanitarian aid access. Fighting paused as both sides began implementing the first phase of the agreement."),
    ("RN-08", "First malaria vaccine approved for broad use in Africa", "The WHO recommended the R21/Matrix-M malaria vaccine developed by the University of Oxford for broad use after it demonstrated up to 75 percent efficacy in clinical trials. The vaccine, manufactured at scale in India, is seen as a major breakthrough in the fight against malaria, which kills more than 600000 people annually, the majority of them children in sub-Saharan Africa."),
    ("RN-09", "Tesla recalls over 2 million vehicles over Autopilot safety concerns", "Tesla recalled more than two million vehicles in the United States after a two-year investigation by the National Highway Traffic Safety Administration found that its Autopilot system did not adequately ensure driver attentiveness. The company issued an over-the-air software update to add new controls and alerts designed to keep drivers engaged while the feature is active."),
    ("RN-10", "COP28 agreement calls for transition away from fossil fuels", "Nations at the COP28 climate summit in Dubai agreed on a historic deal calling for a transition away from fossil fuels for the first time in the three-decade history of UN climate talks. The text stopped short of the outright phaseout demanded by many nations and scientists, but was still described by many delegates as a landmark step toward decarbonizing the global economy."),
]

fake_news = [
    ("FK-11", "Scientists discover humans can photosynthesize sunlight for up to 30 percent of daily energy needs", "Researchers at the International Institute of Human Biophysics claim to have identified a dormant chlorophyll-like compound in human skin cells that can convert sunlight into usable energy. The study suggests that spending two hours daily in direct sunlight could reduce caloric intake requirements by nearly a third. Nutritionists are reportedly revising global dietary guidelines in response."),
    ("FK-12", "Government quietly adds microchips to COVID-19 booster shots, leaked documents show", "Classified documents allegedly obtained by a whistleblower show that health authorities added nano-scale tracking chips to updated COVID-19 booster doses. The chips are said to transmit location data to a centralized government database via 5G networks. Health agencies have not responded to requests for comment, fueling widespread speculation on social media platforms."),
    ("FK-13", "NASA confirms radio signals from Mars are human speech recorded centuries ago", "NASA scientists working with the Perseverance rover have reportedly decoded recurring radio frequency patterns emanating from beneath the Martian surface. Agency insiders claim the patterns match ancient spoken Sumerian, though this has not been officially announced. A press conference has allegedly been scheduled but repeatedly postponed under pressure from unnamed government officials."),
    ("FK-14", "Major bank quietly cancels all customer debts over 50000 due to internal error", "Citibank has allegedly been notifying select customers that outstanding loan balances exceeding 50000 have been written off following a software glitch in their debt management system. Customers who received forgiveness letters are reportedly being advised to stay silent while the bank assesses legal liability. Financial regulators have not confirmed or denied an investigation."),
    ("FK-15", "Scientists revive woolly mammoth; first calf born in Siberian facility", "A biotech startup claims to have successfully birthed a live woolly mammoth calf using reconstructed DNA and an elephant surrogate. The animal, reportedly healthy and kept at an undisclosed Siberian research station, represents what insiders call the greatest achievement in genetic science. The company has refused media access, citing concerns about the animals wellbeing."),
    ("FK-16", "New study finds drinking coffee reverses all effects of aging in the brain", "A landmark study from Harvard Medical School has concluded that drinking four or more cups of coffee daily can fully reverse age-related cognitive decline and even regrow neural connections lost over decades. Participants in their 70s reportedly scored equivalent to 25-year-olds on memory tests after just 90 days. The FDA is said to be fast-tracking coffee as a prescription treatment for dementia."),
    ("FK-17", "Worlds richest man secretly purchases Antarctica and declares it independent nation", "Legal filings obtained by an independent journalist reportedly show that a prominent billionaire has purchased the entirety of Antarctica through a series of shell companies and filed for recognition as a sovereign nation with the United Nations. The new nation, tentatively called Terra Nova, would theoretically be exempt from international environmental treaties currently protecting the continent."),
    ("FK-18", "Leaked memo reveals smartphones automatically record all conversations and sell to advertisers", "An internal document allegedly leaked from a major smartphone manufacturer confirms that all microphones are active at all times, even when devices appear to be off. The audio is reportedly processed by AI to extract purchase intent data, which is then sold to a consortium of advertising firms. Three former employees are said to have signed NDAs preventing them from testifying before Congress."),
    ("FK-19", "Countrys entire national debt erased overnight by anonymous crypto transfer", "Greeces finance ministry has reportedly confirmed that its entire national debt of approximately 350 billion euros was anonymously paid off via a series of untraceable cryptocurrency transactions overnight. Officials are said to be uncertain whether to accept the funds due to concerns about money laundering laws. The IMF has called an emergency meeting to address the unprecedented event."),
    ("FK-20", "New airport body scanners can read thoughts, TSA documents reveal", "Documents obtained via a Freedom of Information Act request allegedly show that next-generation airport security scanners installed at 14 major US airports are capable of detecting cognitive threat patterns by analyzing brainwave activity. Civil liberties groups claim the scanners have already been used to flag travelers for secondary screening based purely on their thoughts during the scan."),
]

print("=" * 80)
print("  TRUTHGUARD AI - DETECTION TEST (20 Articles)")
print("=" * 80)

pass_count = 0
fail_count = 0

print()
print("-" * 80)
print("  REAL NEWS (Expected: REAL)")
print("-" * 80)
for sid, headline, body in real_news:
    r = det.analyze(headline=headline, body=body)
    v = r["verdict"]
    c = r["confidence"]
    ok = (v == "REAL")
    if ok: pass_count += 1
    else: fail_count += 1
    icon = "PASS" if ok else "FAIL"
    print(f"  [{sid}] {icon} | Expected: REAL | Got: {v} ({c:.1f}%)")
    print(f"         {headline[:70]}")
    u = r.get("signals", {}).get("unverified_claims", {})
    a = r.get("signals", {}).get("factual_authority", {})
    if u.get("unverified_phrases"):
        print(f"         Hedge words: {u['unverified_phrases']}")
    if a.get("authorities_found"):
        print(f"         Authorities: {a['authorities_found'][:5]}")
    print()

print("-" * 80)
print("  FAKE NEWS (Expected: FAKE)")
print("-" * 80)
for sid, headline, body in fake_news:
    r = det.analyze(headline=headline, body=body)
    v = r["verdict"]
    c = r["confidence"]
    ok = (v == "FAKE")
    if ok: pass_count += 1
    else: fail_count += 1
    icon = "PASS" if ok else "FAIL"
    print(f"  [{sid}] {icon} | Expected: FAKE | Got: {v} ({c:.1f}%)")
    print(f"         {headline[:70]}")
    u = r.get("signals", {}).get("unverified_claims", {})
    m = r.get("signals", {}).get("misinformation", {})
    if u.get("unverified_phrases"):
        print(f"         Hedge words: {u['unverified_phrases']}")
    if m.get("matched_keywords"):
        print(f"         Misinfo keywords: {m['matched_keywords']}")
    print()

total = pass_count + fail_count
acc = (pass_count / total * 100) if total else 0
print("=" * 80)
print(f"  SUMMARY: {pass_count}/{total} PASSED  |  Accuracy: {acc:.1f}%")
print("=" * 80)
