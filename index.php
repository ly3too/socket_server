<!DOCTYPE html>
<html lang="en">
<head>
  <title>socket server Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="/statics/bootstrap.min.css">
  <script src="/statics/jquery.min.js"></script>
  <script src="/statics/bootstrap.min.js"></script>
  
 <script>
$(document).ready(function(){
    $("#send_message").click(function(){
        $.get("send_message.php?message=" + $("#data").val(),
        function (data, status) {
        	$("#div1").html(data);
        });
    });
    
    var $container = $("#values");
    $container.load("get_datas.php");
    var refreshId = setInterval(function()
    {
        $container.load('get_datas.php');
    }, 3000);
    
    $("#clear").click(function(){
        $.get("clear_data.php",
        function (data, status) {
        	$("#div2").html(data);
        	$container.load("get_datas.php");
        });
    });
});
</script>

</head>

<body>
<div class="container">
  <h2> data from clients </h2>
  <table class="table" id="table1">
    <thead>
      <tr>
        <th>time</th>
        <th>data</th>
      </tr>
    </thead>
    <tbody id="values">
   
    </tbody>
  </table>
  
  <div id="clear" class="btn btn-default">clear all</div>
  <p id="div2"></p>
</div>

<div class="container">
  <h2> send message to clients </h2>
  <form>
    <div class="form-group">
      <label > enter message here: </label>
      <input class="form-control" id="data" placeholder="edit here" name="data">
    </div>
       <div id="send_message" class="btn btn-default">send</div>
       <p id="div1"> </p>
  </form>
</div>

</body>
</html>

