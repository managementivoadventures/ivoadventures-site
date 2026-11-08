# ivoadventures.pl – strona + aktualności

Prosta statyczna strona (bez WordPressa, bez bazy danych): link in bio + blog „Aktualności”.

## Jak dodać wpis
1. Nowy plik w `posts/`, nazwa: `RRRR-MM-DD-krotki-adres.md` (adres = końcówka URL-a).
2. Na górze:
   ```
   ---
   title: Ivo w Programie 1 Polskiego Radia
   date: 2026-11-20
   description: 1–2 zdania do Google (ok. 150 znaków), z „Iwona Kuziora” i „IvoAdventures”.
   category: Radio
   image: img/radio-2026-11.jpg   (opcjonalnie)
   draft: tak                      (opcjonalnie – ukrywa wpis)
   ---
   ```
3. Treść w Markdown (`## nagłówek`, `- lista`, `**pogrubienie**`, `[link](https://...)`).
4. `python3 build.py` → gotowa strona w `public/`.

Albo po prostu napisz do Claude: „dodaj wpis: Ivo była w …”.

## Zdjęcia
Wrzuć do `img/`. Zdjęcie profilowe: `img/ivo.jpg` i w `site.json` ustaw `"photo": "img/ivo.jpg"`.

## SEO (już wbudowane)
- dane strukturalne Person (Iwona Kuziora = IvoAdventures + profile społecznościowe) i BlogPosting,
- sitemap.xml, robots.txt, canonical, Open Graph (ładne podglądy linków na FB/Messengerze).
- Po publikacji: dodać domenę w Google Search Console i zgłosić `https://ivoadventures.pl/sitemap.xml`.
- Wpisać `https://ivoadventures.pl` jako stronę w bio IG/TikTok/YT/FB – to wzajemne linkowanie pomaga Google powiązać profile.

## Hosting
Zawartość `public/` wrzuca się na dowolny hosting (GitHub Pages / Netlify / Cloudflare Pages za darmo albo FTP u obecnego dostawcy domeny). Plik `CNAME` jest dla GitHub Pages.
