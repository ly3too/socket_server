<?php

class MyDB extends SQLite3 {
      function __construct() {
         $this->open('test.db');
      }
   }
   
   $db = new MyDB();
   if(!$db) {
      echo $db->lastErrorMsg();
   }

   $sql =<<<EOF
      delete from datas;
EOF;

   $ret = $db->exec($sql);
   if(!$ret){
     echo $db->lastErrorMsg();
   } else {
      echo "all data cleared\n";
   }
?>
