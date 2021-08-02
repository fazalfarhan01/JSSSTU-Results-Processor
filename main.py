import requests as r
from bs4 import BeautifulSoup
import sqlite3

URL = "http://results.jssstuniv.in/check.php"

conn = sqlite3.connect("results.db")

def createTable(conn):
    if not len(conn.execute(
  """SELECT name FROM sqlite_master WHERE type='table'
  AND name='RESULTS'; """).fetchall()) > 0:
        conn.execute("""CREATE TABLE RESULTS 
        (NAME TEXT NOT NULL,
        USN TEXT NOT NULL,
        EC610 CHAR(20),
        EC620 CHAR(20),
        EC660 CHAR(20),
        EC640 CHAR(20),
        EC67L CHAR(20),
        HU68S CHAR(20),
        EC651 CHAR(20),
        EC662 CHAR(20),
        SGPA FLOAT);
        """)
        print("Table created")
        conn.commit()
    else:
        print("Table exists")

def getResults(usn):
    parameters = {
        "USN": usn
    }
    response = r.post(url=URL, data=parameters)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, "html.parser")
            name = soup.find_all("h1")[0].text
            grades = []
            tables = soup.find_all('table')
            marksTable = tables[0]
            rows = marksTable.find_all("tr")
            for row in rows:
                columns = row.find_all("td")
                if len(columns) > 0:
                    grades.append([content.text for content in columns][:][-1])
            return [usn, name, grades]
        except:
            return -1
    return response.status_code

def addDataToDB(conn, result):
    usn = result[0]
    name = result[1]
    grades = result[2]
    sgpa = result[-1]
    query = """INSERT INTO RESULTS VALUES ("{}", "{}","{}",{});""".format(name,usn,'","'.join([grade.strip() for grade in grades]),sgpa)
    conn.execute(query)

def calculateSGPA(result):
    grades = result[2]
    weights = {
        "S":10,
        "A":9,
        "B":8,
        "C":7,
        "D":5,
        "E":4
    }
    scores = []
    for grade in grades:
        scores.append(weights.get(grade.strip(), 0))
    credits = [4,4,4,4,1,2,3,3]
    return sum(a*b for a,b in zip(scores, credits))/sum(credits)

if __name__ == "__main__":
    createTable(conn)
    for j in range(4):
        for i in range(j*50,j*50+50):
            usn = "01JST18EC{0:03}".format(i)
            print("Getting USN: {}".format(usn))
            result = getResults(usn)
            if result == -1:
                print("Result not Found. :(")
                continue
            result.append(calculateSGPA(result))
            addDataToDB(conn, result)
        conn.commit()

    # result = getResults("01JST18EC055")
    # result.append(calculateSGPA(result))
    # print(result)
    conn.close()