import arxivscraper
import datetime
import time
import requests
import json
from datetime import timedelta

isEmpty = True

def get_daily_code(DateToday, cats):
    """
    @param DateToday: str
    @param cats: dict
    @return paper_with_code: dict
    """
    global isEmpty
    # from_day = until_day = DateToday
    from_day = until_day = '2024-08-21'
    content = dict()
    # content
    output = dict()
    for k,v in cats.items():
        scraper = arxivscraper.Scraper(category=k, date_from=from_day,date_until=until_day)
        tmp = scraper.scrape()
        if isinstance(tmp,list):
            for item in tmp:
                if item["id"] not in output:
                    # print(v, item["categories"], [(x in v) for x in item["categories"]])
                    if any([(x in item["categories"]) for x in v]):
                        output[item["id"]] = item
            isEmpty = False
        time.sleep(10)
    base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"
    cnt = 0

    for k,v in output.items():
        _id = v["id"]
        paper_title = " ".join(v["title"].split())
        paper_url = v["url"]
        paper_abs = v["abstract"]
        url = base_url + _id
        try:
            r = requests.get(url).json()
            if "official" in r and r["official"]:
                cnt += 1
                repo_url = r["official"]["url"]
                repo_name = repo_url.split("/")[-1]
                content[_id] = f"[{paper_title}]({paper_url}), {repo_name}\n\n"
        except Exception as e:
            print(f"exception: {e} with id: {_id}")
    return content

def update_daily_json(filename,data_all):
    with open(filename,"r") as f:
        content = f.read()
        if not content:
            m = {}
        else:
            m = json.loads(content)
    
    #将datas更新到m中
    for data in data_all:
        m.update(data)

    # save data to daily.json

    with open(filename,"w") as f:
        json.dump(m,f)
    



def json_to_md(filename):
    """
    @param filename: str
    @return None
    """

    with open(filename,"r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)
    # clean README.md if daily already exist else creat it
    with open("README.md","w+") as f:
        pass
    # write data into README.md
    with open("README.md","a+") as f:
        # 对data数据排序
        for day in sorted(data.keys(),reverse=True):
            day_content = data[day]
            if not day_content:
                continue
            # the head of each part
            f.write(f"## {day}\n")
            f.write("|paper|code|\n" + "|---|---|\n")
            for k,v in day_content.items():
                f.write(v)
    
    print("finished")        

if __name__ == "__main__":

    DateToday = datetime.date.today()
    N = 2 # 往前查询的天数
    data_all = []
    day = str(DateToday + timedelta(-1))
        # you can add the categories in cats
    cats = {
        # "eess":["eess.SP"],
        "cs":["cs.cv", "cs.gr", "cs.hc", "cs.ai"],
        "physics":["physics.comp-ph"]
    }
    data = get_daily_code(day,cats)
    print(data)
    res = ""
    for k, v in data.items():
        res += v
    with open("daily_out.md", "w") as f:
        if isEmpty:
            f.write("今天是休假喵~")
        else:
            f.write(json.dumps(res))
    # update_daily_json("daily.json",data_all)
    # json_to_md("daily.json")
