<?php
require_once('mysql_config.php');
require_once('functions.php');

mb_language("uni");
mb_internal_encoding("utf-8");
mb_http_input("auto");
mb_http_output("utf-8");

$latest_id = 2147483647;
$limit = 10;
$search_word = '';
if(isset($_GET['latest_id'])){
  $latest_id = $_GET['latest_id'];
}
if(isset($_GET['limit'])){
  $limit = $_GET['limit'];
}
if(isset($_GET['search_word'])){
  $search_word = $_GET['search_word'];
}
$dbh = connect_db();

$sth = $dbh->prepare("SELECT * FROM navernow where id < ${latest_id} and text like '%${search_word}%' order by id desc limit ${limit}");
$sth->execute();

$userData = array();

while($row = $sth->fetch(PDO::FETCH_ASSOC)){
  $userData[]=array(
    'id'=>$row['id'],		
    'uri'=>$row['uri'],
    'title'=>$row['title'],
    'time'=>$row['time'],
    'text'=>$row['text'],
    'thumbnail'=>$row['thumbnail']
    );
}

header('Content-type: application/json');
echo json_encode($userData);
