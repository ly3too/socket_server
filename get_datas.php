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
      SELECT * from datas;
EOF;

   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
      echo "<tr>\n";
        echo "<td>". $row['time'] ."</td>\n";
        echo "<td>". $row['data']  ."</td>\n";
      echo "</tr>\n";
   }
   $db->close();
?>
