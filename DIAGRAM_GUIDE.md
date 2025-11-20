# Diagram Generation Guide

Tämä projektin kaavio avataan ja muokataan draw.io / diagrams.net -editorissa. Alla on reunaehdot seuraaville AI-avustajille tai työkaluajoille, jotta tuotettu XML toimii suoraan editorissa ilman lisäkorjauksia.

## 1. Tiedostomuoto
- **Käärintä:** Kaikki mallit pitää toimittaa `mxfile`-juurielementissä. Sisälle tulee vähintään yksi `<diagram>`-elementti, jonka sisällä varsinainen `<mxGraphModel>` asuu (katso `diagram.xml`).
- **Meta-atribuutit:** `mxfile` tarvitsee vähintään attribuutit `host`, `modified`, `agent`, `etag`, `version` ja `type`. Arvoilla ei ole tiukkaa validointia, mutta ne helpottavat editoria.
- **Rakenteen järjestys:** `mxGraphModel > root` pitää aina aloittaa solmuilla `id="0"` ja `id="1"`. Kaikki muut vertexit tai edget viittaavat `parent="1"` tai muuhun olemassa olevaan konttiin.

## 2. Solmut ja id:t
- Jokaisella `mxCell`-solmulla on yksilöllinen `id`. Käytä kuvaavia nimiä (esim. `widget`, `api`, `genai`).
- Vertexit (`vertex="1"`) vaativat sisäisen `mxGeometry`-elementin, jossa on `x`, `y`, `width`, `height`.
- Edge-solmut (`edge="1"`) viittaavat lähteeseen ja kohteeseen `source`- ja `target`-attribuuteilla. Käytä `mxGeometry relative="1"` -muotoa ellei ole erityistä reititystarvetta.

## 3. Groupit ja hierarkia
- Kontit kuten "Azure AI Foundry" toteutetaan vertexinä, jonka lapset määritetään `parent`-attribuutilla viittaamaan konttiin (`parent="foundry_group"`).
- Kaikki ryhmän sisäiset elementit käyttävät ryhmän paikallista koordinaatistoa (0,0 kontissa).

## 4. Tyylit ja värit
- Käytä valmiita draw.io-tyyliavaimia kuten `shape`, `rounded`, `whiteSpace`, `html`, `fillColor`, `strokeColor` jne.
- Pidä nykyinen väripaletti:
  - Sinertävä (`#dae8fc` / `#6c8ebf`) käyttöliittymä- ja API-kerrokselle.
  - Vihertävä (`#d5e8d4` / `#82b366`) hakukomponenteille.
  - Violetin sävy (`#e1d5e7` / `#9673a6`) GenAI-kerrokselle.
  - Punainen kilpi (`#f8cecc` / `#b85450`) Content Safety -solmulle.
  - Muistilaput ja muistiinpanot `shape=note` + harmaa tausta.

## 5. Sivuasettelu
- Nykyinen piirros käyttää `pageWidth="1200"` ja `pageHeight="900"`. Jos tuot uusi kaavio, pysy lähellä näitä arvoja, jotta iframe-näkymä toimii.
- Elementit on tasattu 50–150 px marginaaleilla ja kulkevat päälinjana vasemmalta oikealle. Uusien komponenttien olisi hyvä noudattaa samaa kulkusuuntaa.

## 6. Vienti ja validointi
- Muista, että selainpohjainen editori lukee XML:n sellaisenaan ilman palvelinta. Älä lisää ulkoisia riippuvuuksia tai kommentteja, jotka rikkovat `mxfile`-rakennetta.
- Tarkista paikallisesti `python3 validate_xml.py` varmistaaksesi XML-syntaksin ennen editoriin lataamista.

Kun nämä ehdot täyttyvät, `diagram.xml` voidaan liittää suoraan `index.html`-tiedoston `diagramXML`-muuttujaan tai tuoda editoriin `File > Import From...` -toiminnolla ilman virheilmoituksia.
