<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
    <script src="js/survey.jquery.min.js"></script>
    <link href="css/survey.css" type="text/css" rel="stylesheet" />
  </head>
  <body>
    <div id="surveyContainer"></div>
    <script>    
        var surveyJSON;
        var survey;
        
        $.getJSON( "json/questions.json", function(data) {
            surveyJSON = data;
        })
        .done(function() {
            survey = new Survey.Model(surveyJSON);
            $("#surveyContainer").Survey({
            model: survey,
            onComplete: sendDataToServer
        });
        });

        function sendDataToServer(survey) {
            //send Ajax request to your web server.
            //alert("The results are:" + JSON.stringify(survey.data));
            $.post( "/posttest", JSON.stringify(survey.data) );
        }

    </script>
  </body>
</html>
