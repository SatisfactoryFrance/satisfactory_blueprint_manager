import os
import re
import requests
from bs4 import BeautifulSoup


class ScimService:

    BASE_URL = "https://satisfactory-calculator.com/fr/blueprints"

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    # ======================================================
    # LISTING
    # ======================================================

    def extract_pagenumber(self, url:str):
        return int(re.search("p/([0-9]+)",url).group(1))
    
    def get_blueprints(self, page: int, query: str = ""):

        url = f"{self.BASE_URL}/index/index/p/{page}"
        if query:
            url += f"/query/{requests.utils.quote(query)}"
        response = requests.get(url, headers=self.headers, timeout=15)

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("div", class_="card-body")

        pagination = soup.find("ul", class_="pagination")
        if (pagination is None):
            pagination_maxpage = 1
        else:
            pagination_maxpage = self.extract_pagenumber(pagination.find_all("li")[-1].find("a").get("href", "p/0"))

        results = type('',(object,),{"items": [],"maxPage":pagination_maxpage})()

        for card in cards:

            link = card.find("a", href=True)
            if not link:
                continue

            # title
            h6 = card.find("h6")
            strong = h6.find("strong") if h6 else None
            title = strong.get_text(strip=True) if strong else "Untitled"

            href = link.get("href", "")
            if "/id/" not in href:
                continue

            blueprint_id = href.split("/id/")[1].split("/")[0]

            # image
            img_tag = link.find("img")
            img_url = img_tag["src"] if img_tag else None

            image_bytes = None
            if img_url:
                try:
                    image_bytes = requests.get(img_url, headers=self.headers, timeout=10).content
                except:
                    pass

            # description = self.get_description(blueprint_id)
            

            results.items.append({
                "id": blueprint_id,
                "title": title,
                "description": None,
                "image": image_bytes,
                "url": f"{self.BASE_URL}/index/details/id/{blueprint_id}"
            })

        return results

    # ======================================================
    # DOWNLOAD
    # ======================================================

    def download_blueprint(self, blueprint_id, title, target_folder):

        base = f"{self.BASE_URL}/index/download"

        sbp_url = f"{base}/id/{blueprint_id}"
        cfg_url = f"{base}-cfg/id/{blueprint_id}"

        safe = self.sanitize_filename(title)

        sbp_path = os.path.join(target_folder, f"{safe}.sbp")
        cfg_path = os.path.join(target_folder, f"{safe}.sbpcfg")

        if os.path.exists(sbp_path):
            raise Exception("Blueprint already exists")

        sbp = requests.get(sbp_url, headers=self.headers, timeout=15)
        cfg = requests.get(cfg_url, headers=self.headers, timeout=15)

        if sbp.status_code != 200 or cfg.status_code != 200:
            raise Exception("Download error")

        with open(sbp_path, "wb") as f:
            f.write(sbp.content)

        with open(cfg_path, "wb") as f:
            f.write(cfg.content)

        return safe

    # ======================================================
    # TROUVER LA DESCRIPTION
    # ======================================================

    def get_description(self, blueprint_id):

        url = f"{self.BASE_URL}/index/details/id/{blueprint_id}"
        response = requests.get(url, headers=self.headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        for bq in soup.find_all("blockquote"):
            txt = bq.get_text(strip=True)
            if txt:
                return " ".join(txt.split()[:150]) + "..."

        return "Pas de description"

    # ======================================================
    # HELPERS
    # ======================================================

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', "_", name)
