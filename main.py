# Import Modules
import postgre as db
import dataGopher as data
import config as cfg
import json
from psycopg2.extras import json as psycop_json
import time


def recordPortfolioToDb():
    c, con = db.getCursor()
    p = data.buildPortfolio(cfg.user['wallet_address'])

    pJson = json.dumps(p)
    print(time.time())
    sql_string = "INSERT INTO public.portfolio_history(portfoliodata, updatetime)\n"
    sql_string += "VALUES (%s, %s)"

    c.execute(sql_string, (pJson, time.time()))

    con.commit()
    c.close()


recordPortfolioToDb()
