<?php
// demo-path-traversal/scripts/get_file.php

$filename = $_GET['file'] ?? 'none';
echo "You tried to get file: " . htmlspecialchars($filename);
?>
