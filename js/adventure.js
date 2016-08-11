var Adventures = {};
//currentAdventure is used for the adventure we're currently on (id). This should be determined at the beginning of the program
Adventures.currentAdventure = 0;
//currentStep is used for the step we're currently on (id). This should be determined at every crossroad, depending on what the user chose
Adventures.currentStep = 0;//todo keep track from db
Adventures.currentUser = 0;
Adventures.currentQuestion = 0;
Adventures.coinStatus = 10;
Adventures.lifeStatus = 100;
Adventures.username="";
Adventures.winOrLOOSE=false;


//TODO: remove for production
Adventures.debugMode = true;
Adventures.DEFAULT_IMG = "./images/choice.jpg";


//Handle Ajax Error, animation error and speech support
Adventures.bindErrorHandlers = function () {
    //Handle ajax error, if the server is not found or experienced an error
    $(document).ajaxError(function (event, jqxhr, settings, thrownError) {
        Adventures.handleServerError(thrownError);
    });

    //Making sure that we don't receive an animation that does not exist
    $("#situation-image").error(function () {
        Adventures.debugPrint("Failed to load img: " + $("#situation-image").attr("src"));
        Adventures.setImage(Adventures.DEFAULT_IMG);
    });
};


//The core function of the app, sends the user's choice and then parses the results to the server and handling the response
Adventures.chooseOption = function () {
    Adventures.currentStep = $(this).val();
    $.ajax("/story", {
        type: "POST",
        data: {
            "user": Adventures.currentUser,
            "adventure": Adventures.currentAdventure,
            "next": Adventures.currentStep,
            "question_id": Adventures.currentQuestion,
            "coins":Adventures.coinStatus,
            "life":Adventures.lifeStatus,
            "username":Adventures.username
            
        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            $(".greeting-text").hide();
            Adventures.write(data);
            Adventures.currentQuestion = data["question"];
            console.log(Adventures.currentQuestion);
            Adventures.coinStatus=data.coins;
            console.log(Adventures.coinStatus);
            Adventures.lifeStatus=data.life;
            console.log(Adventures.lifeStatus);
            $("#coins").text(Adventures.coinStatus);
            $('#life').text(Adventures.lifeStatus);
            Adventures.winOrLOOSE=data.loose;
            console.log(Adventures.winOrLOOSE);
            Adventures.restart();
            
        }
    });
};

Adventures.write = function (message) {
    //Writing new choices and image to screen
    $(".situation-text").text(message["text"]).show();
    for (var i = 0; i < message['options'].length; i++) {
        var opt = $("#option_" + (i + 1));
        opt.text(message['options'][i]['option_text']);
        opt.prop("value", message['options'][i]['option_id']);
    }
    Adventures.setImage(message["image"]);
};


Adventures.start = function () {
    $(document).ready(function () {
        $(".game-option").click(Adventures.chooseOption);
        $("#nameField").keyup(Adventures.checkName);
        $(".adventure-button").click(Adventures.initAdventure);
        $(".adventure").hide();
        $(".welcome-screen").show();
        $("#coins").text(Adventures.coinStatus);
        $('#life').text(Adventures.lifeStatus);

    });
};

Adventures.restart=function(){
    if (Adventures.winOrLOOSE) {
        alert("going toreload")
        location.reload();
    }
};

Adventures.updateCoinsAndLifes=function(coin,life){
    Adventures.coinStatus=Adventures.coinStatus-coin;
    Adventures.lifeStatus=Adventures.lifeStatus-life;
    
};
//Setting the relevant image according to the server response
Adventures.setImage = function (img_name) {
    $("#situation-image").attr("src", "./images/" + img_name);
};

Adventures.checkName = function () {
    if ($(this).val() !== undefined && $(this).val() !== null && $(this).val() !== "") {
        $(".adventure-button").prop("disabled", false);
    }
    else {
        $(".adventure-button").prop("disabled", true);
    }
};


Adventures.initAdventure = function () {

    $.ajax("/start", {
        type: "POST",
        data: {
            "user": $("#nameField").val(),
            "adventure_id": $(this).val(),
            "coins":Adventures.coinStatus,
            "life":Adventures.lifeStatus,

        },
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            Adventures.write(data);
            $(".adventure").show();
            $(".welcome-screen").hide();
            Adventures.currentUser = data.user;
            Adventures.currentAdventure = data.adventure;
            Adventures.currentQuestion = data["question"];
            Adventures.username=data.username;
            console.log(Adventures.currentQuestion);
            // Adventures.updateCoinsAndLifes(data.coin,data.life);
        }
    });
};

Adventures.handleServerError = function (errorThrown) {
    Adventures.debugPrint("Server Error: " + errorThrown);
    var actualError = "";
    if (Adventures.debugMode) {
        actualError = " ( " + errorThrown + " ) ";
    }
    Adventures.write("Sorry, there seems to be an error on the server. Let's talk later. " + actualError);

};

Adventures.debugPrint = function (msg) {
    if (Adventures.debugMode) {
        console.log("Adventures DEBUG: " + msg)
    }
};

Adventures.start();

