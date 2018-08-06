<?php
$address = gethostbyname('localhost');
$service_port = 8001;

/* Create a TCP/IP socket. */
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "socket_create() failed: reason: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}

$result = socket_connect($socket, $address, $service_port);
if ($result === false) {
    echo "socket_connect() failed.\nReason: ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
    exit(1);
} 


$in = $_GET['message'];
if ($in === '') {
	echo "empty input\n";
	exit(1);
} else if ($in[-1] !== "\n") {
	$in .= "\n";
}

socket_write($socket, $in, strlen($in));

echo "message:( $in ) sent successfully\n";
socket_close($socket);

?>
