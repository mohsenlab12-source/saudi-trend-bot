def get_trends(city="saudi-arabia"):
    try:
        url = "https://getdaytrends.com/saudi-arabia/riyadh/" if city=="riyadh" else "https://getdaytrends.com/saudi-arabia/"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('table tr td a')
        clean = []
        for t in trends:
            txt = t.text.strip()
            if txt and txt not in clean: clean.append(txt)
            if len(clean)>=15: break
        
        city_name = {"saudi-arabia":"Saudi Arabia","riyadh":"Riyadh","jeddah":"Jeddah"}[city]
        
        # \u200e يجبر تليجرام يقرأ من اليسار لليمين
        msg = f"\u200e🇸🇦 Trend {city_name} Now\n"
        msg += "\u200e━━━━━━━━━━━━━━\n"
        for i, name in enumerate(clean, 1):
            msg += f"\u200e{i}. {name}\n"
        msg += "\u200e━━━━━━━━━━━━━━"
        return msg
    except Exception as e:
        return f"Error: {e}"
