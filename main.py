from bottle import route, run, template, static_file, request
import random
import json
import pymysql
import os

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
        {"option_id": 1, "option_text": "I fight it"},
        {"option_id": 2, "option_text": "I tell it that I just want to go home"},
        {"option_id": 3, "option_text": "I give him 10 coins"},
        {"option_id": 4, "option_text": "I run away quickly"}
    ]



    connection = pymysql.connect(host="us-cdbr-iron-east-04.cleardb.net",
                                 user="b4524ee2815b1d",
                                 password="2457d197",
                                 db="heroku_6b16247311a9cd6",
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
            question_id = result2["current_question"]
            print("the current question of the user is")
            print(question_id)

            sql3 = "SELECT question_text from questions where question_id='{}'".format(question_id)
            cursor.execute(sql3)
            result3 = cursor.fetchone()
            print(result3["question_text"])
            text = result3["question_text"]

            sql4 = "SELECT option_id,option_text from options where question_id='{}' ORDER BY option_id ASC".format(
                question_id)
            cursor.execute(sql4)
            result4 = cursor.fetchall()
            print(result4)

            next_steps_results = result4
            print(type(question_id))

            return json.dumps({"user": user_id,
                               "adventure": current_adv_id,
                               "current": current_story_id,
                               "text": text,
                               "image": "troll.png",
                               "options": next_steps_results,
                               "question": question_id,
                               "username": username
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
                               "question": 1,
                               "username": username
                               })


@route("/story", method="POST")
def story():
    user_id = request.POST.get("user")
    username = request.POST.get("username")

    current_adv_id = request.POST.get("adventure")
    next_story_id = request.POST.get("next")  # this is what the user chose - use it!
    question_id = request.POST.get("question_id")
    print("the current question is'{}'".format(question_id))
    print(next_story_id)
    end_game=False




    connection = pymysql.connect(host="us-cdbr-iron-east-04.cleardb.net",
                                 user="b4524ee2815b1d",
                                 password="2457d197",
                                 db="heroku_6b16247311a9cd6",
                                 charset="utf8",
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        if user_id == "null":
            sql7 = "SELECT user_id from users WHERE username='{}'".format(username)
            cursor.execute(sql7)
            result7 = cursor.fetchone()
            user_id = result7["user_id"]
            print(result7)

        sql = "SELECT next_question_id from options WHERE question_id='{}' and option_id='{}'".format(question_id,
                                                                                                      next_story_id)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result["next_question_id"])
        nq = result["next_question_id"]

        sql2 = "SELECT question_text from questions where question_id='{}'".format(result["next_question_id"])
        cursor.execute(sql2)
        result2 = cursor.fetchone()
        print(result2["question_text"])
        text = result2["question_text"]

        sql3 = "SELECT option_id,option_text from options where question_id='{}'".format(result["next_question_id"])
        cursor.execute(sql3)
        result3 = cursor.fetchall()

        sql6 = "SELECT * from users where user_id='{}'".format(user_id)
        cursor.execute(sql6)
        result6 = cursor.fetchone()
        print(result6)
        print(result6["gold_state"])
        print(result6["life_state"])

        ucoins = result6["gold_state"]
        ulife = result6["life_state"]

        print(ucoins)
        print(ulife)

        sql5 = "SELECT gold_change,life_change from options where question_id='{}' and option_id='{}'".format(
            question_id, next_story_id)
        cursor.execute(sql5)
        result5 = cursor.fetchone()
        print(result5)
        coins = result5["gold_change"]
        life = result5["life_change"]

        new_coins = ucoins - coins
        new_life = ulife - life
        print(new_coins)
        print(new_life)

        sql4 = "UPDATE users SET current_question='{}',gold_state='{}',life_state='{}' WHERE user_id='{}'".format(nq,
                                                                                                                  new_coins,
                                                                                                                  new_life,
                                                                                                                  user_id)
        cursor.execute(sql4)
        connection.commit()

        if result["next_question_id"]==9 or result["next_question_id"]==10:
            end_game=True
            sql7 = "UPDATE users SET current_question='{}',gold_state='{}',life_state='{}' WHERE user_id='{}'".format(1,10,100)
            cursor.execute(sql7)
            connection.commit()


        return json.dumps({"user": user_id,
                           "adventure": current_adv_id,
                           "question": nq,
                           "text": text,
                           "image": "choice.jpg",
                           "options": result3,
                           "coins": new_coins,
                           "life": new_life,
                           "loose":end_game
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
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



if __name__ == '__main__':
    main()
