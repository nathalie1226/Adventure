from bottle import route, run, template, static_file, request
import random
import json
import pymysql


@route("/", method="GET")
def index():
    return template("adventure.html")


@route("/start", method="POST")
def start():
    username = request.POST.get("user")
    current_adv_id = request.POST.get("adventure")
    print(username)
    current_story_id = 0
    next_steps_results = [
        {"id": 1, "option_text": "I fight it"},
        {"id": 2, "option_text": "I give him 10 coins"},
        {"id": 3, "option_text": "I tell it that I just want to go home"},
        {"id": 4, "option_text": "I run away quickly"}
    ]

    connection = pymysql.connect(host="localhost",
                                 user="root",
                                 password="",
                                 db="adventure",
                                 charset="utf8",
                                 cursorclass=pymysql.cursors.DictCursor)


    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE username='{}'".format(username)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)


        if result:
            print("in")
            user_id = result["user_id"]
            print(user_id)
            sql2 = "SELECT current_question FROM users WHERE user_id='{}'".format(user_id)
            cursor.execute(sql2)
            result2 = cursor.fetchone()
            question_id=result2["current_question"]

            sql3 = "SELECT question_text from questions where question_id='{}'".format(question_id)
            cursor.execute(sql3)
            result3 = cursor.fetchone()
            print(result3["question_text"])
            text = result3["question_text"]

            sql4 = "SELECT option_id,option_text from options where question_id='{}'".format(question_id)
            cursor.execute(sql4)
            result4 = cursor.fetchall()
            print(result4)

            next_steps_results=result4
            print(type(question_id))

            # sql = "SELECT next_question_id from options WHERE question_id='{}' and option_id='{}'".format(question_id,
            #                                                                                               next_story_id)
            # cursor.execute(sql)
            # result = cursor.fetchone()
            # print(result["next_question_id"])
            # nq = result["next_question_id"]
            # print("the new question will be'{}'".format(nq))

            return json.dumps({"user": user_id,
                               "adventure": current_adv_id,
                               "current": current_story_id,
                               "text":text,
                               "image": "troll.png",
                               "options": next_steps_results,
                               "question":question_id
                               })
        else:
            sql = "INSERT INTO users(`username`) VALUES (%s)"
            cursor.execute(sql, username)
            connection.commit()
            user_id = "null"
            return json.dumps({"user": user_id,
                               "adventure": current_adv_id,
                               "current": current_story_id,
                               "text": "You meet a mysterious creature in the woods, what do you do?",
                               "image": "troll.png",
                               "options": next_steps_results,
                               "question":1
                               })







@route("/story", method="POST")
def story():
    user_id = request.POST.get("user")
    current_adv_id = request.POST.get("adventure")
    next_story_id = request.POST.get("next")#this is what the user chose - use it!
    question_id=request.POST.get("question_id")
    print("the current question is'{}'".format(question_id))

    connection = pymysql.connect(host="localhost",
                                 user="root",
                                 password="",
                                 db="adventure",
                                 charset="utf8",
                                 cursorclass=pymysql.cursors.DictCursor)


    with connection.cursor() as cursor:
        sql = "SELECT next_question_id from options WHERE question_id='{}' and option_id='{}'".format(question_id,next_story_id)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result["next_question_id"])
        nq=result["next_question_id"]

        sql2="SELECT question_text from questions where question_id='{}'".format(result["next_question_id"])
        cursor.execute(sql2)
        result2 = cursor.fetchone()
        print(result2["question_text"])
        text=result2["question_text"]

        sql3="SELECT * from options where question_id='{}'".format(result["next_question_id"])
        cursor.execute(sql3)
        result3 = cursor.fetchall()
        print(result3)
        print("the new question will be'{}'".format(nq))

        sql4="UPDATE users SET current_question='{}' WHERE user_id='{}'".format(nq,user_id)
        cursor.execute(sql4)
        connection.commit()

        return json.dumps({"user": user_id,
                       "adventure": current_adv_id,
                       "question":nq,
                       "text": text,
                       "image": "choice.jpg",
                       "options": result3
                       })

@route('/js/<filename:re:.*\.js$>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')

def main():
    run(host='localhost', port=9000)

if __name__ == '__main__':
    main()

