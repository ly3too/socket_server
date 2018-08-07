<?php
   class MyDB extends SQLite3 {
      function __construct() {
      	 $iterator = new DirectoryIterator(dirname(__FILE__));
         $this->open($iterator->getPath(). '/test.db');
      }
   }
   
   $db = new MyDB();
   if(!$db) {
      echo $db->lastErrorMsg();
   }

   $sql =<<<EOF
      SELECT * from datas;
EOF;

	try{
	   $ret = $db->query($sql);
	   if (!$ret) {
	   		echo $db->lastErrorMsg();
	   		exit(1);
	   }
	   while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
		  echo "<tr>\n";
		    echo "<td>". $row['time'] ."</td>\n";
		    echo "<td>". $row['data']  ."</td>\n";
		  echo "</tr>\n";
	   }
	   $db->close();
	} catch (Exception $e) {
		echo "no data temporarily";
	}
?>
