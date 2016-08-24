from bottle import route, run, template, static_file, request
import random
import json
import pymysql
import os

# connection = pymysql.connect(host="us-cdbr-iron-east-04.cleardb.net",
#                              user="b69ece0fa2a81b",
#                              password="58cea4d5",
#                              db="heroku_d958e16ebe26a90",
#                              charset="utf8",
#                              cursorclass=pymysql.cursors.DictCursor)


connection = pymysql.connect(host="localhost",
                             user="root",
                             password="",
                             db="adventure",
                             charset="utf8",
                             cursorclass=pymysql.cursors.DictCursor)

@route("/", method="GET")
def index():
    return template("adventure.html")
#
# def selectUserInfo(username):
#     with connection.cursor() as cursor:
#         sql = "SELECT * FROM users WHERE var1=%s"% (username)
#         # sql = """SELECT ValA FROM %s WHERE Val2 = %s AND Val3 = %s""" % (Val1, Val2, Val3)
#         cursor.execute(sql,username)
#         user_info = cursor.fetchone()
#         print(user_info)
#         return user_info

# def selectUserInfo(variable, instance):
#     with connection.cursor() as cursor:
#         sql = "SELECT * FROM users WHERE '{0}'='{1}'".format(variable, instance)
#         cursor.execute(sql)
#         user_info = cursor.fetchone()
#         print(user_info)
#         return user_info

def selectAllUserInfoFromName(username):
    with connection.cursor() as cursor:
        sql = "SELECT * from users where username='{}'".format(username)
        cursor.execute(sql)
        user_info = cursor.fetchone()
        print(user_info)
        return user_info

def selectAllUserInfoFromID(user_id):
    with connection.cursor() as cursor:
        sql = "SELECT * from users where user_id='{}'".format(user_id)
        cursor.execute(sql)
        user_info = cursor.fetchone()
        print(user_info)
        return user_info

def selectCurrentQuestion(user_id):
    with connection.cursor() as cursor:
        sql2 = "SELECT current_question FROM users WHERE user_id='{}'".format(user_id)
        cursor.execute(sql2)
        cq = cursor.fetchone()
        question_id = cq["current_question"]
        print("the current question of the user is")
        print(question_id)
        return question_id

def selectQuestionText(question_id):
    with connection.cursor() as cursor:
        sql3 = "SELECT question_text from questions where question_id='{}'".format(question_id)
        cursor.execute(sql3)
        result3 = cursor.fetchone()
        text = result3["question_text"]
        print(text)
        return text



def selectQuestionOptions(question_id):
    with connection.cursor() as cursor:
        sql4 = "SELECT option_id,option_text from options where question_id='{}' ORDER BY option_id ASC".format(
            question_id)
        cursor.execute(sql4)
        result4 = cursor.fetchall()
        print(result4)
        return result4

def selectNextQuestionId(question_id,next_story_id):
    with connection.cursor() as cursor:
        sql = "SELECT next_question_id from options WHERE question_id='{}' and option_id='{}'".format(question_id,
                                                                                                      next_story_id)

        cursor.execute(sql)
        result = cursor.fetchone()
        print(result["next_question_id"])
        nq = result["next_question_id"]
        return nq

def selectGoldLifeChanges(question_id,next_story_id):
    with connection.cursor() as cursor:
        sql5 = "SELECT gold_change,life_change from options where question_id='{}' and option_id='{}'".format(
            question_id, next_story_id)
        cursor.execute(sql5)
        result5 = cursor.fetchone()
        print(result5)
        return result5

def updateUserInfo(nq,new_coins,new_life,user_id):
    with connection.cursor() as cursor:
        sql4 = "UPDATE users SET current_question='{}',gold_state='{}',life_state='{}' WHERE user_id='{}'".format(nq,
                                                                                                                  new_coins,
                                                                                                                  new_life,
                                                                                                                  user_id)


        cursor.execute(sql4)
        connection.commit()

@route("/start", method="POST")
def start():
    username = request.POST.get("user")
    current_adv_id = request.POST.get("adventure")
    print(username)
    current_story_id = 0



    with connection.cursor() as cursor:

        # user_info=selectUserInfo("username",username)
        user_info=selectAllUserInfoFromName(username)
        print(user_info)

        if user_info:
            print("in")
            print(user_info)
            user_id = user_info["user_id"]
            print(user_id)

            question_id=selectCurrentQuestion(user_id)
            text=selectQuestionText(question_id)
            next_steps_results = selectQuestionOptions(question_id)
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


            text=selectQuestionText(1)
            options=selectQuestionOptions(1)

            return json.dumps({"user": user_id,
                               "adventure": current_adv_id,
                               "current": current_story_id,
                               "text": text,
                               "image": "troll.png",
                               "options": options,
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

    with connection.cursor() as cursor:
        if user_id == "null":
            user_id=selectAllUserInfoFromName(username)["user_id"]

        nq=selectNextQuestionId(question_id,next_story_id)
        text=selectQuestionText(nq)
        options=selectQuestionOptions(nq)
        user_info=selectAllUserInfoFromID(user_id)
        ucoins = user_info["gold_state"]
        ulife = user_info["life_state"]

        print(ucoins)
        print(ulife)


        coins = selectGoldLifeChanges(question_id,next_story_id)["gold_change"]
        life = selectGoldLifeChanges(question_id,next_story_id)["life_change"]

        new_coins = ucoins - coins
        new_life = ulife - life
        print(new_coins)
        print(new_life)
        updateUserInfo(nq,new_coins,new_life,user_id)


        if int(question_id)==9 or int(question_id)==10:
            end_game=True
            print(end_game)
            print("in")
            sql7 = "UPDATE users SET current_question='{}',gold_state='{}',life_state='{}' WHERE user_id='{}'".format(1,10,100,user_id)
            cursor.execute(sql7)
            connection.commit()




        return json.dumps({"user": user_id,
                           "adventure": current_adv_id,
                           "question": nq,
                           "text": text,
                           "image": "choice.jpg",
                           "options": options,
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
    # run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    run(host="localhost",port="9000")

if __name__ == '__main__':
    main()
