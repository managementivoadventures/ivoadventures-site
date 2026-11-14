# Strona www.ivoadventures.pl - instrukcja dla Claude

Strona Iwony Kuziory (IvoAdventures): link in bio dla fanów + wpisy (blog) pod Google.
Prowadzi ją Kacper Kuziora (manager). Pisz do niego po polsku, krótko.

## Jak to działa
- Statyczna strona generowana skryptem `build.py` (Python, biblioteki: markdown, pyyaml).
- `python3 build.py` → `public/` (to idzie na stronę). `python3 build.py --preview --drafts` → `preview/` (podgląd offline, ze szkicami).
- Publikacja: push na `main` → GitHub Actions (`.github/workflows/deploy.yml`) buduje i wrzuca na GitHub Pages. Strona jest na żywo po 1-2 min.
- Domena: tylko `www.ivoadventures.pl` (CNAME w home.pl). Adres bez www NIE jest podpięty, bo rekord MX poczty wskazuje na główną domenę. Nigdy nie zmieniaj rekordów DNS głównej domeny ani MX/TXT.
- Edytor dla Kacpra i Ivo: Pages CMS (app.pagescms.org), konfiguracja w `.pages.yml`. Pliki edytowane tam i przez Claude to te same pliki, więc przed zmianą zawsze `git pull`.

## Gdzie co jest
- `site.json` - bio, liczby obserwujących, platformy, sekcja „Dla fanów Ivo” (kurs, kody rabatowe), stacje TV/radio z logo (`stations`), „Najnowsze występy” (`appearances`), popularne filmy YouTube (`videos`), kategorie.
- `posts/RRRR-MM-DD-slug.md` - wpisy. Frontmatter: `title`, `date`, `description` (opis do Google, ~150 znaków, z „Iwona Kuziora” i „IvoAdventures”), `category`, opcjonalnie `youtube` (ID filmu), `image`, `station` (polsat / tvn / jedynka / zet), `pinned`, `draft`.
- `pages/o-ivo.md` - strona „O Ivo”.
- `img/` - zdjęcia (`img/ivo.jpg` profilowe, `img/media/` logo stacji).
- `style.css` - wygląd: żółte tło #ffe14d, czarny tekst, białe przyciski z czarnym obrysem i cieniem, różowe akcenty #ff9ecb, fonty Fraunces + Inter.

## Zasady (obowiązkowe)
- Nigdy nie używaj półpauzy „–” ani pauzy „—”. Zawsze zwykły myślnik „-”.
- Nigdy nie publikuj numeru telefonu Kacpra (ani na stronie, ani w repo, ani w historii commitów). Kontakt tylko: management@ivoadventures.pl.
- Nie publikuj adresów (dom, kawiarnia, paczkomat). Paczki PR: marka pisze maila, adres podajemy w odpowiedzi.
- Materiały dla marek (statystyki, case studies, lista marek, media kit) NIE trafiają na stronę ani do repo - repo jest publiczne. Są w osobnej, prywatnej stronie dla marek i w PDF wysyłanym mailem.
- Przy każdym występie w TV/radiu pokazuj logo stacji (pole `station` + `stations` w site.json). Ludzie są wzrokowcami.
- Tylko prawdziwe fakty: występy, daty i opisy z oficjalnych źródeł (halotu.polsat.pl, dziendobry.tvn.pl, polskieradio.pl) albo od Kacpra. Niepewne rzeczy jako `draft: true` i zapytaj Kacpra. Pod wpisem z TV/radia link do źródła.
- Nie używaj kadrów z programów TV ani zdjęć z internetu - tylko zdjęcia od Kacpra/Ivo.
- Kody rabatowe oznacz jako współpraca reklamowa.

## Po każdej zmianie
1. `python3 build.py` i sprawdź: `grep -rl "–" public` (ma być pusto), brak numeru telefonu.
2. Commit + push na `main`.
3. Krótko napisz Kacprowi, co się zmieniło.
